"""Data models for ICM/BF calculation"""
from dataclasses import dataclass
from typing import List

@dataclass
class CalculationInput:
    players: int
    stacks: List[float]
    payouts: List[float]

    def validate(self) -> tuple[bool, str]:
        """Validate input parameters"""
        if not isinstance(self.players, int) or self.players < 2 or self.players > 9:
            return False, "Players must be between 2 and 9"
        
        if len(self.stacks) != self.players:
            return False, "Number of stacks must match player count"
        
        if len(self.payouts) != self.players:
            return False, "Number of payouts must match player count"
        
        if any(s < 0 for s in self.stacks):
            return False, "Stacks must be non-negative"
        
        if any(p < 0 for p in self.payouts):
            return False, "Payouts must be non-negative"
        
        if sum(self.stacks) == 0:
            return False, "Total chips must be greater than 0"
        
        # Verify payouts are in descending order
        if self.payouts != sorted(self.payouts, reverse=True):
            return False, "Payouts must be in descending order"
        
        return True, ""

@dataclass
class CalculationOutput:
    icm: List[float]
    bf: List[float]
    total_chips: float
    total_payout: float
