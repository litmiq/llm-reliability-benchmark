# LLM Reliability Benchmark 2026

A [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) dataset for a single, dated evaluation run of **12 open chat models** on **40 deterministic tests**.

- **Canonical page:** https://litmiq.com/llm-reliability-benchmark
- **Dataset page:** https://litmiq.com/datasets/llm-reliability-benchmark
- **Released:** 12 November 2026
- **License:** CC BY 4.0
- **Citation:** Litmiq (2026). LLM Reliability Benchmark 2026 (suite v1.0) [Data set]. Measured 12 November 2026 on Cloudflare Workers AI. https://litmiq.com/llm-reliability-benchmark and https://litmiq.com/datasets/llm-reliability-benchmark. License: CC BY 4.0.

This is a public data repository. It is not the Litmiq app.

## What was measured

- **12 models** reached on the Cloudflare Workers AI REST API (Workers Free plan). **13 were attempted**; `@cf/google/gemma-3-12b-it` returned HTTP 403 ("This account is not allowed to access") on 12 November 2026 and is listed under `unmeasured` in `summary.json`. It was not scored.
- **40 tests** in five categories (8 each): prompt injection, structured output, instruction following, refusal calibration, and grounded answers.
- **Grader:** deterministic only (no LLM judge). The grader and runner are included (`grade.py`, `run_benchmark.py`). Suite version 1.0, grader version 1.0.1.
- **Decoding:** temperature 0, `max_tokens` 400.
- **Runs:** run 1 is 40 cases × 12 models; run 2 (stability) is 11 security cases × 12 models. `results.csv` has **612** rows.

Do not treat this as a general "best model" ranking. It is one public run, on one provider, on one 40-case suite, on one date.

## Files

| File | Description |
| --- | --- |
| `results.csv` / `results.json` | Per-call results (612 rows) |
| `leaderboard.csv` / `summary.json` | Per-model totals and run metadata |
| `suite-v1.0.json` | The 40-test suite |
| `grade.py` / `run_benchmark.py` | Deterministic grader and runner |
| `CHANGELOG.md` / `latest.json` | Version pointer and changelog |
| `LICENSE` | CC BY 4.0 notice |
| `huggingface-dataset-card.md` | Dataset card ready for a Hugging Face upload |

## Credit

Credit "Litmiq LLM Reliability Benchmark 2026" and link to https://litmiq.com/llm-reliability-benchmark.
