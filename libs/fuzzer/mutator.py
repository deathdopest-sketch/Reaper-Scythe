"""
Mutation Engine Module

Provides mutation engines for fuzzing.
"""

from typing import List, Optional, Callable
import random
import struct


class MutationEngine:
    """
    Base mutation engine.
    """
    
    def __init__(self, seed: Optional[int] = None):
        """
        Initialize mutation engine.
        
        Args:
            seed: Random seed
        """
        if seed is not None:
            random.seed(seed)
    
    def mutate(self, data: bytes) -> bytes:
        """
        Mutate input data.
        
        Args:
            data: Input data
            
        Returns:
            Mutated data
        """
        raise NotImplementedError


class BitFlipMutator(MutationEngine):
    """
    Bit-flip mutator.
    """
    
    def mutate(self, data: bytes, num_flips: int = 1) -> bytes:
        """
        Flip random bits in data.
        
        Args:
            data: Input data
            num_flips: Number of bits to flip
            
        Returns:
            Mutated data
        """
        mutated = bytearray(data)
        
        for _ in range(num_flips):
            if len(mutated) == 0:
                break
            
            byte_idx = random.randint(0, len(mutated) - 1)
            bit_idx = random.randint(0, 7)
            mutated[byte_idx] ^= (1 << bit_idx)
        
        return bytes(mutated)


class ByteFlipMutator(MutationEngine):
    """
    Byte-flip mutator.
    """
    
    def mutate(self, data: bytes, num_flips: int = 1) -> bytes:
        """
        Flip random bytes in data.
        
        Args:
            data: Input data
            num_flips: Number of bytes to flip
            
        Returns:
            Mutated data
        """
        mutated = bytearray(data)
        
        for _ in range(num_flips):
            if len(mutated) == 0:
                break
            
            byte_idx = random.randint(0, len(mutated) - 1)
            mutated[byte_idx] = random.randint(0, 255)
        
        return bytes(mutated)


class InsertMutator(MutationEngine):
    """
    Insert mutator - inserts random bytes.
    """
    
    def mutate(self, data: bytes, num_inserts: int = 1, max_insert_size: int = 10) -> bytes:
        """
        Insert random bytes into data.
        
        Args:
            data: Input data
            num_inserts: Number of insertions
            max_insert_size: Maximum size of each insertion
            
        Returns:
            Mutated data
        """
        mutated = bytearray(data)
        
        for _ in range(num_inserts):
            insert_pos = random.randint(0, len(mutated))
            insert_size = random.randint(1, max_insert_size)
            insert_bytes = bytes(random.randint(0, 255) for _ in range(insert_size))
            mutated[insert_pos:insert_pos] = insert_bytes
        
        return bytes(mutated)


class DeleteMutator(MutationEngine):
    """
    Delete mutator - deletes random bytes.
    """
    
    def mutate(self, data: bytes, num_deletes: int = 1, max_delete_size: int = 10) -> bytes:
        """
        Delete random bytes from data.
        
        Args:
            data: Input data
            num_deletes: Number of deletions
            max_delete_size: Maximum size of each deletion
            
        Returns:
            Mutated data
        """
        mutated = bytearray(data)
        
        for _ in range(num_deletes):
            if len(mutated) == 0:
                break
            
            delete_pos = random.randint(0, len(mutated) - 1)
            delete_size = min(random.randint(1, max_delete_size), len(mutated) - delete_pos)
            del mutated[delete_pos:delete_pos + delete_size]
        
        return bytes(mutated)


class ArithmeticMutator(MutationEngine):
    """
    Arithmetic mutator - performs arithmetic operations on integers.
    """
    
    def mutate(self, data: bytes, num_mutations: int = 1) -> bytes:
        """
        Perform arithmetic mutations on integers in data.
        
        Args:
            data: Input data
            num_mutations: Number of mutations
            
        Returns:
            Mutated data
        """
        if len(data) < 4:
            return data
        
        mutated = bytearray(data)
        
        for _ in range(num_mutations):
            # Find a 4-byte aligned position
            if len(mutated) < 4:
                break
            
            pos = random.randint(0, (len(mutated) - 4) // 4) * 4
            
            # Read as integer
            value = struct.unpack('<I', mutated[pos:pos+4])[0]
            
            # Apply arithmetic operation
            operations = [
                lambda x: x + 1,
                lambda x: x - 1,
                lambda x: x * 2,
                lambda x: x // 2,
                lambda x: x + 100,
                lambda x: x - 100,
            ]
            op = random.choice(operations)
            new_value = op(value) & 0xFFFFFFFF  # Keep as 32-bit
            
            # Write back
            mutated[pos:pos+4] = struct.pack('<I', new_value)
        
        return bytes(mutated)

