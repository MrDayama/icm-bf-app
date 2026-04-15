"""Bubble Factor calculation module"""
from typing import List
from icm import calculate_icm, round_chips

def calculate_bubble_factor(stacks: List[float], payouts: List[float]) -> List[float]:
    """
    Calculate Bubble Factor for each player.
    
    Bubble Factor measures the ratio of the payout variance relative to chip equity.
    BF = (Top Prize - ICM EV) / ICM EV
    
    Where:
    - Top Prize: First place payout
    - ICM EV: Independent Chip Model expected value
    
    Interpretation:
    - BF > 0: Player is incentivized to win (high variance opportunity)
    - BF < 0: Player would prefer chip chop (high risk)
    - BF = 0: Top prize equals ICM value
    
    Args:
        stacks: List of chip stacks for each player
        payouts: List of payouts in descending order
    
    Returns:
        List of Bubble Factor values for each player
    """
    n_players = len(stacks)
    
    # Calculate ICM baselines
    icm_values = calculate_icm(stacks, payouts)
    
    # Bubble Factor calculation
    bubble_factors = []
    first_prize = payouts[0]
    
    for i in range(n_players):
        icm_ev = icm_values[i]
        
        if icm_ev > 0:
            # BF = (1st place prize - ICM EV) / ICM EV
            bf = (first_prize - icm_ev) / icm_ev
        else:
            bf = 0.0
        
        bubble_factors.append(round_chips(bf))
    
    return bubble_factors
