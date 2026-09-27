# MoMo Lens — DSA Benchmark Report
## Linear Search vs. Dictionary Lookup Performance

**Course:** Enterprise Web Development (ALU)  
**Team:** Web Artisans  
**Module:** `dsa/benchmark.py`  
**Dataset:** `modified_sms_v2.xml` (1683 transactions)  

---

### 1. Executive Summary

To satisfy the **Sprint 3 DSA Rubric Requirement**, we benchmarked retrieval by transaction ID using two foundational data structures:
1. **Linear Search (`list[dict]`)**: Sequentially iterates through the collection until the matching `id` is located ($O(n)$ average/worst-case complexity).
2. **Dictionary Hash Lookup (`dict[str, dict]`)**: Uses Python's built-in hash map ($O(1)$ amortized complexity).

**Key Findings:**
- **Evaluated Lookups:** 24 distinct IDs across early, middle, late, and missing categories.
- **Iterations per ID:** 500 repeated cycles for microsecond precision.
- **Average Linear Search Time:** **42.345 µs**
- **Average Dict Lookup Time:** **0.071 µs**
- **Performance Advantage:** Dictionary lookup is **594.9× faster** on average.

---

### 2. Theoretical Complexity Comparison

| Algorithm | Data Structure | Best Case | Average Case | Worst Case | Space Complexity |
|---|---|:---:|:---:|:---:|:---:|
| **Linear Search** | `list[dict]` | $O(1)$ *(index 0)* | $O(n/2) \approx O(n)$ | $O(n)$ *(end or missing)* | $O(1)$ |
| **Dictionary Lookup** | `dict[str, dict]` | $O(1)$ | $O(1)$ | $O(n)$ *(hash collision)* | $O(n)$ auxiliary |

---

### 3. Empirical Results Table (>= 20 Lookups)

| # | Target ID | Position / Test Case | Linear Search (µs) | Dict Lookup (µs) | Speedup Factor |
|---|---|---|:---:|:---:|:---:|
| 1 | `76662021700` | Early (index 0) | 0.281 µs | 0.072 µs | **3.9×** |
| 2 | `26614842768` | Early (index 10) | 0.481 µs | 0.064 µs | **7.5×** |
| 3 | `98755359894` | Early (index 25) | 1.117 µs | 0.062 µs | **18.1×** |
| 4 | `sms_51` | Early (index 50) | 2.196 µs | 0.061 µs | **36.1×** |
| 5 | `sms_107` | Early (index 100) | 3.546 µs | 0.061 µs | **58.5×** |
| 6 | `sms_157` | Early (index 150) | 5.762 µs | 0.063 µs | **92.0×** |
| 7 | `60128198918` | Middle (index 300) | 23.179 µs | 0.14 µs | **165.8×** |
| 8 | `46934619518` | Middle (index 500) | 25.321 µs | 0.069 µs | **369.1×** |
| 9 | `sms_709` | Middle (index 700) | 31.433 µs | 0.068 µs | **462.3×** |
| 10 | `sms_859` | Middle (index 850) | 38.527 µs | 0.066 µs | **585.5×** |
| 11 | `16016087305` | Middle (index 1000) | 43.409 µs | 0.062 µs | **700.1×** |
| 12 | `93824792341` | Middle (index 1150) | 50.383 µs | 0.067 µs | **749.7×** |
| 13 | `sms_1309` | Late (index 1300) | 48.521 µs | 0.063 µs | **775.1×** |
| 14 | `17140081149` | Late (index 1400) | 64.302 µs | 0.071 µs | **908.2×** |
| 15 | `17878271668` | Late (index 1500) | 70.139 µs | 0.067 µs | **1046.8×** |
| 16 | `26480204749` | Late (index 1600) | 70.581 µs | 0.066 µs | **1063.0×** |
| 17 | `98632277447` | Late (index 1650) | 75.219 µs | 0.072 µs | **1044.7×** |
| 18 | `37832903831` | Late (index 1682) | 75.235 µs | 0.066 µs | **1146.9×** |
| 19 | `NOT_FOUND_90001` | Not Found (worst case O(n)) | 61.735 µs | 0.065 µs | **949.8×** |
| 20 | `NOT_FOUND_90002` | Not Found (worst case O(n)) | 62.259 µs | 0.064 µs | **966.8×** |
| 21 | `NOT_FOUND_90003` | Not Found (worst case O(n)) | 59.672 µs | 0.063 µs | **947.2×** |
| 22 | `INVALID_TX_ABC` | Not Found (worst case O(n)) | 75.945 µs | 0.123 µs | **615.4×** |
| 23 | `DUMMY_SMS_9999` | Not Found (worst case O(n)) | 68.038 µs | 0.073 µs | **934.6×** |
| 24 | `UNKNOWN_TRANSACTION_ID` | Not Found (worst case O(n)) | 59.007 µs | 0.063 µs | **939.6×** |

---

### 4. Analysis & Engineering Conclusions

1. **Early vs. Late Position Degradation:**  
   In linear search, lookup times scale linearly with index position. Queries for IDs near the front of the list execute rapidly (~0.281 µs), while queries near the end take up to **75.235 µs**.
2. **Worst-Case Not-Found Lookups:**  
   When an ID does not exist in the collection, linear search is forced to inspect all 1683 elements, resulting in its slowest performance. Conversely, dictionary lookup returns `None` virtually instantaneously in constant time ($O(1)$).
3. **Application to MoMo Lens REST API:**  
   Because the REST API exposes high-throughput endpoints such as `GET /transactions/:id`, `PUT /transactions/:id`, and `DELETE /transactions/:id`, using the in-memory dictionary index ensures sub-microsecond response latency regardless of how large the transaction ledger grows.
