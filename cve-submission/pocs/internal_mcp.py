"""Internal-only MCP server: bound to 127.0.0.1 inside the gateway container.

Simulates a loopback-bound internal service (admin/metrics/sidecar MCP).
Logs every session and tool call with UTC timestamps so the evidence shows
whether the gateway actually reached it.
"""
import asyncio
import datetime
import os

from mcp.server.mcpserver import MCPServer
from mcp.server.transport_security import TransportSecuritySettings

CANARY = os.environ.get("CANARY", "INTERNAL_ONLY_TOOL_REACHED_7f3a")
LOG = os.environ.get("MCP_LOG", "/tmp/internal.log")

mcp = MCPServer("internal-only")
SECURITY = TransportSecuritySettings(enable_dns_rebinding_protection=False)


def log(msg: str) -> None:
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    line = f"{ts} {msg}"
    print(line, flush=True)
    with open(LOG, "a") as f:
        f.write(line + "\n")


@mcp.tool(name="internal_only_secret_tool_7f3a")
def ssrf_proof() -> str:
    """Return the internal-only proof marker."""
    log("TOOL_CALLED internal_only_secret_tool_7f3a")
    return CANARY


async def main():
    log("START internal mcp 127.0.0.1:19000")
    await mcp.run_streamable_http_async(
        host="127.0.0.1",
        port=19000,
        streamable_http_path="/mcp",
        transport_security=SECURITY,
    )


if __name__ == "__main__":
    asyncio.run(main())
