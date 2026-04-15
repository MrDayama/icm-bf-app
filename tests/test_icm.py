"""Test suite for ICM and Bubble Factor calculations"""
import unittest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from icm import calculate_icm, round_chips
from bf import calculate_bubble_factor
from models import CalculationInput

class TestICM(unittest.TestCase):
    """Test ICM calculations"""
    
    def test_two_player_equal_stacks(self):
        """Test 2 players with equal stacks"""
        stacks = [100, 100]
        payouts = [100, 50]
        
        icm = calculate_icm(stacks, payouts)
        
        # Both should have equal ICM value: 75
        self.assertAlmostEqual(icm[0], 75, places=1)
        self.assertAlmostEqual(icm[1], 75, places=1)
        
        # Total should equal payout total
        self.assertAlmostEqual(sum(icm), sum(payouts), places=1)
    
    def test_three_player_example(self):
        """Test 3-player SNG (common scenario)"""
        stacks = [50, 30, 20]
        payouts = [50, 30, 20]
        
        icm = calculate_icm(stacks, payouts)
        
        # Larger stack should have higher ICM value
        self.assertGreater(icm[0], icm[1])
        self.assertGreater(icm[1], icm[2])
        
        # Total should equal payout total
        self.assertAlmostEqual(sum(icm), sum(payouts), places=1)
    
    def test_chip_equity_matches_single_payout(self):
        """Test that equal stacks give equal ICM"""
        stacks = [100, 100, 100]
        payouts = [150, 100, 50]
        
        icm = calculate_icm(stacks, payouts)
        
        # All should be equal
        self.assertAlmostEqual(icm[0], icm[1], places=1)
        self.assertAlmostEqual(icm[1], icm[2], places=1)
        self.assertAlmostEqual(icm[0], 100, places=1)
    
    def test_uneven_stacks_distribution(self):
        """Test distribution with uneven stacks"""
        stacks = [100, 50, 25]
        payouts = [100, 60, 40]
        
        icm = calculate_icm(stacks, payouts)
        
        # Verify total matches
        self.assertAlmostEqual(sum(icm), sum(payouts), places=1)
        
        # Verify chip equity order
        self.assertGreater(icm[0], icm[1])
        self.assertGreater(icm[1], icm[2])
    
    def test_total_preservation(self):
        """Test that total value is preserved"""
        test_cases = [
            ([100, 100], [100, 50]),
            ([50, 30, 20], [50, 30, 20]),
            ([100, 80, 60, 40], [100, 70, 40, 10]),
        ]
        
        for stacks, payouts in test_cases:
            with self.subTest(stacks=stacks, payouts=payouts):
                icm = calculate_icm(stacks, payouts)
                self.assertAlmostEqual(sum(icm), sum(payouts), places=1)
    
    def test_zero_stack_handling(self):
        """Test handling of zero stacks"""
        stacks = [100, 0, 50]
        payouts = [100, 50, 25]
        
        icm = calculate_icm(stacks, payouts)
        
        # Player with 0 chips gets no equity, contributes 0 to ICM
        # But gets distributed from others' equity
        self.assertGreaterEqual(icm[1], 0)
        # ICM sum should still equal payout total
        self.assertAlmostEqual(sum(icm), sum(payouts), places=1)
    
    def test_large_chip_difference(self):
        """Test with large difference between chip stacks"""
        stacks = [1000, 10, 1]
        payouts = [1000, 5, 1]
        
        icm = calculate_icm(stacks, payouts)
        
        # First player should dominate
        self.assertGreater(icm[0], icm[1])
        self.assertGreater(icm[1], icm[2])

class TestBubbleFactor(unittest.TestCase):
    """Test Bubble Factor calculations (per-opponent BF_j)"""

    def test_bubble_factor_structure_and_nonnegative(self):
        stacks = [100, 50]
        payouts = [100, 25]

        bf_list = calculate_bubble_factor(stacks, payouts)

        # Structure check
        self.assertIsInstance(bf_list, list)
        self.assertEqual(len(bf_list), 2)

        for entry in bf_list:
            self.assertIn('player', entry)
            self.assertIn('vs_opponents', entry)
            self.assertIn('average_bf', entry)
            # Each vs_opponent should have bf numeric or inf
            for op in entry['vs_opponents']:
                self.assertIn('opponent', op)
                self.assertIn('bf', op)
                self.assertIn('ev_gain', op)
                self.assertIn('ev_loss', op)
                self.assertTrue(isinstance(op['bf'], float) or op['bf'] == float('inf'))
                self.assertTrue(isinstance(op['ev_gain'], float) or isinstance(op['ev_gain'], int))
                self.assertTrue(isinstance(op['ev_loss'], float) or isinstance(op['ev_loss'], int))
                # Non-negative
                if op['bf'] != float('inf'):
                    self.assertGreaterEqual(op['bf'], 0.0)

    def test_equal_stacks_equal_bf(self):
        stacks = [100, 100]
        payouts = [100, 50]

        bf_list = calculate_bubble_factor(stacks, payouts)

        # Each player has single opponent; values should be symmetric
        bf_p1 = bf_list[0]['vs_opponents'][0]['bf']
        bf_p2 = bf_list[1]['vs_opponents'][0]['bf']
        self.assertAlmostEqual(bf_p1, bf_p2, places=2)

    def test_bubble_factor_consistency(self):
        stacks = [50, 30, 20]
        payouts = [50, 30, 20]

        bf_list = calculate_bubble_factor(stacks, payouts)

        # All entries present and average_bf numeric
        for entry in bf_list:
            self.assertIsInstance(entry['average_bf'], float)
            self.assertEqual(len(entry['vs_opponents']), 2)
            for op in entry['vs_opponents']:
                self.assertTrue(isinstance(op['bf'], float) or op['bf'] == float('inf'))

class TestValidation(unittest.TestCase):
    """Test input validation"""

    def test_valid_input(self):
        """Test valid input passes validation"""
        calc = CalculationInput(
            players=3,
            stacks=[100, 50, 25],
            payouts=[100, 50, 25]
        )
        is_valid, _ = calc.validate()
        self.assertTrue(is_valid)

    def test_invalid_player_count(self):
        """Test invalid player count"""
        calc = CalculationInput(
            players=10,
            stacks=[100, 50, 25],
            payouts=[100, 50, 25]
        )
        is_valid, _ = calc.validate()
        self.assertFalse(is_valid)

    def test_mismatched_stacks_count(self):
        """Test mismatched stacks count"""
        calc = CalculationInput(
            players=3,
            stacks=[100, 50],
            payouts=[100, 50, 25]
        )
        is_valid, _ = calc.validate()
        self.assertFalse(is_valid)

    def test_negative_stacks(self):
        """Test negative stacks"""
        calc = CalculationInput(
            players=2,
            stacks=[-100, 50],
            payouts=[100, 50]
        )
        is_valid, _ = calc.validate()
        self.assertFalse(is_valid)

    def test_unsorted_payouts(self):
        """Test unsorted payouts"""
        calc = CalculationInput(
            players=3,
            stacks=[100, 50, 25],
            payouts=[50, 100, 25]  # Not sorted
        )
        is_valid, _ = calc.validate()
        self.assertFalse(is_valid)


class TestBFScenarios(unittest.TestCase):
    """Additional BF scenario tests requested"""

    def test_case1_survival_on_loss(self):
        # Case 1: [100, 50] -> large side survives when losing
        stacks = [100, 50]
        payouts = [100, 25]
        icm_baseline = calculate_icm(stacks, payouts)

        effective = min(stacks[0], stacks[1])
        stacks_lose = stacks.copy()
        stacks_lose[0] = stacks_lose[0] - effective
        if stacks_lose[0] < 0:
            stacks_lose[0] = 0.0

        icm_lose = calculate_icm(stacks_lose, payouts)[0]
        # Ensure leader still has positive ICM after loss
        self.assertGreater(icm_lose, 0.0)

    def test_case2_equal_stacks(self):
        stacks = [100, 100]
        payouts = [100, 50]
        bf_list = calculate_bubble_factor(stacks, payouts)

        bf_p1 = bf_list[0]['vs_opponents'][0]['bf']
        bf_p2 = bf_list[1]['vs_opponents'][0]['bf']
        self.assertAlmostEqual(bf_p1, bf_p2, places=2)

    def test_case3_leader_bf_reasonable(self):
        stacks = [80, 15, 5]
        payouts = [100, 10, 5]
        bf_list = calculate_bubble_factor(stacks, payouts)

        leader_vs = bf_list[0]['vs_opponents']
        for op in leader_vs:
            self.assertTrue(op['bf'] == float('inf') or (isinstance(op['bf'], float) and op['bf'] < 100))

if __name__ == '__main__':
    unittest.main(verbosity=2)
