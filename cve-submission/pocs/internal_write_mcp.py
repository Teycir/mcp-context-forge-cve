"""Write-only internal MCP server (127.0.0.1:19001) for integrity-impact proof."""
import asyncio, datetime, os
from mcp.server.mcpserver import MCPServer
from mcp.server.transport_security import TransportSecuritySettings

LOG = os.environ.get("MCP_LOG", "/tmp/internal_write.log")
mcp = MCPServer("internal-write-only")
SECURITY = TransportSecuritySettings(enable_dns_rebinding_protection=False)


def log(msg: str) -> None:
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    with open(LOG, "a") as f:
        f.write(f"{ts} {msg}\n")


@mcp.tool(name="internal_write_proof_7f3a")
def write_proof() -> str:
    """Write a proof file on the internal host (integrity impact)."""
    log("TOOL_CALLED internal_write_proof_7f3a")
    with open("/tmp/internal_write_proof.txt", "w") as f:
        f.write("WRITE_PROOF_7f3a")
    return "WROTE_INTERNAL_FILE_7f3a"


async def main() -> None:
    log("START internal write mcp 127.0.0.1:19001")
    await mcp.run_streamable_http_async(host="127.0.0.1", port=19001,
                                        streamable_http_path="/mcp", transport_security=SECURITY)


if __name__ == "__main__":
    asyncio.run(main())
