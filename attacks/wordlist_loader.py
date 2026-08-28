from nltk.corpus import words as nltk_words
import nltk


def load_wordset() -> set:
    try:
        word_list = nltk_words.words()
    except LookupError:
        nltk.download("words", quiet=True)
        word_list = nltk_words.words()
    wordset = {w.lower() for w in word_list}
    print(f"[wordlist_loader] Loaded {len(wordset)} words from the NLTK corpus")
    return wordset


if __name__ == "__main__":
    ws = load_wordset()
    print(f"Total words: {len(ws)}")
    print("Sample:", list(ws)[:10])
