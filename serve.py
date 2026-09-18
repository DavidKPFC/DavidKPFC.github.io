# -*- coding: utf-8 -*-
"""
Local preview server that never lets the browser keep an old copy.

Python's plain `http.server` sends no caching instructions, so a browser may go on showing
yesterday's page after the files have changed.  This one marks every response "no-store".

    py serve.py                          this folder, http://127.0.0.1:8741/
    py serve.py --port 8732 --dir ../budget-simulation/dist
"""
import argparse, functools, http.server, os


class NoCache(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store, max-age=0")
        super().end_headers()

    def log_message(self, fmt, *args):      # keep the terminal quiet
        pass


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8741)
    ap.add_argument("--dir", default=os.path.dirname(os.path.abspath(__file__)))
    a = ap.parse_args()
    handler = functools.partial(NoCache, directory=os.path.abspath(a.dir))
    print("serving %s at http://127.0.0.1:%d/  (no caching)" % (os.path.abspath(a.dir), a.port), flush=True)
    http.server.ThreadingHTTPServer(("127.0.0.1", a.port), handler).serve_forever()
