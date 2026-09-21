#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""lean-serve-broker: singleton `lake serve` multiplexer for Lean 4 projects.

One lake serve per project root, shared by every LSP consumer (pi-lens,
lean-lsp-mcp, ad-hoc clients). The broker:

  - guards uniqueness with flock on a state lock file
  - performs the real initialize handshake once and serves canned
    initialize responses to every attaching client
  - rewrites client request ids into a global namespace so responses
    route back to the right client
  - broadcasts server notifications (publishDiagnostics) to all clients
  - intercepts shutdown/exit so one client cannot kill the shared server
  - detects concurrent `lake build` runs and gates new elaboration
    requests for a bounded window until they finish
  - idles out when the last client disconnects

State lives under ~/.local/state/lean-serve-broker/<sha1(root)[:16]>/.
The attach client (mode "attach") is a dumb stdio<->socket byte pump that
presents itself exactly like `lake serve`, so any existing LSP client
works unchanged. Python 3.8+ standard library only.

ASCII-only per INV-001.
"""

import fcntl
import hashlib
import json
import os
import shlex
import signal
import socket
import subprocess
import sys
import threading
import time
from typing import Any, Dict, IO, NoReturn, Optional, Tuple

STATE_ROOT = os.environ.get(
    "LEAN_SERVE_STATE_HOME",
    os.path.join(
        os.environ.get("XDG_STATE_HOME", os.path.expanduser("~/.local/state")),
        "lean-serve-broker",
    ),
)
BUILD_WAIT_MS = int(os.environ.get("LEAN_SERVE_BUILD_WAIT_MS", "60000"))
IDLE_S = float(os.environ.get("LEAN_SERVE_IDLE_S", "900"))
ROOT_MARKERS = ("lakefile.lean", "lakefile.toml", "lean-toolchain")


def die(msg: str, code: int = 1) -> NoReturn:
    sys.stderr.write("lean-serve-broker: %s\n" % msg)
    sys.exit(code)


def find_root(start: str) -> str:
    d = os.path.abspath(start)
    while True:
        for marker in ROOT_MARKERS:
            if os.path.isfile(os.path.join(d, marker)):
                return d
        parent = os.path.dirname(d)
        if parent == d:
            die(
                "no Lean project root (lakefile.lean/lakefile.toml/lean-toolchain) above %s"
                % start
            )
        d = parent


def state_dir(root: str) -> str:
    key = hashlib.sha1(root.encode("utf-8")).hexdigest()[:16]
    return os.path.join(STATE_ROOT, key)


def atomic_write_status(path: str, fields: Dict[str, Any]) -> None:
    tmp = path + ".tmp.%d" % os.getpid()
    try:
        with open(tmp, "w") as f:
            json.dump(fields, f, indent=1)
        os.replace(tmp, path)
    except OSError:
        pass


def read_lsp_frame(rfile: IO[bytes]) -> Optional[bytes]:
    """Read one Content-Length framed LSP message; return None on EOF."""
    content_length = None
    while True:
        line = rfile.readline()
        if not line:
            return None
        if line in (b"\r\n", b"\n"):
            break
        if b":" in line:
            k, v = line.split(b":", 1)
            if k.strip().lower() == b"content-length":
                try:
                    content_length = int(v.strip())
                except ValueError:
                    return None
    if content_length is None:
        return None
    body = b""
    remaining = content_length
    while remaining > 0:
        chunk = rfile.read(remaining)
        if not chunk:
            return None
        body += chunk
        remaining -= len(chunk)
    return body


def write_lsp_frame(sock_or_file: Any, body: bytes) -> None:
    header = ("Content-Length: %d\r\n\r\n" % len(body)).encode("ascii")
    if hasattr(sock_or_file, "sendall"):
        sock_or_file.sendall(header + body)
    else:
        sock_or_file.write(header + body)
        sock_or_file.flush()


class Broker:
    def __init__(self, root: str, server_cmd: list) -> None:
        self.root = root
        self.server_cmd = server_cmd
        self.state = state_dir(root)
        self.sock_path = os.path.join(self.state, "server.sock")
        self.lock_fd: Optional[IO[Any]] = None
        self.server: Optional[subprocess.Popen] = None
        self.server_stream: Optional[IO[bytes]] = None
        self.clients: Dict[Any, Dict[str, Any]] = {}
        self.clients_lock = threading.Lock()
        self.pending: Dict[int, Tuple[Any, Any]] = {}
        self.pending_lock = threading.Lock()
        self.client_pending: Dict[Any, Dict[Any, int]] = {}
        self.next_id = 1
        self.write_lock = threading.Lock()
        self.cached_init_result: Optional[Dict[str, Any]] = None
        self.building = False
        self.build_pids: list = []
        self.shutdown = threading.Event()

    def log(self, msg: str) -> None:
        try:
            with open(os.path.join(self.state, "broker.log"), "a") as f:
                f.write("%s %s\n" % (time.strftime("%Y-%m-%dT%H:%M:%S"), msg))
        except OSError:
            pass

    def publish_status(self) -> None:
        with self.clients_lock:
            n = len(self.clients)
        atomic_write_status(
            os.path.join(self.state, "status.json"),
            {
                "running": True,
                "pid": os.getpid(),
                "root": self.root,
                "lake_serve_pid": self.server.pid if self.server else None,
                "clients": n,
                "building": self.building,
                "build_pids": self.build_pids,
                "updated": time.strftime("%Y-%m-%dT%H:%M:%S"),
            },
        )

    # -- server (lake serve) plumbing ------------------------------------

    def start_server(self) -> None:
        self.server = subprocess.Popen(
            self.server_cmd,
            cwd=self.root,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
        stream = self.server.stdout
        if stream is None:
            die("lake serve produced no stdout")
        self.server_stream = stream
        # NOTE: server_reader starts only after real_initialize() completes;
        # starting it earlier races the handshake and swallows the response.

    def server_stdin(self) -> Any:
        if self.server is None or self.server.stdin is None:
            die("server stdin unavailable")
        return self.server.stdin

    def real_initialize(self) -> None:
        """Perform the one true initialize handshake and cache the result."""
        params = {
            "processId": os.getpid(),
            "rootUri": "file://" + self.root,
            "rootPath": self.root,
            "capabilities": {
                "textDocument": {
                    "synchronization": {"didSave": True},
                    "hover": {"contentFormat": ["markdown", "plaintext"]},
                    "completion": {
                        "completionItem": {"documentationFormat": ["markdown"]}
                    },
                },
                "workspace": {"configuration": False, "workspaceFolders": False},
            },
        }
        stdin = self.server_stdin()
        init_req = {"jsonrpc": "2.0", "id": 0, "method": "initialize", "params": params}
        initialized_note = {"jsonrpc": "2.0", "method": "initialized", "params": {}}
        with self.write_lock:
            write_lsp_frame(stdin, json.dumps(init_req).encode("utf-8"))
            write_lsp_frame(stdin, json.dumps(initialized_note).encode("utf-8"))
        stream = self.server_stream
        if stream is None:
            die("server stream unavailable")
        deadline = time.time() + 120
        while time.time() < deadline:
            body = read_lsp_frame(stream)
            if body is None:
                die("lake serve exited during initialize")
            msg = json.loads(body.decode("utf-8"))
            if msg.get("id") == 0 and "result" in msg:
                self.cached_init_result = msg["result"]
                return
            # drop early notifications; they have no subscriber yet
        die("lake serve initialize timed out")

    def server_reader(self) -> None:
        stream = self.server_stream
        if stream is None:
            return
        while not self.shutdown.is_set():
            body = read_lsp_frame(stream)
            if body is None:
                break
            try:
                msg = json.loads(body.decode("utf-8"))
            except ValueError:
                continue
            if "method" in msg and "id" in msg:
                # server->client request: lean-lsp-mcp proved lake serve
                # tolerates no reply; drop to keep the hub stateless.
                self.log("drop server request %s" % msg.get("method"))
                continue
            if "id" in msg:
                with self.pending_lock:
                    entry = self.pending.pop(msg["id"], None)
                if entry is None:
                    continue
                conn, client_id = entry
                msg["id"] = client_id
                self.send_to(conn, msg)
            else:
                self.broadcast(msg)
        self.log("server reader exited")

    def send_to(self, conn: Any, msg: Dict[str, Any]) -> None:
        data = json.dumps(msg).encode("utf-8")
        info = self.clients.get(conn)
        if info is None:
            return
        try:
            with info["lock"]:
                write_lsp_frame(conn, data)
        except OSError:
            self.drop_client(conn)

    def broadcast(self, msg: Dict[str, Any]) -> None:
        data = json.dumps(msg).encode("utf-8")
        with self.clients_lock:
            targets = list(self.clients.items())
        for conn, info in targets:
            try:
                with info["lock"]:
                    write_lsp_frame(conn, data)
            except OSError:
                self.drop_client(conn)

    def forward(self, msg: Dict[str, Any]) -> None:
        data = json.dumps(msg).encode("utf-8")
        stdin = self.server_stdin()
        try:
            with self.write_lock:
                write_lsp_frame(stdin, data)
        except OSError:
            self.log("server stdin write failed")

    # -- client plumbing ---------------------------------------------------

    def drop_client(self, conn: Any) -> None:
        with self.clients_lock:
            if conn in self.clients:
                del self.clients[conn]
        with self.pending_lock:
            cp = self.client_pending.pop(conn, {})
            for gid in cp.values():
                self.pending.pop(gid, None)
        try:
            conn.close()
        except OSError:
            pass
        self.publish_status()

    def client_reader(self, conn: Any) -> None:
        info = self.clients.get(conn)
        if info is None:
            return
        rfile = info["rfile"]
        while not self.shutdown.is_set():
            body = read_lsp_frame(rfile)
            if body is None:
                break
            try:
                msg = json.loads(body.decode("utf-8"))
            except ValueError:
                continue
            method = msg.get("method")
            if method == "initialize":
                result = self.cached_init_result or {"capabilities": {}}
                self.send_to(
                    conn, {"jsonrpc": "2.0", "id": msg.get("id"), "result": result}
                )
                continue
            if method == "shutdown":
                self.send_to(
                    conn, {"jsonrpc": "2.0", "id": msg.get("id"), "result": None}
                )
                continue
            if method == "exit":
                break
            if method == "$/cancelRequest":
                cp = self.client_pending.get(conn, {})
                gid = cp.get((msg.get("params") or {}).get("id"))
                if gid is not None:
                    msg["params"]["id"] = gid
                    self.forward(msg)
                continue
            self.wait_if_building(method)
            if "id" in msg:
                with self.pending_lock:
                    gid = self.next_id
                    self.next_id += 1
                    self.pending[gid] = (conn, msg["id"])
                    self.client_pending.setdefault(conn, {})[msg["id"]] = gid
                msg["id"] = gid
            self.forward(msg)
        self.drop_client(conn)

    def wait_if_building(self, method: Optional[str]) -> None:
        """Boundedly hold elaboration-triggering traffic during lake builds."""
        if not method or not method.startswith("textDocument/"):
            return
        deadline = time.time() + BUILD_WAIT_MS / 1000.0
        while self.building and time.time() < deadline and not self.shutdown.is_set():
            time.sleep(0.5)

    # -- build detection ---------------------------------------------------

    def our_subtree(self) -> set:
        """Pids of the broker, the lake serve child, and all descendants."""
        ours = {os.getpid(), self.server.pid if self.server else -1}
        procs: Dict[int, int] = {}
        for pid in os.listdir("/proc"):
            if not pid.isdigit():
                continue
            try:
                with open("/proc/%s/stat" % pid, "rb") as f:
                    fields = f.read().split(b")", 1)[1].split()
                procs[int(pid)] = int(fields[1])
            except (OSError, IndexError, ValueError):
                continue
        children: Dict[int, list] = {}
        for pid, ppid in procs.items():
            children.setdefault(ppid, []).append(pid)
        marked = set(ours)
        stack = [p for p in ours if p in children]
        while stack:
            cur = stack.pop()
            for child in children.get(cur, []):
                if child not in marked:
                    marked.add(child)
                    stack.append(child)
        return marked

    def detect_builds(self) -> Tuple[bool, list]:
        building, pids = False, []
        ours = self.our_subtree()
        for pid in os.listdir("/proc"):
            if not pid.isdigit() or int(pid) in ours:
                continue
            try:
                cwd = os.readlink("/proc/%s/cwd" % pid)
                if cwd != self.root:
                    continue
                with open("/proc/%s/cmdline" % pid, "rb") as f:
                    argv = [
                        a.decode("utf-8", "replace") for a in f.read().split(b"\0") if a
                    ]
                if not argv:
                    continue
                # Match lean-lsp-mcp's proven pgrep semantics, but token-wise
                # so shebang wrappers (argv: /bin/sh .../lake build) also hit.
                names = [os.path.basename(a) for a in argv]
                if "lake" in names:
                    rest = " ".join(argv[names.index("lake") + 1 :])
                    if any(w in rest for w in ("build", "compile", "env")):
                        building, pids = True, pids + [int(pid)]
            except (OSError, ValueError):
                continue
        return building, pids

    def monitor(self) -> None:
        last_idle_mark = None
        while not self.shutdown.is_set():
            building, pids = self.detect_builds()
            if building != self.building or pids != self.build_pids:
                if building and not self.building:
                    self.log("build started pids=%s" % pids)
                elif not building and self.building:
                    self.log("build finished")
                self.building, self.build_pids = building, pids
                self.publish_status()
            with self.clients_lock:
                n = len(self.clients)
            if n == 0:
                if last_idle_mark is None:
                    last_idle_mark = time.time()
                elif time.time() - last_idle_mark > IDLE_S and not building:
                    self.log("idle expiry, shutting down")
                    break
            else:
                last_idle_mark = None
            self.shutdown.wait(2.0)
        self.teardown()

    def teardown(self) -> NoReturn:
        self.shutdown.set()
        try:
            if self.server and self.server.poll() is None:
                self.server.terminate()
                self.server.wait(timeout=10)
        except (OSError, subprocess.TimeoutExpired):
            pass
        try:
            os.unlink(self.sock_path)
        except OSError:
            pass
        atomic_write_status(
            os.path.join(self.state, "status.json"),
            {
                "running": False,
                "pid": None,
                "root": self.root,
                "lake_serve_pid": None,
                "clients": 0,
                "building": False,
                "build_pids": [],
                "updated": time.strftime("%Y-%m-%dT%H:%M:%S"),
            },
        )
        self.log("teardown complete")
        os._exit(0)

    # -- accept loop ---------------------------------------------------------

    def serve(self) -> NoReturn:
        os.makedirs(self.state, exist_ok=True)
        lock_path = os.path.join(self.state, "broker.lock")
        self.lock_fd = open(lock_path, "w")
        try:
            fcntl.flock(self.lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            die("broker already running for %s" % self.root, 3)
        if os.path.exists(self.sock_path):
            os.unlink(self.sock_path)
        with open(os.path.join(self.state, "broker.pid"), "w") as f:
            f.write(str(os.getpid()))

        signal.signal(signal.SIGTERM, lambda *_: self.teardown())
        signal.signal(signal.SIGINT, lambda *_: self.teardown())
        try:
            signal.signal(signal.SIGPIPE, signal.SIG_IGN)
        except (AttributeError, ValueError):
            pass

        self.log("broker start root=%s cmd=%s" % (self.root, " ".join(self.server_cmd)))
        self.start_server()
        self.real_initialize()
        threading.Thread(target=self.server_reader, daemon=True).start()

        srv = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        srv.bind(self.sock_path)
        srv.listen(16)
        threading.Thread(target=self.monitor, daemon=True).start()
        self.publish_status()
        while not self.shutdown.is_set():
            try:
                conn, _ = srv.accept()
            except OSError:
                break
            rfile = conn.makefile("rb")
            with self.clients_lock:
                self.clients[conn] = {"rfile": rfile, "lock": threading.Lock()}
            self.publish_status()
            threading.Thread(
                target=self.client_reader, args=(conn,), daemon=True
            ).start()
        self.teardown()


def cmd_serve(root: str) -> NoReturn:
    server_cmd = shlex.split(os.environ.get("LEAN_SERVE_BROKER_SERVER", "lake serve"))
    Broker(root, server_cmd).serve()


def spawn_broker(root: str) -> None:
    subprocess.Popen(
        [sys.executable, os.path.abspath(__file__), "serve"],
        cwd=root,
        start_new_session=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        stdin=subprocess.DEVNULL,
    )


def socket_connect(sock_path: str, timeout: float = 1.0) -> Optional[socket.socket]:
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect(sock_path)
        return s
    except (OSError, socket.timeout):
        try:
            s.close()
        except OSError:
            pass
        return None


def cmd_attach(root: str) -> NoReturn:
    state = state_dir(root)
    sock_path = os.path.join(state, "server.sock")
    conn = socket_connect(sock_path)
    if conn is None:
        try:
            os.unlink(sock_path)
        except OSError:
            pass
        spawn_broker(root)
        deadline = time.time() + 20
        while time.time() < deadline:
            conn = socket_connect(sock_path, timeout=1.0)
            if conn is not None:
                break
            time.sleep(0.2)
    if conn is None:
        die("could not reach or start broker for %s" % root, 4)

    signal.signal(signal.SIGPIPE, signal.SIG_IGN)

    def pump(read_fn, send_fn, close_fn):
        try:
            while True:
                chunk = read_fn()
                if not chunk:
                    break
                send_fn(chunk)
        except OSError:
            pass
        finally:
            try:
                close_fn()
            except OSError:
                pass

    t1 = threading.Thread(
        target=pump,
        args=(lambda: os.read(0, 65536), conn.sendall, conn.close),
        daemon=True,
    )
    t2 = threading.Thread(
        target=pump,
        args=(lambda: conn.recv(65536), lambda b: os.write(1, b), lambda: os.close(1)),
        daemon=True,
    )
    t1.start()
    t2.start()
    t1.join()
    # give the outbound pump a moment to flush server traffic, then exit
    t2.join(timeout=2.0)
    try:
        conn.close()
    except OSError:
        pass
    os._exit(0)


def cmd_stop(root: str) -> None:
    state = state_dir(root)
    pid_path = os.path.join(state, "broker.pid")
    try:
        with open(pid_path) as f:
            pid = int(f.read().strip())
    except (OSError, ValueError):
        print("no broker running for %s" % root)
        return
    try:
        os.kill(pid, signal.SIGTERM)
    except OSError as e:
        if e.errno == 3:  # ESRCH
            print("broker %d already gone" % pid)
            return
        raise
    sock_path = os.path.join(state, "server.sock")
    for _ in range(50):
        if not os.path.exists(sock_path):
            break
        time.sleep(0.1)
    print("stopped broker %d" % pid)


def cmd_status(root: str) -> None:
    state = state_dir(root)
    try:
        with open(os.path.join(state, "status.json")) as f:
            print(f.read())
    except OSError:
        print(json.dumps({"running": False, "root": root}))


def main() -> None:
    argv = sys.argv[1:]
    if not argv:
        die("usage: lean_serve_broker.py attach|serve|stop|status [--root DIR]", 2)
    mode = argv[0]
    root = None
    if "--root" in argv:
        root = os.path.abspath(argv[argv.index("--root") + 1])
    if mode == "attach":
        cmd_attach(root or find_root(os.getcwd()))
    elif mode == "serve":
        cmd_serve(root or find_root(os.getcwd()))
    elif mode == "stop":
        cmd_stop(root or find_root(os.getcwd()))
    elif mode == "status":
        cmd_status(root or os.getcwd())
    else:
        die("unknown mode %r" % mode, 2)


if __name__ == "__main__":
    main()
