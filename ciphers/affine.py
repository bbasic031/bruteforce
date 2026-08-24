import math

VALID_A = [a for a in range(1, 26) if math.gcd(a, 26) == 1]

def mod_inverse(a: int, m: int = 26) -> int:
    a = a % m
    for x in range(1, m):
        if (a * x) % m == 1:
            return x
    raise ValueError(f"{a} has no inverse modulo {m}")

def encrypt(plaintext: str, a: int, b: int) -> str:
    if math.gcd(a, 26) != 1:
        raise ValueError(f"a={a} must be coprime with 26")
    result = []
    for current_character in plaintext:
        if current_character.isalpha():
            base = ord('A') if current_character.isupper() else ord('a')
            x = ord(current_character) - base
            y = (a * x + b) % 26
            result.append(chr(base + y))
        else:
            result.append(current_character)
    return "".join(result)

def decrypt(ciphertext: str, a: int, b: int) -> str:
    a_inv = mod_inverse(a)
    result = []
    for current_character in ciphertext:
        if current_character.isalpha():
            base = ord('A') if current_character.isupper() else ord('a')
            y = ord(current_character) - base
            x = (a_inv * (y - b)) % 26
            result.append(chr(base + x))
        else:
            result.append(current_character)
    return "".join(result)

def key_space_size() -> int:
    return len(VALID_A) * 26

if __name__ == "__main__":
    plaintext = "Sphinx of black quartz judge my vow"
    a, b = 5, 8
    ciphertext = encrypt(plaintext, a, b)
    print(f"Plaintext:  {plaintext}")
    print(f"Key:        a={a}, b={b}")
    print(f"Ciphertext: {ciphertext}")
    print(f"Decrypted:  {decrypt(ciphertext, a, b)}")
    print(f"Key space:  {key_space_size()}")