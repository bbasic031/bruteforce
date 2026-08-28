import os
import sys
import time
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ciphers import caesar, affine, columnar_transposition as transposition
from attacks import caesar_attack, affine_attack, transposition_attack

TRANSPOSITION_MIN_N = 3
TRANSPOSITION_MAX_N = 9
BASE_PLAINTEXT = (
    "sphinx of black quartz judge my vow "
    "the quick brown fox jumps over the lazy dog"
)


def measure_caesar():
    true_key = 11
    ciphertext = caesar.encrypt(BASE_PLAINTEXT, true_key)
    result = caesar_attack.attack(ciphertext)
    assert result["best_key"] == true_key
    return {
        "cipher": "Caesar",
        "key_space": caesar.key_space_size(),
        "elapsed": result["elapsed_seconds"],
    }


def measure_affine():
    true_key = (5, 8)
    ciphertext = affine.encrypt(BASE_PLAINTEXT, *true_key)
    result = affine_attack.attack(ciphertext)
    assert result["best_key"] == true_key
    return {
        "cipher": "Affine",
        "key_space": affine.key_space_size(),
        "elapsed": result["elapsed_seconds"],
    }


def measure_transposition(n: int):
    key = tuple((i * 7 + 3) % n for i in range(n))
    if sorted(key) != list(range(n)):
        key = tuple(reversed(range(n)))
    ciphertext = transposition.encrypt(BASE_PLAINTEXT, key)
    result = transposition_attack.attack(ciphertext, key_length=n, force_mode="single")
    assert result["best_key"] == key
    return {
        "cipher": f"Transposition (n={n})",
        "key_space": transposition.key_space_size(n),
        "elapsed": result["elapsed_seconds"],
    }


def run_all_measurements():
    results = []
    print("Measuring Caesar...")
    results.append(measure_caesar())
    print("Measuring Affine...")
    results.append(measure_affine())
    for n in range(TRANSPOSITION_MIN_N, TRANSPOSITION_MAX_N + 1):
        print(f"Measuring Transposition (n={n})...")
        results.append(measure_transposition(n))

    print()
    print(f"{'Cipher':<24} {'Key space':>12} {'Time (s)':>12} {'Time per key (us)':>20}")
    print("-" * 72)
    for r in results:
        per_key_us = (r["elapsed"] / r["key_space"]) * 1e6 if r["key_space"] else 0
        print(f"{r['cipher']:<24} {r['key_space']:>12,} {r['elapsed']:>12.5f} {per_key_us:>20.2f}")

    return results


def plot_results(results):
    fig, ax = plt.subplots(figsize=(9, 6.5))

    colors = {"Caesar": "#1f77b4", "Affine": "#ff7f0e", "Transposition": "#2ca02c"}

    caesar_pts = [(r["key_space"], r["elapsed"]) for r in results if r["cipher"] == "Caesar"]
    affine_pts = [(r["key_space"], r["elapsed"]) for r in results if r["cipher"] == "Affine"]
    transposition_pts = [(r["key_space"], r["elapsed"])
                          for r in results if r["cipher"].startswith("Transposition")]

    if caesar_pts:
        xs, ys = zip(*caesar_pts)
        ax.scatter(xs, ys, color=colors["Caesar"], s=90, marker="o",
                   label="Caesar", zorder=3)
    if affine_pts:
        xs, ys = zip(*affine_pts)
        ax.scatter(xs, ys, color=colors["Affine"], s=90, marker="D",
                   label="Affine", zorder=3)
    if transposition_pts:
        transposition_pts.sort()
        xs, ys = zip(*transposition_pts)
        ax.plot(xs, ys, color=colors["Transposition"], marker="s",
                label="Transposition (n=3..%d)" % TRANSPOSITION_MAX_N, zorder=3)

    if caesar_pts:
        x0, y0 = caesar_pts[0]
        rate = y0 / x0 if x0 else 0
        all_x = [r["key_space"] for r in results]
        x_ref = sorted(all_x)
        y_ref = [rate * x for x in x_ref]
        ax.plot(x_ref, y_ref, color="gray", linestyle="--", alpha=0.6,
                label="Perfect linear scaling (reference)", zorder=1)

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Key space size (number of keys, log scale)")
    ax.set_ylabel("Attack time (seconds, log scale)")
    ax.set_title("Brute-force attack time vs. key space size\n(Caesar, Affine, and Transposition on one scale)")
    ax.legend()
    ax.grid(True, which="both", alpha=0.3)
    fig.tight_layout()

    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "complexity_comparison.png")
    fig.savefig(out_path, dpi=150)
    print(f"\nPlot saved to: {out_path}")


if __name__ == "__main__":
    results = run_all_measurements()
    plot_results(results)
