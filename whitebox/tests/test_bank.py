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