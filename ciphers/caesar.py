ALPHABET = "abcdefghijklmnopqrstuvwxyz"

def encrypt(plaintext: str, shift: int) -> str:
    result = []
    for current_character in plaintext:
        if current_character.isalpha():
            base = ord('A') if current_character.isupper() else ord('a')
            shifted = (ord(current_character) - base + shift) % 26
            result.append(chr(base + shifted))
        else:
            result.append(current_character)
    return "".join(result)

def decrypt(ciphertext: str, shift: int) -> str:
    return encrypt(ciphertext, -shift)

def key_space_size() -> int:
    return 26

if __name__ == "__main__":
    plaintext = "Sphinx of black quartz judge my vow"
    key = 7
    ciphertext = encrypt(plaintext, key)
    print(f"Plaintext:  {plaintext}")
    print(f"Key:        {key}")
    print(f"Ciphertext: {ciphertext}")
    print(f"Decrypted:  {decrypt(ciphertext, key)}")