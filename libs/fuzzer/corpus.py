"""
Corpus Management Module

Provides seed corpus management for fuzzing.
"""

from typing import List, Dict, Optional, Set
from pathlib import Path
import hashlib


class CorpusManager:
    """
    Manager for fuzzing seed corpus.
    """
    
    def __init__(self, corpus_dir: Optional[str] = None):
        """
        Initialize corpus manager.
        
        Args:
            corpus_dir: Directory for corpus files
        """
        self.corpus_dir = Path(corpus_dir) if corpus_dir else None
        if self.corpus_dir:
            self.corpus_dir.mkdir(parents=True, exist_ok=True)
        
        self.corpus: List[bytes] = []
        self.corpus_hashes: Set[str] = set()
        self.metadata: Dict[str, Dict[str, Any]] = {}
    
    def add_seed(self, data: bytes, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Add seed to corpus.
        
        Args:
            data: Seed data
            metadata: Optional metadata
            
        Returns:
            True if added (False if duplicate)
        """
        data_hash = self._hash_data(data)
        
        if data_hash in self.corpus_hashes:
            return False
        
        self.corpus.append(data)
        self.corpus_hashes.add(data_hash)
        
        if metadata:
            self.metadata[data_hash] = metadata
        else:
            self.metadata[data_hash] = {}
        
        # Save to file if corpus directory is set
        if self.corpus_dir:
            self._save_seed(data, data_hash)
        
        return True
    
    def load_corpus(self) -> None:
        """Load corpus from directory."""
        if not self.corpus_dir or not self.corpus_dir.exists():
            return
        
        for seed_file in self.corpus_dir.glob('*'):
            if seed_file.is_file():
                try:
                    data = seed_file.read_bytes()
                    self.add_seed(data)
                except Exception:
                    pass
    
    def get_seed(self, index: Optional[int] = None) -> Optional[bytes]:
        """
        Get a seed from corpus.
        
        Args:
            index: Seed index (None for random)
            
        Returns:
            Seed data or None
        """
        if not self.corpus:
            return None
        
        if index is None:
            import random
            index = random.randint(0, len(self.corpus) - 1)
        
        if 0 <= index < len(self.corpus):
            return self.corpus[index]
        
        return None
    
    def _hash_data(self, data: bytes) -> str:
        """Hash data."""
        return hashlib.sha256(data).hexdigest()
    
    def _save_seed(self, data: bytes, data_hash: str) -> None:
        """Save seed to file."""
        if not self.corpus_dir:
            return
        
        seed_file = self.corpus_dir / f"seed_{data_hash[:16]}.bin"
        seed_file.write_bytes(data)
    
    def size(self) -> int:
        """Get corpus size."""
        return len(self.corpus)

