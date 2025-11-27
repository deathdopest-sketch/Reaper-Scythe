"""
Fuzzing Strategy Module

Provides different fuzzing strategies.
"""

from typing import List, Optional, Callable, Any, Union
from .mutator import MutationEngine, BitFlipMutator, ByteFlipMutator
from .coverage import CoverageTracker
from .corpus import CorpusManager


class FuzzingStrategy:
    """
    Base fuzzing strategy.
    """
    
    def __init__(self, mutator: MutationEngine, coverage: CoverageTracker,
                 corpus: CorpusManager):
        """
        Initialize fuzzing strategy.
        
        Args:
            mutator: Mutation engine
            coverage: Coverage tracker
            corpus: Corpus manager
        """
        self.mutator = mutator
        self.coverage = coverage
        self.corpus = corpus
    
    def generate_input(self) -> bytes:
        """
        Generate next input to fuzz.
        
        Returns:
            Input data
        """
        raise NotImplementedError
    
    def update(self, input_data: bytes, was_interesting: bool) -> None:
        """
        Update strategy based on results.
        
        Args:
            input_data: Input that was tested
            was_interesting: Whether input was interesting
        """
        pass


class RandomStrategy(FuzzingStrategy):
    """
    Random fuzzing strategy.
    """
    
    def generate_input(self) -> bytes:
        """Generate random input."""
        import random
        
        # Get seed from corpus or generate random
        seed = self.corpus.get_seed()
        if seed:
            # Mutate seed
            return self.mutator.mutate(seed)
        else:
            # Generate random
            size = random.randint(1, 1000)
            return bytes(random.randint(0, 255) for _ in range(size))


class AFLStrategy(FuzzingStrategy):
    """
    AFL-like fuzzing strategy.
    """
    
    def __init__(self, mutator: MutationEngine, coverage: CoverageTracker,
                 corpus: CorpusManager):
        """Initialize AFL strategy."""
        super().__init__(mutator, coverage, corpus)
        self.favored_inputs: List[bytes] = []
        self.energy: Dict[str, float] = {}
    
    def generate_input(self) -> bytes:
        """Generate input using AFL-like strategy."""
        import random
        
        # Prefer favored inputs
        if self.favored_inputs and random.random() < 0.5:
            seed = random.choice(self.favored_inputs)
        else:
            seed = self.corpus.get_seed()
        
        if not seed:
            # Generate random
            size = random.randint(1, 1000)
            return bytes(random.randint(0, 255) for _ in range(size))
        
        # Mutate seed
        return self.mutator.mutate(seed)
    
    def update(self, input_data: bytes, was_interesting: bool) -> None:
        """Update strategy."""
        if was_interesting:
            data_hash = self.coverage.calculate_hash(input_data)
            if input_data not in self.favored_inputs:
                self.favored_inputs.append(input_data)
                self.energy[data_hash] = 1.0

