import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../moneypoly'))

from moneypoly.player import Player
from moneypoly.property import Property, PropertyGroup
from moneypoly.config import STARTING_BALANCE, GO_SALARY, JAIL_POSITION, BOARD_SIZE


class TestInit:

    def test_start_balance(self):
        """Player starts with configured starting balance."""
        p = Player("Alice")
        assert p.balance == STARTING_BALANCE

    def test_custom_balance(self):
        """Player can be created with custom balance."""
        p = Player("Alice", balance=500)
        assert p.balance == 500

    def test_start_pos(self):
        """Player starts at position 0."""
        p = Player("Alice")
        assert p.position == 0

    def test_start_prop(self):
        """Player starts with no properties."""
        p = Player("Alice")
        assert p.properties == []

    def test_not_eliminated(self):
        """Player starts as not eliminated."""
        p = Player("Alice")
        assert p.is_eliminated is False

    def test_jail_dict(self):
        """Jail dictionary must have correct initial values."""
        p = Player("Alice")
        assert p.jail["in_jail"] is False
        assert p.jail["jail_turns"] == 0
        assert p.jail["free_cards"] == 0


class TestAddMoney:

    def test_add_pos(self):
        """positive amount increases balance."""
        p = Player("Alice")
        p.add_money(500)
        assert p.balance == STARTING_BALANCE + 500

    def test_add_zero(self):
        """adding zero changes nothing."""
        p = Player("Alice")
        p.add_money(0)
        assert p.balance == STARTING_BALANCE

    def test_add_neg(self):
        """negative amount must raise ValueError."""
        p = Player("Alice")
        with pytest.raises(ValueError):
            p.add_money(-100)

    def test_add_neg_msg(self):
        """error message mentions the bad amount."""
        p = Player("Alice")
        with pytest.raises(ValueError, match="-100"):
            p.add_money(-100)

    def test_add_large_amount(self):
        """very large amount works correctly."""
        p = Player("Alice")
        p.add_money(999999)
        assert p.balance == STARTING_BALANCE + 999999

    def test_add_multiple(self):
        """multiple additions accumulate."""
        p = Player("Alice")
        p.add_money(100)
        p.add_money(200)
        p.add_money(300)
        assert p.balance == STARTING_BALANCE + 600


class TestDeductMoney:

    def test_deduct_pos(self):
        """reduces balance."""
        p = Player("Alice")
        p.deduct_money(200)
        assert p.balance == STARTING_BALANCE - 200

    def test_deduct_zero(self):
        """deducting zero changes nothing."""
        p = Player("Alice")
        p.deduct_money(0)
        assert p.balance == STARTING_BALANCE

    def test_deduct_neg(self):
        """negative amount must raise ValueError."""
        p = Player("Alice")
        with pytest.raises(ValueError):
            p.deduct_money(-50)

    def test_deduct_entire_balance(self):
        """Edge case: deduct entire balance leaves zero."""
        p = Player("Alice")
        p.deduct_money(STARTING_BALANCE)
        assert p.balance == 0

    def test_deduct_more_than_balance(self):
        """can go negative (bankruptcy)."""
        p = Player("Alice")
        p.deduct_money(STARTING_BALANCE + 100)
        assert p.balance == -100

    def test_deduct_large_amount(self):
        """large deduction works correctly."""
        p = Player("Alice")
        p.deduct_money(999999)
        assert p.balance == STARTING_BALANCE - 999999


class TestIsBankrupt:

    def test_not_bankrupt(self):
        """balance > 0 returns False."""
        p = Player("Alice")
        assert p.is_bankrupt() is False

    def test_bankrupt_zero(self):
        """balance exactly 0 returns True."""
        p = Player("Alice", balance=0)
        assert p.is_bankrupt() is True

    def test_bankrupt_neg(self):
        """negative balance returns True."""
        p = Player("Alice", balance=-1)
        assert p.is_bankrupt() is True

    def test_bankrupt_1(self):
        """Ebalance of 1 returns False."""
        p = Player("Alice", balance=1)
        assert p.is_bankrupt() is False

    def test_becomes_bankrupt_after_deduction(self):
        """player becomes bankrupt after deducting all money."""
        p = Player("Alice", balance=100)
        p.deduct_money(100)
        assert p.is_bankrupt() is True


class TestMove:

    def test_normal_move(self):
        """simple move within board."""
        p = Player("Alice")
        p.position = 5
        p.move(3)
        assert p.position == 8

    def test_move_no_go_salary(self):
        """position != 0, no salary awarded."""
        p = Player("Alice")
        p.position = 5
        p.move(3)
        assert p.balance == STARTING_BALANCE

    def test_move_on_go(self):
        """position == 0, GO salary awarded."""
        p = Player("Alice")
        p.position = 36
        p.move(4)
        assert p.position == 0
        assert p.balance == STARTING_BALANCE + GO_SALARY

    def test_move_passing_go(self):
        """
        BUG TEST — passing Go without landing on it.
        Player at 38 rolls 5, lands on 3, passed position 0.
        """
        p = Player("Alice")
        p.position = 38
        p.move(5)
        assert p.position == 3
        assert p.balance == STARTING_BALANCE + GO_SALARY  

    def test_move_wraparound(self):
        """position wraps correctly at board boundary."""
        p = Player("Alice")
        p.position = 39
        p.move(3)
        assert p.position == 2

    def test_move_returns_new_pos(self):
        """move() returns the new position."""
        p = Player("Alice")
        p.position = 10
        result = p.move(5)
        assert result == 15

    def test_move_from_zero(self):
        """moving from Go position works correctly."""
        p = Player("Alice")
        p.position = 0
        p.move(7)
        assert p.position == 7


class TestNetWorth:

    def test_net_worth(self):
        """no properties, net worth equals balance."""
        p = Player("Alice")
        assert p.net_worth() == STARTING_BALANCE

    def test_net_worth_includes_properties(self):
        """
        BUG TEST — properties must be included in net worth.
        """
        p = Player("Alice")
        g = PropertyGroup("Dark Blue", "dark_blue")
        prop = Property("Boardwalk", 39, (400, 50), group=g)
        prop.state["owner"] = p
        p.add_property(prop)
        assert p.net_worth() == STARTING_BALANCE + 200

    def test_net_worth_multiple_properties(self):
        """
        BUG TEST — multiple properties all counted.
        """
        p = Player("Alice")
        g = PropertyGroup("Brown", "brown")
        prop1 = Property("Mediterranean", 1, (60, 2), group=g)
        prop2 = Property("Baltic", 3, (60, 4), group=g)
        prop1.state["owner"] = p
        prop2.state["owner"] = p
        p.add_property(prop1)
        p.add_property(prop2)
        assert p.net_worth() == STARTING_BALANCE + 60

    def test_net_worth_after_balance_change(self):
        """net worth reflects current balance."""
        p = Player("Alice")
        p.add_money(500)
        assert p.net_worth() == STARTING_BALANCE + 500


class TestGoToJail:

    def test_go_to_jail(self):
        """go_to_jail must move player to JAIL_POSITION."""
        p = Player("Alice")
        p.go_to_jail()
        assert p.position == JAIL_POSITION

    def test_go_to_jail_flag(self):
        """go_to_jail must set jail dict in_jail to True."""
        p = Player("Alice")
        p.go_to_jail()
        assert p.jail["in_jail"] is True

    def test_go_to_jail_resets_jail_turns(self):
        """go_to_jail must reset jail_turns to 0."""
        p = Player("Alice")
        p.jail["jail_turns"] = 2
        p.go_to_jail()
        assert p.jail["jail_turns"] == 0

    def test_go_to_jail_from_any_position(self):
        """go_to_jail works from any position."""
        p = Player("Alice")
        p.position = 35
        p.go_to_jail()
        assert p.position == JAIL_POSITION

    def test_go_to_jail_does_not_affect_balance(self):
        """go_to_jail must not change player balance."""
        p = Player("Alice")
        p.go_to_jail()
        assert p.balance == STARTING_BALANCE


class TestAddProperty:

    def test_add_property_append(self):
        """property added to holdings."""
        p = Player("Alice")
        g = PropertyGroup("Brown", "brown")
        prop = Property("Mediterranean", 1, (60, 2), group=g)
        p.add_property(prop)
        assert prop in p.properties

    def test_add_property_no_duplicates(self):
        """
        prop already in list, not added again.
        """
        p = Player("Alice")
        g = PropertyGroup("Brown", "brown")
        prop = Property("Mediterranean", 1, (60, 2), group=g)
        p.add_property(prop)
        p.add_property(prop)
        assert len(p.properties) == 1

    def test_add_multiple_properties(self):
        """multiple different properties all added."""
        p = Player("Alice")
        g = PropertyGroup("Brown", "brown")
        prop1 = Property("Mediterranean", 1, (60, 2), group=g)
        prop2 = Property("Baltic", 3, (60, 4), group=g)
        p.add_property(prop1)
        p.add_property(prop2)
        assert len(p.properties) == 2


class TestRemoveProperty:

    def test_remove_existing_property(self):
        """prop in list, gets removed."""
        p = Player("Alice")
        g = PropertyGroup("Brown", "brown")
        prop = Property("Mediterranean", 1, (60, 2), group=g)
        p.add_property(prop)
        p.remove_property(prop)
        assert prop not in p.properties

    def test_remove_nonexistent_prop(self):
        """
        prop not in list, nothing happens (no error).
        """
        p = Player("Alice")
        g = PropertyGroup("Brown", "brown")
        prop = Property("Mediterranean", 1, (60, 2), group=g)
        p.remove_property(prop)  # should not raise
        assert len(p.properties) == 0

    def test_remove_leaves_others(self):
        """removing one property leaves others."""
        p = Player("Alice")
        g = PropertyGroup("Brown", "brown")
        prop1 = Property("Mediterranean", 1, (60, 2), group=g)
        prop2 = Property("Baltic", 3, (60, 4), group=g)
        p.add_property(prop1)
        p.add_property(prop2)
        p.remove_property(prop1)
        assert prop1 not in p.properties
        assert prop2 in p.properties


class TestCountProperties:

    def test_count_zero_at_start(self):
        """no properties, count is 0."""
        p = Player("Alice")
        assert p.count_properties() == 0

    def test_count_after_adding(self):
        """count reflects number of properties."""
        p = Player("Alice")
        g = PropertyGroup("Brown", "brown")
        prop1 = Property("Mediterranean", 1, (60, 2), group=g)
        prop2 = Property("Baltic", 3, (60, 4), group=g)
        p.add_property(prop1)
        p.add_property(prop2)
        assert p.count_properties() == 2

    def test_count_after_removing(self):
        """Ncount decreases after removal."""
        p = Player("Alice")
        g = PropertyGroup("Brown", "brown")
        prop = Property("Mediterranean", 1, (60, 2), group=g)
        p.add_property(prop)
        p.remove_property(prop)
        assert p.count_properties() == 0


class TestStatusLine:

    def test_status_line_not_jailed(self):
        """not in jail, no JAILED tag in output."""
        p = Player("Alice")
        line = p.status_line()
        assert "[JAILED]" not in line

    def test_status_line_jailed(self):
        """in jail, JAILED tag appears in output."""
        p = Player("Alice")
        p.jail["in_jail"] = True
        line = p.status_line()
        assert "[JAILED]" in line

    def test_status_line_contains_name(self):
        """status line includes player name."""
        p = Player("Alice")
        assert "Alice" in p.status_line()

    def test_status_line_contains_balance(self):
        """status line includes balance."""
        p = Player("Alice")
        assert str(STARTING_BALANCE) in p.status_line()

    def test_status_line_contains_position(self):
        """tatus line includes position."""
        p = Player("Alice")
        p.position = 15
        assert "15" in p.status_line()