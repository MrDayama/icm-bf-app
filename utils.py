"""Utility functions"""
from typing import List, Tuple

def normalize_payouts(payouts: List[float]) -> List[float]:
    """Ensure payouts are in descending order"""
    return sorted(payouts, reverse=True)

def parse_input(players_str: str, stacks_str: str, payouts_str: str) -> Tuple[int, List[float], List[float]]:
    """Parse and validate input strings"""
    try:
        players = int(players_str)
        stacks = [float(x.strip()) for x in stacks_str.split(',') if x.strip()]
        payouts = [float(x.strip()) for x in payouts_str.split(',') if x.strip()]
        
        return players, stacks, normalize_payouts(payouts)
    except ValueError as e:
        raise ValueError(f"Invalid input format: {str(e)}")

def format_output(values: List[float], currency: str = "$") -> List[str]:
    """Format values for display"""
    return [f"{currency}{v:.2f}" for v in values]
