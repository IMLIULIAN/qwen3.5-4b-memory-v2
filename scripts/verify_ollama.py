#!/usr/bin/env python3
"""Standalone verification script for Qwen3.5-4B-Memory-V2 on Ollama.

Runs the public synthetic evaluation suite (examples/public_synthetic_eval.jsonl)
against a local or remote Ollama endpoint and checks:
  1. Strict JSON validity (no prose/markdown wrapper)
  2. Output schema compliance (fact extraction & fact admission contracts)
  3. Evidence ID grounding (no hallucinated segment IDs)
  4. Record-date vs effective-date separation & admission decision accuracy
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SUITE = ROOT / "examples" / "public_synthetic_eval.jsonl"
EXTRACT_PROMPT_FILE = ROOT / "prompts" / "fact_extraction_system.txt"
ADMIT_PROMPT_FILE = ROOT / "prompts" / "fact_admission_system.txt"

VALID_FACT_TYPES = {"world", "experience", "observation"}
VALID_DECISIONS = {"pass", "revise", "drop", "hold"}


def call_ollama(
    base_url: str,
    model: str,
    system_prompt: str,
    user_payload: dict,
    num_ctx: int,
    timeout: int,
) -> tuple[str, float, float]:
    url = f"{base_url.rstrip('/')}/api/chat"
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False)},
        ],
        "stream": False,
        "think": False,
        "options": {
            "num_ctx": num_ctx,
            "temperature": 0.0,
            "top_k": 20,
            "top_p": 0.95,
            "presence_penalty": 0.0,
        },
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        res = json.loads(resp.read().decode("utf-8"))
    elapsed = time.time() - t0
    content = ((res.get("message") or {}).get("content") or "").strip()
    eval_count = float(res.get("eval_count") or 0)
    eval_duration_ns = float(res.get("eval_duration") or 0)
    tps = (eval_count / (eval_duration_ns / 1e9)) if eval_duration_ns > 0 else 0.0
    return content, elapsed, tps


def validate_extraction(raw: str, case: dict) -> tuple[bool, list[str]]:
    errors: list[str] = []
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        return False, [f"invalid_json: {exc}"]

    if not isinstance(data, dict) or not isinstance(data.get("facts"), list):
        return False, ["missing top-level list key 'facts'"]

    facts = data["facts"]
    checks = case.get("checks", {})
    valid_ids = set(checks.get("valid_evidence_ids", []))
    forbidden_dates = set(checks.get("forbidden_occurred_dates", []))
    min_facts = int(checks.get("min_facts", 1))

    if len(facts) < min_facts:
        errors.append(f"too_few_facts: got {len(facts)}, expected >= {min_facts}")

    required_keys = {"text", "type", "occurred_start", "occurred_end", "where", "entities", "evidence"}
    all_text = []
    for idx, f in enumerate(facts):
        if not isinstance(f, dict):
            errors.append(f"fact[{idx}] is not an object")
            continue
        missing = required_keys - set(f.keys())
        if missing:
            errors.append(f"fact[{idx}] missing keys: {sorted(missing)}")
        if f.get("type") not in VALID_FACT_TYPES:
            errors.append(f"fact[{idx}] invalid type: {f.get('type')!r}")
        ev = f.get("evidence")
        if not isinstance(ev, list) or not (1 <= len(ev) <= 4):
            errors.append(f"fact[{idx}] invalid evidence list: {ev!r}")
        elif valid_ids and not set(ev).issubset(valid_ids):
            errors.append(f"fact[{idx}] hallucinated evidence IDs: {sorted(set(ev) - valid_ids)}")
        occ_start = str(f.get("occurred_start") or "")
        for fd in forbidden_dates:
            if fd and fd in occ_start:
                errors.append(f"fact[{idx}] record_date leaked into occurred_start: {occ_start}")
        all_text.append(str(f.get("text") or ""))

    must_any = checks.get("must_contain_any", [])
    if must_any:
        joined = "\n".join(all_text)
        if not any(tok in joined for tok in must_any):
            errors.append(f"missing expected key tokens: {must_any}")

    return len(errors) == 0, errors


def validate_admission(raw: str, case: dict) -> tuple[bool, list[str]]:
    errors: list[str] = []
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        return False, [f"invalid_json: {exc}"]

    if not isinstance(data, dict):
        return False, ["top-level JSON must be an object keyed by candidate ID"]

    expected = case.get("expected_decisions", {})
    valid_ids = {seg["id"] for seg in case["input"].get("evidence", [])}

    for cid, allowed in expected.items():
        slot = data.get(cid)
        if not isinstance(slot, dict):
            errors.append(f"slot[{cid}] missing or not an object")
            continue
        for k in ("decision", "evidence", "replacement"):
            if k not in slot:
                errors.append(f"slot[{cid}] missing key {k!r}")
        dec = slot.get("decision")
        if dec not in VALID_DECISIONS:
            errors.append(f"slot[{cid}] invalid decision {dec!r}")
        elif dec not in allowed:
            errors.append(f"slot[{cid}] decision={dec!r}, expected one of {allowed}")
        ev = slot.get("evidence")
        if not isinstance(ev, list) or not set(ev).issubset(valid_ids):
            errors.append(f"slot[{cid}] invalid evidence IDs: {ev!r}")
        if dec == "revise" and not str(slot.get("replacement") or "").strip():
            errors.append(f"slot[{cid}] decision='revise' requires non-empty replacement")
        if dec in {"drop", "hold"} and str(slot.get("replacement") or "").strip():
            errors.append(f"slot[{cid}] decision={dec!r} should have empty replacement")

    return len(errors) == 0, errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify Qwen3.5-4B-Memory-V2 via Ollama API.")
    parser.add_argument("--model", default="qwen3.5:4b-memory-v2", help="Ollama model name")
    parser.add_argument("--base-url", default="http://127.0.0.1:11434", help="Ollama API base URL")
    parser.add_argument("--num-ctx", type=int, default=16384, help="Context window (default: 16384)")
    parser.add_argument("--timeout", type=int, default=90, help="Per-request timeout in seconds")
    parser.add_argument("--suite", type=Path, default=DEFAULT_SUITE, help="Path to synthetic JSONL suite")
    parser.add_argument("--save-report", type=Path, default=None, help="Optional JSON output report path")
    args = parser.parse_args()

    extract_sys = EXTRACT_PROMPT_FILE.read_text(encoding="utf-8").strip()
    admit_sys = ADMIT_PROMPT_FILE.read_text(encoding="utf-8").strip()
    cases = [json.loads(line) for line in args.suite.read_text(encoding="utf-8").splitlines() if line.strip()]

    passed = 0
    total_sec = 0.0
    tps_list = []
    report_rows = []

    print(f"Verifying model={args.model} against {len(cases)} public synthetic cases (num_ctx={args.num_ctx})...\n")
    for idx, case in enumerate(cases, 1):
        task = case["task"]
        sys_prompt = extract_sys if task == "extraction" else admit_sys
        try:
            raw, elapsed, tps = call_ollama(
                args.base_url, args.model, sys_prompt, case["input"], args.num_ctx, args.timeout
            )
            ok, errs = (
                validate_extraction(raw, case) if task == "extraction" else validate_admission(raw, case)
            )
        except urllib.error.URLError as exc:
            raw, elapsed, tps, ok, errs = "", 0.0, 0.0, False, [f"connection_error: {exc}"]
        except Exception as exc:
            raw, elapsed, tps, ok, errs = "", 0.0, 0.0, False, [f"runtime_error: {exc}"]

        total_sec += elapsed
        if tps > 0:
            tps_list.append(tps)
        if ok:
            passed += 1
        status = "PASS" if ok else "FAIL"
        print(f"  [{idx:02d}/{len(cases)}] {case['id']:<12} ({task:<10}) | {status} | {elapsed:5.2f}s | {tps:5.1f} tok/s")
        if errs:
            for e in errs:
                print(f"       -> {e}")
        report_rows.append({
            "id": case["id"],
            "task": task,
            "passed": ok,
            "elapsed_sec": round(elapsed, 3),
            "tokens_per_sec": round(tps, 2),
            "errors": errs,
            "output": raw,
        })

    mean_tps = sum(tps_list) / len(tps_list) if tps_list else 0.0
    print(f"\nSummary: {passed}/{len(cases)} passed | total={total_sec:.2f}s | avg_speed={mean_tps:.1f} tok/s")

    if args.save_report:
        args.save_report.parent.mkdir(parents=True, exist_ok=True)
        args.save_report.write_text(
            json.dumps(
                {
                    "model": args.model,
                    "num_ctx": args.num_ctx,
                    "passed": passed,
                    "total": len(cases),
                    "total_sec": round(total_sec, 3),
                    "avg_tokens_per_sec": round(mean_tps, 2),
                    "cases": report_rows,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        print(f"Report written to {args.save_report}")

    return 0 if passed == len(cases) else 1


if __name__ == "__main__":
    sys.exit(main())
