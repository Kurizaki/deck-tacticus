#  ____                   __          ______                 __                                  
# /\  _`\                /\ \        /\__  _\               /\ \__  __                           
# \ \ \/\ \     __    ___\ \ \/'\    \/_/\ \/    __      ___\ \ ,_\/\_\    ___   __  __    ____  
#  \ \ \ \ \  /'__`\ /'___\ \ , <       \ \ \  /'__`\   /'___\ \ \/\/\ \  /'___\/\ \/\ \  /',__\ 
#   \ \ \_\ \/\  __//\ \__/\ \ \\`\      \ \ \/\ \L\.\_/\ \__/\ \ \_\ \ \/\ \__/\ \ \_\ \/\__, `\
#    \ \____/\ \____\ \____\\ \_\ \_\     \ \_\ \__/.\_\ \____\\ \__\\ \_\ \____\\ \____/\/\____/
#     \/___/  \/____/\/____/ \/_/\/_/      \/_/\/__/\/_/\/____/ \/__/ \/_/\/____/ \/___/  \/___/ 
# By Kurizaki & Sprudello

import unittest
from unittest.mock import patch
from blackjack_env import Card, Deck  # Update with the actual module import if needed

class TestCard(unittest.TestCase):
    """Tests for the Card class."""

    def test_card_initialization(self):
        """Ensure a Card initializes with correct rank, suit, and value."""
        card = Card('A', '♠')
        self.assertEqual(card.rank, 'A')
        self.assertEqual(card.suit, '♠')
        self.assertEqual(card.value, 11)  # Ace is counted as 11 by default

    def test_card_string_representation(self):
        """Check that the string representation matches rank+suit."""
        card = Card('K', '♥')
        self.assertEqual(str(card), "K♥")


class TestDeck(unittest.TestCase):
    """Tests for the Deck class."""

    def test_deck_initialization(self):
        """Check that a deck with multiple decks is built correctly."""
        deck = Deck(num_decks=2)
        # With 2 decks, we expect 104 cards.
        self.assertEqual(len(deck.cards), 104)

        all_ranks = [c.rank for c in deck.cards]
        all_suits = [c.suit for c in deck.cards]

        # Each suit should appear 26 times (2 decks * 13 cards each)
        for suit in Deck.suits:
            self.assertEqual(all_suits.count(suit), 26)
        
        # Each rank should appear 8 times (2 decks * 4 suits)
        for rank in Deck.ranks:
            self.assertEqual(all_ranks.count(rank), 8)

    def test_deck_build_deck(self):
        """Ensure build_deck rebuilds the full deck of cards."""
        deck = Deck(num_decks=1)
        deck.cards = []
        deck.build_deck()
        self.assertEqual(len(deck.cards), 52)

    def test_deck_shuffle(self):
        """Check that shuffle changes the order of cards."""
        deck = Deck(num_decks=1)
        original_order = deck.cards.copy()
        deck.shuffle()
        # While it's possible (but extremely unlikely) the deck remains identical,
        # we test that it doesn't match exactly.
        self.assertNotEqual(original_order, deck.cards)

    def test_deck_deal_card(self):
        """Check that dealing a card removes it from the deck and rebuilds when empty."""
        deck = Deck(num_decks=1)
        initial_count = len(deck.cards)
        card_dealt = deck.deal_card()

        self.assertIsInstance(card_dealt, Card)
        self.assertEqual(len(deck.cards), initial_count - 1)

        # Deal all remaining cards
        for _ in range(len(deck.cards)):
            deck.deal_card()

        # After dealing all cards, the deck should rebuild
        self.assertTrue(len(deck.cards) > 0)


if __name__ == '__main__':
    unittest.main()
