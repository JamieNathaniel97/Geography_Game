// The History games (History_games.md; jobs/history_games.md): H1 historical figures, H2 famous battles, H3 famous
// shipwrecks. Two kinds of game for each:
//   "where": a person, battle or ship comes up; tap where (H1: where they were born, then where they died)
//   "which": the symbols are shown on the map; name the person, battle or ship (typing, or 4 choices)
// Shared: distance scoring (100 within 20 km, 1 at 20,000 km, log scale), Hint (zooms to the area, halves the
// round), rounds of 10, 20, 50 or the whole set (Marathon), personal bests, and the end-of-game summary.
// The app (js/app.js) starts a game with GG.History.start(cfg, api); the map (js/mapview.js) draws this file's marks
// through main.overlay, and passes taps to GG.History.onPoint.
(function () {
  const GG = (window.GG = window.GG || {});
  const $ = id => document.getElementById(id);
  const esc = s => String(s).replace(/[&<>"]/g, ch => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[ch]));
  const R_EARTH = 6371;

  // ---------- the games ----------
  const TOPICS = {
    people: { file: "data/people.json", noun: "person", nouns: "people", title: "Historical figures",
      kinds: [["all", "All"], ["leader", "Leaders"], ["scientist", "Scientists and inventors"], ["artist", "Artists and architects"],
        ["writer", "Writers and poets"], ["composer", "Composers and musicians"], ["philosopher", "Philosophers"], ["explorer", "Explorers"]],
      kindLabel: "Kind", whichBtn: "Who?", levels: true,
      where: "Where were they born, and where did they die?", which: "Who is it?" },
    battles: { file: "data/battles.json", noun: "battle", nouns: "battles", title: "Famous battles",
      kinds: [["all", "All"], ["land", "Land"], ["naval", "Naval"], ["siege", "Sieges"]],
      kindLabel: "Type", whichBtn: "Which battle?",
      where: "Where was it fought?", which: "Which battle was it?" },
    wrecks: { file: "data/wrecks.json", noun: "ship", nouns: "shipwrecks", title: "Famous shipwrecks",
      kinds: [["all", "All"], ["war", "Sunk in war"], ["peace", "Sunk in peace"]],
      kindLabel: "Type", whichBtn: "Which ship?", eras: ["all", "early", "1800s", "1900s"], // (too few ancient or medieval wrecks)
      where: "Where did it sink?", which: "Which ship was it?" },
  };
  const ERAS = [["all", "All"], ["ancient", "Ancient (before 500)"], ["medieval", "Medieval (500–1500)"], ["early", "1500–1800"],
    ["1800s", "1800s"], ["1900s", "1900 and later"]];
  const eraOf = y => (y < 500 ? "ancient" : y < 1500 ? "medieval" : y < 1800 ? "early" : y < 1900 ? "1800s" : "1900s");
  const yearText = y => (y < 0 ? `${-y} BC` : String(y));

  // ---------- scoring ----------
  // 100 within 20 km; 1 at 20,000 km (the far side of the Earth); a log scale in between
  const score = d => (d <= 20 ? 100 : Math.max(1, Math.round(100 - 99 * Math.log(d / 20) / Math.log(1000))));
  const km = (a, b) => d3.geoDistance(a, b) * R_EARTH;
  // distance to a battle's area: 0 inside, else to its nearest edge point
  function kmToArea(ll, area) {
    if (d3.geoContains(area, ll)) return 0;
    let best = Infinity;
    const walk = c => { if (typeof c[0] === "number") best = Math.min(best, km(ll, c)); else c.forEach(walk); };
    walk(area.geometry ? area.geometry.coordinates : area.coordinates);
    return best;
  }
  const fmtKm = d => (d < 1 ? "spot on" : d < 10 ? `${d.toFixed(1)} km away` : `${Math.round(d).toLocaleString("en-GB")} km away`);

  // ---------- forgiving names for "which" games ----------
  const SHIP_PREFIX = /^(rms|hms|ss|uss|mv|ms|hmhs|hmas|hmcs|sms|km|rv|ssn|ts|mts)\s+/i;
  function namesOf(topic, it) {
    const n = it.name.replace(/\s*\(.*\)\s*$/, "");
    const out = [n];
    if (topic === "people") { const parts = n.split(/\s+/); if (parts.length > 1) out.push(parts[parts.length - 1]); }
    if (topic === "battles") out.push(n.replace(/^(battle|siege|sack|bombing|raid|attack|fall|capture)\s+(of|on|at)\s+(the\s+)?/i, ""));
    if (topic === "wrecks") out.push(n.replace(SHIP_PREFIX, ""));
    return [...new Set(out.concat(it.also || []))].filter(Boolean);
  }

  // ---------- state ----------
  let api = null, cfg = null, T = null, items = [], rounds = [], round = 0, total = 0, results = [], phase = "idle";
  let guesses = [], hinted = false, typed = null;
  const data = {};

  async function load(topic) {
    if (!data[topic]) {
      const r = await fetch(TOPICS[topic].file);
      if (!r.ok) throw new Error("no data");
      data[topic] = await r.json();
    }
    return data[topic];
  }
  // which items a game draws from: kind, era, region (the continent boxes of the app's regions)
  function pick(all, c = cfg) {
    const cfg = c; // (the menu counts what each choice would give: GG.History.count)
    const inBox = (ll, box) => !box || (ll && ll[0] >= box[0][0] && ll[0] <= box[1][0] && ll[1] >= box[0][1] && ll[1] <= box[1][1]);
    return all.filter(it => {
      if (cfg.topic === "people" && cfg.level && (it.level || "obscure") !== (cfg.level === "easy" ? "famous" : "obscure")) return false;
      const y = cfg.topic === "people" ? it.born : it.year;
      if (cfg.era !== "all" && eraOf(y) !== cfg.era) return false;
      if (cfg.kind !== "all") {
        if (cfg.topic === "people" && it.kind !== cfg.kind) return false;
        if (cfg.topic === "battles" && (cfg.kind === "naval" ? !it.naval : cfg.kind === "siege" ? !it.siege : it.naval || it.siege)) return false;
        if (cfg.topic === "wrecks" && (cfg.kind === "war") !== !!it.war) return false;
      }
      const lls = cfg.topic === "people" ? [it.bll, it.dll] : [it.ll];
      return lls.every(ll => ll) && lls.some(ll => inBox(ll, cfg.box));
    });
  }

  // ---------- starting and ending ----------
  GG.History = {
    TOPICS, ERAS,
    // how many a choice would give (the menu greys out choices with too few: fewer than 4)
    async count(c) { try { return pick(await load(c.topic), c).length; } catch (e) { return 0; } },
    MIN: 4,
    async start(c, a) {
      api = a; cfg = c; T = TOPICS[cfg.topic];
      let all;
      try { all = await load(cfg.topic); } catch (e) { api.toast(`The ${T.nouns} aren't ready yet`, 3000); return false; }
      items = pick(all);
      if (items.length < 4) { api.toast(`Not enough ${T.nouns} for that choice: try All`, 3000); return false; }
      rounds = d3.shuffle(items.slice()).slice(0, cfg.length === "all" ? items.length : +cfg.length);
      round = 0; total = 0; results = [];
      api.main.overlay = draw; api.main.noMarkers = true;
      $("histBar").hidden = false;
      newRound();
      return true;
    },
    onPoint(view, x, y) {
      if (phase !== "where") return true;   // between rounds, taps do nothing (but are used up)
      const ll = view.lonLatAt(x, y);
      if (!ll) return true;
      guesses.push(ll);
      if (guesses.length >= (cfg.topic === "people" ? 2 : 1)) reveal(); else { prompt(); api.main.requestDraw(); }
      return true;
    },
    stop() { phase = "idle"; if (api) { api.main.overlay = null; api.main.noMarkers = false; api.main.requestDraw(); } $("histBar").hidden = true; $("histEnd").hidden = true; $("histScore").hidden = true; },
    active: () => phase !== "idle",
  };

  // the points: on the map, top left (the score row under the banner is left free for a long name's second line)
  function setScore() {
    $("score").textContent = "";
    $("histScore").innerHTML = `Round <b>${round + 1}</b> of ${rounds.length}<br><b>${total}</b> points`;
    $("histScore").hidden = false;
  }
  // ---------- a round ----------
  const it = () => rounds[round];
  function newRound() {
    guesses = []; hinted = false; typed = null;
    phase = cfg.game === "where" ? "where" : "which";
    $("histHint").hidden = cfg.game !== "where"; $("histHint").disabled = false;
    $("histNext").hidden = true;
    $("histChoices").innerHTML = ""; $("histChoices").hidden = true;
    $("histInput").hidden = true; $("histInput").value = "";
    $("histCard").hidden = true;
    api.unlockZoom();
    if (cfg.game === "where") api.home();
    else fitTo(answerPoints(), 0.5);
    if (cfg.game === "which") setupAnswer();
    api.lockZoom(cfg.game === "where");
    prompt();
    api.main.requestDraw();
  }
  function answerPoints() { const x = it(); return cfg.topic === "people" ? [x.bll, x.dll] : [x.ll]; }
  function fitTo(pts, padFrac, minDeg = 6) {
    const lons = pts.map(p => p[0]), lats = pts.map(p => p[1]);
    let w = Math.min(...lons), e = Math.max(...lons), s = Math.min(...lats), n = Math.max(...lats);
    const span = Math.max(e - w, n - s, minDeg), pad = span * padFrac;
    w -= pad; e += pad; s -= pad; n += pad;
    const cx = (w + e) / 2, cy = (s + n) / 2, half = Math.max(e - w, n - s) / 2;
    api.main.fitBox([[cx - half, Math.max(-85, cy - half)], [cx + half, Math.min(85, cy + half)]]);
  }
  // Wikidata's descriptions often end with the years, "(1882–1971)", which the prompt already shows
  const plainDesc = d => (d || "").replace(/\s*\([^()]*\d{3,4}[^()]*\)\s*$/, "");
  function prompt() {
    const x = it(), where = cfg.game === "where";
    let step = where ? T.where : T.which;
    if (where && phase === "where" && cfg.topic === "people") step = guesses.length ? "Now tap where they died" : "Tap where they were born";
    $("eyebrow").innerHTML = `${esc(T.title)}<span class="beta">Beta</span> · ${esc(step)}`;
    let t;
    if (cfg.topic === "people") t = where ? `${x.name} · ${yearText(x.born)}–${yearText(x.died)}` : "Who was born and died here?";
    else if (cfg.topic === "battles") t = where ? `${x.name} · ${yearText(x.year)}${x.end && x.end !== x.year ? "–" + yearText(x.end) : ""}` : `⚔ ${yearText(x.year)}: which battle?`;
    else t = where ? `${x.name} · ${yearText(x.year)}` : `Sunk in ${yearText(x.year)}: which ship?`;
    $("target").textContent = t;
    $("target").hidden = false;
    setScore();
  }

  // Hint: zoom to the area (a generous frame, slightly random, so the frame doesn't give the answer away); halves the round
  function hint() {
    if (phase !== "where" || hinted) return;
    hinted = true; $("histHint").disabled = true;
    const pts = answerPoints(), lons = pts.map(p => p[0]), lats = pts.map(p => p[1]);
    const cx = (Math.min(...lons) + Math.max(...lons)) / 2, cy = (Math.min(...lats) + Math.max(...lats)) / 2;
    const span = Math.max(14, (Math.max(...lons) - Math.min(...lons)) * 1.8, (Math.max(...lats) - Math.min(...lats)) * 1.8);
    const jx = (Math.random() - 0.5) * span * 0.4, jy = (Math.random() - 0.5) * span * 0.4;
    api.unlockZoom();
    api.main.fitBox([[cx + jx - span / 2, Math.max(-85, cy + jy - span / 2)], [cx + jx + span / 2, Math.min(85, cy + jy + span / 2)]]);
    setTimeout(() => api.lockZoom(true), 900);
    api.toast("Hint: this round is worth half", 1800);
  }

  // the answer: symbols, lines, distances, the round's score
  function reveal() {
    const x = it();
    let pts, dists;
    if (cfg.topic === "people") { dists = [km(guesses[0], x.bll), km(guesses[1], x.dll)]; pts = dists.map(score); }
    else if (cfg.topic === "battles" && x.area) { dists = [kmToArea(guesses[0], x.area)]; pts = dists.map(score); }
    else { dists = [km(guesses[0], x.ll)]; pts = dists.map(score); }
    let s = Math.round(pts.reduce((a, b) => a + b, 0) / pts.length);
    if (hinted) s = Math.round(s / 2);
    total += s;
    results.push({ item: x, score: s, dist: dists.reduce((a, b) => a + b, 0) / dists.length, hinted });
    phase = "shown";
    api.unlockZoom();
    fitTo(guesses.concat(answerPoints()), 0.25, 4);
    $("histHint").hidden = true;
    $("target").textContent = `${x.name}: ${dists.map(fmtKm).join(" · ")} → ${s} points${hinted ? " (hint)" : ""}`;
    setScore();
    showCard(x);
    $("histNext").hidden = false;
    $("histNext").textContent = round + 1 < rounds.length ? "Next ›" : "See results ›";
    api.main.requestDraw();
  }

  // "which": type the name, or choose from 4 (others of the same kind and era)
  function setupAnswer() {
    const x = it();
    if (cfg.mc === "on") {
      const same = items.filter(o => o !== x && (cfg.topic !== "people" || o.kind === x.kind) &&
        eraOf(cfg.topic === "people" ? o.born : o.year) === eraOf(cfg.topic === "people" ? x.born : x.year));
      const pool = d3.shuffle((same.length >= 1 ? same : items.filter(o => o !== x)).slice()).slice(0, 1); // two answers: the right one and one other
      const opts = d3.shuffle(pool.concat([x]));
      $("histChoices").innerHTML = opts.map((o, i) => `<button type="button" data-i="${i}">${esc(o.name)}</button>`).join("");
      $("histChoices").hidden = false;
      $("histChoices").onclick = e => {
        const b = e.target.closest("button"); if (!b || phase !== "which") return;
        const o = opts[+b.dataset.i];
        b.classList.add(o === x ? "good" : "bad");
        if (o !== x) $("histChoices").querySelectorAll("button").forEach((bb, i) => { if (opts[i] === x) bb.classList.add("good"); });
        answered(o === x);
      };
    } else {
      const inp = $("histInput");
      inp.hidden = false; inp.placeholder = `Type the ${T.noun === "person" ? "name" : T.noun === "ship" ? "ship's name" : "battle"}`;
      setTimeout(() => inp.focus(), 50);
      inp.oninput = () => {
        if (phase !== "which") return;
        const m = GG.nameMatches({ names: namesOf(cfg.topic, x), name: x.name }, inp.value, "names");
        if (m) answered(true, m);
      };
    }
  }
  function answered(right, m) {
    const x = it(), s = right ? 100 : 0;
    total += s;
    results.push({ item: x, score: s, right });
    phase = "shown";
    $("histInput").blur();
    $("target").textContent = right ? `Right: ${x.name}${m && !m.exact ? ` (you typed “${$("histInput").value.trim()}”)` : ""}` : `It was ${x.name}`;
    setScore();
    showCard(x);
    $("histNext").hidden = false;
    $("histNext").textContent = round + 1 < rounds.length ? "Next ›" : "See results ›";
  }
  function giveUpRound() {
    if (phase === "which") { answered(false); return true; }
    return false;
  }

  // the card under the map: the facts, plainly
  function showCard(x) {
    const rows = [];
    if (cfg.topic === "people") {
      rows.push(["Born", `${x.bp || "?"}, ${yearText(x.born)}`], ["Died", `${x.dp || "?"}, ${yearText(x.died)}`]);
    } else if (cfg.topic === "battles") {
      // who fought, who won, the losses on each side, and the war (from the Wikipedia infobox: tools/history_wiki.py)
      const side = t => (t || "").split(", ")[0].replace(/…$/, "").slice(0, 34);
      rows.push(["When", yearText(x.year) + (x.end && x.end !== x.year ? "–" + yearText(x.end) : "")]);
      if (x.war) rows.push(["War", x.war]);
      if (x.sides && x.sides.length === 2) rows.push(["Fought", `${x.sides[0]} vs ${x.sides[1]}`]);
      if (x.result) rows.push(["Result", x.result]);
      else if (x.winners && x.winners.length) rows.push(["Won by", x.winners.join(", ")]);
      if (x.strength && x.strength.some(Boolean) && x.sides && x.sides.length === 2)
        rows.push(["Strength", x.strength.map((v, i) => v ? `${side(x.sides[i])}: ${v}` : "").filter(Boolean).join(" · ")]);
      if (x.losses && x.losses.some(Boolean) && x.sides && x.sides.length === 2)
        rows.push(["Losses", x.losses.map((v, i) => v ? `${side(x.sides[i])}: ${v}` : "").filter(Boolean).join(" · ")]);
    } else {
      rows.push(["Sank", yearText(x.year)]);
      if (x.cause) rows.push(["How it sank", x.cause]);
      if (x.warName) rows.push(["War", x.warName]);
      rows.push(["Lives lost", x.deaths === 0 ? "No lives lost" : x.deaths ? x.deaths.toLocaleString("en-GB") : "Not known"]);
      if (x.found) rows.push(["Wreck found", String(x.found)]);
      if (x.raised) rows.push(["Raised", typeof x.raised === "string" ? x.raised : "Yes: the ship is now ashore"]);
      if (x.grave) rows.push(["War grave", "Yes: protected as a war grave"]);
    }
    // portraits (people): data/people/<id>.webp, with the picture's credit and licence (tools/build_people.py --images)
    const src = (window.GG_PORTRAITS && window.GG_PORTRAITS[x.id]) || `data/people/${x.id}.webp`; // (the preview build carries them in the page)
    const img = x.img ? `<img src="${esc(src)}" alt="" loading="lazy"><small>${esc([x.img.credit, x.img.licence].filter(Boolean).join(" · "))}</small>` : "";
    $("histCard").innerHTML = `<div class="hcimg">${img}</div><div><b>${esc(x.name)}</b>${x.desc ? `<p>${esc(plainDesc(x.desc))}</p>` : ""}` +
      rows.map(([k, v]) => `<div class="hcrow"><span>${esc(k)}</span><span>${esc(v)}</span></div>`).join("") + `</div>`;
    $("histCard").hidden = false;
  }

  function next() {
    if (phase !== "shown") return;
    round++;
    if (round >= rounds.length) { end(); return; }
    newRound();
  }
  function end(gaveUp) {
    phase = "done";
    api.unlockZoom();
    const n = results.length || 1, maxPts = rounds.length * 100;
    const where = cfg.game === "where", dists = results.filter(r => r.dist !== undefined);
    const best = where && dists.length ? dists.reduce((a, b) => (b.dist < a.dist ? b : a)) : null;
    const worst = where && dists.length ? dists.reduce((a, b) => (b.dist > a.dist ? b : a)) : null;
    const key = `${cfg.topic}.${cfg.game}.${cfg.length}`;
    let pb = {};
    try { pb = JSON.parse(localStorage.getItem("gg.hist.v1") || "{}"); } catch (e) { /* no storage */ }
    const value = cfg.length === "all" ? Math.round(total / n) : total;
    const isBest = !gaveUp && (pb[key] === undefined || value > pb[key]);
    if (isBest) { pb[key] = value; try { localStorage.setItem("gg.hist.v1", JSON.stringify(pb)); } catch (e) { /* no storage */ } }
    $("histEnd").innerHTML = `<h3>${esc(T.title)}</h3>
      <p class="big"><b>${total.toLocaleString("en-GB")}</b> of ${maxPts.toLocaleString("en-GB")}${isBest ? ' <span class="pb">New best!</span>' : ""}</p>
      <p>Average ${Math.round(total / n)} a round${where && dists.length ? ` · average distance ${Math.round(dists.reduce((a, r) => a + r.dist, 0) / dists.length).toLocaleString("en-GB")} km` : ""}</p>
      ${best ? `<p>Best: ${esc(best.item.name)} (${fmtKm(best.dist)})<br>Worst: ${esc(worst.item.name)} (${fmtKm(worst.dist)})</p>` : ""}
      ${!where ? `<p>${results.filter(r => r.right).length} of ${rounds.length} right</p>` : ""}
      <div class="row"><button class="btn primary" id="histAgain" type="button">Play again</button><button class="btn" id="histMenu" type="button">Menu</button></div>`;
    $("histEnd").hidden = false;
    $("histAgain").onclick = () => { $("histEnd").hidden = true; GG.History.start(cfg, api); };
    $("histMenu").onclick = () => { $("histEnd").hidden = true; api.openMenu(); };
    $("histNext").hidden = true; $("histHint").hidden = true;
    $("target").textContent = `Finished: ${total} points`;
  }

  // ---------- drawing: guesses (green, then red), answers (symbols), lines, areas ----------
  function draw(ctx, pt, proj) {
    if (phase === "idle" || !rounds.length || round >= rounds.length) return;
    const x = it(), col = api.main.col, path = d3.geoPath(proj, ctx);
    const showAnswer = phase === "shown" || phase === "which" || phase === "done";
    // a battle's area
    if (cfg.topic === "battles" && x.area && showAnswer) {
      ctx.beginPath(); path(x.area); ctx.globalAlpha = 0.3; ctx.fillStyle = col.bad; ctx.fill(); ctx.globalAlpha = 1;
      ctx.lineWidth = 1.5; ctx.strokeStyle = col.bad; ctx.stroke();
    }
    const answers = answerPoints();
    // lines from each guess to its answer
    if (phase === "shown" && cfg.game === "where") {
      ctx.setLineDash([5, 4]); ctx.lineWidth = 1.5; ctx.strokeStyle = col.fg;
      guesses.forEach((g, i) => { ctx.beginPath(); path({ type: "LineString", coordinates: [g, answers[Math.min(i, answers.length - 1)]] }); ctx.stroke(); });
      ctx.setLineDash([]);
    }
    // the guesses: first green, second red (H1: birth, then death)
    guesses.forEach((g, i) => {
      const p = pt(g); if (!p) return;
      ctx.beginPath(); ctx.arc(p[0], p[1], 7, 0, 2 * Math.PI);
      ctx.fillStyle = i === 0 ? col.good : col.bad; ctx.fill(); ctx.lineWidth = 2; ctx.strokeStyle = "#fff"; ctx.stroke();
    });
    if (!showAnswer) return;
    // the answer symbols, with their labels
    const syms = cfg.topic === "people" ? [["baby", x.bll, `${x.bp || ""}, ${yearText(x.born)}`], ["skull", x.dll, `${x.dp || ""}, ${yearText(x.died)}`]]
      : cfg.topic === "battles" ? [[x.naval ? "anchor" : x.siege ? "castle" : "swords", x.ll, yearText(x.year)]]
      : [["wreck", x.ll, yearText(x.year)]];
    // labels: the birth place's under its symbol, the death place's above (so two close places don't overlap)
    syms.forEach(([kind, ll, text]) => {
      const p = pt(ll); if (!p) return;
      symbol(ctx, kind, p[0], p[1], col);
      const above = kind === "skull", y = above ? p[1] - 15 : p[1] + 15;
      ctx.font = "600 12px Barlow, system-ui, sans-serif"; ctx.textAlign = "center"; ctx.textBaseline = above ? "bottom" : "top";
      ctx.lineWidth = 3; ctx.strokeStyle = col.halo || col.panel; ctx.strokeText(text, p[0], y);
      ctx.fillStyle = col.fg; ctx.fillText(text, p[0], y);
    });
  }
  // small drawn symbols (not emoji, so they look the same everywhere): baby, skull, crossed swords, anchor, castle, wreck
  function symbol(ctx, kind, x, y, col) {
    ctx.save(); ctx.translate(x, y);
    ctx.beginPath(); ctx.arc(0, 0, 13, 0, 2 * Math.PI); ctx.fillStyle = col.panel || "#fff"; ctx.fill();
    ctx.lineWidth = 2; ctx.strokeStyle = col.fg; ctx.stroke();
    ctx.fillStyle = col.fg; ctx.strokeStyle = col.fg; ctx.lineWidth = 1.6; ctx.lineCap = "round";
    if (kind === "baby") {
      ctx.beginPath(); ctx.arc(0, 1, 7, 0, 2 * Math.PI); ctx.stroke();                 // face
      ctx.beginPath(); ctx.arc(-2.5, 0, 1, 0, 2 * Math.PI); ctx.arc(2.5, 0, 1, 0, 2 * Math.PI); ctx.fill(); // eyes
      ctx.beginPath(); ctx.arc(0, 3, 2, 0.15 * Math.PI, 0.85 * Math.PI); ctx.stroke(); // smile
      ctx.beginPath(); ctx.moveTo(0, -6); ctx.quadraticCurveTo(3, -9, 1, -10); ctx.stroke(); // curl
    } else if (kind === "skull") {
      ctx.beginPath(); ctx.arc(0, -1.5, 6.5, Math.PI * 0.85, Math.PI * 2.15); ctx.lineTo(3.5, 7); ctx.lineTo(-3.5, 7); ctx.closePath(); ctx.fill();
      ctx.fillStyle = col.panel || "#fff";
      ctx.beginPath(); ctx.arc(-2.6, -1, 1.8, 0, 2 * Math.PI); ctx.arc(2.6, -1, 1.8, 0, 2 * Math.PI); ctx.fill();
      ctx.fillRect(-0.6, 2, 1.2, 2.2);
    } else if (kind === "swords") {
      [[-1, 1], [1, 1]].forEach(([sx]) => {
        ctx.beginPath(); ctx.moveTo(-7 * sx, -7); ctx.lineTo(6 * sx, 6); ctx.stroke();
        ctx.beginPath(); ctx.moveTo(2.5 * sx, 6.5); ctx.lineTo(6.5 * sx, 2.5); ctx.stroke();
      });
    } else if (kind === "anchor") {
      ctx.beginPath(); ctx.arc(0, -6, 2, 0, 2 * Math.PI); ctx.stroke();
      ctx.beginPath(); ctx.moveTo(0, -4); ctx.lineTo(0, 7); ctx.moveTo(-4, -1); ctx.lineTo(4, -1); ctx.stroke();
      ctx.beginPath(); ctx.arc(0, 1, 6, 0.15 * Math.PI, 0.85 * Math.PI); ctx.stroke();
    } else if (kind === "castle") {
      ctx.beginPath(); ctx.moveTo(-7, 7); ctx.lineTo(-7, -5); ctx.lineTo(-4.5, -5); ctx.lineTo(-4.5, -2); ctx.lineTo(-1.5, -2); ctx.lineTo(-1.5, -5);
      ctx.lineTo(1.5, -5); ctx.lineTo(1.5, -2); ctx.lineTo(4.5, -2); ctx.lineTo(4.5, -5); ctx.lineTo(7, -5); ctx.lineTo(7, 7); ctx.closePath(); ctx.fill();
      ctx.fillStyle = col.panel || "#fff"; ctx.beginPath(); ctx.arc(0, 4, 2.2, Math.PI, 0); ctx.lineTo(2.2, 7); ctx.lineTo(-2.2, 7); ctx.fill();
    } else { // a sunken ship: a hull tilted under a wave line
      ctx.beginPath(); ctx.moveTo(-8, -6); ctx.quadraticCurveTo(-4, -8, 0, -6); ctx.quadraticCurveTo(4, -4, 8, -6); ctx.stroke();
      ctx.save(); ctx.rotate(-0.35);
      ctx.beginPath(); ctx.moveTo(-7, 1); ctx.lineTo(7, 1); ctx.lineTo(4.5, 5.5); ctx.lineTo(-5, 5.5); ctx.closePath(); ctx.fill();
      ctx.fillRect(-1, -3, 2, 4);
      ctx.restore();
    }
    ctx.restore();
  }

  // buttons
  document.addEventListener("DOMContentLoaded", () => {
    $("histHint").onclick = hint;
    $("histNext").onclick = next;
  });
  GG.History.giveUp = () => { if (!giveUpRound()) end(true); };
  GG.History.score = score; // (for tests)
})();
