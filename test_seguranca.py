#!/usr/bin/env python3
"""
test_seguranca.py
Dispara N requisições sequenciais e verifica ocorrência de 429 (Too Many Requests).
Uso:
    python test_seguranca.py --url https://meuecommerce.test/api/login --requests 160 --delay 0.3
AVISO: respeite as políticas do serviço e não execute sem autorização.
"""
import argparse, requests, time, os, json
from datetime import datetime

def ensure_results_dir(path="results"):
    os.makedirs(path, exist_ok=True)
    return path

def run_rate_test(target, requests_count, delay_between):
    s = requests.Session()
    statuses = []
    first_ts = time.time()
    for i in range(requests_count):
        try:
            r = s.get(target, timeout=5)
            statuses.append({"i": i+1, "status": r.status_code, "ts": time.time()})
        except Exception as e:
            statuses.append({"i": i+1, "status": "ERR", "error": str(e), "ts": time.time()})
        time.sleep(delay_between)
    duration = time.time() - first_ts
    return statuses, duration

def analyze(statuses, duration, meta_rpm=100.0):
    counts = {}
    for s in statuses:
        st = s["status"]
        counts[st] = counts.get(st, 0) + 1
    # detect first 429 index
    first_429 = next((s["i"] for s in statuses if s["status"]==429), None)
    rpm_observed = len(statuses) / (duration/60.0) if duration>0 else float("nan")
    passed = (429 in counts) and (rpm_observed >= meta_rpm)
    return {"counts": counts, "first_429_req": first_429, "duration_s": duration, "rpm_observed": rpm_observed, "passed": passed, "meta": f"{meta_rpm} req/min/IP"}

def save_all(statuses, summary, prefix="security"):
    d = datetime.now().strftime("%Y%m%d_%H%M%S")
    p = ensure_results_dir()
    fn_raw = os.path.join(p, f"{prefix}_raw_{d}.json")
    fn_sum = os.path.join(p, f"{prefix}_summary_{d}.json")
    with open(fn_raw, "w", encoding="utf-8") as f:
        json.dump(statuses, f, indent=2, ensure_ascii=False)
    with open(fn_sum, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    return fn_raw, fn_sum

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--requests", type=int, default=160)
    parser.add_argument("--delay", type=float, default=0.3)
    parser.add_argument("--meta_rpm", type=float, default=100.0)
    args = parser.parse_args()

    print("AVISO: Não executar contra produção sem autorização. URL:", args.url)
    statuses, duration = run_rate_test(args.url, args.requests, args.delay)
    summary = analyze(statuses, duration, args.meta_rpm)
    raw_fn, sum_fn = save_all(statuses, summary)
    print("=== Segurança (Rate Limiting) ===")
    print("Counts sample:", summary["counts"])
    print(f"First 429 at request: {summary['first_429_req']}")
    print(f"Observed RPM: {summary['rpm_observed']:.2f}")
    print("Resultado:", "APROVADO" if summary["passed"] else "REPROVADO")
    print("Saved:", raw_fn, sum_fn)

if __name__ == "__main__":
    main()
