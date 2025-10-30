#!/usr/bin/env python3
"""
test_estresse.py
Ramp-up incremental para detectar ponto de quebra (simplificado). Cada nível executa um curto burst de requests.
Uso:
    python test_estresse.py --url https://meuecommerce.test/ --start 1000 --step 1000 --max 30000
AVISO: NÃO rode contra ambiente de produção sem autorização.
"""
import argparse, requests, time, os, json
from multiprocessing import Pool, cpu_count
from datetime import datetime

def ensure_results_dir(path="results"):
    os.makedirs(path, exist_ok=True)
    return path

def worker_batch(args):
    target, requests_per_worker = args
    s = requests.Session()
    success = 0
    errors = 0
    latencies = []
    for _ in range(requests_per_worker):
        t0 = time.perf_counter()
        try:
            r = s.get(target, timeout=10)
            elapsed = (time.perf_counter() - t0)*1000.0
            latencies.append(elapsed)
            if 200 <= r.status_code < 400:
                success += 1
            else:
                errors += 1
        except Exception:
            errors += 1
    return {"success": success, "errors": errors, "latencies": latencies}

def test_level(target, virtual_users, per_process_requests=20):
    # distribute work across processes
    procs = min(cpu_count()*2, virtual_users)
    # each "virtual user" represented by small batch of requests
    requests_per_process = max(1, int((virtual_users * per_process_requests) / procs))
    pool = Pool(processes=procs)
    args = [(target, requests_per_process) for _ in range(procs)]
    results = pool.map(worker_batch, args)
    pool.close(); pool.join()
    total_success = sum(r["success"] for r in results)
    total_errors = sum(r["errors"] for r in results)
    all_lat = [v for r in results for v in r["latencies"]]
    p95 = sorted(all_lat)[int(0.95 * len(all_lat))] if all_lat else float("nan")
    error_rate = (total_errors / (total_success + total_errors) * 100) if (total_success+total_errors)>0 else 100.0
    return {"users": virtual_users, "p95_ms": p95, "error_rate_pct": error_rate, "success": total_success, "errors": total_errors}

def save_json(all_results, prefix="stress"):
    d = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = ensure_results_dir()
    fn = os.path.join(path, f"{prefix}_summary_{d}.json")
    with open(fn, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    return fn

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--start", type=int, default=1000)
    parser.add_argument("--step", type=int, default=1000)
    parser.add_argument("--max", type=int, default=30000)
    parser.add_argument("--meta_breakpoint", type=int, default=15000)
    args = parser.parse_args()

    print("AVISO: Não executar contra produção sem autorização. URL:", args.url)
    users = args.start
    all_results = []
    breakpoint_detected = None
    while users <= args.max:
        print(f"Testando nível: ~{users} usuários (este é um teste simplificado; em produção use Locust/k6)")
        res = test_level(args.url, users)
        print(f" -> P95={res['p95_ms']:.2f} ms, ErrorRate={res['error_rate_pct']:.2f}%")
        all_results.append(res)
        # fail criteria: error_rate > 5% or p95 > 2000 ms
        if res["error_rate_pct"] > 5.0 or (res["p95_ms"] and res["p95_ms"] > 2000.0):
            breakpoint_detected = users
            print(f"PONTO DE QUEBRA detectado em ~{users} usuários.")
            break
        users += args.step

    summary = {"levels": all_results, "breakpoint_users": breakpoint_detected, "meta": f"> {args.meta_breakpoint} users"}
    summary["passed"] = (breakpoint_detected is not None and breakpoint_detected > args.meta_breakpoint)
    fn = save_json(summary, prefix="stress")
    print("Resultado salvo em:", fn)
    print("Meta (>15000):", "APROVADO" if summary["passed"] else "REPROVADO")

if __name__ == "__main__":
    main()
