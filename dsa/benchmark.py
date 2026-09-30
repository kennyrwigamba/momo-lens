"""Compare linear search vs dictionary lookup on at least 20 transaction ids"""

import json
import time
from pathlib import Path

from dsa.search import dict_search, linear_search
from dsa.store import get_default_store

DOCS_DIR = Path(__file__).resolve().parent.parent / "docs"
REPEATS = 200  


def time_lookup(search_fn, data, target_id):
    start = time.perf_counter()
    for _ in range(REPEATS):
        search_fn(data, target_id)
    return (time.perf_counter() - start) / REPEATS * 1_000_000


def main():
    store = get_default_store()
    transaction_list = store.transaction_list
    transaction_dict = store.transaction_dict
    total = len(transaction_list)

    step = max(1, total // 20)
    target_ids = [transaction_list[i]["id"] for i in range(0, total, step)][:20]

    print(f"Transactions loaded: {total}")
    print(f"Testing {len(target_ids)} ids ({REPEATS} repeats each)\n")
    print(f"{'#':<4} {'ID':<20} {'Linear (us)':>14} {'Dict (us)':>12}")
    print("-" * 52)

    results = []
    linear_sum = 0.0
    dict_sum = 0.0

    for number, target_id in enumerate(target_ids, start=1):
        linear_us = time_lookup(linear_search, transaction_list, target_id)
        dict_us = time_lookup(dict_search, transaction_dict, target_id)
        linear_sum += linear_us
        dict_sum += dict_us

        print(f"{number:<4} {target_id:<20} {linear_us:>14.2f} {dict_us:>12.2f}")
        results.append({
            "id": target_id,
            "linear_us": round(linear_us, 2),
            "dict_us": round(dict_us, 2),
        })

    avg_linear = linear_sum / len(target_ids)
    avg_dict = dict_sum / len(target_ids)
    speedup = avg_linear / avg_dict if avg_dict else 0

    print("-" * 52)
    print(f"Average linear search: {avg_linear:.2f} us  (O(n))")
    print(f"Average dict lookup:   {avg_dict:.2f} us  (O(1))")
    print(f"Dict lookup is about {speedup:.0f}x faster on average")

    report = {
        "dataset_size": total,
        "ids_tested": len(target_ids),
        "repeats_per_id": REPEATS,
        "avg_linear_us": round(avg_linear, 2),
        "avg_dict_us": round(avg_dict, 2),
        "speedup": round(speedup, 1),
        "results": results,
    }

    DOCS_DIR.mkdir(exist_ok=True)
    json_path = DOCS_DIR / "benchmark_results.json"
    json_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"\nSaved {json_path}")


if __name__ == "__main__":
    main()
