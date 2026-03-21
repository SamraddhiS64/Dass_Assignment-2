import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../moneypoly'))

from moneypoly.cards import CardDeck, CHANCE_CARDS, COMMUNITY_CHEST_CARDS


class TestCardDeckInit:

    def test_chance(self):
        """Chance deck must have exactly 12 cards."""
        deck = CardDeck(CHANCE_CARDS)
        assert len(deck) == 12

    def test_community(self):
        """Community chest deck must have exactly 12 cards."""
        deck = CardDeck(COMMUNITY_CHEST_CARDS)
        assert len(deck) == 12

    def test_index(self):
        """Index must start at 0 on creation."""
        deck = CardDeck(CHANCE_CARDS)
        assert deck.index == 0

    def test_cards_are_copied(self):
        """Cards list must be a copy so original is not modified."""
        original = [{"description": "Test", "action": "collect", "value": 10}]
        deck = CardDeck(original)
        deck.cards.append({"description": "Extra", "action": "pay", "value": 5})
        assert len(original) == 1

    def test_empty_deck_initializes(self):
        """empty list initializes without error."""
        deck = CardDeck([])
        assert len(deck) == 0
        assert deck.index == 0


class TestDraw:

    def test_draw(self):
        """first draw returns the first card."""
        deck = CardDeck(CHANCE_CARDS)
        card = deck.draw()
        assert card == CHANCE_CARDS[0]

    def test_draw_inc(self):
        """index increments after each draw."""
        deck = CardDeck(CHANCE_CARDS)
        deck.draw()
        assert deck.index == 1
        deck.draw()
        assert deck.index == 2

    def test_draw_order(self):
        """cards come out in the same order they went in."""
        deck = CardDeck(CHANCE_CARDS)
        for i in range(len(CHANCE_CARDS)):
            card = deck.draw()
            assert card == CHANCE_CARDS[i]

    def test_draw_cycles(self):
        """index wraps around when all cards drawn.
        Drawing card 13 from a 12-card deck returns card 1 again.
        """
        deck = CardDeck(CHANCE_CARDS)
        for _ in range(12):
            deck.draw()
        card = deck.draw()
        assert card == CHANCE_CARDS[0]

    def test_draw_empty_deck(self):
        """if not self.cards returns None.
        """
        deck = CardDeck([])
        result = deck.draw()
        assert result is None

    def test_draw_empty_deck_index(self):
        """
        drawing from empty deck must not change index.
        """
        deck = CardDeck([])
        deck.draw()
        assert deck.index == 0

    def test_draw_single_card_deck(self):
        """
        deck with one card always returns same card.
        """
        single = [{"description": "Only card", "action": "collect", "value": 50}]
        deck = CardDeck(single)
        card1 = deck.draw()
        card2 = deck.draw()
        assert card1 == card2

    def test_drawn_action(self):
        """drawn card has correct action field."""
        deck = CardDeck(CHANCE_CARDS)
        card = deck.draw()
        assert "action" in card
        assert "value" in card
        assert "description" in card

    def test_draw_all_actions_valid(self):
        """
        Valid actions are collect, pay, jail, jail_free, move_to,
        collect_from_all, birthday.
        """
        valid_actions = {
            "collect", "pay", "jail",
            "jail_free", "move_to",
            "collect_from_all", "birthday"
        }
        deck = CardDeck(CHANCE_CARDS)
        for _ in range(len(CHANCE_CARDS)):
            card = deck.draw()
            assert card["action"] in valid_actions

    def test_draw_community_all_actions_valid(self):
        """every community chest card has valid action."""
        valid_actions = {
            "collect", "pay", "jail",
            "jail_free", "move_to",
            "collect_from_all", "birthday"
        }
        deck = CardDeck(COMMUNITY_CHEST_CARDS)
        for _ in range(len(COMMUNITY_CHEST_CARDS)):
            card = deck.draw()
            assert card["action"] in valid_actions


class TestPeek:

    def test_peek(self):
        """peek returns the next card."""
        deck = CardDeck(CHANCE_CARDS)
        card = deck.peek()
        assert card == CHANCE_CARDS[0]

    def test_peekindex(self):
        """
        peek must NOT change the index.
        Peeking multiple times returns same card.
        """
        deck = CardDeck(CHANCE_CARDS)
        deck.peek()
        deck.peek()
        assert deck.index == 0

    def test_peek_matches_next_draw(self):
        """
        peeked card must be same as next drawn card.
        """
        deck = CardDeck(CHANCE_CARDS)
        peeked = deck.peek()
        drawn = deck.draw()
        assert peeked == drawn

    def test_peek_after_draws(self):
        """
        peek shows correct card after some draws.
        """
        deck = CardDeck(CHANCE_CARDS)
        deck.draw()
        deck.draw()
        peeked = deck.peek()
        drawn = deck.draw()
        assert peeked == drawn

    def test_peek_empty_deck(self):
        """
        if not self.cards returns None.
        """
        deck = CardDeck([])
        assert deck.peek() is None

    def test_peek_cycles(self):
        """
        peek works correctly after deck has cycled.
        """
        deck = CardDeck(CHANCE_CARDS)
        for _ in range(12):
            deck.draw()
        peeked = deck.peek()
        drawn = deck.draw()
        assert peeked == drawn


class TestReshuffle:

    def test_reshuffle(self):
        """
        index goes back to 0 after reshuffle.
        """
        deck = CardDeck(CHANCE_CARDS)
        deck.draw()
        deck.draw()
        deck.draw()
        deck.reshuffle()
        assert deck.index == 0

    def test_reshuffle_card_count(self):
        """
        reshuffle does not add or remove cards.
        """
        deck = CardDeck(CHANCE_CARDS)
        deck.reshuffle()
        assert len(deck) == 12

    def test_reshuffle_drawable(self):
        """
        can still draw after reshuffle.
        """
        deck = CardDeck(CHANCE_CARDS)
        deck.reshuffle()
        card = deck.draw()
        assert card is not None
        assert "action" in card

    def test_reshuffle_empty_deck(self):
        """
        reshuffling empty deck does not crash.
        """
        deck = CardDeck([])
        deck.reshuffle()
        assert deck.index == 0
        assert len(deck) == 0


class TestCardsRemaining:

    def test_full_deck(self):
        """
        fresh deck has all 12 cards remaining.
        """
        deck = CardDeck(CHANCE_CARDS)
        assert deck.cards_remaining() == 12

    def test_decreases_draw(self):
        """
        remaining count decreases after each draw.
        """
        deck = CardDeck(CHANCE_CARDS)
        deck.draw()
        assert deck.cards_remaining() == 11
        deck.draw()
        assert deck.cards_remaining() == 10

    def test_resets_full_cycle(self):
        """
        after drawing all 12 cards, remaining resets to 12.
        """
        deck = CardDeck(CHANCE_CARDS)
        for _ in range(12):
            deck.draw()
        assert deck.cards_remaining() == 12

    def test_empty_deck_remaining(self):
        """
        empty deck, cards_remaining would cause
        division by zero.
        """
        deck = CardDeck([])
        with pytest.raises(ZeroDivisionError):
            deck.cards_remaining()


class TestLen:

    def test_len_chance(self):
        """must return 12 for chance deck."""
        deck = CardDeck(CHANCE_CARDS)
        assert len(deck) == 12

    def test_len_community(self):
        """must return 12 for community deck."""
        deck = CardDeck(COMMUNITY_CHEST_CARDS)
        assert len(deck) == 12

    def test_len_empty(self):
        """len of empty deck is 0."""
        deck = CardDeck([])
        assert len(deck) == 0

    def test_len_draw(self):
        """
        drawing does not change deck length.
        """
        deck = CardDeck(CHANCE_CARDS)
        deck.draw()
        deck.draw()
        assert len(deck) == 12


class TestCardValues:

    def test_chance_collect(self):
        """All collect action cards must have value > 0."""
        for card in CHANCE_CARDS:
            if card["action"] == "collect":
                assert card["value"] > 0

    def test_chance_pay(self):
        """All pay action cards must have value > 0."""
        for card in CHANCE_CARDS:
            if card["action"] == "pay":
                assert card["value"] > 0

    def test_community_collect(self):
        """All community chest collect cards must have value > 0."""
        for card in COMMUNITY_CHEST_CARDS:
            if card["action"] == "collect":
                assert card["value"] > 0

    def test_all_cards_keys(self):
        """Every card in both decks must have description, action, value."""
        all_cards = CHANCE_CARDS + COMMUNITY_CHEST_CARDS
        for card in all_cards:
            assert "description" in card
            assert "action" in card
            assert "value" in card

    def test_move_to_boardwalk(self):
        """
        Advance to Boardwalk card must have value 39.
        """
        boardwalk_card = next(
            c for c in CHANCE_CARDS if "Boardwalk" in c["description"]
        )
        assert boardwalk_card["value"] == 39

    def test_move_to_go(self):
        """
        Advance to Go card must have value 0.
        """
        go_card = next(
            c for c in CHANCE_CARDS if "Advance to Go" in c["description"]
        )
        assert go_card["value"] == 0