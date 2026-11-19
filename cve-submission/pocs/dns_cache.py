"""Minimal TTL-honouring caching resolver for the lab (replaces dnsmasq).

Listens on 127.0.0.1:53 inside the gateway container, forwards rebind.test to
the attacker's authoritative server, and caches the answer for its TTL.
TTL=0 is not cached (same behaviour as dnsmasq). SIGHUP clears the cache.
"""
import signal
import socket
import struct
import threading
import time

UPSTREAM = ("10.77.0.3", 5353)
ZONE = "rebind.test"
LOG = "/tmp/dns_cache.log"

cache = {}
lock = threading.Lock()


def log(msg):
    with open(LOG, "a") as f:
        f.write(f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} {msg}\n")


def parse_qname(data, off=12):
    labels = []
    while True:
        n = data[off]
        off += 1
        if n == 0:
            break
        labels.append(data[off:off + n].decode(errors="replace"))
        off += n
    return ".".join(labels).lower(), off


def answer(data, ip, ttl):
    _, off = parse_qname(data)
    question = data[12:off + 4]
    return (data[:2] + struct.pack("!HHHHH", 0x8180, 1, 1, 0, 0) + question
            + b"\xc0\x0c" + struct.pack("!HHIH", 1, 1, ttl, 4) + socket.inet_aton(ip))


def parse_a(resp):
    _, off = parse_qname(resp)
    off += 4
    if resp[off] & 0xC0 == 0xC0:
        off += 2
    else:
        while resp[off]:
            off += resp[off] + 1
        off += 1
    rtype, _rclass, ttl, rdlen = struct.unpack("!HHIH", resp[off:off + 10])
    off += 10
    if rtype == 1 and rdlen == 4:
        return socket.inet_ntoa(resp[off:off + 4]), ttl
    return None, ttl


def on_hup(*_):
    with lock:
        n = len(cache)
        cache.clear()
    log(f"CACHE_FLUSH {n}")


def main():
    open(LOG, "w").close()
    signal.signal(signal.SIGHUP, on_hup)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("127.0.0.1", 53))
    log("START cache 127.0.0.1:53 upstream 10.77.0.3:5353")
    while True:
        data, addr = s.recvfrom(4096)
        try:
            name, _ = parse_qname(data)
            if name != ZONE:
                log(f"DROP name={name}")
                continue
            with lock:
                hit = cache.get(name)
                if hit and hit[1] > time.time():
                    ip, exp = hit
                    ttl = int(exp - time.time())
                    s.sendto(answer(data, ip, ttl), addr)
                    log(f"HIT {name} -> {ip} ttl={ttl}")
                    continue
            u = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            u.settimeout(3)
            u.sendto(data, UPSTREAM)
            resp, _ = u.recvfrom(4096)
            u.close()
            ip, ttl = parse_a(resp)
            if ip and ttl > 0:
                with lock:
                    cache[name] = (ip, time.time() + ttl)
            log(f"MISS {name} -> {ip} ttl={ttl} cached={bool(ip and ttl > 0)}")
            s.sendto(resp, addr)
        except Exception as e:  # noqa: BLE001
            log(f"ERR {e}")


if __name__ == "__main__":
    main()
