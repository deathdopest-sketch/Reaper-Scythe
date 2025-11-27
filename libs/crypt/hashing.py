"""
Crypt Hashing Module

This module provides hashing and password hashing capabilities
for the Reaper security-focused programming language.

Features:
- Cryptographic hashes (SHA family, MD5, BLAKE2)
- Password hashing (bcrypt, scrypt, Argon2)
- Key derivation functions (PBKDF2, HKDF)
- Hash-based message authentication (HMAC)
- Salt generation and management

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
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.backends import default_backend
import bcrypt

logger = logging.getLogger(__name__)

class HashAlgorithm(Enum):
    """Supported hash algorithms"""
    MD5 = "md5"
    SHA1 = "sha1"
    SHA224 = "sha224"
    SHA256 = "sha256"
    SHA384 = "sha384"
    SHA512 = "sha512"
    SHA3_224 = "sha3_224"
    SHA3_256 = "sha3_256"
    SHA3_384 = "sha3_384"
    SHA3_512 = "sha3_512"
    BLAKE2B = "blake2b"
    BLAKE2S = "blake2s"

class PasswordHashType(Enum):
    """Password hashing algorithms"""
    BCRYPT = "bcrypt"
    SCRYPT = "scrypt"
    PBKDF2_SHA256 = "pbkdf2_sha256"
    PBKDF2_SHA512 = "pbkdf2_sha512"

@dataclass
class HashConfig:
    """Configuration for hashing operations"""
    default_algorithm: HashAlgorithm = HashAlgorithm.SHA256
    salt_size: int = 32
    bcrypt_rounds: int = 12
    scrypt_n: int = 16384
    scrypt_r: int = 8
    scrypt_p: int = 1
    pbkdf2_iterations: int = 100000

@dataclass
class HashResult:
    """Result of hashing operation"""
    hash_value: bytes
    salt: Optional[bytes] = None
    algorithm: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class CryptHasher:
    """
    Cryptographic hashing engine for the Crypt library.
    
    Provides various hashing algorithms, password hashing,
    and key derivation functions.
    """
    
    def __init__(self, config: Optional[HashConfig] = None):
        """
        Initialize hashing engine.
        
        Args:
            config: HashConfig with hashing parameters
        """
        self.config = config or HashConfig()
        self.backend = default_backend()
    
    def generate_salt(self, size: int = None) -> bytes:
        """
        Generate cryptographically secure salt.
        
        Args:
            size: Salt size in bytes
            
        Returns:
            Random salt bytes
        """
        size = size or self.config.salt_size
        return secrets.token_bytes(size)
    
    def hash_data(self, data: bytes, algorithm: HashAlgorithm = None) -> HashResult:
        """
        Hash data using specified algorithm.
        
        Args:
            data: Data to hash
            algorithm: Hash algorithm to use
            
        Returns:
            HashResult with hash value
        """
        algorithm = algorithm or self.config.default_algorithm
        
        if algorithm == HashAlgorithm.MD5:
            hash_value = hashlib.md5(data).digest()
        elif algorithm == HashAlgorithm.SHA1:
            hash_value = hashlib.sha1(data).digest()
        elif algorithm == HashAlgorithm.SHA224:
            hash_value = hashlib.sha224(data).digest()
        elif algorithm == HashAlgorithm.SHA256:
            hash_value = hashlib.sha256(data).digest()
        elif algorithm == HashAlgorithm.SHA384:
            hash_value = hashlib.sha384(data).digest()
        elif algorithm == HashAlgorithm.SHA512:
            hash_value = hashlib.sha512(data).digest()
        elif algorithm == HashAlgorithm.SHA3_224:
            hash_value = hashlib.sha3_224(data).digest()
        elif algorithm == HashAlgorithm.SHA3_256:
            hash_value = hashlib.sha3_256(data).digest()
        elif algorithm == HashAlgorithm.SHA3_384:
            hash_value = hashlib.sha3_384(data).digest()
        elif algorithm == HashAlgorithm.SHA3_512:
            hash_value = hashlib.sha3_512(data).digest()
        elif algorithm == HashAlgorithm.BLAKE2B:
            hash_value = hashlib.blake2b(data).digest()
        elif algorithm == HashAlgorithm.BLAKE2S:
            hash_value = hashlib.blake2s(data).digest()
        else:
            raise ValueError(f"Unsupported hash algorithm: {algorithm}")
        
        return HashResult(
            hash_value=hash_value,
            algorithm=algorithm.value,
            metadata={"input_size": len(data)}
        )
    
    def hash_file(self, file_path: str, algorithm: HashAlgorithm = None, 
                  chunk_size: int = 8192) -> HashResult:
        """
        Hash a file using specified algorithm.
        
        Args:
            file_path: Path to file to hash
            algorithm: Hash algorithm to use
            chunk_size: Chunk size for reading file
            
        Returns:
            HashResult with file hash
        """
        algorithm = algorithm or self.config.default_algorithm
        
        if algorithm == HashAlgorithm.MD5:
            hasher = hashlib.md5()
        elif algorithm == HashAlgorithm.SHA1:
            hasher = hashlib.sha1()
        elif algorithm == HashAlgorithm.SHA224:
            hasher = hashlib.sha224()
        elif algorithm == HashAlgorithm.SHA256:
            hasher = hashlib.sha256()
        elif algorithm == HashAlgorithm.SHA384:
            hasher = hashlib.sha384()
        elif algorithm == HashAlgorithm.SHA512:
            hasher = hashlib.sha512()
        elif algorithm == HashAlgorithm.SHA3_224:
            hasher = hashlib.sha3_224()
        elif algorithm == HashAlgorithm.SHA3_256:
            hasher = hashlib.sha3_256()
        elif algorithm == HashAlgorithm.SHA3_384:
            hasher = hashlib.sha3_384()
        elif algorithm == HashAlgorithm.SHA3_512:
            hasher = hashlib.sha3_512()
        elif algorithm == HashAlgorithm.BLAKE2B:
            hasher = hashlib.blake2b()
        elif algorithm == HashAlgorithm.BLAKE2S:
            hasher = hashlib.blake2s()
        else:
            raise ValueError(f"Unsupported hash algorithm: {algorithm}")
        
        try:
            with open(file_path, 'rb') as f:
                while chunk := f.read(chunk_size):
                    hasher.update(chunk)
            
            hash_value = hasher.digest()
            
            return HashResult(
                hash_value=hash_value,
                algorithm=algorithm.value,
                metadata={"file_path": file_path, "file_size": os.path.getsize(file_path)}
            )
            
        except Exception as e:
            logger.error(f"File hashing failed: {e}")
            raise
    
    def hash_password_bcrypt(self, password: str, rounds: int = None) -> HashResult:
        """
        Hash password using bcrypt.
        
        Args:
            password: Password to hash
            rounds: Bcrypt rounds (cost factor)
            
        Returns:
            HashResult with hashed password
        """
        rounds = rounds or self.config.bcrypt_rounds
        
        # Generate salt and hash password
        salt = bcrypt.gensalt(rounds=rounds)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        
        return HashResult(
            hash_value=hashed,
            algorithm="bcrypt",
            metadata={"rounds": rounds, "salt": salt}
        )
    
    def verify_password_bcrypt(self, password: str, hashed_password: bytes) -> bool:
        """
        Verify password against bcrypt hash.
        
        Args:
            password: Password to verify
            hashed_password: Bcrypt hash
            
        Returns:
            True if password matches
        """
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed_password)
        except Exception as e:
            logger.error(f"Password verification failed: {e}")
            return False
    
    def hash_password_scrypt(self, password: str, salt: bytes = None, 
                            n: int = None, r: int = None, p: int = None) -> HashResult:
        """
        Hash password using scrypt.
        
        Args:
            password: Password to hash
            salt: Salt bytes (generated if None)
            n: CPU/memory cost parameter
            r: Block size parameter
            p: Parallelization parameter
            
        Returns:
            HashResult with hashed password
        """
        salt = salt or self.generate_salt()
        n = n or self.config.scrypt_n
        r = r or self.config.scrypt_r
        p = p or self.config.scrypt_p
        
        # Use hashlib's scrypt implementation
        hashed = hashlib.scrypt(
            password.encode('utf-8'),
            salt=salt,
            n=n,
            r=r,
            p=p,
            dklen=64
        )
        
        return HashResult(
            hash_value=hashed,
            salt=salt,
            algorithm="scrypt",
            metadata={"n": n, "r": r, "p": p, "dklen": 64}
        )
    
    def verify_password_scrypt(self, password: str, hashed_password: bytes, 
                              salt: bytes, n: int, r: int, p: int) -> bool:
        """
        Verify password against scrypt hash.
        
        Args:
            password: Password to verify
            hashed_password: Scrypt hash
            salt: Salt used for hashing
            n, r, p: Scrypt parameters
            
        Returns:
            True if password matches
        """
        try:
            computed_hash = hashlib.scrypt(
                password.encode('utf-8'),
                salt=salt,
                n=n,
                r=r,
                p=p,
                dklen=len(hashed_password)
            )
            return computed_hash == hashed_password
        except Exception as e:
            logger.error(f"Password verification failed: {e}")
            return False
    
    def hash_password_pbkdf2(self, password: str, salt: bytes = None, 
                             algorithm: str = "SHA256", iterations: int = None) -> HashResult:
        """
        Hash password using PBKDF2.
        
        Args:
            password: Password to hash
            salt: Salt bytes (generated if None)
            algorithm: Hash algorithm for PBKDF2
            iterations: Number of iterations
            
        Returns:
            HashResult with hashed password
        """
        salt = salt or self.generate_salt()
        iterations = iterations or self.config.pbkdf2_iterations
        
        # Map algorithm string to hashes object
        hash_map = {
            "SHA256": hashes.SHA256(),
            "SHA512": hashes.SHA512(),
            "SHA1": hashes.SHA1()
        }
        
        if algorithm not in hash_map:
            raise ValueError(f"Unsupported PBKDF2 algorithm: {algorithm}")
        
        kdf = PBKDF2HMAC(
            algorithm=hash_map[algorithm],
            length=64,
            salt=salt,
            iterations=iterations,
            backend=self.backend
        )
        
        hashed = kdf.derive(password.encode('utf-8'))
        
        return HashResult(
            hash_value=hashed,
            salt=salt,
            algorithm=f"pbkdf2_{algorithm.lower()}",
            metadata={"iterations": iterations, "length": 64}
        )
    
    def verify_password_pbkdf2(self, password: str, hashed_password: bytes, 
                               salt: bytes, algorithm: str, iterations: int) -> bool:
        """
        Verify password against PBKDF2 hash.
        
        Args:
            password: Password to verify
            hashed_password: PBKDF2 hash
            salt: Salt used for hashing
            algorithm: Hash algorithm used
            iterations: Number of iterations used
            
        Returns:
            True if password matches
        """
        try:
            hash_map = {
                "SHA256": hashes.SHA256(),
                "SHA512": hashes.SHA512(),
                "SHA1": hashes.SHA1()
            }
            
            kdf = PBKDF2HMAC(
                algorithm=hash_map[algorithm],
                length=len(hashed_password),
                salt=salt,
                iterations=iterations,
                backend=self.backend
            )
            
            computed_hash = kdf.derive(password.encode('utf-8'))
            return computed_hash == hashed_password
            
        except Exception as e:
            logger.error(f"Password verification failed: {e}")
            return False
    
    def generate_hmac(self, data: bytes, key: bytes, algorithm: HashAlgorithm = None) -> bytes:
        """
        Generate HMAC for data.
        
        Args:
            data: Data to authenticate
            key: HMAC key
            algorithm: Hash algorithm for HMAC
            
        Returns:
            HMAC value
        """
        algorithm = algorithm or self.config.default_algorithm
        
        # Map HashAlgorithm to hashes object
        hash_map = {
            HashAlgorithm.SHA256: hashes.SHA256(),
            HashAlgorithm.SHA512: hashes.SHA512(),
            HashAlgorithm.SHA1: hashes.SHA1(),
            HashAlgorithm.SHA384: hashes.SHA384()
        }
        
        if algorithm not in hash_map:
            raise ValueError(f"Unsupported HMAC algorithm: {algorithm}")
        
        h = hmac.HMAC(key, hash_map[algorithm], backend=self.backend)
        h.update(data)
        return h.finalize()
    
    def verify_hmac(self, data: bytes, key: bytes, hmac_value: bytes, 
                   algorithm: HashAlgorithm = None) -> bool:
        """
        Verify HMAC for data.
        
        Args:
            data: Data to verify
            key: HMAC key
            hmac_value: HMAC to verify against
            algorithm: Hash algorithm for HMAC
            
        Returns:
            True if HMAC is valid
        """
        try:
            computed_hmac = self.generate_hmac(data, key, algorithm)
            return secrets.compare_digest(computed_hmac, hmac_value)
        except Exception as e:
            logger.error(f"HMAC verification failed: {e}")
            return False
    
    def derive_key_hkdf(self, master_key: bytes, salt: bytes = None, 
                       info: bytes = None, length: int = 32) -> bytes:
        """
        Derive key using HKDF.
        
        Args:
            master_key: Master key for derivation
            salt: Salt bytes (generated if None)
            info: Additional info bytes
            length: Length of derived key
            
        Returns:
            Derived key
        """
        salt = salt or self.generate_salt()
        info = info or b""
        
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=length,
            salt=salt,
            info=info,
            backend=self.backend
        )
        
        return hkdf.derive(master_key)
    
    def crack_password_simple(self, password_hash: bytes, wordlist: list, 
                             algorithm: str = "bcrypt") -> Optional[str]:
        """
        Simple password cracking using wordlist.
        
        Args:
            password_hash: Hashed password to crack
            wordlist: List of passwords to try
            algorithm: Hashing algorithm used
            
        Returns:
            Cracked password if found, None otherwise
        """
        logger.warning("Password cracking is for educational purposes only")
        
        for password in wordlist:
            try:
                if algorithm == "bcrypt":
                    if self.verify_password_bcrypt(password, password_hash):
                        return password
                elif algorithm.startswith("pbkdf2"):
                    # This would need salt and iterations - simplified for demo
                    pass
                elif algorithm == "scrypt":
                    # This would need salt and parameters - simplified for demo
                    pass
            except Exception:
                continue
        
        return None

# Convenience functions
def hash_data(data: bytes, algorithm: HashAlgorithm = HashAlgorithm.SHA256) -> bytes:
    """Hash data using specified algorithm"""
    hasher = CryptHasher()
    result = hasher.hash_data(data, algorithm)
    return result.hash_value

def hash_file(file_path: str, algorithm: HashAlgorithm = HashAlgorithm.SHA256) -> bytes:
    """Hash file using specified algorithm"""
    hasher = CryptHasher()
    result = hasher.hash_file(file_path, algorithm)
    return result.hash_value

def hash_password(password: str, algorithm: PasswordHashType = PasswordHashType.BCRYPT) -> HashResult:
    """Hash password using specified algorithm"""
    hasher = CryptHasher()
    
    if algorithm == PasswordHashType.BCRYPT:
        return hasher.hash_password_bcrypt(password)
    elif algorithm == PasswordHashType.SCRYPT:
        return hasher.hash_password_scrypt(password)
    elif algorithm == PasswordHashType.PBKDF2_SHA256:
        return hasher.hash_password_pbkdf2(password, algorithm="SHA256")
    elif algorithm == PasswordHashType.PBKDF2_SHA512:
        return hasher.hash_password_pbkdf2(password, algorithm="SHA512")
    else:
        raise ValueError(f"Unsupported password hash type: {algorithm}")

def verify_password(password: str, hashed_password: bytes, algorithm: str = "bcrypt", 
                   salt: bytes = None, **kwargs) -> bool:
    """Verify password against hash"""
    hasher = CryptHasher()
    
    if algorithm == "bcrypt":
        return hasher.verify_password_bcrypt(password, hashed_password)
    elif algorithm == "scrypt":
        if not salt:
            raise ValueError("Salt required for scrypt verification")
        return hasher.verify_password_scrypt(password, hashed_password, salt, **kwargs)
    elif algorithm.startswith("pbkdf2"):
        if not salt:
            raise ValueError("Salt required for PBKDF2 verification")
        return hasher.verify_password_pbkdf2(password, hashed_password, salt, **kwargs)
    else:
        raise ValueError(f"Unsupported verification algorithm: {algorithm}")

# Export main classes and functions
__all__ = [
    'CryptHasher', 'HashConfig', 'HashAlgorithm', 'PasswordHashType', 'HashResult',
    'hash_data', 'hash_file', 'hash_password', 'verify_password'
]
