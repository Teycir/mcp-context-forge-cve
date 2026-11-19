"""Isolation control: run inside the attacker container.

Proves the internal MCP port is not reachable from the attacker network
position, so the only path to it is the gateway's own loopback.
"""
import socket

for host in ("10.77.0.2", "127.0.0.1"):
    s = socket.socket()
    s.settimeout(3)
    try:
        s.connect((host, 19000))
        print(f"{host}:19000 OPEN")
    except Exception as e:  # noqa: BLE001
        print(f"{host}:19000 BLOCKED {type(e).__name__}: {e}")
    finally:
        s.close()
