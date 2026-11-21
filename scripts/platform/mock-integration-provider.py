#!/usr/bin/env python3
"""Deterministic local HTTP provider used only by Rubrova failure-injection tests."""

from __future__ import annotations

import argparse
import json
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit


class MockProviderHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _send(self, status: int, payload: bytes, content_type: str = "application/json") -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Connection", "close")
        self.close_connection = True
        self.end_headers()
        try:
            self.wfile.write(payload)
        except (BrokenPipeError, ConnectionResetError):
            # Expected when the client enforces its timeout before this stub responds.
            pass

    def do_GET(self) -> None:
        request = urlsplit(self.path)
        if request.path == "/health":
            self._send(200, b'{"status":"ready"}')
            return
        if request.path == "/ok":
            self._send(200, b'{"status":"ok","provider":"Rubrova Mock Provider"}')
            return
        if request.path == "/slow":
            params = parse_qs(request.query)
            delay = min(max(float(params.get("delay", ["5"])[0]), 0.0), 10.0)
            time.sleep(delay)
            self._send(200, b'{"status":"slow-response"}')
            return
        if request.path == "/status/408":
            self._send(408, b'{"error":"request timeout"}')
            return
        if request.path == "/status/425":
            self._send(425, b'{"error":"too early"}')
            return
        if request.path == "/status/429":
            self.send_response(429)
            self.send_header("Retry-After", "2")
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        if request.path == "/status/400":
            self._send(400, b'{"error":"bad request"}')
            return
        if request.path == "/status/401":
            self._send(401, b'{"error":"unauthorized"}')
            return
        if request.path == "/status/403":
            self._send(403, b'{"error":"forbidden"}')
            return
        if request.path == "/status/409":
            self._send(409, b'{"error":"conflict"}')
            return
        if request.path == "/status/503":
            self._send(503, b'{"error":"temporarily unavailable"}')
            return
        if request.path == "/invalid-json":
            self._send(200, b'{"broken":', "application/json")
            return
        self._send(404, b'{"error":"not found"}')

    def log_message(self, fmt: str, *args: object) -> None:
        # Keep test logs deterministic and free of request bodies or headers.
        print("mock-provider " + (fmt % args), flush=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=18765)
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), MockProviderHandler)
    print(f"mock-provider-ready {args.host}:{args.port}", flush=True)
    try:
        server.serve_forever(poll_interval=0.2)
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
