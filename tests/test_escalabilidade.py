#!/usr/bin/env python3
"""
test_escalabilidade.py
Calcula eficiência horizontal dado throughput de 1 instância e N instâncias.
Uso:
    python test_escalabilidade.py --t1 1200 --tN 2100 --instances 2
Retorna: eficiência = (throughput_N / (throughput_1 * instances)) * 100
"""
import argparse, json, os
from datetime import datetime

def ensure_results_dir(path="results"):
    os.makedirs(path, exist_ok=True)
    return path

def eficiencia(t1, tN, instances):
    if t1 * instances == 0:
        return 0.0
    return (tN / (t1 * instances)) * 100.0

def save_summary(summary, prefix="scalability"):
    d = datetime.now().strftime("%Y%m%d_%H%M%S")
    p = ensure_results_dir()
    fn = os.path.join(p, f"{prefix}_summary_{d}.json")
    with open(fn, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    return fn

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--t1", type=float, required=True, help="Throughput (req/s) 1 instância")
    parser.add_argument("--tN", type=float, required=True, help="Throughput (req/s) N instâncias")
    parser.add_argument("--instances", type=int, default=2)
    parser.add_argument("--meta_eff", type=float, default=80.0)
    args = parser.parse_args()

    eff = eficiencia(args.t1, args.tN, args.instances)
    summary = {
        "throughput_one_instance": args.t1,
        "throughput_N_instances": args.tN,
        "instances": args.instances,
        "eficiencia_pct": eff,
        "meta": f"> {args.meta_eff}%"
    }
    summary["passed"] = eff > args.meta_eff
    fn = save_summary(summary)
    print("=== Escalabilidade ===")
    print(f"T1: {args.t1:.2f} req/s, TN: {args.tN:.2f} req/s, Instances: {args.instances}")
    print(f"Eficiência horizontal: {eff:.2f}% -> {'APROVADO' if summary['passed'] else 'REPROVADO'}")
    print("Saved:", fn)

if __name__ == "__main__":
    main()
