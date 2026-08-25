import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ciphers import caesar
from attacks.scorer import score_with_spaces

def attack(ciphertext: str, verbose: bool = False) -> dict:
    start = time.perf_counter()
    best_key = None
    best_score = -1.0
    best_plaintext = None
    all_results = []

    for key in range(caesar.key_space_size()):
        candidate = caesar.decrypt(ciphertext, key)
        score = score_with_spaces(candidate)
        all_results.append((key, score))

        if verbose:
            print(f"  key={key:2d}  score={score:.2f}  text='{candidate[:40]}'")

        if score > best_score:
            best_score = score
            best_key = key
            best_plaintext = candidate

    elapsed = time.perf_counter() - start

    return {
        "cipher": "caesar",
        "best_key": best_key,
        "best_plaintext": best_plaintext,
        "best_score": best_score,
        "attempts": caesar.key_space_size(),
        "elapsed_seconds": elapsed,
        "all_results": all_results,
    }

if __name__ == "__main__":
    plaintext = "Sphinx of black quartz judge my vow"
    true_key = 11
    ciphertext = caesar.encrypt(plaintext, true_key)

    print(f"Plaintext:  {plaintext}")
    print(f"True key:   {true_key}")
    print(f"Ciphertext: {ciphertext}")
    print()

    result = attack(ciphertext, verbose=True)

    print()
    print(f"Key found:    {result['best_key']}  (score={result['best_score']:.2f})")
    print(f"Decrypted:    {result['best_plaintext']}")
    print(f"Attempts:     {result['attempts']}")
    print(f"Elapsed time: {result['elapsed_seconds']*1000:.4f} ms")
    print(f"Success:      {result['best_key'] == true_key}")
