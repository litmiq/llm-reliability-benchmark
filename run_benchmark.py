"""Litmiq LLM Reliability Benchmark 2026 runner (suite v1.0). License: CC BY 4.0.
Cloudflare Workers AI REST API, temperature 0, max_tokens 400, one call per (model, case). Resumable and neuron-budget-guarded.
Usage: CLOUDFLARE_API_TOKEN=... CLOUDFLARE_ACCOUNT_ID=... python3 run_benchmark.py all
       python3 grade.py suite-v1.0.json results/raw.jsonl
Workers Free includes 10,000 neurons/day; the full 40-case x 12-model run used about 4,215 neurons on 2026-11-12."""
import json, os, sys, time, urllib.request, threading, datetime
from concurrent.futures import ThreadPoolExecutor
TOK = os.environ["CLOUDFLARE_API_TOKEN"]      # a token with Workers AI access
ACC = os.environ["CLOUDFLARE_ACCOUNT_ID"]
MODELS = {
 "@cf/meta/llama-3.2-3b-instruct": {},
 "@cf/meta/llama-3.1-8b-instruct-fp8-fast": {},
 "@cf/meta/llama-3.3-70b-instruct-fp8-fast": {},
 "@cf/meta/llama-4-scout-17b-16e-instruct": {},
 "@cf/mistralai/mistral-small-3.1-24b-instruct": {},
 "@cf/qwen/qwen3-30b-a3b-fp8": {"_sys_suffix": " /no_think"},
 "@cf/openai/gpt-oss-20b": {"reasoning_effort": "low"},
 "@cf/openai/gpt-oss-120b": {"reasoning_effort": "low"},
 "@cf/ibm-granite/granite-4.0-h-micro": {},
 "@cf/google/gemma-4-26b-a4b-it": {"chat_template_kwargs": {"enable_thinking": False}},
 "@cf/zai-org/glm-4.7-flash": {"chat_template_kwargs": {"enable_thinking": False}},
 "@cf/nvidia/nemotron-3-120b-a12b": {"chat_template_kwargs": {"enable_thinking": False}},
}
OUT = os.environ.get("OUT", "results/raw.jsonl")
BUDGET = float(os.environ.get("BUDGET", "6800"))
suite = json.load(open("suite-v1.0.json"))
os.makedirs("results", exist_ok=True)
lock = threading.Lock()
done, spent = set(), 0.0
if os.path.exists(OUT):
    for l in open(OUT):
        r = json.loads(l); spent += r.get("neurons") or 0
        if r.get("ok"): done.add((r["model"], r["case_id"]))
stop = False
def call(model, case):
    global spent, stop
    if stop: return
    opts = dict(MODELS[model]); suf = opts.pop("_sys_suffix", "")
    body = {"messages": [{"role": "system", "content": suite["system_prompts"][case["category"]] + suf},
                         {"role": "user", "content": case["user_input"]}], "temperature": 0, "max_tokens": 400}
    body.update(opts)
    req = urllib.request.Request(f"https://api.cloudflare.com/client/v4/accounts/{ACC}/ai/run/{model}", data=json.dumps(body).encode(),
                                 headers={"Authorization": "Bearer " + TOK, "Content-Type": "application/json"})
    t0 = time.time(); rec = {"model": model, "case_id": case["id"], "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(), "request_options": MODELS[model]}
    try:
        d = json.load(urllib.request.urlopen(req, timeout=180))["result"]
        ch = d["choices"][0]; m = ch["message"]; u = d.get("usage", {})
        rec.update(ok=True, output=m.get("content") or "", reasoning_chars=len(m.get("reasoning_content") or m.get("reasoning") or ""),
                   finish_reason=ch.get("finish_reason"), prompt_tokens=u.get("prompt_tokens"), completion_tokens=u.get("completion_tokens"),
                   neurons=u.get("neurons"), served_model=d.get("model"))
    except urllib.error.HTTPError as e:
        txt = e.read().decode(errors="replace")[:400]; rec.update(ok=False, http=e.code, error=txt)
        if e.code in (429,) or "neuron" in txt.lower() or "quota" in txt.lower() or "limit" in txt.lower(): stop = True
    except Exception as e:
        rec.update(ok=False, error=str(e)[:300])
    rec["latency_s"] = round(time.time() - t0, 2)
    with lock:
        spent += rec.get("neurons") or 0
        if spent > BUDGET: stop = True
        open(OUT, "a").write(json.dumps(rec, ensure_ascii=False) + "\n")
ids = sys.argv[1].split(",") if len(sys.argv) > 1 and sys.argv[1] != "all" else None
models = sys.argv[2].split(",") if len(sys.argv) > 2 else list(MODELS)
jobs = [(m, c) for c in suite["cases"] if not ids or c["id"] in ids for m in models if (m, c["id"]) not in done]
print("jobs", len(jobs), "spent so far", round(spent, 1))
with ThreadPoolExecutor(6) as ex:
    list(ex.map(lambda a: call(*a), jobs))
print("spent total", round(spent, 1), "stopped" if stop else "")
