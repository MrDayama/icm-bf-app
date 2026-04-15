"""Bubble Factor calculation module (per-opponent BF_j)"""
from typing import List, Dict, Any
from icm import calculate_icm


def calculate_bubble_factor(stacks: List[float], payouts: List[float]) -> List[Dict[str, Any]]:
    """
    Calculate Bubble Factor per player against each opponent using stack-transfer model.

    Rules:
    - effective_stack = min(stack_i, stack_j)
    - Win: i gains effective_stack, j loses effective_stack
    - Lose: i loses effective_stack, j gains effective_stack
      (if stack_i <= stack_j, i may become 0)

    Returns a list where each element corresponds to a player and contains:
    {
        'player': 'P1',
        'vs_opponents': [ {'opponent': 'P2', 'bf': 1.23}, ... ],
        'average_bf': 1.23  # optional reference (average of finite BF_j)
    }
    """
    n_players = len(stacks)
    icm_baseline = calculate_icm(stacks, payouts)

    results: List[Dict[str, Any]] = []

    for i in range(n_players):
        player_label = f'P{i+1}'
        vs_list: List[Dict[str, Any]] = []
        bfs: List[float] = []

        for j in range(n_players):
            if i == j:
                continue

            # effective stack transfer
            effective = min(stacks[i], stacks[j])

            # Win scenario: i gains, j loses
            stacks_win = stacks.copy()
            stacks_win[i] = stacks_win[i] + effective
            stacks_win[j] = stacks_win[j] - effective

            # Lose scenario: i loses, j gains
            stacks_lose = stacks.copy()
            stacks_lose[i] = stacks_lose[i] - effective
            stacks_lose[j] = stacks_lose[j] + effective

            # Normalize negatives to zero
            if stacks_win[j] < 0:
                stacks_win[j] = 0.0
            if stacks_lose[i] < 0:
                stacks_lose[i] = 0.0

            icm_win = calculate_icm(stacks_win, payouts)[i]
            icm_lose = calculate_icm(stacks_lose, payouts)[i]

            ev_gain = icm_win - icm_baseline[i]
            ev_loss = icm_baseline[i] - icm_lose

            eps = 1e-12
            reason = ''
            if ev_gain <= eps:
                if ev_loss > eps:
                    bf_val = float('inf')
                    reason = 'EV_gain=0'
                else:
                    bf_val = 1.0
                    reason = 'neutral'
            else:
                bf_val = ev_loss / ev_gain

            display_val = float('inf') if bf_val == float('inf') else round(bf_val, 2)

            vs_list.append({
                'opponent': f'P{j+1}',
                'bf': display_val,
                'ev_gain': round(ev_gain, 4),
                'ev_loss': round(ev_loss, 4),
                'reason': reason
            })

            if display_val != float('inf'):
                bfs.append(display_val)

        # Compute average over finite bfs if any
        if len(bfs) == 0:
            average = float('inf') if any(v['bf'] == float('inf') for v in vs_list) else 1.0
        else:
            average = round(sum(bfs) / len(bfs), 2)

        results.append({
            'player': player_label,
            'vs_opponents': vs_list,
            'average_bf': average
        })

    return results
