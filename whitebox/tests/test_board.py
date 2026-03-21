import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../moneypoly'))

from moneypoly.board import Board, SPECIAL_TILES
from moneypoly.player import Player

class TestGetPropertyAt:

    def test_returns_property(self):
        """property exists"""
        b = Board()
        prop = b.get_property_at(1)
        assert prop is not None
        assert prop.name == "Mediterranean Avenue"

    def test_returns_none_for_Go(self):
        """no property at position, loop ends
        (Position 0 is Go no property object exists)
        """
        b = Board()
        prop = b.get_property_at(0)
        assert prop is None

    def test_returns_none_for_nonexistent(self):
        """position has no property at all.
        (Position 99 is off the board entirely.)
        """
        b = Board()
        prop = b.get_property_at(99)
        assert prop is None

    def test_returns_boardwalk(self):
        """property found at position 39.
        """
        b = Board()
        prop = b.get_property_at(39)
        assert prop is not None
        assert prop.name == "Boardwalk"

    def test_returns_none_for_jail(self):
        """jail tile at position 10 has no property.
        """
        b = Board()
        prop = b.get_property_at(10)
        assert prop is None

    def test_returns_none_for_chance(self):
        """chance tile at position 7 has no property.
        """
        b = Board()
        prop = b.get_property_at(7)
        assert prop is None

class TestGetTileType:

    def test_position_go(self):
        """
        position in SPECIAL_TILES.
        Position 0 is Go.
        """
        b = Board()
        assert b.get_tile_type(0) == "go"

    def test_jail_position(self):
        """
        position in SPECIAL_TILES.
        Position 10 is jail.
        """
        b = Board()
        assert b.get_tile_type(10) == "jail"

    def test_go_to_jail(self):
        """
        position in SPECIAL_TILES.
        Position 30 is go_to_jail.
        """
        b = Board()
        assert b.get_tile_type(30) == "go_to_jail"

    def test_free_parking(self):
        """
        position in SPECIAL_TILES.
        Position 20 is free_parking.
        """
        b = Board()
        assert b.get_tile_type(20) == "free_parking"

    def test_income_tax(self):
        """
        position in SPECIAL_TILES.
        Position 4 is income_tax.
        """
        b = Board()
        assert b.get_tile_type(4) == "income_tax"

    def test_luxury_tax(self):
        """
        position in SPECIAL_TILES.
        Position 38 is luxury_tax.
        """
        b = Board()
        assert b.get_tile_type(38) == "luxury_tax"

    def test_chance(self):
        """
        position in SPECIAL_TILES.
        Position 7 is chance.
        """
        b = Board()
        assert b.get_tile_type(7) == "chance"

    def test_community_chest(self):
        """
        position in SPECIAL_TILES.
        Position 2 is community_chest.
        """
        b = Board()
        assert b.get_tile_type(2) == "community_chest"

    def test_railroad(self):
        """
        position in SPECIAL_TILES.
        Position 5 is railroad.
        """
        b = Board()
        assert b.get_tile_type(5) == "railroad"

    def test_property(self):
        """
        not in SPECIAL_TILES, but property exists.
        Position 1 is Mediterranean Avenue.
        """
        b = Board()
        assert b.get_tile_type(1) == "property"

    def test_blank(self):
        """
        not in SPECIAL_TILES, no property exists.
        Position 99 is off the board entirely.
        """
        b = Board()
        assert b.get_tile_type(99) == "blank"

    def test_all_railroads(self):
        """
        all four railroad positions return railroad.
        """
        b = Board()
        for pos in [5, 15, 25, 35]:
            assert b.get_tile_type(pos) == "railroad"

    def test_all_chance(self):
        """
        all three chance positions return chance.
        """
        b = Board()
        for pos in [7, 22, 36]:
            assert b.get_tile_type(pos) == "chance"

    def test_all_community_chest(self):
        """
        all three community chest positions.
        """
        b = Board()
        for pos in [2, 17, 33]:
            assert b.get_tile_type(pos) == "community_chest"

class TestIsPurchasable:

    def test_unowned_not_mortgaged_is_purchasable(self):
        """
        all checks pass, returns True.
        """
        b = Board()
        assert b.is_purchasable(1) is True

    def test_special_tile(self):
        """
        prop is None (special tile has no property).
        Position 0 is Go, nothing to buy.
        """
        b = Board()
        assert b.is_purchasable(0) is False

    def test_invalid_position(self):
        """
        prop is None (position doesn't exist).
        """
        b = Board()
        assert b.is_purchasable(99) is False

    def test_owned_property(self):
        """
        owner is not None, returns False.
        """
        b = Board()
        player = Player("Alice")
        prop = b.get_property_at(1)
        prop.state["owner"]= player
        assert b.is_purchasable(1) is False

    def test_mortgaged_property(self):
        """
        is_mortgaged is True, returns False.
        """
        b = Board()
        prop = b.get_property_at(1)
        prop.state["is_mortgaged"] = True
        assert b.is_purchasable(1) is False

    def test_boardwalk(self):
        """
        property starts purchasable.
        """
        b = Board()
        assert b.is_purchasable(39) is True

    def test_railroad(self):
        """
        railroads in SPECIAL_TILES, not purchasable.
        """
        b = Board()
        assert b.is_purchasable(5) is False


class TestIsSpecialTile:

    def test_go(self):
        """position in SPECIAL_TILES, returns True."""
        b = Board()
        assert b.is_special_tile(0) is True

    def test_jail(self):
        """position in SPECIAL_TILES, returns True."""
        b = Board()
        assert b.is_special_tile(10) is True

    def test_property(self):
        """position not in SPECIAL_TILES, returns False."""
        b = Board()
        assert b.is_special_tile(1) is False

    def test_invalid_position(self):
        """Edge case, position off the board is not special."""
        b = Board()
        assert b.is_special_tile(99) is False

    def test_all_special_tiles(self):
        """every key in SPECIAL_TILES must return True."""
        b = Board()
        for pos in SPECIAL_TILES:
            assert b.is_special_tile(pos) is True


class TestPropertiesOwnedBy:

    def test_no_properties_owned(self):
        """
        player owns nothing, returns empty list.
        """
        b = Board()
        player = Player("Alice")
        assert b.properties_owned_by(player) == []

    def test_returns_owned_properties(self):
        """
        player owns some properties, returns them.
        """
        b = Board()
        player = Player("Alice")
        prop1 = b.get_property_at(1)
        prop2 = b.get_property_at(3)
        prop1.state["owner"] = player
        prop2.state["owner"] = player
        owned = b.properties_owned_by(player)
        assert len(owned) == 2
        assert prop1 in owned
        assert prop2 in owned

    def test_returns_correct_players_properties(self):
        """
        Edge case, two players, each only gets their own properties.
        """
        b = Board()
        alice = Player("Alice")
        bob = Player("Bob")
        prop1 = b.get_property_at(1)
        prop2 = b.get_property_at(3)
        prop1.state["owner"]= alice
        prop2.state["owner"] = bob
        assert len(b.properties_owned_by(alice)) == 1
        assert len(b.properties_owned_by(bob)) == 1

class TestUnownedProperties:

    def test_all_unowned_at_start(self):
        """
        no properties owned, all returned.
        """
        b = Board()
        unowned = b.unowned_properties()
        assert len(unowned) == 22

    def test_owned_properties_excluded(self):
        """
        owned properties filtered out of results.
        """
        b = Board()
        player = Player("Alice")
        prop = b.get_property_at(1)
        prop.state["owner"] = player
        unowned = b.unowned_properties()
        assert len(unowned) == 21
        assert prop not in unowned

    def test_all_owned(self):
        """
        if all properties owned, returns empty list.
        """
        b = Board()
        player = Player("Alice")
        for prop in b.properties:
            prop.state["owner"] = player
        assert b.unowned_properties() == []


class TestBoardInit:

    def test_board(self):
        """Board must have exactly 22 purchasable properties."""
        b = Board()
        assert len(b.properties) == 22

    def test_board_groups(self):
        """Board must have exactly 8 colour groups."""
        b = Board()
        assert len(b.groups) == 8

    def test_all_groups(self):
        """all 8 specific group names must exist."""
        b = Board()
        expected = [
            "brown", "light_blue", "pink", "orange",
            "red", "yellow", "green", "dark_blue"
        ]
        for group_name in expected:
            assert group_name in b.groups
