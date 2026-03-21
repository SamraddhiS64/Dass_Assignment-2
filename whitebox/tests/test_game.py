import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../moneypoly'))

from moneypoly.game import Game
from moneypoly.player import Player

# helpers

def make_game():
    """Create a fresh two-player game for each test."""
    return Game(["Alice", "Bob"])


def get_prop(game, position):
    """Get property at a board position."""
    return game.board.get_property_at(position)


class TestBuyProperty:

    def test_insufficient_funds(self):
        """
        balance < price, returns False.
        """
        g = make_game()
        player = g.players[0]
        prop = get_prop(g, 1)
        player.balance = prop.price - 1
        assert g.buy_property(player, prop) is False

    def test_exact(self):
        """
        BUG TEST — Branch: balance == price.
        Player with exactly enough money should be able to buy.
        """
        g = make_game()
        player = g.players[0]
        prop = get_prop(g, 1)
        player.balance = prop.price
        assert g.buy_property(player, prop) is True  # FAILS before fix

    def test_more(self):
        """balance > price, purchase succeeds."""
        g = make_game()
        player = g.players[0]
        prop = get_prop(g, 1)
        player.balance = prop.price + 500
        assert g.buy_property(player, prop) is True

    def test_sets_owner(self):
        """purchase assigns owner correctly."""
        g = make_game()
        player = g.players[0]
        prop = get_prop(g, 1)
        player.balance = prop.price + 500
        g.buy_property(player, prop)
        assert prop.state["owner"] == player

    def test_deducts(self):
        """purchase reduces player balance by exact price."""
        g = make_game()
        player = g.players[0]
        prop = get_prop(g, 1)
        player.balance = prop.price + 500
        before = player.balance
        g.buy_property(player, prop)
        assert player.balance == before - prop.price

    def test_add_to_prop(self):
        """property added to player's property list."""
        g = make_game()
        player = g.players[0]
        prop = get_prop(g, 1)
        player.balance = prop.price + 500
        g.buy_property(player, prop)
        assert prop in player.properties

    def test_failed_buy(self):
        """failed purchase leaves owner as None."""
        g = make_game()
        player = g.players[0]
        prop = get_prop(g, 1)
        player.balance = 0
        g.buy_property(player, prop)
        assert prop.state["owner"] is None

    def test_failed_balance(self):
        """failed purchase leaves balance unchanged."""
        g = make_game()
        player = g.players[0]
        prop = get_prop(g, 1)
        player.balance = prop.price - 1
        before = player.balance
        g.buy_property(player, prop)
        assert player.balance == before


class TestPayRent:

    def test_mortgaged(self):
        """
        is_mortgaged = True, returns immediately.
        Renter balance must not change.
        """
        g = make_game()
        renter = g.players[0]
        owner = g.players[1]
        prop = get_prop(g, 1)
        prop.state["owner"] = owner
        prop.state["is_mortgaged"] = True
        before = renter.balance
        g.pay_rent(renter, prop)
        assert renter.balance == before

    def test_no_owner_no_rent_charged(self):
        """
        owner is None, returns immediately.
        Should not crash and balance unchanged.
        """
        g = make_game()
        renter = g.players[0]
        prop = get_prop(g, 1)
        prop.state["owner"] = None
        before = renter.balance
        g.pay_rent(renter, prop)
        assert renter.balance == before

    def test_rent_deducted_from_renter(self):
        """
        valid rent — renter loses money.
        """
        g = make_game()
        renter = g.players[0]
        owner = g.players[1]
        prop = get_prop(g, 1)
        prop.state["owner"] = owner
        prop.state["is_mortgaged"] = False
        rent = prop.get_rent()
        before = renter.balance
        g.pay_rent(renter, prop)
        assert renter.balance == before - rent

    def test_rent_transferred_to_owner(self):
        """
        BUG TEST — Branch: valid rent — owner must receive money.
        """
        g = make_game()
        renter = g.players[0]
        owner = g.players[1]
        prop = get_prop(g, 1)
        prop.state["owner"] = owner
        prop.state["is_mortgaged"] = False
        rent = prop.get_rent()
        before = owner.balance
        g.pay_rent(renter, prop)
        assert owner.balance == before + rent


class TestFindWinner:

    def test_no_players_returns_none(self):
        """
        empty players list returns None.
        """
        g = make_game()
        g.players.clear()
        assert g.find_winner() is None

    def test_single_player_returns_that_player(self):
        """
        only one player, must be returned.
        """
        g = Game(["Alice"])
        assert g.find_winner().name == "Alice"

    def test_returns_richest_player(self):
        """
        BUG TEST — Branch: multiple players.
        """
        g = make_game()
        g.players[0].balance = 3000
        g.players[1].balance = 500
        winner = g.find_winner()
        assert winner.name == "Alice"

    def test_winner_with_equal_balance(self):
        """
        Edge case, equal balances - either player acceptable.
        """
        g = make_game()
        g.players[0].balance = 1000
        g.players[1].balance = 1000
        winner = g.find_winner()
        assert winner is not None


class TestMortgageProperty:

    def test_not_owner_returns_false(self):
        """
        player doesn't own property, returns False.
        """
        g = make_game()
        player = g.players[0]
        other = g.players[1]
        prop = get_prop(g, 1)
        prop.state["owner"] = other
        assert g.mortgage_property(player, prop) is False

    def test_already_mortgaged_returns_false(self):
        """
        property already mortgaged, payout = 0, returns False.
        """
        g = make_game()
        player = g.players[0]
        prop = get_prop(g, 1)
        prop.state["owner"] = player
        prop.state["is_mortgaged"] = True
        assert g.mortgage_property(player, prop) is False

    def test_successful_mortgage_returns_true(self):
        """
        valid mortgage, returns True.
        """
        g = make_game()
        player = g.players[0]
        prop = get_prop(g, 1)
        prop.state["owner"] = player
        prop.state["is_mortgaged"] = False
        assert g.mortgage_property(player, prop) is True

    def test_successful_mortgage_credits_player(self):
        """
        player balance increases by mortgage value.
        """
        g = make_game()
        player = g.players[0]
        prop = get_prop(g, 1)
        prop.state["owner"] = player
        prop.state["is_mortgaged"] = False
        before = player.balance
        g.mortgage_property(player, prop)
        assert player.balance == before + prop.mortgage_value

    def test_successful_mortgage_sets_flag(self):
        """
        after mortgage, is_mortgaged must be True.
        """
        g = make_game()
        player = g.players[0]
        prop = get_prop(g, 1)
        prop.state["owner"] = player
        prop.state["is_mortgaged"] = False
        g.mortgage_property(player, prop)
        assert prop.state["is_mortgaged"] is True


class TestUnmortgageProperty:

    def test_not_owner_returns_false(self):
        """
        player doesn't own property, returns False.
        """
        g = make_game()
        player = g.players[0]
        other = g.players[1]
        prop = get_prop(g, 1)
        prop.state["owner"] = other
        assert g.unmortgage_property(player, prop) is False

    def test_not_mortgaged_returns_false(self):
        """
        property is not mortgaged, cost = 0, returns False.
        """
        g = make_game()
        player = g.players[0]
        prop = get_prop(g, 1)
        prop.state["owner"] = player
        prop.state["is_mortgaged"] = False
        assert g.unmortgage_property(player, prop) is False

    def test_cannot_afford_returns_false(self):
        """
        player can't afford redemption cost, returns False.
        """
        g = make_game()
        player = g.players[0]
        prop = get_prop(g, 39)
        prop.state["owner"] = player
        prop.state["is_mortgaged"] = True
        player.balance = 0
        assert g.unmortgage_property(player, prop) is False

    def test_successful_unmortgage_returns_true(self):
        """
        all checks pass, returns True.
        """
        g = make_game()
        player = g.players[0]
        prop = get_prop(g, 1)
        prop.state["owner"] = player
        prop.state["is_mortgaged"] = True
        player.balance = 9999
        assert g.unmortgage_property(player, prop) is True

    def test_successful_unmortgage_deducts_balance(self):
        """
        redemption cost deducted from player balance.
        Cost = mortgage_value * 1.1
        """
        g = make_game()
        player = g.players[0]
        prop = get_prop(g, 1)
        prop.state["owner"] = player
        prop.state["is_mortgaged"] = True
        player.balance = 9999
        before = player.balance
        cost = int(prop.mortgage_value * 1.1)
        g.unmortgage_property(player, prop)
        assert player.balance == before - cost

    def test_successful_unmortgage_clears_flag(self):
        """
        after unmortgage, is_mortgaged must be False.
        """
        g = make_game()
        player = g.players[0]
        prop = get_prop(g, 1)
        prop.state["owner"] = player
        prop.state["is_mortgaged"] = True
        player.balance = 9999
        g.unmortgage_property(player, prop)
        assert prop.state["is_mortgaged"] is False


class TestTrade:

    def test_seller_not_owner_fails(self):
        """
        seller doesn't own property, returns False.
        """
        g = make_game()
        seller = g.players[0]
        buyer = g.players[1]
        prop = get_prop(g, 1)
        prop.state["owner"] = buyer
        assert g.trade(seller, buyer, prop, 100) is False

    def test_buyer_cannot_afford_fails(self):
        """
        buyer has insufficient funds, returns False.
        """
        g = make_game()
        seller = g.players[0]
        buyer = g.players[1]
        prop = get_prop(g, 1)
        prop.state["owner"] = seller
        seller.add_property(prop)
        buyer.balance = 0
        assert g.trade(seller, buyer, prop, 500) is False

    def test_successful_trade_returns_true(self):
        """
        valid trade, returns True.
        """
        g = make_game()
        seller = g.players[0]
        buyer = g.players[1]
        prop = get_prop(g, 1)
        prop.state["owner"] = seller
        seller.add_property(prop)
        assert g.trade(seller, buyer, prop, 100) is True

    def test_successful_trade_changes_owner(self):
        """
        property ownership transfers to buyer.
        """
        g = make_game()
        seller = g.players[0]
        buyer = g.players[1]
        prop = get_prop(g, 1)
        prop.state["owner"] = seller
        seller.add_property(prop)
        g.trade(seller, buyer, prop, 100)
        assert prop.state["owner"] == buyer

    def test_successful_trade_deducts_buyer_balance(self):
        """
        cash deducted from buyer.
        """
        g = make_game()
        seller = g.players[0]
        buyer = g.players[1]
        prop = get_prop(g, 1)
        prop.state["owner"] = seller
        seller.add_property(prop)
        before = buyer.balance
        g.trade(seller, buyer, prop, 100)
        assert buyer.balance == before - 100

    def test_successful_trade_moves_property_list(self):
        """
        property removed from seller, added to buyer.
        """
        g = make_game()
        seller = g.players[0]
        buyer = g.players[1]
        prop = get_prop(g, 1)
        prop.state["owner"] = seller
        seller.add_property(prop)
        g.trade(seller, buyer, prop, 100)
        assert prop not in seller.properties
        assert prop in buyer.properties

    def test_zero_cash_trade_succeeds(self):
        """
        Edge case, trade for $0 is valid.
        """
        g = make_game()
        seller = g.players[0]
        buyer = g.players[1]
        prop = get_prop(g, 1)
        prop.state["owner"] = seller
        seller.add_property(prop)
        assert g.trade(seller, buyer, prop, 0) is True


class TestCheckBankruptcy:

    def test_positive_balance_not_eliminated(self):
        """
        Branch: balance > 0, player stays in game.
        """
        g = make_game()
        player = g.players[0]
        player.balance = 100
        g._check_bankruptcy(player)
        assert player in g.players

    def test_zero_balance_eliminated(self):
        """
        Branch: balance == 0, player eliminated.
        """
        g = make_game()
        player = g.players[0]
        player.balance = 0
        g._check_bankruptcy(player)
        assert player not in g.players

    def test_negative_balance_eliminated(self):
        """
        Branch: balance < 0, player eliminated.
        """
        g = make_game()
        player = g.players[0]
        player.balance = -100
        g._check_bankruptcy(player)
        assert player not in g.players

    def test_bankruptcy_releases_properties(self):
        """
        bankrupt player's properties released back to bank.
        All owned properties must have owner set to None.
        """
        g = make_game()
        player = g.players[0]
        prop = get_prop(g, 1)
        prop.state["owner"] = player
        player.add_property(prop)
        player.balance = 0
        g._check_bankruptcy(player)
        assert prop.state["owner"] is None

    def test_bankruptcy_clears_property_list(self):
        """
        bankrupt player's property list cleared.
        """
        g = make_game()
        player = g.players[0]
        prop = get_prop(g, 1)
        prop.state["owner"] = player
        player.add_property(prop)
        player.balance = 0
        g._check_bankruptcy(player)
        assert len(player.properties) == 0

    def test_bankruptcy_sets_eliminated_flag(self):
        """
        is_eliminated set to True.
        """
        g = make_game()
        player = g.players[0]
        player.balance = 0
        g._check_bankruptcy(player)
        assert player.is_eliminated is True


class TestAdvanceTurn:

    def test_turn_number_increments(self):
        """turn number goes up by 1."""
        """moves to next player."""

        g = make_game()
        g.advance_turn()
        assert g.state["turn_number"] == 1
        assert g.state["current_index"] == 1

    def test_index_wraps_to_zero(self):
        """
        after last player, index wraps back to 0.
        """
        g = make_game()
        g.advance_turn()  # index = 1 (Bob)
        g.advance_turn()  # index = 0 (Alice again)
        assert g.state["current_index"] == 0


class TestCurrentPlayer:

    def test_first_player_is_alice(self):
        """ first player is the first name passed in."""
        """after one advance, current player is Bob."""
        g = make_game()
        assert g.current_player().name == "Alice"
        g.advance_turn()
        assert g.current_player().name == "Bob"
