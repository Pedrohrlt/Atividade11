#!/usr/bin/env python3
"""
test_carga.py
Gera requisições contínuas com ThreadPoolExecutor por DURATION segundos e mede throughput.
Uso:
    python test_carga.py --url https://meuecommerce.test/ --duration 30 --workers 200
AVISO: NÃO rode contra ambiente de produção sem autorização.
"""
import argparse, requests, time, os, json
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

def ensure_results_dir(path="results"):
    os.makedirs(path, exist_ok=True)
    return path

def single_request(session, url, timeout=5):
    try:
        r = session.get(url, timeout=timeout)
        return r.status_code, True
    except Exception:
        return None, False

def run_load(target, duration, workers):
    session = requests.Session()
    total = 0
    success = 0
    start = time.time()
    end = start + duration
    events = []  # keep timestamp per request
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = []
        # continuously submit tasks while time is left
        while time.time() < end:
            futures.append(ex.submit(single_request, session, target))
            # gather finished futures to prevent memory growth
            done = [f for f in futures if f.done()]
            for f in done:
                futures.remove(f)
                total += 1
                status, ok = f.result()
                if ok and status and 200 <= status < 400:
                    success += 1
                events.append({"ts": time.time(), "status": status if status else "ERR"})
    elapsed = time.time() - start
    throughput = total / elapsed if elapsed > 0 else 0.0
    success_rate = (success / total * 100) if total else 0.0
    return {
        "total_requests": total,
        "success": success,
        "throughput_rps": throughput,
        "success_rate_pct": success_rate,
        "duration_s": elapsed,
        "events_sample": events[:1000]  # avoid huge json
    }

def save_json(summary, prefix="load"):
    d = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = ensure_results_dir()
    fn = os.path.join(path, f"{prefix}_summary_{d}.json")
    with open(fn, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    return fn

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--duration", type=int, default=30)
    parser.add_argument("--workers", type=int, default=200)
    parser.add_argument("--meta_throughput", type=float, default=2000.0)
    args = parser.parse_args()

    print("AVISO: Não executar contra produção sem autorização. URL:", args.url)
    summary = run_load(args.url, args.duration, args.workers)
    summary["meta"] = f"Throughput > {args.meta_throughput} req/s"
    summary["passed"] = summary["throughput_rps"] > args.meta_throughput and summary["success_rate_pct"] >= 98.0
    fn = save_json(summary, prefix="load")
    print("=== Carga (Resumo) ===")
    print(f"Total reqs: {summary['total_requests']}, Throughput: {summary['throughput_rps']:.2f} req/s, SuccessRate: {summary['success_rate_pct']:.2f}%")
    print(f"Meta Throughput > {args.meta_throughput}: {'APROVADO' if summary['passed'] else 'REPROVADO'}")
    print(f"Saved: {fn}")

if __name__ == "__main__":
    main()
