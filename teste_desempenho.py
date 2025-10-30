#!/usr/bin/env python3
"""
test_desempenho.py
Mede latências (ms) de N requisições assíncronas e calcula P50/P90/P95/P99.
Uso:
    python test_desempenho.py --url https://meuecommerce.test/produtos --requests 500
AVISO: NÃO rode contra ambiente de produção sem autorização.
"""
import argparse, asyncio, aiohttp, time, os, json
from datetime import datetime
import numpy as np

def ensure_results_dir(path="results"):
    os.makedirs(path, exist_ok=True)
    return path

async def fetch(session, url, timeout):
    t0 = time.perf_counter()
    try:
        async with session.get(url, timeout=timeout) as r:
            await r.read()
            t = (time.perf_counter() - t0) * 1000.0
            return {"status": r.status, "latency_ms": t}
    except Exception as e:
        t = (time.perf_counter() - t0) * 1000.0
        return {"status": "ERR", "latency_ms": t, "error": str(e)}

async def run_async(target, n, concurrency, timeout):
    sem = asyncio.Semaphore(concurrency)
    results = []
    async with aiohttp.ClientSession() as session:
        async def guarded_fetch():
            async with sem:
                return await fetch(session, target, timeout)
        tasks = [asyncio.create_task(guarded_fetch()) for _ in range(n)]
        for t in asyncio.as_completed(tasks):
            results.append(await t)
    return results

def summarize(results, meta_p95=500.0):
    latencies = [r["latency_ms"] for r in results if isinstance(r["latency_ms"], (int,float))]
    statuses = [r["status"] for r in results]
    success = sum(1 for s in statuses if isinstance(s,int) and 200 <= s < 400)
    errors = len(results) - success
    if latencies:
        p50 = float(np.percentile(latencies,50))
        p90 = float(np.percentile(latencies,90))
        p95 = float(np.percentile(latencies,95))
        p99 = float(np.percentile(latencies,99))
        avg = float(sum(latencies)/len(latencies))
    else:
        p50=p90=p95=p99=avg=float("nan")
    passed = p95 < meta_p95
    return {
        "total_requests": len(results),
        "success_count": success,
        "error_count": errors,
        "avg_ms": avg,
        "p50_ms": p50,
        "p90_ms": p90,
        "p95_ms": p95,
        "p99_ms": p99,
        "passed": passed,
        "meta": f"P95 < {meta_p95} ms"
    }

def save_json(summary, raw, prefix="performance"):
    d = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = ensure_results_dir()
    fn_raw = os.path.join(path, f"{prefix}_raw_{d}.json")
    fn_summary = os.path.join(path, f"{prefix}_summary_{d}.json")
    with open(fn_raw, "w", encoding="utf-8") as f:
        json.dump(raw, f, indent=2, ensure_ascii=False)
    with open(fn_summary, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    return fn_raw, fn_summary

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--requests", type=int, default=500)
    parser.add_argument("--concurrency", type=int, default=200)
    parser.add_argument("--timeout", type=int, default=10)
    parser.add_argument("--meta_p95", type=float, default=500.0)
    args = parser.parse_args()

    print("AVISO: Não executar contra produção sem autorização. URL:", args.url)
    results = asyncio.run(run_async(args.url, args.requests, args.concurrency, args.timeout))
    summary = summarize(results, args.meta_p95)
    raw_fn, sum_fn = save_json(summary, results, prefix="performance")
    print("=== Desempenho (Resumo) ===")
    print(f"Total: {summary['total_requests']}, Success: {summary['success_count']}, Errors: {summary['error_count']}")
    print(f"P95 = {summary['p95_ms']:.2f} ms -> { 'APROVADO' if summary['passed'] else 'REPROVADO' } (Meta: {summary['meta']})")
    print(f"Summary saved: {sum_fn}")
    print(f"Raw saved: {raw_fn}")

if __name__ == "__main__":
    main()
