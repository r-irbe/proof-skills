#!/usr/bin/env python3
"""
Standalone HTTP Server & Launcher for Lean 4 Formalization DAG Visualizer.

Strict 7-bit ASCII only (INV-001).
Zero external dependencies: uses only Python standard library.

Usage:
    python3 serve.py
    python3 serve.py --port 8088
    python3 serve.py --graph /path/to/graph.json
    python3 serve.py --corpus flt --no-browser
"""

import argparse
import http.server
import json
import os
import socketserver
import sys
import webbrowser

DIR_PATH = os.path.dirname(os.path.abspath(__file__))


class CustomGraphHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP Request Handler with optional custom graph API endpoint."""

    custom_graph_data = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIR_PATH, **kwargs)

    def do_GET(self):
        if self.path.startswith("/api/custom-graph.json"):
            if CustomGraphHandler.custom_graph_data is not None:
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(CustomGraphHandler.custom_graph_data)
                return
            else:
                self.send_response(404)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(b'{"error": "No custom graph loaded"}')
                return
        return super().do_GET()

    def log_message(self, format, *args):
        # Suppress verbose asset logging, keep terminal clean
        if self.path.endswith((".js", ".css", ".ico")):
            return
        sys.stderr.write(f"[{self.log_date_time_string()}] {format % args}\n")


def find_available_port(start_port=8088, max_attempts=20):
    """Find an open TCP port starting from start_port."""
    import socket
    for port in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", port)) != 0:
                return port
    return start_port


def parse_args():
    parser = argparse.ArgumentParser(
        description="Launch standalone Lean 4 Formalization DAG Visualizer"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8088,
        help="Port to bind HTTP server (default: 8088, auto-increments if in use)",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host address to bind HTTP server (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--graph",
        type=str,
        default=None,
        help="Path to custom formalization graph JSON exported from formalization_breakdown.py",
    )
    parser.add_argument(
        "--corpus",
        type=str,
        choices=["nse", "flt", "easci"],
        default=None,
        help="Default preloaded corpus to display (nse, flt, easci)",
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Do not open web browser automatically",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    if args.graph:
        if not os.path.isfile(args.graph):
            print(f"Error: Specified graph file not found: {args.graph}", file=sys.stderr)
            sys.exit(1)
        try:
            with open(args.graph, "rb") as f:
                data = f.read()
                # Verify valid JSON
                json.loads(data)
                CustomGraphHandler.custom_graph_data = data
            print(f"[OK] Loaded custom graph: {args.graph} ({len(data)} bytes)")
        except Exception as e:
            print(f"Error parsing JSON from {args.graph}: {e}", file=sys.stderr)
            sys.exit(1)

    port = find_available_port(args.port)
    html_file = os.path.join(DIR_PATH, "index.html")

    if not os.path.isfile(html_file):
        print(f"Error: index.html not found in {DIR_PATH}", file=sys.stderr)
        sys.exit(1)

    url_params = []
    if args.corpus:
        url_params.append(f"corpus={args.corpus}")
    query_string = ("?" + "&".join(url_params)) if url_params else ""
    local_url = f"http://{args.host}:{port}/{query_string}"
    file_url = f"file://{html_file}"

    print("=" * 72)
    print(" Lean 4 Formalization DAG Visualizer & Tufte Proof-Walk Engine")
    print("=" * 72)
    print(f" Web Server URL : {local_url}")
    print(f" Direct File URL: {file_url}")
    print(f" Root Directory : {DIR_PATH}")
    print("-" * 72)
    print(" Features:")
    print("  * Pure client-side zero-dependency application (no node/npm/CDN needed)")
    print("  * Built-in preloaded corpora:")
    print("      - Navier-Stokes & Euler (3D Blowup, BKM contradiction)")
    print("      - Fermat's Last Theorem (Frey curve, Mazur, Ribet, Taylor-Wiles)")
    print("      - EASCI (Stochastic CCV Contraction, simplex invariant)")
    print("  * Interactive pan/zoom, topological layering (Kahn/Tarjan), Tufte cards")
    print("  * SVG export for papers & presentations")
    print("  * Custom JSON graph import via 'Load JSON...' modal or --graph argument")
    print("=" * 72)
    print(" Press Ctrl+C to stop the server.")
    print("")

    if not args.no_browser:
        try:
            webbrowser.open(local_url)
        except Exception:
            pass

    socketserver.TCPServer.allow_reuse_address = True
    try:
        with socketserver.TCPServer((args.host, port), CustomGraphHandler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[OK] Server stopped cleanly.")
        sys.exit(0)


if __name__ == "__main__":
    main()
