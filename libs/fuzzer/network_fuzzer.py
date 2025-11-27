"""
Network Protocol Fuzzer Module

Provides fuzzing for network protocols.
"""

from typing import Callable, Optional, Dict, Any
from .mutator import MutationEngine, BitFlipMutator
from .strategy import FuzzingStrategy
from .coverage import CoverageTracker
from .corpus import CorpusManager


class NetworkFuzzer:
    """
    Fuzzer for network protocols.
    """
    
    def __init__(self, target_host: str, target_port: int,
                 protocol_handler: Callable[[bytes], bytes],
                 mutator: Optional[MutationEngine] = None):
        """
        Initialize network fuzzer.
        
        Args:
            target_host: Target host
            target_port: Target port
            protocol_handler: Function to send/receive protocol data
            mutator: Mutation engine (default: BitFlipMutator)
        """
        self.target_host = target_host
        self.target_port = target_port
        self.protocol_handler = protocol_handler
        self.mutator = mutator or BitFlipMutator()
        self.coverage = CoverageTracker()
        self.corpus = CorpusManager()
    
    def fuzz(self, seed_data: bytes, iterations: int = 1000) -> Dict[str, Any]:
        """
        Fuzz network protocol.
        
        Args:
            seed_data: Seed data
            iterations: Number of iterations
            
        Returns:
            Fuzzing results
        """
        self.corpus.add_seed(seed_data)
        
        crashes = []
        interesting_inputs = []
        
        for i in range(iterations):
            # Generate mutated input
            input_data = self.mutator.mutate(seed_data)
            
            try:
                # Send to target
                response = self.protocol_handler(input_data)
                
                # Check if interesting
                if self.coverage.is_interesting(input_data):
                    interesting_inputs.append(input_data)
                    self.corpus.add_seed(input_data)
                
            except Exception as e:
                # Crash detected
                crash_info = {
                    'iteration': i,
                    'input': input_data,
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

