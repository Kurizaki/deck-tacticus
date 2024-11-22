import random
from typing import List

CARD_VALUES = {}
COUNT_VALUES = {}


class Card:
    """Represents a single playing card."""
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit
        self.value = self.value = CARD_VALUES[self.rank]
    def __str__(self):
        return f"{self.rank}{self.suit}"

class Deck:
    """Represents a shoe containing multiple decks."""
    suits = ['♠', '♥', '♦', '♣']
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10',
             'J', 'Q', 'K', 'A']

    def __init__(self, num_decks=1):
        self.num_decks = num_decks
        self.cards: list[Card] = []
        self.build_deck()
        self.shuffle()

    def build_deck(self):
        """Builds the deck with the specified number of decks."""
        self.cards = []
        for i in range(self.num_decks):
            for suit in self.suits:
                for rank in self.ranks:
                    self.cards.append(Card(rank, suit))

    def shuffle(self):
        """Shuffles the deck."""
        random.shuffle(self.cards)

    def deal_card(self):
        """Deals a single card from the deck."""
        if self.cards:
            first_card = self.cards[0]
            self.cards.pop(0)
            return first_card
        else:
            return None

class Hand:
    """Represents a hand of cards for a player or dealer."""

    def __init__(self):
        self.cards = []
        self.value = 0
        self.aces = 0  # Number of aces in the hand

    def add_card(self, card):
        """Adds a card to the hand and adjusts for aces."""
        pass  # Logic to add a card and adjust for aces

    def adjust_for_ace(self):
        """Adjusts the hand value if there are aces and the total is over 21."""
        pass  # Logic to adjust the value for aces

    def is_busted(self):
        """Checks if the hand is busted."""
        pass  # Logic to check if hand value exceeds 21

    def __str__(self):
        pass  # Return a string representation of the hand


class Player:
    """Represents a player in the game."""

    def __init__(self, name="Player"):
        self.name = name
        self.hand = Hand()

    def make_bet(self):
        """Makes a bet (placeholder for betting logic)."""
        pass  # Logic for placing a bet

    def play(self, deck, dealer_card):
        """Player's turn logic (can be overridden for AI players)."""
        pass  # Logic for player's actions during their turn


class Dealer(Player):
    """Represents the dealer."""

    def __init__(self):
        super().__init__(name="Dealer")

    def play(self, deck, dealer_card=None):
        """Dealer's turn logic."""
        pass  # Logic for dealer's actions during their turn


class Game:
    """Controls the flow of the Blackjack game."""

    def __init__(self, num_decks=1):
        self.deck = Deck(num_decks)
        self.count = 0  # Running count for card counting
        self.true_count = 0  # True count adjusted by decks remaining

    def update_count(self, card):
        """Updates the running count based on the card dealt."""
        pass  # Logic to update the card counting system

    def deal_initial_cards(self, player, dealer):
        """Deals initial two cards to player and dealer."""
        pass  # Logic to deal initial cards

    def play_round(self):
        """Plays a single round of Blackjack."""
        pass  # Logic to play a round

    def determine_winner(self, player, dealer):
        """Determines and announces the winner."""
        pass  # Logic to determine the winner of the round


def main():
    num_decks = int(input("Enter number of decks to use: "))
    game = Game(num_decks=num_decks)

    while True:
        game.play_round()
        again = input("Play another round? (y/n): ")
        if again.lower() != 'y':
            break


if __name__ == "__main__":
    main()
