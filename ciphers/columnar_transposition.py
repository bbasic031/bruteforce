import math

def _prepare_text(text: str) -> str:
    return "".join(current_character.lower() for current_character in text if current_character.isalpha())

def encrypt(plaintext: str, key: tuple) -> str:
    text = _prepare_text(plaintext)
    n = len(key)

    pad_len = (-len(text)) % n
    text += "x" * pad_len

    rows = [text[i:i + n] for i in range(0, len(text), n)]

    ciphertext = []
    for column in key:
        for row in rows:
            ciphertext.append(row[column])
    return "".join(ciphertext)

def decrypt(ciphertext: str, key: tuple) -> str:
    n = len(key)
    num_rows = len(ciphertext) // n

    columns = {}
    idx = 0
    for column in key:
        columns[column] = ciphertext[idx: idx + num_rows]
        idx += num_rows

    plaintext = []
    for r in range(num_rows):
        for c in range(n):
            plaintext.append(columns[c][r])
    return "".join(plaintext)

def key_space_size(key_length: int) -> int:
    return math.factorial(key_length)

if __name__ == "__main__":
    plaintext = "Sphinx of black quartz judge my vow"
    key = (3, 0, 4, 1, 2)
    ciphertext = encrypt(plaintext, key)
    print(f"Plaintext:  {plaintext}")
    print(f"Key:        {key}")
    print(f"Ciphertext: {ciphertext}")
    print(f"Decrypted:  {decrypt(ciphertext, key)}")
    print(f"Key space (n=4): {key_space_size(4)}")
    print(f"Key space (n=8): {key_space_size(8)}")
