# DSA Performance Benchmark: Linear Search vs Dictionary Lookup
# Compares search times across 24 test cases with multiple repetitions

import json
import sys
import time
from pathlib import Path

# Add project root to sys.path so imports work properly
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from dsa.search import dict_search, linear_search
from dsa.store import get_default_store


# Run benchmark comparing linear search vs dict lookup across >=20 target IDs
def run_benchmark(iterations_per_id=500):
    store = get_default_store()
    transaction_list = store.list
    transaction_dict = store.dict
    total_records = len(transaction_list)

    if total_records == 0:
        raise ValueError("Store is empty. Cannot run benchmark.")

    # Select 24 target IDs across different positions:
    # 6 Early positions (best-case for linear search)
    # 6 Middle positions (average-case for linear search)
    # 6 Late positions (worst-case hit for linear search)
    # 6 Non-existent IDs (worst-case miss: scans entire list)
    sample_indices = [
        # Early
        0, 10, 25, 50, 100, 150,
        # Middle
        300, 500, 700, 850, 1000, 1150,
        # Late
        1300, 1400, 1500, 1600, 1650, total_records - 1,
    ]

    targets = []
    for index in sample_indices:
        if index < total_records:
            transaction = transaction_list[index]
            position_label = "Early" if index < 200 else ("Middle" if index < 1200 else "Late")
            targets.append({
                "target_id": transaction["id"],
                "category": f"{position_label} (index {index})",
                "index": index,
                "exists": True,
            })

    # Add 6 non-existent IDs for worst-case analysis
    missing_ids = [
        "NOT_FOUND_90001",
        "NOT_FOUND_90002",
        "NOT_FOUND_90003",
        "INVALID_TX_ABC",
        "DUMMY_SMS_9999",
        "UNKNOWN_TRANSACTION_ID",
    ]
    for missing_id in missing_ids:
        targets.append({
            "target_id": missing_id,
            "category": "Not Found (worst case O(n))",
            "index": -1,
            "exists": False,
        })

    lookup_results = []
    total_linear_time_us = 0.0
    total_dict_time_us = 0.0

    print(f"\nRunning benchmark across {len(targets)} lookups ({iterations_per_id} iterations each)...")
    print(f"Total dataset size: {total_records} transactions\n")

    for run_number, target in enumerate(targets, start=1):
        target_id = target["target_id"]

        # 1. Benchmark Linear Search
        start_time = time.perf_counter()
        for _ in range(iterations_per_id):
            linear_result = linear_search(transaction_list, target_id)
        linear_duration = (time.perf_counter() - start_time) / iterations_per_id
        linear_microseconds = linear_duration * 1_000_000

        # 2. Benchmark Dictionary Lookup
        start_time = time.perf_counter()
        for _ in range(iterations_per_id):
            dict_result = dict_search(transaction_dict, target_id)
        dict_duration = (time.perf_counter() - start_time) / iterations_per_id
        dict_microseconds = dict_duration * 1_000_000

        # Speedup calculation
        speedup = (linear_microseconds / dict_microseconds) if dict_microseconds > 0 else 1.0
        total_linear_time_us += linear_microseconds
        total_dict_time_us += dict_microseconds

        lookup_results.append({
            "run": run_number,
            "target_id": target_id,
            "position": target["category"],
            "exists": target["exists"],
            "linear_time_us": round(linear_microseconds, 3),
            "dict_time_us": round(dict_microseconds, 3),
            "speedup_x": round(speedup, 1),
        })

    average_linear_us = total_linear_time_us / len(targets)
    average_dict_us = total_dict_time_us / len(targets)
    overall_speedup = (average_linear_us / average_dict_us) if average_dict_us > 0 else 1.0

    benchmark_data = {
        "dataset_size": total_records,
        "lookups_evaluated": len(targets),
        "iterations_per_id": iterations_per_id,
        "summary": {
            "avg_linear_search_time_us": round(average_linear_us, 3),
            "avg_dict_lookup_time_us": round(average_dict_us, 3),
            "overall_speedup_factor": round(overall_speedup, 1),
            "linear_complexity": "O(n)",
            "dict_complexity": "O(1)",
        },
        "results": lookup_results,
    }

    return benchmark_data


# Print clean summary table in the console
def print_ascii_table(benchmark_data):
    summary = benchmark_data["summary"]
    results = benchmark_data["results"]

    print("=" * 88)
    print("           MOMO LENS: DSA SEARCH BENCHMARK (LINEAR SEARCH vs DICT LOOKUP)")
    print("=" * 88)
    print(f"{'#':<3} | {'Target ID':<22} | {'Position / Case':<28} | {'Linear (us)':<11} | {'Dict (us)':<9} | {'Speedup':<8}")
    print("-" * 88)

    for result in results:
        print(
            f"{result['run']:<3} | {result['target_id']:<22} | {result['position']:<28} | "
            f"{result['linear_time_us']:>11.3f} | {result['dict_time_us']:>9.3f} | {result['speedup_x']:>7.1f}x"
        )

    print("-" * 88)
    print(f"Overall Average Linear Search Time : {summary['avg_linear_search_time_us']} us (O(n))")
    print(f"Overall Average Dict Lookup Time   : {summary['avg_dict_lookup_time_us']} us (O(1))")
    print(f"Dictionary Lookup Speedup          : {summary['overall_speedup_factor']}x FASTER")
    print("=" * 88 + "\n")


# Save benchmark results in Markdown and JSON formats for the team report
def save_reports(benchmark_data):
    docs_dir = ROOT_DIR / "docs"
    docs_dir.mkdir(exist_ok=True)

    # 1. Save JSON
    json_path = docs_dir / "benchmark_results.json"
    with open(json_path, "w", encoding="utf-8") as file:
        json.dump(benchmark_data, file, indent=2)

    # 2. Save Markdown
    summary = benchmark_data["summary"]
    results = benchmark_data["results"]
    markdown_path = docs_dir / "benchmark_results.md"

    content = f"""# MoMo Lens — DSA Benchmark Report
## Linear Search vs. Dictionary Lookup Performance

**Course:** Enterprise Web Development (ALU)  
**Team:** Web Artisans  
**Module:** `dsa/benchmark.py`  
**Dataset:** `modified_sms_v2.xml` ({benchmark_data['dataset_size']} transactions)  

---

### 1. Executive Summary

To satisfy the **Sprint 3 DSA Rubric Requirement**, we benchmarked retrieval by transaction ID using two foundational data structures:
1. **Linear Search (`list[dict]`)**: Sequentially iterates through the collection until the matching `id` is located ($O(n)$ average/worst-case complexity).
2. **Dictionary Hash Lookup (`dict[str, dict]`)**: Uses Python's built-in hash map ($O(1)$ amortized complexity).

**Key Findings:**
- **Evaluated Lookups:** {benchmark_data['lookups_evaluated']} distinct IDs across early, middle, late, and missing categories.
- **Iterations per ID:** {benchmark_data['iterations_per_id']} repeated cycles for microsecond precision.
- **Average Linear Search Time:** **{summary['avg_linear_search_time_us']} µs**
- **Average Dict Lookup Time:** **{summary['avg_dict_lookup_time_us']} µs**
- **Performance Advantage:** Dictionary lookup is **{summary['overall_speedup_factor']}× faster** on average.

---

### 2. Theoretical Complexity Comparison

| Algorithm | Data Structure | Best Case | Average Case | Worst Case | Space Complexity |
|---|---|:---:|:---:|:---:|:---:|
| **Linear Search** | `list[dict]` | $O(1)$ *(index 0)* | $O(n/2) \\approx O(n)$ | $O(n)$ *(end or missing)* | $O(1)$ |
| **Dictionary Lookup** | `dict[str, dict]` | $O(1)$ | $O(1)$ | $O(n)$ *(hash collision)* | $O(n)$ auxiliary |

---

### 3. Empirical Results Table (>= 20 Lookups)

| # | Target ID | Position / Test Case | Linear Search (µs) | Dict Lookup (µs) | Speedup Factor |
|---|---|---|:---:|:---:|:---:|
"""

    for result in results:
        content += (
            f"| {result['run']} | `{result['target_id']}` | {result['position']} | "
            f"{result['linear_time_us']} µs | {result['dict_time_us']} µs | **{result['speedup_x']}×** |\n"
        )

    content += f"""
---

### 4. Analysis & Engineering Conclusions

1. **Early vs. Late Position Degradation:**  
   In linear search, lookup times scale linearly with index position. Queries for IDs near the front of the list execute rapidly (~{results[0]['linear_time_us']} µs), while queries near the end take up to **{results[17]['linear_time_us']} µs**.
2. **Worst-Case Not-Found Lookups:**  
   When an ID does not exist in the collection, linear search is forced to inspect all {benchmark_data['dataset_size']} elements, resulting in its slowest performance. Conversely, dictionary lookup returns `None` virtually instantaneously in constant time ($O(1)$).
3. **Application to MoMo Lens REST API:**  
   Because the REST API exposes high-throughput endpoints such as `GET /transactions/:id`, `PUT /transactions/:id`, and `DELETE /transactions/:id`, using the in-memory dictionary index ensures sub-microsecond response latency regardless of how large the transaction ledger grows.
"""

    with open(markdown_path, "w", encoding="utf-8") as file:
        file.write(content)

    return markdown_path, json_path


if __name__ == "__main__":
    benchmark_data = run_benchmark(iterations_per_id=500)
    print_ascii_table(benchmark_data)
    markdown_file, json_file = save_reports(benchmark_data)
    print(f"Saved Markdown report to: {markdown_file}")
    print(f"Saved JSON data to:       {json_file}")
