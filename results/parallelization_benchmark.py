import os
import sys
import statistics
import multiprocessing as mp
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ciphers import columnar_transposition as transposition
from attacks.transposition_attack import attack

MIN_N = 4
MAX_N = 9
REPEATS = 1
BASE_PLAINTEXT = (
    "sphinx of black quartz judge my vow "
    "the quick brown fox jumps over the lazy dog"
)


def make_ciphertext(n: int) -> tuple:
    key = tuple((i * 7 + 3) % n for i in range(n))
    if sorted(key) != list(range(n)):
        key = tuple(reversed(range(n)))
    ciphertext = transposition.encrypt(BASE_PLAINTEXT, key)
    return key, ciphertext


def measure_repeated(ciphertext: str, n: int, key: tuple, force_mode: str,
                      num_workers: int, repeats: int) -> tuple:
    times = []
    for _ in range(repeats):
        result = attack(ciphertext, key_length=n, force_mode=force_mode,
                         num_workers=num_workers)
        assert result["best_key"] == key
        times.append(result["elapsed_seconds"])

    avg = statistics.mean(times)
    stdev = statistics.stdev(times) if repeats > 1 else 0.0
    return avg, stdev


def run_benchmark():
    ns = list(range(MIN_N, MAX_N + 1))
    key_spaces = [transposition.key_space_size(n) for n in ns]
    single_avg_times = []
    single_stdevs = []
    parallel_avg_times = []
    parallel_stdevs = []
    num_workers = mp.cpu_count()

    print(f"CPU cores available: {num_workers}")
    print(f"Repeats per measurement: {REPEATS}")
    print(f"{'n':>3} {'key space':>12} {'single avg (s)':>15} {'parallel avg (s)':>17} {'speedup':>8}")
    print("-" * 62)

    for n in ns:
        key, ciphertext = make_ciphertext(n)

        avg_single, std_single = measure_repeated(
            ciphertext, n, key, "single", num_workers, REPEATS)
        avg_parallel, std_parallel = measure_repeated(
            ciphertext, n, key, "parallel", num_workers, REPEATS)

        single_avg_times.append(avg_single)
        single_stdevs.append(std_single)
        parallel_avg_times.append(avg_parallel)
        parallel_stdevs.append(std_parallel)

        speedup = avg_single / avg_parallel if avg_parallel > 0 else float("inf")
        print(f"{n:>3} {transposition.key_space_size(n):>12,} "
              f"{avg_single:>15.4f} {avg_parallel:>17.4f} {speedup:>7.2f}x")

    return (ns, key_spaces, single_avg_times, single_stdevs,
            parallel_avg_times, parallel_stdevs, num_workers)


def plot_results(ns, key_spaces, single_avg_times, single_stdevs,
                  parallel_avg_times, parallel_stdevs, num_workers):
    fig, ax = plt.subplots(figsize=(9, 6))

    ax.errorbar(ns, single_avg_times, yerr=single_stdevs, marker="o",
                label="Single-threaded (avg)", color="#d62728", capsize=4)
    ax.errorbar(ns, parallel_avg_times, yerr=parallel_stdevs, marker="s",
                label=f"Parallel ({num_workers} workers, avg)", color="#2ca02c", capsize=4)

    ax.set_yscale("log")
    ax.set_xlabel("Key length (n)")
    ax.set_ylabel("Elapsed time (seconds, log scale)")
    ax.set_title(f"Brute-force attack on columnar transposition:\n"
                 f"single-threaded vs. parallel execution time (avg of {REPEATS} runs)")

    ax2 = ax.secondary_xaxis("top")
    ax2.set_xticks(ns)
    ax2.set_xticklabels([f"{ks:,}" for ks in key_spaces], rotation=45, fontsize=8)
    ax2.set_xlabel("Key space size (n!)")

    crossover_n = None
    for i in range(1, len(ns)):
        if single_avg_times[i - 1] <= parallel_avg_times[i - 1] and single_avg_times[i] > parallel_avg_times[i]:
            crossover_n = ns[i]
            break
    if crossover_n is not None:
        ax.axvline(crossover_n, color="gray", linestyle="--", alpha=0.7)
        ax.text(crossover_n + 0.1, min(single_avg_times), f"crossover ~ n={crossover_n}",
                rotation=90, va="bottom", fontsize=9, color="gray")

    ax.legend()
    ax.grid(True, which="both", alpha=0.3)
    fig.tight_layout()

    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "parallelization_benchmark.png")
    fig.savefig(out_path, dpi=150)
    print(f"\nPlot saved to: {out_path}")

    if crossover_n is not None:
        crossover_key_space = transposition.key_space_size(crossover_n)
        print(f"\nCrossover point: n={crossover_n} (key space = {crossover_key_space:,})")
        print(f"Suggested PARALLEL_THRESHOLD: {crossover_key_space}")
    else:
        print("\nNo crossover found in the tested range.")


if __name__ == "__main__":
    (ns, key_spaces, single_avg_times, single_stdevs,
     parallel_avg_times, parallel_stdevs, num_workers) = run_benchmark()
    plot_results(ns, key_spaces, single_avg_times, single_stdevs,
                 parallel_avg_times, parallel_stdevs, num_workers)
