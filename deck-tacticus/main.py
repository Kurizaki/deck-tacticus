import random
from typing import List


CARD_VALUES = {
    '2': 2, '3': 3, '4': 4, '5': 5, '6': 6,
    '7': 7, '8': 8, '9': 9, '10': 10,
    'J': 10, 'Q': 10, 'K': 10, 'A': 11
}
COUNT_VALUES = {
    '2': 1, '3': 1, '4': 1, '5': 1, '6': 1,
    '7': 0, '8': 0, '9': 0, '10': -1,
    'J': -1, 'Q': -1, 'K': -1, 'A': -1
}


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
        self.cards.append(card)
        self.value += card.value
        if card.rank == 'A':
            self.aces += 1
        self.adjust_for_ace()

    def adjust_for_ace(self):
        while self.value > 21 and self.aces:
            self.value -= 10
            self.aces -= 1


    def is_busted(self):
        return self.value > 21

    def __str__(self):
        return ', '.join(str(card) for card in self.cards)


class Player:
    """Represents a player in the game."""

    def __init__(self, name="Player"):
        self.name = name
        self.hand = Hand()
        self.balance = 1000  # Starting balance; adjust as needed

    def make_bet(self):
        """Makes a bet (placeholder for betting logic)."""
        # Implement betting logic here, e.g., deduct bet from balance
        bet = 10  # Default bet amount
        # Add logic to check if the player has enough balance
        return bet

    def play(self, deck, dealer_card):
        """Player's turn logic allowing the player to decide their move."""
        print(f"\nDealer's visible card: {dealer_card}")
        print(f"{self.name}'s hand: {self.hand} (Value: {self.hand.value})")

        while True:
            if self.hand.is_busted():
                print(f"{self.name} busts with {self.hand.value}!")
                break
            elif self.hand.value == 21 and len(self.hand.cards) == 2:
                print(f"{self.name} has Blackjack!")
                break

            # Prompt the player for their action
            action = input("Do you want to [h]it or [s]tand? ").lower()
            if action == 'h':
                card = deck.deal_card()
                self.hand.add_card(card)
                print(f"\nYou drew: {card}")
                print(f"{self.name}'s hand: {self.hand} (Value: {self.hand.value})")
            elif action == 's':
                print(f"{self.name} stands with {self.hand.value}.")
                break
            else:
                print("Invalid input. Please enter 'h' to hit or 's' to stand.")


class Dealer(Player):
    """Represents the dealer."""

    def __init__(self):
        super().__init__(name="Dealer")

    def play(self, deck, dealer_card=None):
        """Dealer's turn logic."""
        print(f"\nDealer's hand: {self.hand} (Value: {self.hand.value})")
        while self.hand.value < 17:
            card = deck.deal_card()
            self.hand.add_card(card)
            print(f"Dealer hits: {card}")
            print(f"Dealer's hand: {self.hand} (Value: {self.hand.value})")
            if self.hand.is_busted():
                print("Dealer busts!")
                break
        else:
            print(f"Dealer stands with {self.hand.value}.")


class Game:
    """Controls the flow of the Blackjack game."""

    def __init__(self, num_decks=1):
        self.deck = Deck(num_decks)
        self.count = 0  # Running count for card counting
        self.true_count = 0  # True count adjusted by decks remaining

    def update_count(self, card):
        """Updates the running count based on the card dealt."""
        self.count += COUNT_VALUES[card.rank]

    def deal_initial_cards(self, player, dealer):
        """Deals initial two cards to player and dealer."""
        # Deal the first card to player and dealer
        player.hand.add_card(self.deck.deal_card())
        self.update_count(player.hand.cards[-1])

        dealer.hand.add_card(self.deck.deal_card())
        self.update_count(dealer.hand.cards[-1])

        # Deal the second card to player and dealer (dealer's is hidden)
        player.hand.add_card(self.deck.deal_card())
        self.update_count(player.hand.cards[-1])

        dealer.hand.add_card(self.deck.deal_card())

    def play_round(self):
        """Plays a single round of Blackjack."""
        player = Player()
        dealer = Dealer()
        self.deal_initial_cards(player, dealer)

        # Show initial hands
        print(f"{player.name}'s hand: {player.hand}")
        print(f"Dealer shows: {dealer.hand.cards[0]}")

        # Player's turn
        player.play(self.deck, dealer.hand.cards[0])

        # Dealer's turn if player hasn't busted
        if not player.hand.is_busted():
            dealer.play(self.deck)

        # Determine the outcome
        self.determine_winner(player, dealer)


    def determine_winner(self, player, dealer):
        """Determines and announces the winner."""
        if player.hand.is_busted():
            print("Dealer wins!")
        elif dealer.hand.is_busted() or player.hand.value > dealer.hand.value:
            print(f"{player.name} wins!")
        elif player.hand.value < dealer.hand.value:
            print("Dealer wins!")
        else:
            print("Push! It's a tie.")


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
