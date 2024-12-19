import unittest
from unittest.mock import patch
from blackjack_env import Card, Deck  # Replace with the actual name of your module

class TestCard(unittest.TestCase):
    def test_card_initialization(self):
        card = Card('A', '♠')
        self.assertEqual(card.rank, 'A')
        self.assertEqual(card.suit, '♠')
        self.assertEqual(card.value, 11)  # Ace is counted as 11 by default

    def test_card_string_representation(self):
        card = Card('K', '♥')
        self.assertEqual(str(card), "K♥")


class TestDeck(unittest.TestCase):
    def test_deck_initialization(self):
        deck = Deck(num_decks=2)
        # A standard deck has 52 cards; with num_decks=2, we should have 104 cards
        self.assertEqual(len(deck.cards), 104)
        # Check if deck has the right composition
        all_ranks = [c.rank for c in deck.cards]
        all_suits = [c.suit for c in deck.cards]

        # Each suit should appear 2 * 13 = 26 times
        for suit in Deck.suits:
            self.assertEqual(all_suits.count(suit), 26)
        
        # Each rank should appear 2 * 4 = 8 times
        for rank in Deck.ranks:
            self.assertEqual(all_ranks.count(rank), 8)

    def test_deck_build_deck(self):
        deck = Deck(num_decks=1)
        # rebuild deck to ensure build_deck works independently
        deck.cards = []
        deck.build_deck()
        self.assertEqual(len(deck.cards), 52)

    def test_deck_shuffle(self):
        deck = Deck(num_decks=1)
        original_order = deck.cards.copy()
        deck.shuffle()
        # After shuffle, order should not be the same. 
        # There's a small probability a shuffle could match, 
        # but it's astronomically small. For test, we assume a difference.
        self.assertNotEqual(original_order, deck.cards)

    def test_deck_deal_card(self):
        deck = Deck(num_decks=1)
        initial_count = len(deck.cards)
        card_dealt = deck.deal_card()
        self.assertIsInstance(card_dealt, Card)
        self.assertEqual(len(deck.cards), initial_count - 1)

        # If we deal all cards, deck should rebuild and shuffle
        for _ in range(len(deck.cards)):
            deck.deal_card()
        # After dealing all cards, deck should rebuild:
        self.assertTrue(len(deck.cards) > 0)


if __name__ == '__main__':
    unittest.main()
