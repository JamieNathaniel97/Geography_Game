// Forgiving name matching for the naming games (PLAN.md, game 2). What you type is only ever compared with
// the country you tapped, so being forgiving can never accept the wrong country.
//  - capitals, accents, punctuation, spaces and a leading "the" are ignored
//  - "&" = "and", "St" / "St." = "Saint"
//  - any of the country's accepted names counts (common, official, short forms like UK, USA, UAE)
//  - one typo (a wrong, missing, extra or swapped letter) is allowed in names of 6 or more letters,
//    but not just for leaving off the end of the name
(function () {
  const GG = (window.GG = window.GG || {});

  GG.normName = function (s) {
    return s.normalize("NFD").replace(/[\u0300-\u036f]/g, "") // drop accents
      .toLowerCase()
      .replace(/&/g, " and ")
      .replace(/[^a-z0-9]+/g, " ")
      .replace(/\bst\b/g, "saint")
      .trim()
      .replace(/^the /, "")
      .replace(/ /g, "");
  };

  // Damerau-Levenshtein distance, stopping early once it's clearly more than `max`
  function distance(a, b, max) {
    if (Math.abs(a.length - b.length) > max) return max + 1;
    const prev2 = [], prev = [], cur = [];
    for (let j = 0; j <= b.length; j++) prev[j] = j;
    for (let i = 1; i <= a.length; i++) {
      cur[0] = i;
      let rowMin = cur[0];
      for (let j = 1; j <= b.length; j++) {
        const cost = a[i - 1] === b[j - 1] ? 0 : 1;
        let v = Math.min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + cost);
        if (i > 1 && j > 1 && a[i - 1] === b[j - 2] && a[i - 2] === b[j - 1]) v = Math.min(v, prev2[j - 2] + 1);
        cur[j] = v;
        if (v < rowMin) rowMin = v;
      }
      if (rowMin > max) return max + 1;
      for (let j = 0; j <= b.length; j++) { prev2[j] = prev[j]; prev[j] = cur[j]; }
    }
    return prev[b.length];
  }

  // Does `typed` name country c? Returns null, or { exact, name } where `name` is the accepted spelling it
  // matched (so a misspelling can be shown with the right spelling).
  GG.nameMatches = function (c, typed) {
    const t = GG.normName(typed);
    if (!t) return null;
    const names = c.names || [c.name];
    if (!c._norm) c._norm = names.map(GG.normName);
    const exact = c._norm.indexOf(t);
    if (exact >= 0) return { exact: true, name: names[exact] };
    // one typo; a name you're still typing (the start of the right name) isn't counted early
    const i = c._norm.findIndex(n => n.length >= 6 && !n.startsWith(t) && distance(t, n, 1) <= 1);
    return i >= 0 ? { exact: false, name: names[i] } : null;
  };
})();
