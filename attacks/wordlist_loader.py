import os

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_DATA_DIR = os.path.join(os.path.dirname(_THIS_DIR), "data")
_LOCAL_WORDLIST = os.path.join(_DATA_DIR, "wordlist.txt")
_SYSTEM_WORDLIST = "/usr/share/dict/words"

_FALLBACK_WORDS = """
the be to of and a in that have i it for not on with he as you do at
this but his by from they we say her she or an will my one all would
there their what so up out if about who get which go me when make can
like time no just him know take people into year your good some could
them see other than then now look only come its over think also back
after use two how our work first well way even new want because any
these give day most us attack dawn meet midnight north south east west
army general troops enemy retreat advance camp fort river bridge road
message secret plan king queen soldier war peace gold silver treasure
map location coordinates deliver package tonight tomorrow yesterday
morning evening night hour minute second location target base command
control unit force strike defend hold position weapon supply line
""".split()

_FALLBACK_SET = set(w.lower() for w in _FALLBACK_WORDS)

def load_wordset() -> set:
    if os.path.isfile(_LOCAL_WORDLIST):
        with open(_LOCAL_WORDLIST, "r", encoding="utf-8", errors="ignore") as f:
            words = {line.strip().lower() for line in f if line.strip()}
        if len(words) > 1000:
            print(f"[wordlist_loader] Loaded {len(words)} words from {_LOCAL_WORDLIST}")
            return words

    if os.path.isfile(_SYSTEM_WORDLIST):
        with open(_SYSTEM_WORDLIST, "r", encoding="utf-8", errors="ignore") as f:
            words = {line.strip().lower() for line in f if line.strip().isalpha()}
        if len(words) > 1000:
            print(f"[wordlist_loader] Loaded {len(words)} words from {_SYSTEM_WORDLIST}")
            return words

    try:
        import nltk
        from nltk.corpus import words as nltk_words
        try:
            word_list = nltk_words.words()
        except LookupError:
            nltk.download("words", quiet=True)
            word_list = nltk_words.words()
        wordset = {w.lower() for w in word_list}
        print(f"[wordlist_loader] Loaded {len(wordset)} words from the NLTK corpus")
        return wordset
    except Exception:
        pass

    print(f"[wordlist_loader] Using built-in fallback list of {len(_FALLBACK_SET)} words")
    return _FALLBACK_SET

if __name__ == "__main__":
    ws = load_wordset()
    print(f"Total words: {len(ws)}")
    print("Sample:", list(ws)[:10])
