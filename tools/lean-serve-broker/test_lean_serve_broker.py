#!/usr/bin/env python3
"""Tests for lean_serve_broker.py (CONV-LEAN-SERVE-SINGLETON infrastructure).

Two layers:
  - pure-function tests: LSP framing, root discovery, state paths,
    atomic status writes, the bounded build gate
  - one integration test driving a real Broker against a stub `lake
    serve` over a socketpair: the cached-initialize handshake, the
    global-id rewrite round trip, notification broadcast, shutdown/exit
    interception, and pending-map cleanup on client drop

Stdlib only (mirrors the broker's own constraint). ASCII-only per
INV-001. Run: python3 test_lean_serve_broker.py -v
"""

import contextlib
import importlib.util
import io
import json
import os
import socket
import sys
import tempfile
import threading
import time
import unittest

_HERE = os.path.dirname(os.path.abspath(__file__))
_TMP = tempfile.mkdtemp(prefix="lsb-test-")
os.environ["LEAN_SERVE_STATE_HOME"] = os.path.join(_TMP, "state")

_spec = importlib.util.spec_from_file_location(
    "lean_serve_broker", os.path.join(_HERE, "lean_serve_broker.py")
)
lsb = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(lsb)


def frame(body: bytes) -> bytes:
    return f"Content-Length: {len(body)}\r\n\r\n".encode("ascii") + body


def jmsg(obj) -> bytes:
    return frame(json.dumps(obj).encode("utf-8"))


STUB_SERVER = r"""
import sys, json

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
    body = b""
    while length > 0:
        chunk = rfile.read(length)
        if not chunk:
            return None
        body += chunk
        length -= len(chunk)
    return body

def write(body):
    sys.stdout.write(("Content-Length: %d\r\n\r\n" % len(body)).encode("ascii").decode())
    sys.stdout.write(body.decode("utf-8"))
    sys.stdout.flush()

rfile = sys.stdin.buffer
while True:
    body = read_frame(rfile)
    if body is None:
        break
    msg = json.loads(body.decode("utf-8"))
    method = msg.get("method", "")
    with open(sys.argv[1], "a") as log:
        log.write(method + "\n")
    if method == "initialize":
        write(json.dumps({"jsonrpc": "2.0", "id": 0,
                          "result": {"capabilities": {"stub": True}}}).encode("utf-8"))
    elif "id" in msg:
        write(json.dumps({"jsonrpc": "2.0", "id": msg["id"],
                          "result": {"echo": method}}).encode("utf-8"))
"""


class PureFunctionTests(unittest.TestCase):
    def test_read_frame_round_trip(self):
        body = b'{"jsonrpc": "2.0"}'
        self.assertEqual(lsb.read_lsp_frame(io.BytesIO(frame(body))), body)

    def test_read_frame_eof(self):
        self.assertIsNone(lsb.read_lsp_frame(io.BytesIO(b"")))

    def test_read_frame_missing_content_length(self):
        self.assertIsNone(lsb.read_lsp_frame(io.BytesIO(b"X-Other: 1\r\n\r\n{}")))

    def test_read_frame_bad_content_length(self):
        self.assertIsNone(
            lsb.read_lsp_frame(io.BytesIO(b"Content-Length: NaN\r\n\r\n{}"))
        )

    def test_read_frame_chunked_body(self):
        body = b"x" * 100

        class Chunky:
            """One byte per read; readline splits on b"\n" incrementally."""

            def __init__(self, data):
                self.data = data
                self.pos = 0

            def readline(self):
                nl = self.data.find(b"\n", self.pos)
                if nl == -1:
                    out, self.pos = self.data[self.pos :], len(self.data)
                    return out
                out, self.pos = self.data[self.pos : nl + 1], nl + 1
                return out

            def read(self, n):
                out = self.data[self.pos : self.pos + 1] if n else b""
                self.pos += len(out)
                return out

        self.assertEqual(lsb.read_lsp_frame(Chunky(frame(body))), body)

    def test_write_frame_file_and_socket_paths(self):
        buf = io.BytesIO()
        lsb.write_lsp_frame(buf, b"hi")
        self.assertTrue(buf.getvalue().startswith(b"Content-Length: 2\r\n\r\nhi"))

        class FakeSock:
            def __init__(self):
                self.sent = b""

            def sendall(self, data):
                self.sent += data

        s = FakeSock()
        lsb.write_lsp_frame(s, b"hi")
        self.assertEqual(s.sent, b"Content-Length: 2\r\n\r\nhi")

    def test_find_root_walks_up(self):
        base = tempfile.mkdtemp(dir=_TMP)
        sub = os.path.join(base, "a", "b")
        os.makedirs(sub)
        with open(os.path.join(base, "lakefile.lean"), "w") as f:
            f.write("root := .\n")
        self.assertEqual(lsb.find_root(sub), base)

    def test_find_root_dies_without_marker(self):
        with self.assertRaises(SystemExit):
            lsb.find_root(_TMP)

    def test_state_dir_deterministic(self):
        a, b = lsb.state_dir("/some/root"), lsb.state_dir("/some/root")
        self.assertEqual(a, b)
        self.assertTrue(a.startswith(lsb.STATE_ROOT))
        self.assertEqual(len(os.path.basename(a)), 16)
        self.assertNotEqual(a, lsb.state_dir("/other/root"))

    def test_atomic_write_status_and_no_tmp_left(self):
        path = os.path.join(_TMP, "status.json")
        lsb.atomic_write_status(path, {"running": True, "clients": 2})
        with open(path) as f:
            self.assertEqual(json.load(f)["clients"], 2)
        leftovers = [n for n in os.listdir(_TMP) if ".tmp." in n]
        self.assertEqual(leftovers, [])

    def test_atomic_write_status_swallows_oserror(self):
        lsb.atomic_write_status(
            os.path.join(_TMP, "no-such-dir", "s.json"), {"running": False}
        )

    def test_build_gate_bounds_the_wait(self):
        broker = lsb.Broker(_TMP, ["true"])
        old = lsb.BUILD_WAIT_MS
        lsb.BUILD_WAIT_MS = 150
        broker.building = True
        t0 = time.time()
        broker.wait_if_building("textDocument/definition")
        waited = time.time() - t0
        lsb.BUILD_WAIT_MS = old
        self.assertGreaterEqual(waited, 0.1)
        self.assertLess(waited, 3.0)

    def test_build_gate_passes_non_elaboration_methods(self):
        broker = lsb.Broker(_TMP, ["true"])
        broker.building = True
        old = lsb.BUILD_WAIT_MS
        lsb.BUILD_WAIT_MS = 60000
        t0 = time.time()
        broker.wait_if_building("shutdown")
        self.assertLess(time.time() - t0, 1.0)
        lsb.BUILD_WAIT_MS = old


class BrokerIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(dir=_TMP)
        with open(os.path.join(self.root, "lakefile.lean"), "w") as f:
            f.write("root := .\n")
        self.stub_log = os.path.join(self.root, "stub-methods.log")
        stub_path = os.path.join(self.root, "stub_serve.py")
        with open(stub_path, "w") as f:
            f.write(STUB_SERVER)
        self.broker = lsb.Broker(
            self.root, [sys.executable, stub_path, self.stub_log]
        )
        self.broker.state = os.path.join(_TMP, "state-broker")
        os.makedirs(self.broker.state, exist_ok=True)
        self.broker.start_server()
        self.broker.real_initialize()
        self.reader_thread = threading.Thread(
            target=self.broker.server_reader, daemon=True
        )
        self.reader_thread.start()

        self.client_sock, broker_side = socket.socketpair()
        with self.broker.clients_lock:
            self.broker.clients[broker_side] = {
                "rfile": broker_side.makefile("rb"),
                "lock": threading.Lock(),
            }
        self.client_rfile = self.client_sock.makefile("rb")
        self.client_thread = threading.Thread(
            target=self.broker.client_reader, args=(broker_side,), daemon=True
        )
        self.client_thread.start()

    def tearDown(self):
        self.broker.shutdown.set()
        with contextlib.suppress(OSError):
            if self.broker.server and self.broker.server.poll() is None:
                self.broker.server.terminate()
        with contextlib.suppress(OSError):
            self.client_sock.close()

    def recv_msg(self, timeout=5.0):
        end = time.time() + timeout
        self.client_sock.settimeout(max(0.05, end - time.time()))
        body = lsb.read_lsp_frame(self.client_rfile)
        self.assertIsNotNone(body, "no response within the window")
        return json.loads(body.decode("utf-8"))

    def stub_methods(self):
        try:
            with open(self.stub_log) as f:
                return f.read().split()
        except OSError:
            return []

    def test_initialize_handshake_cached_and_served(self):
        self.assertEqual(
            self.broker.cached_init_result, {"capabilities": {"stub": True}}
        )
        self.client_sock.sendall(jmsg({"jsonrpc": "2.0", "id": 5, "method": "initialize"}))
        msg = self.recv_msg()
        self.assertEqual(msg["id"], 5)
        self.assertEqual(msg["result"], {"capabilities": {"stub": True}})
        # served from cache: the stub saw the real handshake exactly once
        self.assertEqual(self.stub_methods().count("initialize"), 1)

    def test_request_id_rewrite_round_trip(self):
        self.client_sock.sendall(
            jmsg(
                {
                    "jsonrpc": "2.0",
                    "id": 7,
                    "method": "textDocument/definition",
                    "params": {},
                }
            )
        )
        msg = self.recv_msg()
        self.assertEqual(msg["id"], 7)
        self.assertEqual(msg["result"], {"echo": "textDocument/definition"})
        # the global pending map consumes the entry on response...
        with self.broker.pending_lock:
            self.assertEqual(len(self.broker.pending), 0)
        # ...while the per-client id map is retained by design for
        # $/cancelRequest routing; it clears on drop_client
        with self.broker.clients_lock:
            cp = self.broker.client_pending.get(
                next(iter(self.broker.clients)), {}
            )
        self.assertEqual(cp, {7: 1})

    def test_notification_broadcast_reaches_client(self):
        note = {"jsonrpc": "2.0", "method": "textDocument/publishDiagnostics",
                "params": {"uri": "file:///x.lean", "diagnostics": []}}
        self.broker.broadcast(note)
        msg = self.recv_msg()
        self.assertEqual(msg["method"], "textDocument/publishDiagnostics")

    def test_shutdown_and_exit_intercepted(self):
        self.client_sock.sendall(jmsg({"jsonrpc": "2.0", "id": 11, "method": "shutdown"}))
        msg = self.recv_msg()
        self.assertEqual(msg["id"], 11)
        self.assertIn("result", msg)
        self.assertIsNone(msg["result"])
        self.assertNotIn("shutdown", self.stub_methods())

    def test_drop_client_clears_pending(self):
        conn = next(iter(self.broker.clients.keys()))
        with self.broker.pending_lock:
            self.broker.pending[999] = (conn, 42)
            self.broker.client_pending.setdefault(conn, {})[42] = 999
        self.broker.drop_client(conn)
        with self.broker.pending_lock:
            self.assertNotIn(999, self.broker.pending)
        with self.broker.clients_lock:
            self.assertEqual(len(self.broker.clients), 0)


class StopCommandTests(unittest.TestCase):
    def test_stop_without_pidfile(self):
        state = lsb.state_dir("/definitely/not/a/root")
        os.makedirs(state, exist_ok=True)
        with contextlib.suppress(OSError):
            os.unlink(os.path.join(state, "broker.pid"))
        buf = io.StringIO()
        old = sys.stdout
        sys.stdout = buf
        try:
            lsb.cmd_stop("/definitely/not/a/root")
        finally:
            sys.stdout = old
        self.assertIn("no broker running", buf.getvalue())

    def test_stop_with_stale_pid(self):
        state = lsb.state_dir("/definitely/not/a/root")
        os.makedirs(state, exist_ok=True)
        with open(os.path.join(state, "broker.pid"), "w") as f:
            f.write(str(2 ** 22))
        buf = io.StringIO()
        old = sys.stdout
        sys.stdout = buf
        try:
            lsb.cmd_stop("/definitely/not/a/root")
        finally:
            sys.stdout = old
        self.assertIn("already gone", buf.getvalue())


if __name__ == "__main__":
    unittest.main(verbosity=2)
