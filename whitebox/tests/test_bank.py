import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../moneypoly'))

from moneypoly.bank import Bank
from moneypoly.player import Player
from moneypoly.config import BANK_STARTING_FUNDS

class TestGetBalance:

    def test_initial_balance_is_correct(self):
        """checking starting funds"""
        b = Bank()
        assert b.get_balance() == BANK_STARTING_FUNDS

    def test_balance_reflects_changes(self):
        """Balance updating checks"""
        b = Bank()
        b.collect(1000)
        assert b.get_balance() == BANK_STARTING_FUNDS + 1000

class TestCollect:

    def test_collect_positive(self):
        """Normal case, increases bank funds."""
        b = Bank()
        initial = b.get_balance()
        b.collect(500)
        assert b.get_balance() == initial + 500

    def test_collect_zero(self):
        """Edge case, balance unchanged."""
        b = Bank()
        initial = b.get_balance()
        b.collect(0)
        assert b.get_balance() == initial

    def test_collect_negative(self):
        """ BUG TEST — docstring says negative amounts are silently ignored
        but code does self._funds += amount which reduces funds.
        """
        b = Bank()
        initial = b.get_balance()
        b.collect(-100)
        assert b.get_balance() == initial

    def test_collect_large_amount(self):
        """Edge case, very large amount"""
        b = Bank()
        initial = b.get_balance()
        b.collect(999999)
        assert b.get_balance() == initial + 999999