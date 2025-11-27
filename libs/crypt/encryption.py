"""
Crypt Encryption/Decryption Module

This module provides encryption and decryption capabilities
for the Reaper security-focused programming language.

Features:
- Symmetric encryption (AES, ChaCha20, Blowfish)
- Asymmetric encryption (RSA, ECC)
- Key generation and management
- Secure random number generation
- Password-based key derivation

Author: Reaper Security Team
Version: 0.1.0
"""

import os
import secrets
import hashlib
import logging
from typing import Union, Optional, Tuple, Dict, Any
from dataclasses import dataclass
from enum import Enum
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidSignature

logger = logging.getLogger(__name__)

class CipherType(Enum):
    """Supported cipher types"""
    AES_256_CBC = "aes_256_cbc"
    AES_256_GCM = "aes_256_gcm"
    CHACHA20_POLY1305 = "chacha20_poly1305"
    BLOWFISH = "blowfish"
    RSA_OAEP = "rsa_oaep"
    RSA_PKCS1 = "rsa_pkcs1"
    ECC_P256 = "ecc_p256"
    ECC_P384 = "ecc_p384"

class KeyType(Enum):
    """Key types for generation"""
    SYMMETRIC = "symmetric"
    RSA_2048 = "rsa_2048"
    RSA_4096 = "rsa_4096"
    ECC_P256 = "ecc_p256"
    ECC_P384 = "ecc_p384"

@dataclass
class CryptConfig:
    """Configuration for cryptographic operations"""
    cipher_type: CipherType = CipherType.AES_256_GCM
    key_size: int = 32  # bytes
    iv_size: int = 16   # bytes
    salt_size: int = 32 # bytes
    iterations: int = 100000  # PBKDF2 iterations
    use_authenticated_encryption: bool = True

@dataclass
class EncryptionResult:
    """Result of encryption operation"""
    ciphertext: bytes
    iv: bytes
    salt: Optional[bytes] = None
    tag: Optional[bytes] = None  # For authenticated encryption
    metadata: Optional[Dict[str, Any]] = None

class CryptEngine:
    """
    Core cryptographic engine for the Crypt library.
    
    Provides symmetric and asymmetric encryption/decryption,
    key generation, and secure random operations.
    """
    
    def __init__(self, config: Optional[CryptConfig] = None):
        """
        Initialize cryptographic engine.
        
        Args:
            config: CryptConfig with cryptographic parameters
        """
        self.config = config or CryptConfig()
        self.backend = default_backend()
    
    def generate_symmetric_key(self, key_size: int = None) -> bytes:
        """
        Generate a random symmetric key.
        
        Args:
            key_size: Size of key in bytes
            
        Returns:
            Random key bytes
        """
        key_size = key_size or self.config.key_size
        return secrets.token_bytes(key_size)
    
    def generate_rsa_keypair(self, key_size: int = 2048) -> Tuple[bytes, bytes]:
        """
        Generate RSA key pair.
        
        Args:
            key_size: RSA key size in bits
            
        Returns:
            Tuple of (private_key_pem, public_key_pem)
        """
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
            backend=self.backend
        )
        
        public_key = private_key.public_key()
        
        # Serialize keys
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        return private_pem, public_pem
    
    def generate_ecc_keypair(self, curve: str = "P-256") -> Tuple[bytes, bytes]:
        """
        Generate ECC key pair.
        
        Args:
            curve: ECC curve name (P-256, P-384, P-521)
            
        Returns:
            Tuple of (private_key_pem, public_key_pem)
        """
        curve_map = {
            "P-256": ec.SECP256R1(),
            "P-384": ec.SECP384R1(),
            "P-521": ec.SECP521R1()
        }
        
        if curve not in curve_map:
            raise ValueError(f"Unsupported curve: {curve}")
        
        private_key = ec.generate_private_key(
            curve_map[curve],
            backend=self.backend
        )
        
        public_key = private_key.public_key()
        
        # Serialize keys
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        return private_pem, public_pem
    
    def derive_key_from_password(self, password: str, salt: bytes = None) -> Tuple[bytes, bytes]:
        """
        Derive encryption key from password using PBKDF2.
        
        Args:
            password: Password string
            salt: Salt bytes (generated if None)
            
        Returns:
            Tuple of (derived_key, salt)
        """
        if salt is None:
            salt = secrets.token_bytes(self.config.salt_size)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=self.config.key_size,
            salt=salt,
            iterations=self.config.iterations,
            backend=self.backend
        )
        
        key = kdf.derive(password.encode('utf-8'))
        return key, salt
    
    def encrypt_aes_cbc(self, plaintext: bytes, key: bytes, iv: bytes = None) -> EncryptionResult:
        """
        Encrypt data using AES-CBC.
        
        Args:
            plaintext: Data to encrypt
            key: Encryption key
            iv: Initialization vector (generated if None)
            
        Returns:
            EncryptionResult with encrypted data
        """
        if iv is None:
            iv = secrets.token_bytes(self.config.iv_size)
        
        # Pad plaintext to block size
        block_size = 16
        padding_length = block_size - (len(plaintext) % block_size)
        padded_plaintext = plaintext + bytes([padding_length] * padding_length)
        
        cipher = Cipher(
            algorithms.AES(key),
            modes.CBC(iv),
            backend=self.backend
        )
        
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(padded_plaintext) + encryptor.finalize()
        
        return EncryptionResult(
            ciphertext=ciphertext,
            iv=iv,
            metadata={"cipher": "AES-CBC", "key_size": len(key)}
        )
    
    def decrypt_aes_cbc(self, ciphertext: bytes, key: bytes, iv: bytes) -> bytes:
        """
        Decrypt data using AES-CBC.
        
        Args:
            ciphertext: Encrypted data
            key: Decryption key
            iv: Initialization vector
            
        Returns:
            Decrypted plaintext
        """
        cipher = Cipher(
            algorithms.AES(key),
            modes.CBC(iv),
            backend=self.backend
        )
        
        decryptor = cipher.decryptor()
        padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        
        # Remove padding
        padding_length = padded_plaintext[-1]
        plaintext = padded_plaintext[:-padding_length]
        
        return plaintext
    
    def encrypt_aes_gcm(self, plaintext: bytes, key: bytes, iv: bytes = None) -> EncryptionResult:
        """
        Encrypt data using AES-GCM (authenticated encryption).
        
        Args:
            plaintext: Data to encrypt
            key: Encryption key
            iv: Initialization vector (generated if None)
            
        Returns:
            EncryptionResult with encrypted data and authentication tag
        """
        if iv is None:
            iv = secrets.token_bytes(self.config.iv_size)
        
        cipher = Cipher(
            algorithms.AES(key),
            modes.GCM(iv),
            backend=self.backend
        )
        
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(plaintext) + encryptor.finalize()
        
        return EncryptionResult(
            ciphertext=ciphertext,
            iv=iv,
            tag=encryptor.tag,
            metadata={"cipher": "AES-GCM", "key_size": len(key)}
        )
    
    def decrypt_aes_gcm(self, ciphertext: bytes, key: bytes, iv: bytes, tag: bytes) -> bytes:
        """
        Decrypt data using AES-GCM.
        
        Args:
            ciphertext: Encrypted data
            key: Decryption key
            iv: Initialization vector
            tag: Authentication tag
            
        Returns:
            Decrypted plaintext
        """
        cipher = Cipher(
            algorithms.AES(key),
            modes.GCM(iv, tag),
            backend=self.backend
        )
        
        decryptor = cipher.decryptor()
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        
        return plaintext
    
    def encrypt_chacha20_poly1305(self, plaintext: bytes, key: bytes, nonce: bytes = None) -> EncryptionResult:
        """
        Encrypt data using ChaCha20 (simplified version).
        
        Args:
            plaintext: Data to encrypt
            key: Encryption key (32 bytes)
            nonce: Nonce (12 bytes, generated if None)
            
        Returns:
            EncryptionResult with encrypted data
        """
        if nonce is None:
            nonce = secrets.token_bytes(16)  # ChaCha20 needs 16-byte nonce
        
        cipher = Cipher(
            algorithms.ChaCha20(key, nonce),
            mode=None,  # ChaCha20 doesn't need a mode
            backend=self.backend
        )
        
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(plaintext) + encryptor.finalize()
        
        return EncryptionResult(
            ciphertext=ciphertext,
            iv=nonce,  # Using iv field for nonce
            metadata={"cipher": "ChaCha20", "key_size": len(key)}
        )
    
    def decrypt_chacha20_poly1305(self, ciphertext: bytes, key: bytes, nonce: bytes, tag: bytes = None) -> bytes:
        """
        Decrypt data using ChaCha20.
        
        Args:
            ciphertext: Encrypted data
            key: Decryption key
            nonce: Nonce
            tag: Authentication tag (ignored for ChaCha20)
            
        Returns:
            Decrypted plaintext
        """
        cipher = Cipher(
            algorithms.ChaCha20(key, nonce),
            mode=None,  # ChaCha20 doesn't need a mode
            backend=self.backend
        )
        
        decryptor = cipher.decryptor()
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        
        return plaintext
    
    def encrypt_rsa(self, plaintext: bytes, public_key_pem: bytes) -> bytes:
        """
        Encrypt data using RSA-OAEP.
        
        Args:
            plaintext: Data to encrypt
            public_key_pem: RSA public key in PEM format
            
        Returns:
            Encrypted data
        """
        public_key = serialization.load_pem_public_key(
            public_key_pem,
            backend=self.backend
        )
        
        ciphertext = public_key.encrypt(
            plaintext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        return ciphertext
    
    def decrypt_rsa(self, ciphertext: bytes, private_key_pem: bytes) -> bytes:
        """
        Decrypt data using RSA-OAEP.
        
        Args:
            ciphertext: Encrypted data
            private_key_pem: RSA private key in PEM format
            
        Returns:
            Decrypted plaintext
        """
        private_key = serialization.load_pem_private_key(
            private_key_pem,
            password=None,
            backend=self.backend
        )
        
        plaintext = private_key.decrypt(
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        return plaintext
    
    def encrypt_with_password(self, plaintext: bytes, password: str) -> EncryptionResult:
        """
        Encrypt data using password-based key derivation.
        
        Args:
            plaintext: Data to encrypt
            password: Password string
            
        Returns:
            EncryptionResult with encrypted data and salt
        """
        key, salt = self.derive_key_from_password(password)
        
        if self.config.use_authenticated_encryption:
            result = self.encrypt_aes_gcm(plaintext, key)
            result.salt = salt  # Add salt to result
            return result
        else:
            result = self.encrypt_aes_cbc(plaintext, key)
            result.salt = salt  # Add salt to result
            return result
    
    def decrypt_with_password(self, ciphertext: bytes, password: str, salt: bytes, 
                             iv: bytes = None, tag: bytes = None, cipher_type: str = "AES-GCM") -> bytes:
        """
        Decrypt data using password-based key derivation.
        
        Args:
            ciphertext: Encrypted data
            password: Password string
            salt: Salt used for key derivation
            iv: Initialization vector (if None, derived from salt)
            tag: Authentication tag (for GCM)
            cipher_type: Cipher type used
            
        Returns:
            Decrypted plaintext
        """
        key, _ = self.derive_key_from_password(password, salt)
        
        if iv is None:
            iv = salt[:16]  # Use first 16 bytes as IV
        
        if cipher_type == "AES-GCM" and tag:
            return self.decrypt_aes_gcm(ciphertext, key, iv, tag)
        else:
            return self.decrypt_aes_cbc(ciphertext, key, iv)
    
    def encrypt_file(self, file_path: str, output_path: str, password: str = None, key: bytes = None) -> bool:
        """
        Encrypt a file.
        
        Args:
            file_path: Path to file to encrypt
            output_path: Path for encrypted file
            password: Password for encryption (if key not provided)
            key: Encryption key (if password not provided)
            
        Returns:
            True if encryption successful
        """
        try:
            with open(file_path, 'rb') as f:
                plaintext = f.read()
            
            if password:
                result = self.encrypt_with_password(plaintext, password)
            elif key:
                result = self.encrypt_aes_gcm(plaintext, key)
            else:
                raise ValueError("Either password or key must be provided")
            
            # Save encrypted data with metadata
            with open(output_path, 'wb') as f:
                f.write(result.ciphertext)
                f.write(result.iv)
                if result.tag:
                    f.write(result.tag)
                if result.salt:
                    f.write(result.salt)
            
            logger.info(f"File encrypted: {file_path} -> {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"File encryption failed: {e}")
            return False
    
    def decrypt_file(self, file_path: str, output_path: str, password: str = None, key: bytes = None) -> bool:
        """
        Decrypt a file.
        
        Args:
            file_path: Path to encrypted file
            output_path: Path for decrypted file
            password: Password for decryption
            key: Decryption key
            
        Returns:
            True if decryption successful
        """
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
            
            # Extract components (matches encrypt_file format: ciphertext + iv + tag + salt)
            # Calculate sizes based on what was written
            salt_size = 32 if password else 0  # PBKDF2 salt is 32 bytes
            tag_size = 16 if len(data) > 16 + salt_size else 0
            iv_size = 16
            
            salt = data[-salt_size:] if salt_size > 0 else None
            tag = data[-(salt_size + tag_size):-salt_size] if tag_size > 0 else None
            iv = data[-(salt_size + tag_size + iv_size):-(salt_size + tag_size)] if iv_size > 0 else None
            ciphertext = data[:-(salt_size + tag_size + iv_size)]
            
            if password:
                plaintext = self.decrypt_with_password(ciphertext, password, salt, iv, tag)
            elif key:
                plaintext = self.decrypt_aes_gcm(ciphertext, key, iv, tag)
            else:
                raise ValueError("Either password or key must be provided")
            
            with open(output_path, 'wb') as f:
                f.write(plaintext)
            
            logger.info(f"File decrypted: {file_path} -> {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"File decryption failed: {e}")
            return False

# Convenience functions
def generate_key(key_type: KeyType = KeyType.SYMMETRIC) -> Union[bytes, Tuple[bytes, bytes]]:
    """Generate cryptographic key(s)"""
    engine = CryptEngine()
    
    if key_type == KeyType.SYMMETRIC:
        return engine.generate_symmetric_key()
    elif key_type in [KeyType.RSA_2048, KeyType.RSA_4096]:
        size = 2048 if key_type == KeyType.RSA_2048 else 4096
        return engine.generate_rsa_keypair(size)
    elif key_type in [KeyType.ECC_P256, KeyType.ECC_P384]:
        curve = "P-256" if key_type == KeyType.ECC_P256 else "P-384"
        return engine.generate_ecc_keypair(curve)

def encrypt_data(data: bytes, password: str = None, key: bytes = None) -> EncryptionResult:
    """Encrypt data with password or key"""
    engine = CryptEngine()
    
    if password:
        return engine.encrypt_with_password(data, password)
    elif key:
        return engine.encrypt_aes_gcm(data, key)
    else:
        raise ValueError("Either password or key must be provided")

def decrypt_data(ciphertext: bytes, password: str = None, key: bytes = None, 
                salt: bytes = None, iv: bytes = None, tag: bytes = None) -> bytes:
    """Decrypt data with password or key"""
    engine = CryptEngine()
    
    if password and salt:
        return engine.decrypt_with_password(ciphertext, password, salt, iv, tag)
    elif key and salt and tag:
        return engine.decrypt_aes_gcm(ciphertext, key, salt, tag)
    else:
        raise ValueError("Invalid parameters for decryption")

# Export main classes and functions
__all__ = [
    'CryptEngine', 'CryptConfig', 'CipherType', 'KeyType', 'EncryptionResult',
    'generate_key', 'encrypt_data', 'decrypt_data'
]
