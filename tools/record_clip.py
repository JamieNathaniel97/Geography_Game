"""Records a page of the app as a smooth video, one frame at a time (Learning_mode_clip.md).

Headless Chrome is driven over its DevTools connection with the page's clock paused: each frame, virtual time moves on
by exactly 1/fps seconds, then a screenshot is taken. Slow frames can't stutter, so the video is always smooth.
ffmpeg joins the frames into WebM (for the app) and MP4 (a fallback), plus a poster image of the first frame.

  python tools/record_clip.py --url "http://localhost:8000/index.html?demo=learning" --size 510x550 --scale 2 \
      --dark --start-when window.__demoStart --stop-when window.__demoDone --seconds 60 --out media/Learning_mode_clip
  python tools/record_clip.py --url ... --frames-only --out scratch/frames      (just the PNG frames, for checking)

Needs Google Chrome and ffmpeg on the PATH. No Python packages beyond the standard library (a minimal WebSocket client
is below, so nothing has to be installed).
"""
import argparse
import base64
import json
import os
import pathlib
import shutil
import socket
import struct
import subprocess
import sys
import tempfile
import time
import urllib.request

CHROME = r"C:/Program Files/Google/Chrome/Application/chrome.exe"


class DevTools:
    """Just enough of a WebSocket client to talk to Chrome's DevTools protocol."""

    def __init__(self, ws_url):
        host_port, path = ws_url[len("ws://"):].split("/", 1)
        host, port = host_port.split(":")
        self.sock = socket.create_connection((host, int(port)))
        self.sock.settimeout(180)  # a page that stops answering raises instead of hanging
        key = base64.b64encode(os.urandom(16)).decode()
        self.sock.sendall((f"GET /{path} HTTP/1.1\r\nHost: {host_port}\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n"
                           f"Sec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n").encode())
        resp = b""
        while b"\r\n\r\n" not in resp:
            resp += self.sock.recv(4096)
        if b" 101 " not in resp.split(b"\r\n")[0]:
            raise RuntimeError(resp.decode(errors="replace"))
        self.buf = resp.split(b"\r\n\r\n", 1)[1]
        self.next_id = 0
        self.events = []

    def _read(self, n):
        while len(self.buf) < n:
            chunk = self.sock.recv(1 << 20)
            if not chunk:
                raise ConnectionError("DevTools connection closed")
            self.buf += chunk
        out, self.buf = self.buf[:n], self.buf[n:]
        return out

    def _recv(self):
        data = b""
        while True:
            b1, b2 = self._read(2)
            n = b2 & 0x7F
            if n == 126:
                n = struct.unpack(">H", self._read(2))[0]
            elif n == 127:
                n = struct.unpack(">Q", self._read(8))[0]
            data += self._read(n)
            if b1 & 0x80:  # final fragment
                return json.loads(data)

    def send(self, method, **params):
        self.next_id += 1
        msg = json.dumps({"id": self.next_id, "method": method, "params": params}).encode()
        mask = os.urandom(4)
        head = bytes([0x81])
        n = len(msg)
        head += bytes([0x80 | n]) if n < 126 else bytes([0x80 | 126]) + struct.pack(">H", n) if n < 65536 else bytes([0x80 | 127]) + struct.pack(">Q", n)
        self.sock.sendall(head + mask + bytes(b ^ mask[i % 4] for i, b in enumerate(msg)))
        want = self.next_id
        while True:
            m = self._recv()
            if m.get("id") == want:
                if "error" in m:
                    raise RuntimeError(f"{method}: {m['error']}")
                return m.get("result", {})
            self.events.append(m)

    def wait_event(self, name, timeout=60):
        end = time.time() + timeout
        while time.time() < end:
            for i, e in enumerate(self.events):
                if e.get("method") == name:
                    return self.events.pop(i)
            self.events.append(self._recv())
        raise TimeoutError(name)


def record(url, width, height, scale, fps, seconds, skip_ms, frames_dir, dark=False, start_when=None, stop_when=None):
    port = 9300 + os.getpid() % 500
    profile = tempfile.mkdtemp(prefix="gq-rec-")
    chrome = subprocess.Popen([CHROME, "--headless=new", "--disable-gpu", f"--remote-debugging-port={port}", f"--user-data-dir={profile}",
                               "--no-first-run", "--hide-scrollbars", "--mute-audio", f"--window-size={width},{height}", "about:blank"],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(100):
            try:
                targets = json.load(urllib.request.urlopen(f"http://127.0.0.1:{port}/json"))
                page = next(t for t in targets if t["type"] == "page")
                break
            except Exception:
                time.sleep(0.2)
        dt = DevTools(page["webSocketDebuggerUrl"])
        dt.send("Page.enable")
        dt.send("Emulation.setDeviceMetricsOverride", width=width, height=height, deviceScaleFactor=scale, mobile=False)
        if dark:  # the app's dark theme (prefers-color-scheme: dark)
            dt.send("Emulation.setEmulatedMedia", features=[{"name": "prefers-color-scheme", "value": "dark"}])
        dt.send("Emulation.setVirtualTimePolicy", policy="pause")
        dt.send("Page.navigate", url=url)
        step = 1000.0 / fps

        def advance(ms):
            if ms <= 0:
                return  # (a zero budget never reports back)
            dt.send("Emulation.setVirtualTimePolicy", policy="pauseIfNetworkFetchesPending", budget=ms)
            dt.wait_event("Emulation.virtualTimeBudgetExpired", timeout=120)

        advance(max(300, skip_ms))  # loading, and anything before the recording starts
        if start_when:  # wait (in page time) until the page says it's ready, e.g. the demo's first frame
            for _ in range(int(60000 / step)):
                if dt.send("Runtime.evaluate", expression=f"!!({start_when})", returnByValue=True)["result"].get("value"):
                    break
                advance(step)
            else:
                raise TimeoutError(f"never true: {start_when}")
        frames_dir.mkdir(parents=True, exist_ok=True)
        n = int(round(seconds * fps))
        for i in range(n):
            shot = dt.send("Page.captureScreenshot", format="png")
            (frames_dir / f"f{i:05d}.png").write_bytes(base64.b64decode(shot["data"]))
            advance(step)
            if stop_when and dt.send("Runtime.evaluate", expression=f"!!({stop_when})", returnByValue=True)["result"].get("value"):
                return i + 1  # (--seconds is then just the longest it may run)
            if i % fps == 0:
                print(f"  {i / fps:.0f} s", flush=True)
        return n
    finally:
        chrome.terminate()
        try:
            chrome.wait(10)
        except Exception:
            chrome.kill()
        shutil.rmtree(profile, ignore_errors=True)


def encode(frames_dir, fps, out, width_px):
    out.parent.mkdir(parents=True, exist_ok=True)
    src = ["-framerate", str(fps), "-i", str(frames_dir / "f%05d.png")]
    sz = ["-vf", f"scale={width_px}:-2:flags=lanczos"]
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *src, *sz, "-c:v", "libvpx-vp9", "-b:v", "0", "-crf", "38", "-row-mt", "1",
                    "-pix_fmt", "yuv420p", "-an", str(out.with_suffix(".webm"))], check=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *src, *sz, "-c:v", "libx264", "-crf", "24", "-preset", "slow",
                    "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an", str(out.with_suffix(".mp4"))], check=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(frames_dir / "f00000.png"), *sz, "-q:v", "4",
                    str(out.with_suffix(".jpg"))], check=True)
    for ext in (".webm", ".mp4", ".jpg"):
        print(out.with_suffix(ext), os.path.getsize(out.with_suffix(ext)) // 1024, "KB")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True)
    ap.add_argument("--size", default="510x550", help="page size in CSS pixels")
    ap.add_argument("--scale", type=float, default=2, help="device pixel ratio")
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--seconds", type=float, default=21)
    ap.add_argument("--skip", type=float, default=0, help="ms of page time to let pass before the first frame")
    ap.add_argument("--video-width", type=int, default=816, help="output width in pixels")
    ap.add_argument("--frames-only", action="store_true")
    ap.add_argument("--dark", action="store_true", help="record in the dark theme")
    ap.add_argument("--stop-when", help="JavaScript expression: recording stops once it's true (e.g. window.__demoDone)")
    ap.add_argument("--start-when", help="JavaScript expression: recording starts once it's true (e.g. window.__demoStart)")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    w, h = map(int, a.size.split("x"))
    out = pathlib.Path(a.out)
    frames = out if a.frames_only else pathlib.Path(tempfile.mkdtemp(prefix="gq-frames-"))
    n = record(a.url, w, h, a.scale, a.fps, a.seconds, a.skip, frames, a.dark, a.start_when, a.stop_when)
    print(n, "frames")
    if not a.frames_only:
        encode(frames, a.fps, out, a.video_width)
        shutil.rmtree(frames, ignore_errors=True)


if __name__ == "__main__":
    main()
