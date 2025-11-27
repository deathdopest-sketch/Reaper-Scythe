#!/usr/bin/env python3
"""
Crypt Library Demo - Reaper Security Language
Demonstrates encryption, hashing, and steganography capabilities
"""

import os
import tempfile
from libs.crypt.encryption import CryptEngine, generate_key, encrypt_data, decrypt_data
from libs.crypt.hashing import CryptHasher, hash_data, hash_file, hash_password, verify_password
from libs.crypt.steganography import CryptSteganographer, hide_in_image, extract_from_image

def demo_encryption():
    """Demonstrate encryption capabilities"""
    print("=== ENCRYPTION DEMO ===")
    
    # Initialize engine
    engine = CryptEngine()
    
    # Test data
    test_data = b"This is sensitive data that needs encryption!"
    password = "secure_password_123"
    
    print(f"Original data: {test_data}")
    print(f"Password: {password}")
    
    # Generate keys
    print("\n--- Key Generation ---")
    symmetric_key = engine.generate_symmetric_key()
    print(f"Symmetric key: {symmetric_key[:16]}...")
    
    rsa_keypair = engine.generate_rsa_keypair(2048)
    print(f"RSA keypair generated: {len(rsa_keypair.public_key)} bytes public, {len(rsa_keypair.private_key)} bytes private")
    
    ecc_keypair = engine.generate_ecc_keypair("P-256")
    print(f"ECC keypair generated: {len(ecc_keypair.public_key)} bytes public, {len(ecc_keypair.private_key)} bytes private")
    
    # Password-based encryption
    print("\n--- Password-based Encryption ---")
    result = engine.encrypt_with_password(test_data, password)
    print(f"Encrypted with password: {len(result.ciphertext)} bytes")
    print(f"IV: {result.iv[:8]}...")
    print(f"Salt: {result.salt[:8]}...")
    print(f"Tag: {result.tag[:8]}...")
    
    decrypted = engine.decrypt_with_password(result.ciphertext, password, result.salt, result.iv, result.tag)
    print(f"Decryption successful: {decrypted == test_data}")
    
    # AES-GCM encryption
    print("\n--- AES-GCM Encryption ---")
    result = engine.encrypt_aes_gcm(test_data, symmetric_key)
    print(f"Encrypted with AES-GCM: {len(result.ciphertext)} bytes")
    
    decrypted = engine.decrypt_aes_gcm(result.ciphertext, symmetric_key, result.iv, result.tag)
    print(f"Decryption successful: {decrypted == test_data}")
    
    # RSA encryption
    print("\n--- RSA Encryption ---")
    result = engine.encrypt_rsa(test_data, rsa_keypair.public_key)
    print(f"Encrypted with RSA: {len(result.ciphertext)} bytes")
    
    decrypted = engine.decrypt_rsa(result.ciphertext, rsa_keypair.private_key)
    print(f"Decryption successful: {decrypted == test_data}")
    
    # File encryption
    print("\n--- File Encryption ---")
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(test_data)
        temp_file_path = temp_file.name
    
    encrypted_path = temp_file_path + ".enc"
    decrypted_path = temp_file_path + ".dec"
    
    success = engine.encrypt_file(temp_file_path, encrypted_path, password=password)
    print(f"File encryption: {success}")
    
    success = engine.decrypt_file(encrypted_path, decrypted_path, password=password)
    print(f"File decryption: {success}")
    
    if success:
        with open(decrypted_path, 'rb') as f:
            decrypted_file_data = f.read()
        print(f"File decryption successful: {decrypted_file_data == test_data}")
    
    # Cleanup
    os.unlink(temp_file_path)
    if os.path.exists(encrypted_path):
        os.unlink(encrypted_path)
    if os.path.exists(decrypted_path):
        os.unlink(decrypted_path)

def demo_hashing():
    """Demonstrate hashing capabilities"""
    print("\n=== HASHING DEMO ===")
    
    # Initialize hasher
    hasher = CryptHasher()
    
    # Test data
    test_data = b"This is data to be hashed!"
    password = "user_password_123"
    
    print(f"Test data: {test_data}")
    print(f"Password: {password}")
    
    # Hash data
    print("\n--- Data Hashing ---")
    sha256_hash = hasher.hash_data(test_data, "sha256")
    print(f"SHA256: {sha256_hash.hex()}")
    
    sha512_hash = hasher.hash_data(test_data, "sha512")
    print(f"SHA512: {sha512_hash.hex()}")
    
    md5_hash = hasher.hash_data(test_data, "md5")
    print(f"MD5: {md5_hash.hex()}")
    
    # HMAC
    print("\n--- HMAC ---")
    hmac_result = hasher.generate_hmac(test_data, "secret_key", "sha256")
    print(f"HMAC-SHA256: {hmac_result.hex()}")
    
    verification = hasher.verify_hmac(test_data, "secret_key", hmac_result, "sha256")
    print(f"HMAC verification: {verification}")
    
    # Password hashing
    print("\n--- Password Hashing ---")
    bcrypt_hash = hasher.hash_password(password, "bcrypt")
    print(f"bcrypt hash: {bcrypt_hash}")
    
    verification = hasher.verify_password(password, bcrypt_hash, "bcrypt")
    print(f"bcrypt verification: {verification}")
    
    pbkdf2_hash = hasher.hash_password(password, "pbkdf2")
    print(f"PBKDF2 hash: {pbkdf2_hash}")
    
    verification = hasher.verify_password(password, pbkdf2_hash, "pbkdf2")
    print(f"PBKDF2 verification: {verification}")
    
    # Key derivation
    print("\n--- Key Derivation ---")
    salt = hasher.generate_salt(32)
    derived_key = hasher.derive_key_hkdf(password.encode(), salt, 32, "sha256")
    print(f"HKDF derived key: {derived_key.hex()}")

def demo_steganography():
    """Demonstrate steganography capabilities"""
    print("\n=== STEGANOGRAPHY DEMO ===")
    
    # Initialize steganographer
    stego = CryptSteganographer()
    
    # Test data
    secret_data = b"This is hidden data!"
    test_text = "This is a much longer text message for steganography testing that provides enough space between words to hide the required data bits for the steganography algorithm to work properly. " * 10
    
    print(f"Secret data: {secret_data}")
    print(f"Text length: {len(test_text)} characters")
    
    # Text steganography
    print("\n--- Text Steganography ---")
    stego_text = stego.hide_in_text_whitespace(test_text, secret_data)
    print(f"Stego text length: {len(stego_text)} characters")
    print(f"Text changed: {stego_text != test_text}")
    
    result = stego.extract_from_text_whitespace(stego_text)
    print(f"Extraction successful: {result.success}")
    if result.success:
        print(f"Extracted data: {result.data}")
        print(f"Data match: {result.data == secret_data}")
    
    # Analyze steganography
    print("\n--- Steganography Analysis ---")
    analysis = stego.analyze_file(stego_text.encode())
    print(f"Analysis result: {analysis}")
    
    # Test edge cases
    print("\n--- Edge Cases ---")
    empty_data = b""
    stego_text_empty = stego.hide_in_text_whitespace(test_text, empty_data)
    result_empty = stego.extract_from_text_whitespace(stego_text_empty)
    print(f"Empty data handling: {result_empty.success and result_empty.data == empty_data}")

def demo_convenience_functions():
    """Demonstrate convenience functions"""
    print("\n=== CONVENIENCE FUNCTIONS DEMO ===")
    
    test_data = b"Data for convenience functions!"
    password = "convenience_password"
    
    # Encryption convenience functions
    print("--- Encryption Functions ---")
    result = encrypt_data(test_data, password=password)
    print(f"Encrypted: {len(result.ciphertext)} bytes")
    
    decrypted = decrypt_data(result.ciphertext, password=password, salt=result.salt, iv=result.iv, tag=result.tag)
    print(f"Decrypted successfully: {decrypted == test_data}")
    
    # Hashing convenience functions
    print("\n--- Hashing Functions ---")
    hash_result = hash_data(test_data, "sha256")
    print(f"SHA256 hash: {hash_result.hex()}")
    
    password_hash = hash_password(password, "bcrypt")
    verification = verify_password(password, password_hash, "bcrypt")
    print(f"Password verification: {verification}")
    
    # Steganography convenience functions
    print("\n--- Steganography Functions ---")
    test_text = "This is a test message for steganography. " * 20
    secret = b"Hidden message!"
    
    stego_text = hide_in_text(test_text, secret)
    extracted = extract_from_text(stego_text)
    print(f"Steganography success: {extracted == secret}")

if __name__ == "__main__":
    print("Crypt Library Demo - Reaper Security Language")
    print("=" * 50)
    
    try:
        demo_encryption()
        demo_hashing()
        demo_steganography()
        demo_convenience_functions()
        
        print("\n" + "=" * 50)
        print("Demo completed successfully!")
        
    except Exception as e:
        print(f"\nDemo failed with error: {e}")
        import traceback
        traceback.print_exc()
