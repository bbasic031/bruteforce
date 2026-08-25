import os
import sys
import time
import multiprocessing as mp
from itertools import permutations

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ciphers import columnar_transposition as transposition
from attacks.scorer import score_no_spaces

PARALLEL_THRESHOLD = 40320

def _evaluate_key(args: tuple) -> tuple:
    ciphertext, perm = args
    candidate = transposition.decrypt(ciphertext, perm)
    score = score_no_spaces(candidate)
    return (perm, score, candidate)

def _attack_single_threaded(ciphertext: str, key_length: int, top_n_report: int) -> dict:
    start = time.perf_counter()

    best_key = None
    best_score = -1.0
    best_plaintext = None
    attempts = 0
    top_results = []

    for perm in permutations(range(key_length)):
        attempts += 1
        candidate = transposition.decrypt(ciphertext, perm)
        score = score_no_spaces(candidate)
        top_results.append((perm, score))

        if score > best_score:
            best_score = score
            best_key = perm
            best_plaintext = candidate

    elapsed = time.perf_counter() - start
    top_results.sort(key=lambda x: -x[1])

    return {
        "cipher": "columnar_transposition",
        "mode": "single-threaded",
        "best_key": best_key,
        "best_plaintext": best_plaintext,
        "best_score": best_score,
        "attempts": attempts,
        "elapsed_seconds": elapsed,
        "workers_used": 1,
        "top_results": top_results[:top_n_report],
    }

def _attack_parallel(ciphertext: str, key_length: int, num_workers: int,
                      top_n_report: int) -> dict:
    start = time.perf_counter()

    tasks = [(ciphertext, perm) for perm in permutations(range(key_length))]

    with mp.Pool(processes=num_workers) as pool:
        chunksize = max(1, len(tasks) // (num_workers * 4))
        results = pool.map(_evaluate_key, tasks, chunksize=chunksize)

    elapsed = time.perf_counter() - start

    best_key, best_score, best_plaintext = max(results, key=lambda r: r[1])
    top_results = sorted(
        [(perm, score) for perm, score, _ in results],
        key=lambda x: -x[1]
    )[:top_n_report]

    return {
        "cipher": "columnar_transposition",
        "mode": "parallel",
        "best_key": best_key,
        "best_plaintext": best_plaintext,
        "best_score": best_score,
        "attempts": len(tasks),
        "elapsed_seconds": elapsed,
        "workers_used": num_workers,
        "top_results": top_results,
    }

def attack(ciphertext: str, key_length: int, num_workers: int = None,
           top_n_report: int = 5, force_mode: str = None) -> dict:
    key_space = transposition.key_space_size(key_length)

    if force_mode == "single":
        use_parallel = False
    elif force_mode == "parallel":
        use_parallel = True
    else:
        use_parallel = key_space >= PARALLEL_THRESHOLD

    if use_parallel:
        if num_workers is None:
            num_workers = mp.cpu_count()
        return _attack_parallel(ciphertext, key_length, num_workers, top_n_report)
    else:
        return _attack_single_threaded(ciphertext, key_length, top_n_report)

if __name__ == "__main__":
    plaintext = "Sphinx of black quartz judge my vow"
    true_key = (3, 0, 4, 1, 2)
    ciphertext = transposition.encrypt(plaintext, true_key)

    key_space = transposition.key_space_size(len(true_key))

    print(f"Plaintext:  {plaintext}")
    print(f"True key:   {true_key}")
    print(f"Ciphertext: {ciphertext}")
    print()
    print(f"Key space size: {key_space} (threshold: {PARALLEL_THRESHOLD})")
    print(f"CPU cores available: {mp.cpu_count()}")

    result = attack(ciphertext, key_length=len(true_key))

    print(f"Mode chosen: {result['mode']}")
    print()
    print(f"Key found:      {result['best_key']}  (score={result['best_score']:.2f})")
    print(f"Decrypted:      {result['best_plaintext']}")
    print(f"Attempts:       {result['attempts']}")
    print(f"Workers used:   {result['workers_used']}")
    print(f"Elapsed time:   {result['elapsed_seconds']*1000:.2f} ms")
    print(f"Success:        {result['best_key'] == true_key}")
    print()
    print("Top 5 results:")
    for key, score in result["top_results"]:
        print(f"  {key}  score={score:.2f}")