"""
File Format Fuzzer Module

Provides fuzzing for file formats.
"""

from typing import Callable, Optional, Dict, Any
from .mutator import MutationEngine, BitFlipMutator
from .strategy import FuzzingStrategy
from .coverage import CoverageTracker
from .corpus import CorpusManager


class FileFuzzer:
    """
    Fuzzer for file formats.
    """
    
    def __init__(self, file_handler: Callable[[bytes], Any],
                 mutator: Optional[MutationEngine] = None):
        """
        Initialize file fuzzer.
        
        Args:
            file_handler: Function to process file data
            mutator: Mutation engine (default: BitFlipMutator)
        """
        self.file_handler = file_handler
        self.mutator = mutator or BitFlipMutator()
        self.coverage = CoverageTracker()
        self.corpus = CorpusManager()
    
    def fuzz(self, seed_file: bytes, iterations: int = 1000) -> Dict[str, Any]:
        """
        Fuzz file format.
        
        Args:
            seed_file: Seed file data
            iterations: Number of iterations
            
        Returns:
            Fuzzing results
        """
        self.corpus.add_seed(seed_file)
        
        crashes = []
        interesting_inputs = []
        
        for i in range(iterations):
            # Generate mutated file
            mutated_file = self.mutator.mutate(seed_file)
            
            try:
                # Process file
                result = self.file_handler(mutated_file)
                
                # Check if interesting
                if self.coverage.is_interesting(mutated_file):
                    interesting_inputs.append(mutated_file)
                    self.corpus.add_seed(mutated_file)
                
            except Exception as e:
                # Crash detected
                crash_info = {
                    'iteration': i,
                    'input': mutated_file[:100],  # Preview
                    'exception': str(e),
                }
                crashes.append(crash_info)
        
        return {
            'iterations': iterations,
            'crashes': len(crashes),
            'interesting_inputs': len(interesting_inputs),
            'coverage': self.coverage.get_coverage(),
            'crash_details': crashes,
        }

