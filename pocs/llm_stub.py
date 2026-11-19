"""Deterministic OpenAI-compatible LLM stub.

Stands in for the configured model. First call (tools present, no tool result):
asks the model to call the first discovered tool. Second call (tool result
present): echoes the tool output verbatim. No hidden magic: the only thing the
stub decides is *to call the tool that the connected MCP server exposed*.
"""
import datetime
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

LOG = os.environ.get("LLM_LOG", "/tmp/llm_stub.log")


def log(obj) -> None:
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    with open(LOG, "a") as f:
        f.write(json.dumps({"ts": ts, "req": obj}) + "\n")


class H(BaseHTTPRequestHandler):
    def do_POST(self):  # noqa: N802
        n = int(self.headers.get("Content-Length", "0"))
        body = json.loads(self.rfile.read(n) or b"{}")
        log(body)
        msgs = body.get("messages", [])
        tools = body.get("tools") or []
        tool_msgs = [m for m in msgs if m.get("role") == "tool"]
        model = body.get("model", "stub-model")

        if tool_msgs:
            content = "ECHO:" + str(tool_msgs[-1].get("content"))
            msg = {"role": "assistant", "content": content}
            finish = "stop"
        elif tools:
            name = tools[0]["function"]["name"]
            msg = {
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "id": "call_internal_1",
                        "type": "function",
                        "function": {"name": name, "arguments": "{}"},
                    }
                ],
            }
            finish = "tool_calls"
        else:
            msg = {"role": "assistant", "content": "no tools"}
            finish = "stop"

        if body.get("stream"):
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()

            def emit(delta, fr=None):
                c = {"id": "chatcmpl-stub", "object": "chat.completion.chunk",
                     "created": 0, "model": model,
                     "choices": [{"index": 0, "delta": delta, "finish_reason": fr}]}
                self.wfile.write(b"data: " + json.dumps(c).encode() + b"\n\n")
                self.wfile.flush()

            first = {"role": "assistant"}
            first.update({k: v for k, v in msg.items() if k != "role"})
            emit(first)
            emit({}, finish)
            self.wfile.write(b"data: [DONE]\n\n")
            self.wfile.flush()
            return

        resp = {
            "id": "chatcmpl-stub",
            "object": "chat.completion",
            "created": 0,
            "model": model,
            "choices": [{"index": 0, "message": msg, "finish_reason": finish}],
            "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
        }
        out = json.dumps(resp).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(out)))
        self.end_headers()
        self.wfile.write(out)

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    open(LOG, "w").close()
    ThreadingHTTPServer(("0.0.0.0", 8081), H).serve_forever()
