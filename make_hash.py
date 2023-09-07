import sha3

# Create a SHA3-256 hash object
hasher = sha3.keccak_256()

# Convert the input integer to bytes and hash it
input_int = 801
input_bytes = input_int.to_bytes(32, byteorder='big')
hasher.update(input_bytes)
hash_hex = hasher.hexdigest()

# Print the hash value in hexadecimal format
print(f"0x{hash_hex}")
