"""Bubble Factor calculation module"""
from typing import List
from icm import calculate_icm, round_chips

def calculate_bubble_factor(stacks: List[float], payouts: List[float]) -> List[float]:
    """
    Calculate Bubble Factor for each player.

    New definition:
    BF = (ICM_loss_if_lose) / (ICM_gain_if_win)

    Implementation (pairwise average): for each player i, simulate
    - Win vs each opponent j: transfer opponent j's stack to player i (j eliminated) and recompute ICM
    - Lose vs each opponent j: set player i's stack to 0 (i eliminated) and recompute ICM
    Then per-opponent BF_j = (ICM_i - ICM_i_if_lose) / (ICM_i_if_win - ICM_i)
    and BF for player i is the average of BF_j across all opponents.

    Args:
        stacks: List of chip stacks for each player
        payouts: List of payouts in descending order

    Returns:
        List of Bubble Factor multipliers (floats). Values are rounded to 2 decimals for display.
        If division by zero occurs (no gain), returns float('inf') for that opponent and propagated.
    """
    n_players = len(stacks)
    icm_values = calculate_icm(stacks, payouts)

    bubble_factors: List[float] = []

    for i in range(n_players):
        per_opponent_bfs: List[float] = []

        for j in range(n_players):
            if i == j:
                continue

            # Win scenario: i gains j's stack, j eliminated
            stacks_win = stacks.copy()
            stacks_win[i] = stacks_win[i] + stacks_win[j]
            stacks_win[j] = 0.0

            # Lose scenario: i eliminated
            stacks_lose = stacks.copy()
            stacks_lose[i] = 0.0

            icm_win = calculate_icm(stacks_win, payouts)[i]
            icm_lose = calculate_icm(stacks_lose, payouts)[i]

            ev_gain = icm_win - icm_values[i]
            ev_loss = icm_values[i] - icm_lose

            # Safety epsilon to avoid floating noise
            eps = 1e-12
            if ev_gain <= eps:
                # If there is no gain but there is loss, define as infinite sensitivity
                if ev_loss > eps:
                    per_opponent_bfs.append(float('inf'))
                else:
                    # Both gain and loss are ~0, treat as neutral (1.0)
                    per_opponent_bfs.append(1.0)
            else:
                per_opponent_bfs.append(ev_loss / ev_gain)

        # Aggregate: if any opponent produced infinity, set BF to infinity
        if any((b == float('inf')) for b in per_opponent_bfs):
            bf_value = float('inf')
        elif len(per_opponent_bfs) == 0:
            bf_value = 1.0
        else:
            bf_value = sum(per_opponent_bfs) / len(per_opponent_bfs)

        # Round to 2 decimals for display consistency
        if bf_value != float('inf'):
            bf_value = round(bf_value, 2)

        bubble_factors.append(bf_value)

    return bubble_factors
