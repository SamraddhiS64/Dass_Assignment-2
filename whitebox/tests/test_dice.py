import sys
import os
import pytest
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../moneypoly'))

from moneypoly.dice import Dice


class TestDiceInit:

    def test_initial_zero(self):
        """Both dice start at 0 before any roll."""
        d = Dice()
        assert d.die1 == 0
        assert d.die2 == 0

    def test_initial_streak(self):
        """doubles_streak starts at 0 before any roll."""
        d = Dice()
        assert d.doubles_streak == 0


class TestReset:

    def test_reset(self):
        """After reset, die1 is 0."""
        d = Dice()
        d.die1 = 5
        d.die2 = 4
        d.reset()
        assert d.die1 == 0
        assert d.die2 == 0

    def test_reset_streak(self):
        """After reset, doubles_streak is 0."""
        d = Dice()
        d.doubles_streak = 3
        d.reset()
        assert d.doubles_streak == 0


class TestRoll:

    def test_roll(self):
        """roll() must return an integer."""
        d = Dice()
        result = d.roll()
        assert isinstance(result, int)

    def test_roll_total(self):
        """roll() return value must equal die1 + die2."""
        d = Dice()
        result = d.roll()
        assert result == d.die1 + d.die2

    def test_roll_range(self):
        """
        BUG TEST — each die must produce values 1 to 6.
        Current code uses randint(1, 5) so 6 is never possible.
        """
        d = Dice()
        values_seen = set()
        for _ in range(1000):
            d.roll()
            values_seen.add(d.die1)
            values_seen.add(d.die2)
        assert 6 in values_seen  

    def test_roll_minimum(self):
        """minimum possible roll is 2 (both dice show 1)."""
        d = Dice()
        for _ in range(200):
            result = d.roll()
            assert result >= 2

    def test_roll_maximum(self):
        """
        BUG TEST — maximum roll must be 12 (both dice show 6).
        """
        d = Dice()
        results = set()
        for _ in range(10000):
            results.add(d.roll())
        assert 12 in results  

    def test_roll_updates_die1(self):
        """After rolling, dies must be between 1 and 6."""
        d = Dice()
        d.roll()
        assert 1 <= d.die1 <= 6
        assert 1 <= d.die2 <= 6

    def test_roll_doubles_inc(self):
        """
        is_doubles() True, streak must increment.
        Use mock to force doubles (both dice = 4).
        """
        d = Dice()
        with patch('random.randint', return_value=4):
            d.roll()
        assert d.doubles_streak == 1

    def test_roll_consec_inc(self):
        """
        multiple doubles in a row
        """
        d = Dice()
        with patch('random.randint', return_value=3):
            d.roll()
            d.roll()
            d.roll()
        assert d.doubles_streak == 3

    def test_roll_doubles_resets(self):
        """
        is_doubles() False, streak resets to 0.
        """
        d = Dice()
        with patch('random.randint', return_value=4):
            d.roll()
        assert d.doubles_streak == 1
        d.die1 = 2
        d.die2 = 5
        with patch('moneypoly.dice.random.randint', side_effect=[2, 5]):
            d.roll()
        assert d.doubles_streak == 0

    def test_roll_streak_resets_after_non_doubles(self):
        """
        non-doubles after a streak resets to 0 not decrements.
        """
        d = Dice()
        d.doubles_streak = 5
        with patch('moneypoly.dice.random.randint', side_effect=[1, 2]):
            d.roll()
        assert d.doubles_streak == 0


class TestIsDoubles:

    def test_is_doubles(self):
        """die1 == die2 returns True."""
        d = Dice()
        d.die1 = 4
        d.die2 = 4
        assert d.is_doubles() is True

    def test_is_doubles_false(self):
        """die1 != die2 returns False."""
        d = Dice()
        d.die1 = 3
        d.die2 = 5
        assert d.is_doubles() is False

    def test_is_doubles_all_values(self):
        """every matching pair (1,1) through (6,6) is doubles."""
        d = Dice()
        for value in range(1, 7):
            d.die1 = value
            d.die2 = value
            assert d.is_doubles() is True


class TestTotal:

    def test_total(self):
        """total is die1 + die2."""
        d = Dice()
        d.die1 = 3
        d.die2 = 4
        assert d.total() == 7

    def test_total_minimum(self):
        """minimum total is 2 """
        d = Dice()
        d.die1 = 1
        d.die2 = 1
        assert d.total() == 2

    def test_total_maximum(self):
        """maximum total is 12 (6 + 6)."""
        d = Dice()
        d.die1 = 6
        d.die2 = 6
        assert d.total() == 12

    def test_total_zero_before_roll(self):
        """total is 0 before any roll."""
        d = Dice()
        assert d.total() == 0


class TestDescribe:

    def test_describe(self):
        """describe shows individual die values and includes the total."""
        d = Dice()
        d.die1 = 3
        d.die2 = 4
        result = d.describe()
        assert "3" in result
        assert "4" in result
        assert "7" in result        

    def test_describe_doubles_note(self):
        """
        is_doubles() True, describe includes DOUBLES note.
        """
        d = Dice()
        d.die1 = 4
        d.die2 = 4
        result = d.describe()
        assert "DOUBLES" in result

    def test_describe_no_note(self):
        """
        is_doubles() False, no DOUBLES in description.
        """
        d = Dice()
        d.die1 = 2
        d.die2 = 5
        result = d.describe()
        assert "DOUBLES" not in result

    def test_describe_format(self):
        """output follows expected format."""
        d = Dice()
        d.die1 = 2
        d.die2 = 3
        result = d.describe()
        assert "2 + 3 = 5" in result