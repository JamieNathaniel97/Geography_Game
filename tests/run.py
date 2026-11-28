"""Gaia Quest's tests: the real app in headless Chrome, driven by the suites in tests/suites/, plus a few file checks.

  python tests/run.py                 the quick set (about 2 minutes): files, smoke, menu, fixes, back, earth, perf
  python tests/run.py --full          also every country map (tests/suites/maps.js, one page per map: about 30 minutes)
  python tests/run.py earth menu      just those suites
  python tests/run.py --maps at,es    just those country maps
  python tests/run.py --online        also the live earthquake feed (needs the internet)
  options: -v (show every check and note), --jobs N (pages at once, default 3), --update-baseline, --chrome PATH,
           --keep-going (a suite's fail doesn't stop the run; it never does: every suite runs, the summary lists fails)

How it works: a small web server serves the repo; /__test__<suite>.html is index.html with tests/harness.js and the
suite added, so the suite drives the app itself. Each page opens in its own headless Chrome (a fresh profile, 390x844,
a phone's size). Suites report passes, fails and metrics to /_t. Metrics are compared with tests/baseline.json: a
number may not drop below its baseline (accuracy, counts), and text must match. --update-baseline saves the current
ones (do that only after checking a change is meant). Exit code 0 if everything passed.
"""
import argparse
import http.server
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

ROOT = pathlib.Path(__file__).resolve().parent.parent
TESTS = ROOT / "tests"
BASELINE = TESTS / "baseline.json"
QUICK = ["smoke", "menu", "fixes", "back", "earth", "perf"]
ALONE = {"perf"}  # suites run on their own after the others (timings)
TIMEOUT = {"smoke": 150, "menu": 200, "fixes": 200, "back": 150, "earth": 300, "perf": 300, "maps": 600, "quakes": 60}
CHROMES = [os.environ.get("CHROME", ""), r"C:\Program Files\Google\Chrome\Application\chrome.exe",
           r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
           "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "/usr/bin/google-chrome", "/usr/bin/chromium"]

RUNDIR = TESTS / ".runs"  # each page's messages, one JSON line each (git-ignored); the server writes, the runner reads


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=str(ROOT), **k)

    def log_message(self, fmt, *a):
        if os.environ.get("GQ_TEST_LOG"):
            with open(os.environ["GQ_TEST_LOG"], "a", encoding="utf8") as f:
                f.write((fmt % a) + "\n")

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def do_GET(self):
        url = urllib.parse.urlparse(self.path)
        if url.path == "/_t":
            q = urllib.parse.parse_qs(url.query)
            run = re.sub(r"[^A-Za-z0-9_.-]", "_", q.get("run", ["unknown"])[0])
            with open(RUNDIR / (run + ".jsonl"), "a", encoding="utf8") as f:
                f.write(json.dumps([q.get("k", [""])[0], q.get("m", [""])[0]]) + "\n")
            self.send_response(204); self.end_headers(); return
        m = re.fullmatch(r"/__test__([a-z0-9_-]+)\.html", url.path)
        if m:
            suite = TESTS / "suites" / (m.group(1) + ".js")
            if not suite.exists():
                self.send_error(404); return
            page = (ROOT / "index.html").read_text(encoding="utf8")
            if m.group(1) == "quakes":  # (a page of its own: the module, not the app)
                page = '<!doctype html><meta charset="utf-8"><body></body>'
            tags = f'<script src="tests/harness.js"></script><script src="tests/suites/{m.group(1)}.js"></script>'
            page = page.replace("</body>", tags + "</body>")
            # errors from the very start (a script that doesn't parse runs before the harness): kept for the harness
            early = "<script>window.__gqErrors=[];addEventListener('error',e=>__gqErrors.push(e.message+' @ '+(e.filename||'').split('/').pop()+':'+e.lineno));</script>"
            page = page.replace("<head>", "<head>" + early, 1) if "<head>" in page else early + page
            data = page.encode("utf8")
            self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data))); self.end_headers(); self.wfile.write(data); return
        super().do_GET()


def find_chrome(arg):
    for c in [arg] + CHROMES:
        if c and pathlib.Path(c).exists():
            return c
    sys.exit("Chrome not found: pass --chrome PATH or set CHROME")


def messages(run):
    f = RUNDIR / (run + ".jsonl")
    if not f.exists():
        return []
    return [tuple(json.loads(l)) for l in f.read_text(encoding="utf8").splitlines() if l.strip()]


def run_page(chrome, port, suite, query, timeout):
    """One suite in its own headless Chrome; returns the messages it sent."""
    run = f"{suite}-{query.get('d', '')}-{time.time_ns()}"
    q = urllib.parse.urlencode({**query, "run": run})
    prof = tempfile.mkdtemp(prefix="gqtest_")
    p = subprocess.Popen([chrome, "--headless=new", f"--user-data-dir={prof}", "--window-size=390,844", "--hide-scrollbars",
                          "--no-first-run", "--no-default-browser-check", "--disable-gpu",
                          f"http://127.0.0.1:{port}/__test__{suite}.html?{q}"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    t0 = time.time()
    try:
        while time.time() - t0 < timeout:
            time.sleep(0.5)
            msgs = messages(run)
            if any(k == "done" for k, _ in msgs):
                break
        else:
            msgs = messages(run)
            msgs.append(("fail", f"timed out after {timeout} s (the suite didn't finish)"))
    finally:
        p.kill()
        if os.name == "nt":  # headless Chrome leaves helper processes; end the ones using this profile
            subprocess.run(["powershell", "-NoProfile", "-Command",
                            f"Get-CimInstance Win32_Process -Filter \"Name='chrome.exe'\" | Where-Object {{ $_.CommandLine -like '*{pathlib.Path(prof).name}*' }} | "
                            "ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }"], capture_output=True)
        time.sleep(0.5)
        shutil.rmtree(prof, ignore_errors=True)
    return msgs


def file_checks():
    """Checks that need no browser: the offline cache's file list, the page's scripts and styles."""
    out = []
    sw = (ROOT / "sw.js").read_text(encoding="utf8")
    shell = re.search(r"const SHELL = \[(.*?)\];", sw, re.S).group(1)
    files = [f for f in re.findall(r'"([^"]+)"', shell) if f != "./"]
    missing = [f for f in files if not (ROOT / f).exists()]
    out.append(("pass" if not missing else "fail", f"sw.js: all {len(files)} files in the offline cache exist" + (f" (missing: {', '.join(missing)})" if missing else "")))
    out.append(("pass" if re.search(r'const CACHE = "gaia-quest-v\d+";', sw) else "fail", "sw.js: CACHE is gaia-quest-v<number>"))
    page = (ROOT / "index.html").read_text(encoding="utf8")
    refs = re.findall(r'<script src="([^"]+)"', page) + re.findall(r'<link[^>]+href="([^"#]+\.css)"', page)
    bad = [r for r in refs if not r.startswith("http") and not (ROOT / r).exists()]
    out.append(("pass" if not bad else "fail", f"index.html: its {len(refs)} scripts and styles exist" + (f" (missing: {', '.join(bad)})" if bad else "")))
    js = [f for f in re.findall(r'<script src="(js/[^"]+)"', page)]
    uncached = [f for f in js if f not in files]
    out.append(("pass" if not uncached else "fail", "sw.js: every script the page loads is in the offline cache" + (f" (not cached: {', '.join(uncached)})" if uncached else "")))
    return out


def compare(metrics, base, label):
    """Metrics against the baseline: numbers mustn't drop, text must match. Returns (kind, message) list."""
    out = []
    for name, value in metrics:
        key = f"{label} · {name}"
        if key not in base:
            out.append(("info", f"new metric {key} = {value!r} (not in the baseline yet: --update-baseline saves it)"))
            continue
        want = base[key]
        if isinstance(want, (int, float)) and isinstance(value, (int, float)) and name.endswith("(ms)"):
            # a timing: lower is better; up to 30% slower (and half a millisecond) passes, as timings vary
            ok = value <= want * 1.3 + 0.5
            out.append(("pass" if ok else "fail", f"{key}: {value} ms (baseline {want} ms{'' if ok else ': slower'})"))
        elif isinstance(want, (int, float)) and isinstance(value, (int, float)):
            ok = value >= want - 1e-9
            out.append(("pass" if ok else "fail", f"{key}: {value} (baseline {want})"))
        else:
            out.append(("pass" if value == want else "fail", f"{key}: {value!r}" + ("" if value == want else f" (baseline {want!r})")))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("suites", nargs="*")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--maps")
    ap.add_argument("--online", action="store_true")
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--update-baseline", action="store_true")
    ap.add_argument("--chrome", default="")
    ap.add_argument("--port", type=int, default=8790)
    ap.add_argument("-v", action="store_true")
    ap.add_argument("--serve", action="store_true", help=argparse.SUPPRESS)  # (the server process the runner starts)
    a = ap.parse_args()
    RUNDIR.mkdir(exist_ok=True)
    if a.serve:
        http.server.ThreadingHTTPServer(("127.0.0.1", a.port), Handler).serve_forever()
        return
    chrome = find_chrome(a.chrome)
    for old in RUNDIR.glob("*.jsonl"):
        old.unlink()
    # the web server runs as its own process (in a thread of this one, Chrome's big data requests stalled)
    srv = subprocess.Popen([sys.executable, __file__, "--serve", "--port", str(a.port)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.5)

    jobs = []  # (label, suite, query)
    names = a.suites or ([] if a.maps else QUICK)
    if a.online and "quakes" not in names:
        names.append("quakes")
    for s in names:
        if s != "maps":
            jobs.append((s, s, {}))
    if a.full or a.maps or "maps" in names:
        # every country map: the app lists them (GG.debug.datasets) in a tiny first run
        msgs = run_page(chrome, a.port, "list", {}, 90)
        listed = [json.loads(m) for k, m in msgs if k == "metric"]
        maps = listed[0][1] if listed else []
        if a.maps:
            want = set(a.maps.split(","))
            maps = [d for d in maps if d[0] in want]
        jobs += [(f"maps:{d}", "maps", {"d": d, "r": r}) for d, r in maps]

    base = json.loads(BASELINE.read_text(encoding="utf8")) if BASELINE.exists() else {}
    results, new_base = [], dict(base)
    t0 = time.time()
    print(f"Gaia Quest tests: {len(jobs)} page(s), {a.jobs} at a time\n")
    files = file_checks()
    results.append(("files", files))
    report("files", files, a.v)

    def one(job):
        label, suite, query = job
        msgs = run_page(chrome, a.port, suite, query, TIMEOUT.get(suite, 300))
        # a page that fails is tried once more (a busy test machine can drop a request); a pass on the second try is
        # reported, so a test that keeps needing it can be looked at
        first = [m for k, m in msgs if k == "fail"]
        if first:
            again = run_page(chrome, a.port, suite, query, TIMEOUT.get(suite, 300))
            if not any(k == "fail" for k, _ in again):
                msgs = again + [("info", "FLAKY: passed on the second try; the first failed: " + " | ".join(first)[:300])]
        metrics = [json.loads(m) for k, m in msgs if k == "metric"]
        msgs = [(k, m) for k, m in msgs if k in ("pass", "fail", "info")] + compare(metrics, base, label)
        for name, value in metrics:
            new_base[f"{label} · {name}"] = value
        return label, msgs

    with ThreadPoolExecutor(max_workers=max(1, a.jobs)) as pool:
        for label, msgs in pool.map(one, [j for j in jobs if j[1] not in ALONE]):
            results.append((label, msgs))
            report(label, msgs, a.v)
    for job in [j for j in jobs if j[1] in ALONE]:
        label, msgs = one(job)
        results.append((label, msgs))
        report(label, msgs, a.v)

    fails = [(l, m) for l, ms in results for k, m in ms if k == "fail"]
    passes = sum(1 for _, ms in results for k, _ in ms if k == "pass")
    print(f"\n{passes} passed, {len(fails)} failed, in {time.time() - t0:.0f} s")
    for l, m in fails:
        print(f"  FAIL  {l}: {m}")
    if a.update_baseline:
        BASELINE.write_text(json.dumps(dict(sorted(new_base.items())), ensure_ascii=False, indent=1), encoding="utf8")
        print(f"baseline saved: {BASELINE.relative_to(ROOT)} ({len(new_base)} metrics)")
    srv.kill()
    sys.exit(1 if fails else 0)


def report(label, msgs, verbose):
    p = sum(1 for k, _ in msgs if k == "pass"); f = [m for k, m in msgs if k == "fail"]
    print(f"{'FAIL' if f else 'ok  '}  {label}: {p} passed" + (f", {len(f)} failed" if f else ""))
    for k, m in msgs:
        if verbose or k == "fail":
            print(f"        {k:5} {m}")
    sys.stdout.flush()


if __name__ == "__main__":
    sys.stdout.reconfigure(line_buffering=True, errors="replace")
    main()
