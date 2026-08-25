try:
    from attacks.wordlist_loader import load_wordset
except ImportError:
    from wordlist_loader import load_wordset

WORDSET = load_wordset()

def score_with_spaces(text: str) -> float:
    words = [w.strip(".,!?;:\"'()").lower() for w in text.split()]
    words = [w for w in words if w]
    if not words:
        return 0.0
    recognized = sum(1 for w in words if w in WORDSET)
    return recognized / len(words)

def score_no_spaces(text: str, max_word_len: int = 12) -> float:
    text = text.lower()
    n = len(text)
    i = 0
    recognized_chars = 0
    while i < n:
        matched = False
        for length in range(min(max_word_len, n - i), 1, -1):
            candidate = text[i:i + length]
            if candidate in WORDSET:
                recognized_chars += length
                i += length
                matched = True
                break
        if not matched:
            i += 1
    return recognized_chars / n if n > 0 else 0.0

if __name__ == "__main__":
    good = "attack at dawn"
    bad = "izzisg iz xiov"
    print(f"'{good}' -> score {score_with_spaces(good):.2f}")
    print(f"'{bad}' -> score {score_with_spaces(bad):.2f}")

    no_space_good = "attackatdawn"
    no_space_bad = "tawemixacdmadhat"
    print(f"'{no_space_good}' -> score {score_no_spaces(no_space_good):.2f}")
    print(f"'{no_space_bad}' -> score {score_no_spaces(no_space_bad):.2f}")
