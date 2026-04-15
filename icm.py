"""ICM (Independent Chip Model) calculation module"""
from typing import List, Tuple, Dict

PRECISION = 10  # Decimal places for rounding

def round_chips(value: float) -> float:
    """Round to specified precision"""
    return round(value, PRECISION)

def calculate_icm(stacks: List[float], payouts: List[float]) -> List[float]:
    """
    Calculate ICM (Independent Chip Model) equity using recursive algorithm with memoization.
    
    Args:
        stacks: List of chip stacks for each player (order preserved)
        payouts: List of payouts in descending order
    
    Returns:
        List of ICM values for each player (same order as input stacks)
    """
    n_players = len(stacks)
    
    memo: Dict[Tuple[Tuple[float, ...], Tuple[float, ...]], List[float]] = {}
    
    def icm_recursive(remaining_stacks: Tuple[float, ...], 
                     remaining_payouts: Tuple[float, ...]) -> List[float]:
        """
        Recursive ICM calculation with memoization.
        
        For each player position i, calculate EV as:
        EV[i] = (chips[i] / total_chips) × payout[0] + 
                (1 - chips[i] / total_chips) × avg(ICM of others on remaining payouts)
        """
        key = (remaining_stacks, remaining_payouts)
        if key in memo:
            return memo[key]
        
        n = len(remaining_stacks)
        total = sum(remaining_stacks)
        
        # Base case: only one player
        if n == 1:
            result = [remaining_payouts[0]]
        
        # Base case: only two players
        elif n == 2:
            s1, s2 = remaining_stacks
            p1, p2 = remaining_payouts
            
            # Player 1: wins with probability s1/total, gets p1
            #           loses with probability s2/total, gets p2
            ev1 = (s1 / total) * p1 + (s2 / total) * p2
            
            # Player 2: opposite
            ev2 = (s2 / total) * p1 + (s1 / total) * p2
            
            result = [round_chips(ev1), round_chips(ev2)]
        
        else:
            # General case: calculate EV for each player
            result = []
            
            for i in range(n):
                chip_equity = remaining_stacks[i] / total
                
                # If player i wins this position
                win_value = remaining_payouts[0]
                
                # If player i doesn't win, calculate EV of others
                remaining_stacks_without_i = tuple(
                    remaining_stacks[j] for j in range(n) if j != i
                )
                remaining_payouts_without_first = remaining_payouts[1:]
                
                # Recursively calculate for remaining players
                if remaining_stacks_without_i and remaining_payouts_without_first:
                    others_evs = icm_recursive(remaining_stacks_without_i, 
                                              remaining_payouts_without_first)
                    lose_value = sum(others_evs) / len(others_evs)
                else:
                    lose_value = 0.0
                
                # Expected value
                ev = chip_equity * win_value + (1 - chip_equity) * lose_value
                result.append(round_chips(ev))
        
        memo[key] = result
        return result
    
    # Run the recursive calculation on all players
    icm_values = icm_recursive(tuple(stacks), tuple(payouts))
    
    return icm_values
