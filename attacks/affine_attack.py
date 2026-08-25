import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ciphers import affine
from attacks.scorer import score_with_spaces

def attack(ciphertext: str, verbose: bool = False) -> dict:
    start = time.perf_counter()
    best_key = None
    best_score = -1.0
    best_plaintext = None
    attempts = 0
    all_results = []

    for a in affine.VALID_A:
        for b in range(26):
            attempts += 1
            candidate = affine.decrypt(ciphertext, a, b)
            score = score_with_spaces(candidate)
            all_results.append(((a, b), score))

            if verbose and score > 0:
                print(f"  a={a:2d} b={b:2d}  score={score:.2f}  text='{candidate[:40]}'")

            if score > best_score:
                best_score = score
                best_key = (a, b)
                best_plaintext = candidate

    elapsed = time.perf_counter() - start

    return {
        "cipher": "affine",
        "best_key": best_key,
        "best_plaintext": best_plaintext,
        "best_score": best_score,
        "attempts": attempts,
        "elapsed_seconds": elapsed,
        "all_results": all_results,
    }


if __name__ == "__main__":
    plaintext = "Sphinx of black quartz judge my vow"
    true_key = (5, 8)
    ciphertext = affine.encrypt(plaintext, *true_key)

    print(f"Plaintext:  {plaintext}")
    print(f"True key:   a={true_key[0]}, b={true_key[1]}")
    print(f"Ciphertext: {ciphertext}")
    print()

    result = attack(ciphertext, verbose=True)

    print()
    print(f"Key found:    {result['best_key']}  (score={result['best_score']:.2f})")
    print(f"Decrypted:    {result['best_plaintext']}")
    print(f"Attempts:     {result['attempts']}")
    print(f"Elapsed time: {result['elapsed_seconds']*1000:.4f} ms")
    print(f"Success:      {result['best_key'] == true_key}")
