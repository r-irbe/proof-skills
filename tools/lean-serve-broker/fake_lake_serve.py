#!/usr/bin/env python3
"""Fake LSP server standing in for `lake serve` in broker tests.

Behavior:
  - initialize -> proper capabilities result (logged)
  - any other request -> echoed back as {"echo": params} with the same id
  - textDocument/didOpen -> emits a publishDiagnostics notification
  - every received method name is appended to $FAKE_LOG for assertions

ASCII-only per INV-001.
"""

import json
import os
import sys
import tempfile
import threading

LOG = os.environ.get("FAKE_LOG", os.path.join(tempfile.gettempdir(), "fake_lake_serve.log"))


def log(method):
    try:
        with open(LOG, "a") as f:
            f.write(method + "\n")
    except OSError:
        pass


def read_frame(rfile):
    length = None
    while True:
        line = rfile.readline()
        if not line:
            return None
        if line in (b"\r\n", b"\n"):
            break
        if b":" in line:
            k, v = line.split(b":", 1)
            if k.strip().lower() == b"content-length":
                length = int(v.strip())
    if length is None:
        return None
    return rfile.read(length)


def send(obj):
    body = json.dumps(obj).encode("utf-8")
    sys.stdout.buffer.write(f"Content-Length: {len(body)}\r\n\r\n".encode("ascii"))
    sys.stdout.buffer.write(body)
    sys.stdout.buffer.flush()


def main():
    lock = threading.Lock()
    while True:
        body = read_frame(sys.stdin.buffer)
        if body is None:
            return
        try:
            msg = json.loads(body.decode("utf-8"))
        except ValueError:
            continue
        method = msg.get("method", "")
        log(method)
        if method == "initialize":
            with lock:
                send(
                    {
                        "jsonrpc": "2.0",
                        "id": msg["id"],
                        "result": {
                            "capabilities": {
                                "textDocumentSync": 1,
                                "hoverProvider": True,
                            },
                            "serverInfo": {"name": "fake-lake-serve"},
                        },
                    }
                )
        elif method == "textDocument/didOpen":
            uri = (msg.get("params", {}).get("textDocument", {}) or {}).get("uri", "")
            with lock:
                send(
                    {
                        "jsonrpc": "2.0",
                        "method": "textDocument/publishDiagnostics",
                        "params": {"uri": uri, "diagnostics": []},
                    }
                )
        elif "id" in msg and "method" in msg:
            with lock:
                send(
                    {
                        "jsonrpc": "2.0",
                        "id": msg["id"],
                        "result": {"echo": msg.get("params")},
                    }
                )
        # notifications without echo behavior: logged only


if __name__ == "__main__":
    main()
