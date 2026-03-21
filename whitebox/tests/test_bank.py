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
        """Normal case, increases bank funds"""
        b = Bank()
        initial = b.get_balance()
        b.collect(500)
        assert b.get_balance() == initial + 500

    def test_collect_zero(self):
        """Edge case, balance unchanged"""
        b = Bank()
        initial = b.get_balance()
        b.collect(0)
        assert b.get_balance() == initial

    def test_collect_negative(self):
        """ BUG TEST — docstring says negative amounts are silently ignored
        but code does self._funds += amount which reduces funds
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

class TestPayOut:

    def test_pay_out_normal(self):
        """Sufficient funds, returns amount paid"""
        b = Bank()
        initial = b.get_balance()
        result = b.pay_out(200)
        assert result == 200
        assert b.get_balance() == initial - 200

    def test_pay_out_zero(self):
        """amount == 0, returns 0, funds unchanged"""
        b = Bank()
        initial = b.get_balance()
        result = b.pay_out(0)
        assert result == 0
        assert b.get_balance() == initial

    def test_pay_out_negative(self):
        """Branch: negative amount, returns 0, funds unchanged."""
        b = Bank()
        initial = b.get_balance()
        result = b.pay_out(-50)
        assert result == 0
        assert b.get_balance() == initial

    def test_pay_out_exactly_all_funds(self):
        """Edge case, pay out exactly all funds, balance becomes 0."""
        b = Bank()
        total = b.get_balance()
        result = b.pay_out(total)
        assert result == total
        assert b.get_balance() == 0

    def test_pay_out_insufficient_funds_raises(self):
        """Branch: amount > funds raises ValueError."""
        b = Bank()
        with pytest.raises(ValueError):
            b.pay_out(9999999)

    def test_pay_out_one_over_balance_raises(self):
        """Edge case, exactly one dollar over balance raises ValueError."""
        b = Bank()
        total = b.get_balance()
        with pytest.raises(ValueError):
            b.pay_out(total + 1)

class TestGiveLoan:

    def test_give_loan_normal(self):
        """player balance increases by loan amount.
        BUG TEST — docstring says bank funds are reduced accordingly
        but code never does self._funds -= amount.
        """
        b = Bank()
        p = Player("Bob")
        intial_player = p.balance
        initial_bank = b.get_balance()
        b.give_loan(p, 500)
        assert p.balance == intial_player + 500
        assert b.get_balance() == initial_bank - 500

    def test_give_loan_records(self):
        """loan is recorded in the loans list."""
        b = Bank()
        p = Player("Bob")
        b.give_loan(p, 300)
        assert b.loan_count() == 1
        assert b.total_loans_issued() == 300

    def test_give_loan_zero(self):
        """amount == 0, nothing happens."""
        b = Bank()
        p = Player("Bob")
        initial_player = p.balance
        initial_bank = b.get_balance()
        b.give_loan(p, 0)
        assert p.balance == initial_player
        assert b.get_balance() == initial_bank
        assert b.loan_count() == 0

    def test_give_loan_negative(self):
        """negative amount, nothing happens."""
        b = Bank()
        p = Player("Bob")
        initial_player = p.balance
        b.give_loan(p, -200)
        assert p.balance == initial_player
        assert b.loan_count() == 0

    def test_give_loan_multiple_loans(self):
        """Edge case, multiple loans all tracked correctly."""
        b = Bank()
        p1 = Player("Alice")
        p2 = Player("Bob")
        b.give_loan(p1, 200)
        b.give_loan(p2, 300)
        assert b.loan_count() == 2
        assert b.total_loans_issued() == 500
