import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../moneypoly'))

from moneypoly.property import Property, PropertyGroup
from moneypoly.player import Player

# helpers

def make_property(name="Test", position=1, price=100, rent=10, group=None):
    """create a Property with pricing tuple."""
    return Property(name, position, (price, rent), group)


def make_group(name="Brown", color="brown"):
    """create a PropertyGroup."""
    return PropertyGroup(name, color)


class TestPropertyInit:

    def test_price_set_from_pricing_tuple(self):
        """price is pricing[0]."""
        prop = make_property(price=200)
        assert prop.price == 200

    def test_base_rent_set_from_pricing_tuple(self):
        """base_rent is pricing[1]."""
        prop = make_property(rent=25)
        assert prop.base_rent == 25

    def test_mortgage_value_is_half_price(self):
        """mortgage_value = price // 2."""
        prop = make_property(price=200)
        assert prop.mortgage_value == 100

    def test_mortgage_value_floors_odd_price(self):
        """Edge case, odd price floors correctly."""
        prop = make_property(price=61)
        assert prop.mortgage_value == 30

    def test_state_owner_starts_none(self):
        """Owner must start as None."""
        prop = make_property()
        assert prop.state["owner"] is None

    def test_state_mortgaged_starts_false(self):
        """is_mortgaged must start as False."""
        prop = make_property()
        assert prop.state["is_mortgaged"] is False

    def test_state_houses_starts_zero(self):
        """houses must start at 0."""
        prop = make_property()
        assert prop.state["houses"] == 0

    def test_registered_with_group_on_creation(self):
        """
        group is not None.
        Property must register itself with its group during init.
        """
        g = make_group()
        prop = make_property(group=g)
        assert prop in g.properties

    def test_not_registered_twice_in_group(self):
        """
        Edge case, creating same property does not duplicate in group.
        """
        g = make_group()
        prop = make_property(group=g)
        assert g.properties.count(prop) == 1

    def test_no_group_is_fine(self):
        """
        group is None, no registration attempted.
        """
        prop = make_property(group=None)
        assert prop.group is None


class TestGetRent:

    def test_mortgaged_returns_zero(self):
        """
        is_mortgaged = True, returns 0 immediately.
        No rent charged on mortgaged property.
        """
        prop = make_property(rent=10)
        prop.state["is_mortgaged"] = True
        assert prop.get_rent() == 0

    def test_no_group_returns_base_rent(self):
        """
        group is None, no multiplier possible.
        Returns base rent directly.
        """
        prop = make_property(rent=10, group=None)
        assert prop.get_rent() == 10

    def test_partial_group_returns_base_rent(self):
        """
        player owns only ONE of two properties.
        Expected: base rent (no doubling).

        BUG: all_owned_by uses any() so currently returns doubled rent.
        """
        g = make_group()
        p1 = Property("Prop1", 1, (100, 10), g)
        p2 = Property("Prop2", 3, (100, 10), g)
        alice = Player("Alice")
        bob = Player("Bob")
        p1.state["owner"] = alice
        p2.state["owner"] = bob
        assert p1.get_rent() == 10

    def test_full_group_doubles_rent(self):
        """
        player owns ALL properties in group.
        Rent must be doubled.
        """
        g = make_group()
        p1 = Property("Prop1", 1, (100, 10), g)
        p2 = Property("Prop2", 3, (100, 10), g)
        alice = Player("Alice")
        p1.state["owner"] = alice
        p2.state["owner"] = alice
        assert p1.get_rent() == 20  # 10 * 2

    def test_unowned_property_returns_base_rent(self):
        """
        group exists but owner is None.
        all_owned_by(None) returns False, base rent returned.
        """
        g = make_group()
        prop = Property("Prop1", 1, (100, 10), g)
        assert prop.get_rent() == 10

    def test_multiplier_is_two(self):
        """
        Edge case, verify FULL_GROUP_MULTIPLIER is exactly 2.
        """
        assert Property.FULL_GROUP_MULTIPLIER == 2

    def test_three_property_group_all_owned(self):
        """
        Edge case, three-property group, all owned by same player.
        """
        g = make_group()
        p1 = Property("Prop1", 1, (100, 10), g)
        p2 = Property("Prop2", 3, (100, 12), g)
        p3 = Property("Prop3", 6, (100, 14), g)
        alice = Player("Alice")
        p1.state["owner"] = alice
        p2.state["owner"] = alice
        p3.state["owner"] = alice
        assert p1.get_rent() == 20

    def test_three_property_group_partial_ownership(self):
        """
        Edge case, three-property group, player owns two of three.
        Rent must NOT double.
        """
        g = make_group()
        p1 = Property("Prop1", 1, (100, 10), g)
        p2 = Property("Prop2", 3, (100, 12), g)
        p3 = Property("Prop3", 6, (100, 14), g)
        alice = Player("Alice")
        bob = Player("Bob")
        p1.state["owner"] = alice
        p2.state["owner"] = alice
        p3.state["owner"] = bob
        assert p1.get_rent() == 10  # FAILS before fix


class TestMortgage:

    def test_mortgage_returns_half_price(self):
        """
        not mortgaged, payout = mortgage_value = price // 2.
        """
        prop = make_property(price=200)
        payout = prop.mortgage()
        assert payout == 100

    def test_mortgage_sets_flag(self):
        """
        after mortgage, is_mortgaged must be True.
        """
        prop = make_property(price=200)
        prop.mortgage()
        assert prop.state["is_mortgaged"] is True

    def test_mortgage_already_mortgaged_returns_zero(self):
        """
        is_mortgaged = True, returns 0.
        Cannot mortgage the same property twice.
        """
        prop = make_property(price=200)
        prop.state["is_mortgaged"] = True
        assert prop.mortgage() == 0

    def test_mortgage_already_mortgaged_stays_mortgaged(self):
        """
        Edge case, calling mortgage on already-mortgaged property
        must not change the flag.
        """
        prop = make_property(price=200)
        prop.state["is_mortgaged"] = True
        prop.mortgage()
        assert prop.state["is_mortgaged"] is True

    def test_mortgage_cheap_property(self):
        """Edge case, low price property — mortgage_value floors correctly."""
        prop = make_property(price=60)
        payout = prop.mortgage()
        assert payout == 30

    def test_mortgage_expensive_property(self):
        """Edge case, high price property."""
        prop = make_property(price=400)
        payout = prop.mortgage()
        assert payout == 200


class TestUnmortgage:

    def test_unmortgage_not_mortgaged_returns_zero(self):
        """
        is_mortgaged = False, returns 0.
        Nothing to unmortgage.
        """
        prop = make_property(price=200)
        assert prop.unmortgage() == 0

    def test_unmortgage_returns_correct_cost(self):
        """
        is_mortgaged = True, cost = mortgage_value * 1.1.
        200 // 2 = 100, 100 * 1.1 = 110.
        """
        prop = make_property(price=200)
        prop.state["is_mortgaged"] = True
        cost = prop.unmortgage()
        assert cost == 110

    def test_unmortgage_clears_flag(self):
        """
        after unmortgage, is_mortgaged must be False.
        """
        prop = make_property(price=200)
        prop.state["is_mortgaged"] = True
        prop.unmortgage()
        assert prop.state["is_mortgaged"] is False

    def test_unmortgage_boardwalk_cost(self):
        """
        Edge case, Boardwalk price=400, mortgage=200, unmortgage=220.
        """
        prop = make_property(price=400)
        prop.state["is_mortgaged"] = True
        cost = prop.unmortgage()
        assert cost == 220  # 200 * 1.1

    def test_unmortgage_cheap_property(self):
        """Edge case, cheap property unmortgage cost."""
        prop = make_property(price=60)
        prop.state["is_mortgaged"] = True
        cost = prop.unmortgage()
        assert cost == 33  # 30 * 1.1 = 33

    def test_unmortgage_not_mortgaged_flag_unchanged(self):
        """
        Edge case, calling unmortgage on non-mortgaged property
        must not change the flag.
        """
        prop = make_property(price=200)
        prop.unmortgage()
        assert prop.state["is_mortgaged"] is False


class TestIsAvailable:

    def test_unowned_not_mortgaged_is_available(self):
        """
        both conditions True — property is available.
        """
        prop = make_property()
        assert prop.is_available() is True

    def test_owned_not_available(self):
        """
        owner is set, property is not available.
        """
        prop = make_property()
        prop.state["owner"] = Player("Alice")
        assert prop.is_available() is False

    def test_mortgaged_not_available(self):
        """
        is_mortgaged = True, property is not available.
        """
        prop = make_property()
        prop.state["is_mortgaged"] = True
        assert prop.is_available() is False

    def test_owned_and_mortgaged_not_available(self):
        """
        Edge case, both owner set and mortgaged, still not available.
        """
        prop = make_property()
        prop.state["owner"] = Player("Alice")
        prop.state["is_mortgaged"] = True
        assert prop.is_available() is False


class TestPropertyGroup:

    def test_group_starts_empty(self):
        """New group has no properties."""
        g = make_group()
        assert g.properties == []

    def test_add_property_adds_to_group(self):
        """
        prop not in group, adds it.
        """
        g = make_group()
        prop = make_property()
        g.add_property(prop)
        assert prop in g.properties

    def test_add_property_sets_back_link(self):
        """
        add_property sets prop.group back to this group.
        """
        g = make_group()
        prop = make_property()
        g.add_property(prop)
        assert prop.group == g

    def test_add_property_not_duplicated(self):
        """
        prop already in group, not added again.
        """
        g = make_group()
        prop = make_property()
        g.add_property(prop)
        g.add_property(prop)
        assert g.properties.count(prop) == 1

    def test_size_empty_group(self):
        """Edge case, empty group has size 0."""
        g = make_group()
        assert g.size() == 0

    def test_size_with_properties(self):
        """size reflects number of properties."""
        g = make_group()
        g.add_property(make_property("P1", 1))
        g.add_property(make_property("P2", 2))
        assert g.size() == 2


class TestAllOwnedBy:

    def test_player_none_returns_false(self):
        """
        player is None, returns False immediately.
        """
        g = make_group()
        make_property(group=g)
        assert g.all_owned_by(None) is False

    def test_empty_group(self):
        """
        Empty group is owned by noone.
        """
        g = make_group()
        alice = Player("Alice")
        assert g.all_owned_by(alice) is False

    def test_single_property_owned_returns_true(self):
        """one property, player owns it."""
        g = make_group()
        prop = Property("P1", 1, (100, 10), g)
        alice = Player("Alice")
        prop.state["owner"] = alice
        assert g.all_owned_by(alice) is True

    def test_single_property_not_owned_returns_false(self):
        """one property, player does not own it."""
        g = make_group()
        prop = Property("P1", 1, (100, 10), g)
        alice = Player("Alice")
        assert g.all_owned_by(alice) is False

    def test_partial_ownership_returns_false(self):
        """
        BUG TEST — player owns only one of two properties.
        """
        g = make_group()
        p1 = Property("P1", 1, (100, 10), g)
        p2 = Property("P2", 3, (100, 10), g)
        alice = Player("Alice")
        bob = Player("Bob")
        p1.state["owner"] = alice
        p2.state["owner"] = bob
        assert g.all_owned_by(alice) is False

    def test_full_ownership_returns_true(self):
        """
        player owns every property in group.
        Must return True.
        """
        g = make_group()
        p1 = Property("P1", 1, (100, 10), g)
        p2 = Property("P2", 3, (100, 10), g)
        alice = Player("Alice")
        p1.state["owner"] = alice
        p2.state["owner"] = alice
        assert g.all_owned_by(alice) is True

    def test_different_player_owns_all_returns_false(self):
        """
        Edge case, different player owns everything, target owns nothing.
        """
        g = make_group()
        p1 = Property("P1", 1, (100, 10), g)
        p2 = Property("P2", 3, (100, 10), g)
        alice = Player("Alice")
        bob = Player("Bob")
        p1.state["owner"] = alice
        p2.state["owner"] = alice
        assert g.all_owned_by(bob) is False


class TestGetOwnerCounts:

    def test_no_owners_returns_empty_dict(self):
        """no properties owned, empty dict."""
        g = make_group()
        Property("P1", 1, (100, 10), g)
        assert g.get_owner_counts() == {}

    def test_one_owner_counted(self):
        """one player owns one property."""
        g = make_group()
        prop = Property("P1", 1, (100, 10), g)
        alice = Player("Alice")
        prop.state["owner"] = alice
        counts = g.get_owner_counts()
        assert counts[alice] == 1

    def test_one_player_owns_multiple(self):
        """Edge case, one player owns two properties in group."""
        g = make_group()
        p1 = Property("P1", 1, (100, 10), g)
        p2 = Property("P2", 3, (100, 10), g)
        alice = Player("Alice")
        p1.state["owner"] = alice
        p2.state["owner"] = alice
        counts = g.get_owner_counts()
        assert counts[alice] == 2

    def test_two_players_each_own_one(self):
        """Edge case, split ownership tracked correctly."""
        g = make_group()
        p1 = Property("P1", 1, (100, 10), g)
        p2 = Property("P2", 3, (100, 10), g)
        alice = Player("Alice")
        bob = Player("Bob")
        p1.state["owner"] = alice
        p2.state["owner"] = bob
        counts = g.get_owner_counts()
        assert counts[alice] == 1
        assert counts[bob] == 1