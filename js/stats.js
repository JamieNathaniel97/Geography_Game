// Progress tracking, kept on the phone (localStorage). PLAN.md, "Progress and learning".
//
//  countries: { [skill]: { [iso]: { a: times asked, c: times right, t: last seen (ms) } } }
//     skill "country" = Find countries + Name countries; skill "capital" = Find by capital + Name capitals
//  bests:     { "<mode>|<region>": { pct, secs, date } }   best score, then fastest time at that score
//  games:     [ { mode, region, score, total, secs, date, gaveUp } ]   the last 100 games, newest first
(function () {
  const GG = (window.GG = window.GG || {});
  const KEY = "gg.stats.v1";
  const empty = () => ({ countries: { country: {}, capital: {}, flag: {} }, bests: {}, games: [] });
  let data = empty();
  try { const s = JSON.parse(localStorage.getItem(KEY)); if (s && s.countries) data = Object.assign(empty(), s); } catch (e) { /* fresh start */ }
  data.countries.flag = data.countries.flag || {}; // added with the flag games
  const save = () => { try { localStorage.setItem(KEY, JSON.stringify(data)); } catch (e) { /* storage full or blocked */ } };

  const skillOf = mode => (mode === "findcap" || mode === "namecap" ? "capital" : mode === "findflag" || mode === "nameflag" ? "flag" : "country");

  GG.Stats = {
    skillOf,
    // one answer: right = right first time (Find) or named (Name)
    answer(mode, iso, right) {
      const s = data.countries[skillOf(mode)], e = s[iso] || (s[iso] = { a: 0, c: 0, t: 0 });
      e.a++; if (right) e.c++; e.t = Date.now();
      save();
    },
    // a finished game; returns true if it's a new personal best for this game and region
    game(mode, region, score, total, secs, gaveUp, weak) {
      const pct = Math.round(100 * score / Math.max(1, total)), key = mode + "|" + region, best = data.bests[key];
      // knowledge gaps games are a different set of questions, so they don't count for personal bests
      const isBest = !weak && (!best || pct > best.pct || (pct === best.pct && secs < best.secs));
      if (isBest) data.bests[key] = { pct, secs, date: Date.now() };
      data.games.unshift({ mode, region, score, total, secs, date: Date.now(), gaveUp: !!gaveUp, weak: !!weak });
      data.games.length = Math.min(data.games.length, 100);
      save();
      return isBest && !!best; // "new best" only when there was one to beat
    },
    entry(skill, iso) { return data.countries[skill][iso] || null; },
    bests() { return data.bests; },
    games() { return data.games; },
    reset() { data = empty(); save(); },
  };
})();
