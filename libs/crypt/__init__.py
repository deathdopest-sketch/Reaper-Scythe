# Crypt Cryptography Library
# Encryption, hashing, steganography, key generation

__version__ = "0.1.0"
__author__ = "Reaper Security Team"

# Core features implemented in L1-T003
from .encryption import (
    CryptEngine, CryptConfig, CipherType, KeyType, EncryptionResult,
    generate_key, encrypt_data, decrypt_data
)

from .hashing import (
    CryptHasher, HashConfig, HashAlgorithm, PasswordHashType, HashResult,
    hash_data, hash_file, hash_password, verify_password
)

from .steganography import (
    CryptSteganographer, SteganographyConfig, SteganographyType,
    SteganographyMethod, SteganographyResult,
    hide_in_image, extract_from_image, hide_in_audio, extract_from_audio,
    hide_in_text, extract_from_text, analyze_file
)

__all__ = [
    # Encryption
    'CryptEngine', 'CryptConfig', 'CipherType', 'KeyType', 'EncryptionResult',
    'generate_key', 'encrypt_data', 'decrypt_data',
    
    # Hashing
    'CryptHasher', 'HashConfig', 'HashAlgorithm', 'PasswordHashType', 'HashResult',
    'hash_data', 'hash_file', 'hash_password', 'verify_password',
    
    # Steganography
    'CryptSteganographer', 'SteganographyConfig', 'SteganographyType',
    'SteganographyMethod', 'SteganographyResult',
    'hide_in_image', 'extract_from_image', 'hide_in_audio', 'extract_from_audio',
    'hide_in_text', 'extract_from_text', 'analyze_file'
]
