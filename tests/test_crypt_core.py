"""
Tests for Crypt Cryptography Library

This module contains comprehensive tests for the Crypt library
including encryption, hashing, and steganography operations.

Author: Reaper Security Team
Version: 0.1.0
"""

import unittest
import tempfile
import os
from unittest.mock import patch, MagicMock

# Import crypt modules
from libs.crypt.encryption import (
    CryptEngine, CryptConfig, CipherType, KeyType, EncryptionResult,
    generate_key, encrypt_data, decrypt_data
)

from libs.crypt.hashing import (
    CryptHasher, HashConfig, HashAlgorithm, PasswordHashType, HashResult,
    hash_data, hash_file, hash_password, verify_password
)

from libs.crypt.steganography import (
    CryptSteganographer, SteganographyConfig, SteganographyType,
    SteganographyMethod, SteganographyResult,
    hide_in_image, extract_from_image, hide_in_audio, extract_from_audio,
    hide_in_text, extract_from_text, analyze_file
)

class TestCryptEngine(unittest.TestCase):
    """Test cases for CryptEngine class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.engine = CryptEngine()
        self.test_data = b"Hello, Reaper Security World!"
        self.test_password = "test_password_123"
    
    def test_engine_initialization(self):
        """Test engine initialization"""
        engine = CryptEngine()
        self.assertIsInstance(engine.config, CryptConfig)
        self.assertEqual(engine.config.cipher_type, CipherType.AES_256_GCM)
    
    def test_engine_with_custom_config(self):
        """Test engine with custom configuration"""
        config = CryptConfig(
            cipher_type=CipherType.AES_256_CBC,
            key_size=16,
            iterations=50000
        )
        engine = CryptEngine(config)
        self.assertEqual(engine.config.cipher_type, CipherType.AES_256_CBC)
        self.assertEqual(engine.config.key_size, 16)
        self.assertEqual(engine.config.iterations, 50000)
    
    def test_generate_symmetric_key(self):
        """Test symmetric key generation"""
        key = self.engine.generate_symmetric_key()
        self.assertIsInstance(key, bytes)
        self.assertEqual(len(key), 32)  # Default key size
        
        # Test custom key size
        key_16 = self.engine.generate_symmetric_key(16)
        self.assertEqual(len(key_16), 16)
    
    def test_generate_rsa_keypair(self):
        """Test RSA key pair generation"""
        private_key, public_key = self.engine.generate_rsa_keypair()
        
        self.assertIsInstance(private_key, bytes)
        self.assertIsInstance(public_key, bytes)
        self.assertIn(b"BEGIN PRIVATE KEY", private_key)
        self.assertIn(b"BEGIN PUBLIC KEY", public_key)
        
        # Test different key sizes
        private_4096, public_4096 = self.engine.generate_rsa_keypair(4096)
        self.assertIsInstance(private_4096, bytes)
        self.assertIsInstance(public_4096, bytes)
    
    def test_generate_ecc_keypair(self):
        """Test ECC key pair generation"""
        private_key, public_key = self.engine.generate_ecc_keypair()
        
        self.assertIsInstance(private_key, bytes)
        self.assertIsInstance(public_key, bytes)
        self.assertIn(b"BEGIN PRIVATE KEY", private_key)
        self.assertIn(b"BEGIN PUBLIC KEY", public_key)
        
        # Test different curves
        private_p384, public_p384 = self.engine.generate_ecc_keypair("P-384")
        self.assertIsInstance(private_p384, bytes)
        self.assertIsInstance(public_p384, bytes)
    
    def test_derive_key_from_password(self):
        """Test password-based key derivation"""
        key, salt = self.engine.derive_key_from_password(self.test_password)
        
        self.assertIsInstance(key, bytes)
        self.assertIsInstance(salt, bytes)
        self.assertEqual(len(key), 32)  # Default key size
        self.assertEqual(len(salt), 32)  # Default salt size
        
        # Test with custom salt
        custom_salt = b"custom_salt_123456789012345678901234"
        key2, salt2 = self.engine.derive_key_from_password(self.test_password, custom_salt)
        self.assertEqual(salt2, custom_salt)
        self.assertNotEqual(key, key2)  # Different salts should produce different keys
    
    def test_encrypt_decrypt_aes_cbc(self):
        """Test AES-CBC encryption and decryption"""
        key = self.engine.generate_symmetric_key()
        
        # Encrypt
        result = self.engine.encrypt_aes_cbc(self.test_data, key)
        self.assertIsInstance(result, EncryptionResult)
        self.assertIsInstance(result.ciphertext, bytes)
        self.assertIsInstance(result.iv, bytes)
        self.assertNotEqual(result.ciphertext, self.test_data)
        
        # Decrypt
        decrypted = self.engine.decrypt_aes_cbc(result.ciphertext, key, result.iv)
        self.assertEqual(decrypted, self.test_data)
    
    def test_encrypt_decrypt_aes_gcm(self):
        """Test AES-GCM encryption and decryption"""
        key = self.engine.generate_symmetric_key()
        
        # Encrypt
        result = self.engine.encrypt_aes_gcm(self.test_data, key)
        self.assertIsInstance(result, EncryptionResult)
        self.assertIsInstance(result.ciphertext, bytes)
        self.assertIsInstance(result.iv, bytes)
        self.assertIsInstance(result.tag, bytes)
        
        # Decrypt
        decrypted = self.engine.decrypt_aes_gcm(result.ciphertext, key, result.iv, result.tag)
        self.assertEqual(decrypted, self.test_data)
    
    def test_encrypt_decrypt_chacha20_poly1305(self):
        """Test ChaCha20-Poly1305 encryption and decryption"""
        key = self.engine.generate_symmetric_key(32)  # ChaCha20 needs 32-byte key
        
        # Encrypt
        result = self.engine.encrypt_chacha20_poly1305(self.test_data, key)
        self.assertIsInstance(result, EncryptionResult)
        self.assertIsInstance(result.ciphertext, bytes)
        self.assertIsInstance(result.iv, bytes)  # Used for nonce
        # ChaCha20 doesn't have authentication tag
        
        # Decrypt
        decrypted = self.engine.decrypt_chacha20_poly1305(
            result.ciphertext, key, result.iv, result.tag
        )
        self.assertEqual(decrypted, self.test_data)
    
    def test_encrypt_decrypt_rsa(self):
        """Test RSA encryption and decryption"""
        private_key, public_key = self.engine.generate_rsa_keypair()
        
        # Encrypt with public key
        ciphertext = self.engine.encrypt_rsa(self.test_data, public_key)
        self.assertIsInstance(ciphertext, bytes)
        self.assertNotEqual(ciphertext, self.test_data)
        
        # Decrypt with private key
        decrypted = self.engine.decrypt_rsa(ciphertext, private_key)
        self.assertEqual(decrypted, self.test_data)
    
    def test_encrypt_decrypt_with_password(self):
        """Test password-based encryption and decryption"""
        # Encrypt with password
        result = self.engine.encrypt_with_password(self.test_data, self.test_password)
        self.assertIsInstance(result, EncryptionResult)
        self.assertIsInstance(result.salt, bytes)
        
        # Decrypt with password
        decrypted = self.engine.decrypt_with_password(
            result.ciphertext, self.test_password, result.salt, 
            iv=result.iv, tag=result.tag
        )
        self.assertEqual(decrypted, self.test_data)
    
    def test_file_encryption_decryption(self):
        """Test file encryption and decryption"""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(self.test_data)
            temp_file_path = temp_file.name
        
        try:
            encrypted_path = temp_file_path + ".enc"
            decrypted_path = temp_file_path + ".dec"
            
            # Encrypt file
            success = self.engine.encrypt_file(temp_file_path, encrypted_path, password=self.test_password)
            self.assertTrue(success)
            self.assertTrue(os.path.exists(encrypted_path))
            
            # Decrypt file
            success = self.engine.decrypt_file(encrypted_path, decrypted_path, password=self.test_password)
            self.assertTrue(success)
            self.assertTrue(os.path.exists(decrypted_path))
            
            # Verify decrypted content
            with open(decrypted_path, 'rb') as f:
                decrypted_content = f.read()
            self.assertEqual(decrypted_content, self.test_data)
            
        finally:
            # Cleanup
            for path in [temp_file_path, encrypted_path, decrypted_path]:
                if os.path.exists(path):
                    os.unlink(path)

class TestCryptHasher(unittest.TestCase):
    """Test cases for CryptHasher class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.hasher = CryptHasher()
        self.test_data = b"Hello, Reaper Security World!"
        self.test_password = "test_password_123"
    
    def test_hasher_initialization(self):
        """Test hasher initialization"""
        hasher = CryptHasher()
        self.assertIsInstance(hasher.config, HashConfig)
        self.assertEqual(hasher.config.default_algorithm, HashAlgorithm.SHA256)
    
    def test_generate_salt(self):
        """Test salt generation"""
        salt = self.hasher.generate_salt()
        self.assertIsInstance(salt, bytes)
        self.assertEqual(len(salt), 32)  # Default salt size
        
        # Test custom salt size
        salt_16 = self.hasher.generate_salt(16)
        self.assertEqual(len(salt_16), 16)
    
    def test_hash_data(self):
        """Test data hashing with different algorithms"""
        algorithms = [
            HashAlgorithm.MD5, HashAlgorithm.SHA1, HashAlgorithm.SHA256,
            HashAlgorithm.SHA512, HashAlgorithm.SHA3_256, HashAlgorithm.BLAKE2B
        ]
        
        for algorithm in algorithms:
            result = self.hasher.hash_data(self.test_data, algorithm)
            self.assertIsInstance(result, HashResult)
            self.assertIsInstance(result.hash_value, bytes)
            self.assertEqual(result.algorithm, algorithm.value)
            
            # Verify hash is deterministic
            result2 = self.hasher.hash_data(self.test_data, algorithm)
            self.assertEqual(result.hash_value, result2.hash_value)
    
    def test_hash_file(self):
        """Test file hashing"""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(self.test_data)
            temp_file_path = temp_file.name
        
        try:
            result = self.hasher.hash_file(temp_file_path)
            self.assertIsInstance(result, HashResult)
            self.assertIsInstance(result.hash_value, bytes)
            self.assertIn("file_path", result.metadata)
            
        finally:
            os.unlink(temp_file_path)
    
    def test_password_hashing_bcrypt(self):
        """Test bcrypt password hashing"""
        result = self.hasher.hash_password_bcrypt(self.test_password)
        
        self.assertIsInstance(result, HashResult)
        self.assertIsInstance(result.hash_value, bytes)
        self.assertEqual(result.algorithm, "bcrypt")
        
        # Verify password
        is_valid = self.hasher.verify_password_bcrypt(self.test_password, result.hash_value)
        self.assertTrue(is_valid)
        
        # Test wrong password
        is_invalid = self.hasher.verify_password_bcrypt("wrong_password", result.hash_value)
        self.assertFalse(is_invalid)
    
    def test_password_hashing_scrypt(self):
        """Test scrypt password hashing"""
        result = self.hasher.hash_password_scrypt(self.test_password)
        
        self.assertIsInstance(result, HashResult)
        self.assertIsInstance(result.hash_value, bytes)
        self.assertIsInstance(result.salt, bytes)
        self.assertEqual(result.algorithm, "scrypt")
        
        # Verify password
        is_valid = self.hasher.verify_password_scrypt(
            self.test_password, result.hash_value, result.salt,
            result.metadata["n"], result.metadata["r"], result.metadata["p"]
        )
        self.assertTrue(is_valid)
    
    def test_password_hashing_pbkdf2(self):
        """Test PBKDF2 password hashing"""
        result = self.hasher.hash_password_pbkdf2(self.test_password, algorithm="SHA256")
        
        self.assertIsInstance(result, HashResult)
        self.assertIsInstance(result.hash_value, bytes)
        self.assertIsInstance(result.salt, bytes)
        self.assertEqual(result.algorithm, "pbkdf2_sha256")
        
        # Verify password
        is_valid = self.hasher.verify_password_pbkdf2(
            self.test_password, result.hash_value, result.salt,
            "SHA256", result.metadata["iterations"]
        )
        self.assertTrue(is_valid)
    
    def test_hmac_generation_verification(self):
        """Test HMAC generation and verification"""
        key = b"test_hmac_key_123456789012345678901234"
        
        # Generate HMAC
        hmac_value = self.hasher.generate_hmac(self.test_data, key)
        self.assertIsInstance(hmac_value, bytes)
        
        # Verify HMAC
        is_valid = self.hasher.verify_hmac(self.test_data, key, hmac_value)
        self.assertTrue(is_valid)
        
        # Test with wrong key
        wrong_key = b"wrong_key_123456789012345678901234"
        is_invalid = self.hasher.verify_hmac(self.test_data, wrong_key, hmac_value)
        self.assertFalse(is_invalid)
    
    def test_key_derivation_hkdf(self):
        """Test HKDF key derivation"""
        master_key = b"master_key_123456789012345678901234"
        
        derived_key = self.hasher.derive_key_hkdf(master_key, length=32)
        self.assertIsInstance(derived_key, bytes)
        self.assertEqual(len(derived_key), 32)
        
        # Test with custom salt and info
        salt = b"custom_salt_123456789012345678901234"
        info = b"additional_info"
        derived_key2 = self.hasher.derive_key_hkdf(master_key, salt=salt, info=info, length=64)
        self.assertEqual(len(derived_key2), 64)
        self.assertNotEqual(derived_key, derived_key2)

class TestCryptSteganographer(unittest.TestCase):
    """Test cases for CryptSteganographer class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.stego = CryptSteganographer()
        self.test_data = b"Hidden message in steganography!"
        self.test_text = "This is a much longer text message for steganography testing that provides enough space between words to hide the required data bits for the steganography algorithm to work properly. " * 20
    
    def test_stego_initialization(self):
        """Test steganographer initialization"""
        stego = CryptSteganographer()
        self.assertIsInstance(stego.config, SteganographyConfig)
        self.assertEqual(stego.config.method, SteganographyMethod.HIDE)
    
    def test_text_whitespace_steganography(self):
        """Test text whitespace steganography"""
        # Hide data in text
        stego_text = self.stego.hide_in_text_whitespace(self.test_text, self.test_data)
        self.assertIsInstance(stego_text, str)
        self.assertNotEqual(stego_text, self.test_text)
        
        # Extract data from text
        result = self.stego.extract_from_text_whitespace(stego_text)
        self.assertIsInstance(result, SteganographyResult)
        self.assertTrue(result.success)
        self.assertEqual(result.data, self.test_data)
    
    def test_text_steganography_edge_cases(self):
        """Test text steganography edge cases"""
        # Test with empty data
        empty_data = b""
        stego_text = self.stego.hide_in_text_whitespace(self.test_text, empty_data)
        result = self.stego.extract_from_text_whitespace(stego_text)
        self.assertTrue(result.success)
        self.assertEqual(result.data, empty_data)
        
        # Test with data too large for text
        large_data = b"x" * 10000  # Very large data
        with self.assertRaises(ValueError):
            self.stego.hide_in_text_whitespace(self.test_text, large_data)
    
    def test_analyze_text_steganography(self):
        """Test text steganography analysis"""
        # Analyze normal text
        result = self.stego._analyze_text("test_file.txt")
        # This will fail because file doesn't exist, but we can test the method structure
        self.assertIsInstance(result, SteganographyResult)
    
    @patch('PIL.Image')
    def test_image_lsb_steganography(self, mock_image):
        """Test image LSB steganography with mocked PIL"""
        # Mock PIL Image
        mock_img = MagicMock()
        mock_img.mode = 'RGB'
        mock_img.size = (100, 100)
        mock_img.getdata.return_value = [(255, 255, 255)] * 10000  # White pixels
        mock_image.open.return_value = mock_img
        
        # Mock image operations
        with patch('PIL.Image.new') as mock_new:
            mock_new_img = MagicMock()
            mock_new.return_value = mock_new_img
            
            # Test hiding data
            result = self.stego.hide_in_image_lsb("test.png", self.test_data, "output.png")
            self.assertIsInstance(result, SteganographyResult)
    
    @patch('wave.open')
    def test_audio_lsb_steganography(self, mock_wave):
        """Test audio LSB steganography with mocked wave"""
        # Mock wave file
        mock_wave_file = MagicMock()
        mock_wave_file.readframes.return_value = b'\x00\x01' * 1000  # Mock audio data
        mock_wave_file.getnframes.return_value = 1000
        mock_wave_file.getsampwidth.return_value = 2
        mock_wave_file.getnchannels.return_value = 1
        mock_wave_file.getframerate.return_value = 44100
        mock_wave.return_value.__enter__.return_value = mock_wave_file
        
        # Test hiding data
        result = self.stego.hide_in_audio_lsb("test.wav", self.test_data, "output.wav")
        self.assertIsInstance(result, SteganographyResult)

class TestConvenienceFunctions(unittest.TestCase):
    """Test convenience functions"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_data = b"Hello, Reaper Security World!"
        self.test_text = "This is a much longer text message for steganography testing that provides enough space between words to hide the required data bits for the steganography algorithm to work properly. " * 20
    
    def test_generate_key_function(self):
        """Test generate_key convenience function"""
        # Test symmetric key
        key = generate_key(KeyType.SYMMETRIC)
        self.assertIsInstance(key, bytes)
        
        # Test RSA keypair
        private, public = generate_key(KeyType.RSA_2048)
        self.assertIsInstance(private, bytes)
        self.assertIsInstance(public, bytes)
        
        # Test ECC keypair
        private_ecc, public_ecc = generate_key(KeyType.ECC_P256)
        self.assertIsInstance(private_ecc, bytes)
        self.assertIsInstance(public_ecc, bytes)
    
    def test_encrypt_decrypt_data_functions(self):
        """Test encrypt_data and decrypt_data convenience functions"""
        password = "test_password"
        
        # Encrypt data
        result = encrypt_data(self.test_data, password=password)
        self.assertIsInstance(result, EncryptionResult)
        
        # Decrypt data
        decrypted = decrypt_data(
            result.ciphertext, password=password, 
            salt=result.salt, iv=result.iv, tag=result.tag
        )
        self.assertEqual(decrypted, self.test_data)
    
    def test_hash_functions(self):
        """Test hash convenience functions"""
        # Test hash_data
        hash_value = hash_data(self.test_data)
        self.assertIsInstance(hash_value, bytes)
        
        # Test hash_password
        result = hash_password("test_password")
        self.assertIsInstance(result, HashResult)
        
        # Test verify_password
        is_valid = verify_password("test_password", result.hash_value)
        self.assertTrue(is_valid)
    
    def test_steganography_functions(self):
        """Test steganography convenience functions"""
        # Test text steganography
        stego_text = hide_in_text(self.test_text, self.test_data)
        self.assertIsInstance(stego_text, str)
        
        result = extract_from_text(stego_text)
        self.assertTrue(result.success)
        self.assertEqual(result.data, self.test_data)

if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)
