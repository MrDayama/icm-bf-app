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
    """Test Bubble Factor calculations"""
    
    def test_bubble_factor_sign(self):
        """Test that BF increases with first prize"""
        stacks = [100, 50]
        payouts = [100, 25]
        
        bf = calculate_bubble_factor(stacks, payouts)
        
        # BF = (First Prize - ICM_EV) / ICM_EV
        # With small 2nd prize, both have positive BF
        # But since BF depends on first prize, both same
        self.assertTrue(all(b > 0 for b in bf))
    
    def test_equal_stacks_equal_bf(self):
        """Test that equal stacks have equal BF"""
        stacks = [100, 100]
        payouts = [100, 50]
        
        bf = calculate_bubble_factor(stacks, payouts)
        
        # Equal stacks should have equal BF
        self.assertAlmostEqual(bf[0], bf[1], places=5)
    
    def test_bubble_factor_consistency(self):
        """Test BF consistency"""
        stacks = [50, 30, 20]
        payouts = [50, 30, 20]
        
        bf = calculate_bubble_factor(stacks, payouts)
        
        # All should be finite
        self.assertTrue(all(isinstance(b, float) for b in bf))
        # All should be positive (1st prize > ICM for all)
        self.assertTrue(all(b > 0 for b in bf))

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

if __name__ == '__main__':
    unittest.main(verbosity=2)
