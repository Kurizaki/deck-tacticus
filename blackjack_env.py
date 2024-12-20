#  ____                   __          ______                 __                                  
# /\  _`\                /\ \        /\__  _\               /\ \__  __                           
# \ \ \/\ \     __    ___\ \ \/'\    \/_/\ \/    __      ___\ \ ,_\/\_\    ___   __  __    ____  
#  \ \ \ \ \  /'__`\ /'___\ \ , <       \ \ \  /'__`\   /'___\ \ \/\/\ \  /'___\/\ \/\ \  /',__\ 
#   \ \ \_\ \/\  __//\ \__/\ \ \\`\      \ \ \/\ \L\.\_/\ \__/\ \ \_\ \ \/\ \__/\ \ \_\ \/\__, `\
#    \ \____/\ \____\ \____\\ \_\ \_\     \ \_\ \__/.\_\ \____\\ \__\\ \_\ \____\\ \____/\/\____/
#     \/___/  \/____/\/____/ \/_/\/_/      \/_/\/__/\/_/\/____/ \/__/ \/_/\/____/ \/___/  \/___/ 
# By Kurizaki & Sprudello

import random
import numpy as np
import gym
from gym import spaces
import pandas as pd
import logging

# ============================================================
# Configuration and Constants
# ============================================================

logging.basicConfig(level=logging.ERROR)  # Set to ERROR to suppress warnings

CARD_VALUES = {
    '2': 2, '3': 3, '4': 4, '5': 5,
    '6': 6, '7': 7, '8': 8, '9': 9,
    '10': 10, 'J': 10, 'Q': 10,
    'K': 10, 'A': 11
}

COUNT_VALUES = {
    '2': 1, '3': 1, '4': 1, '5': 1,
    '6': 1, '7': 0, '8': 0, '9': 0,
    '10': -1, 'J': -1, 'Q': -1,
    'K': -1, 'A': -1
}


# ============================================================
# Card and Deck Classes
# ============================================================

class Card:
    """Represents a single playing card."""
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit
        self.value = CARD_VALUES[self.rank]

    def __str__(self):
        return f"{self.rank}{self.suit}"


class Deck:
    """
    Represents a shoe containing multiple decks of cards.
    Automatically rebuilds and shuffles when cards run out.
    """
    suits = ['♠', '♥', '♦', '♣']
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10',
             'J', 'Q', 'K', 'A']

    def __init__(self, num_decks=8):
        self.num_decks = num_decks
        self.cards = []
        self.build_deck()
        self.shuffle()

    def build_deck(self):
        self.cards = []
        for _ in range(self.num_decks):
            for suit in self.suits:
                for rank in self.ranks:
                    self.cards.append(Card(rank, suit))

    def shuffle(self):
        random.shuffle(self.cards)

    def deal_card(self):
        if not self.cards:
            self.build_deck()
            self.shuffle()
        return self.cards.pop(0)


# ============================================================
# Hand Class
# ============================================================

class Hand:
    """Represents a hand of cards held by a player or the dealer."""
    def __init__(self, is_split_aces=False):
        self.cards = []
        self.value = 0
        self.aces = 0
        self.doubled = False
        self.is_split_aces = is_split_aces
        self.is_split = False

    def add_card(self, card):
        self.cards.append(card)
        self.value += card.value
        if card.rank == 'A':
            self.aces += 1
        self.adjust_for_ace()

    def adjust_for_ace(self):
        """Adjust the value of Aces if the hand is over 21."""
        while self.value > 21 and self.aces:
            self.value -= 10
            self.aces -= 1

    def is_busted(self):
        return self.value > 21

    def has_blackjack(self):
        return (self.value == 21 and len(self.cards) == 2 and not self.is_split)

    def is_six_card_charlie(self):
        return (len(self.cards) == 6 and not self.is_busted())

    def can_double(self):
        return (len(self.cards) == 2 and not self.is_split_aces)

    def can_split(self):
        # Split if both cards have the same Blackjack value
        return (len(self.cards) == 2 and
                CARD_VALUES[self.cards[0].rank] == CARD_VALUES[self.cards[1].rank])

    def __str__(self):
        return ', '.join(str(card) for card in self.cards)


# ============================================================
# Blackjack Environment
# ============================================================

class BlackjackEnv(gym.Env):
    """
    A custom Blackjack environment.

    Observation: [True count, Percentage remaining, Dealer's visible card value, 0(no insurance)]
    Action: A discrete value 0-9 indicating the bet amount (bet = action+1).
    """

    metadata = {'render.modes': ['human']}

    def __init__(self, num_decks=8):
        super(BlackjackEnv, self).__init__()

        self.num_decks = num_decks
        self.deck = Deck(num_decks=self.num_decks)
        self.player_hands = []
        self.dealer_hand = None
        self.count = 0
        self.true_count = 0

        # Action space: Bet amount only (0-9 -> bet 1-10)
        self.action_space = spaces.Discrete(10)

        # Observation space:
        # [true_count, percentage_remaining, dealer_visible_value, insurance_offered(=0)]
        self.observation_space = spaces.Box(
            low=np.array([-10, 0, 1, 0]),
            high=np.array([10, 1, 11, 0]),
            dtype=np.float32
        )

        # Load basic strategy tables
        self.hard_totals = pd.read_csv('hard_totals.csv', index_col='PlayerTotal')
        self.soft_totals = pd.read_csv('soft_totals.csv', index_col='PlayerTotal')
        self.pairs = pd.read_csv('pairs.csv', index_col='Pair')

        self.basic_strategy_cache = {}

    def minimum_deck_size(self):
        return int(0.25 * 52 * self.num_decks)

    def reset(self):
        """Reset the environment for a new round."""
        self.player_hands = []
        self.dealer_hand = Hand()

        if len(self.deck.cards) < self.minimum_deck_size():
            self.deck = Deck(num_decks=self.num_decks)
            self.count = 0
            self.true_count = 0

        self._deal_initial_cards()
        observation = self._get_observation()
        return observation

    def step(self, action):
        """
        Execute a betting action, then simulate the player and dealer plays.
        Return the final observation, reward, done, and info.
        """
        self.current_bet = action + 1
        player_results = []

        # Player plays for each hand
        for hand in self.player_hands:
            results = self._player_play(hand)
            player_results.append(results)

        # Reveal and count the dealer's hidden card
        self._update_count(self.dealer_hand.cards[1])

        dealer_blackjack = self.dealer_hand.has_blackjack()

        # If no dealer blackjack, dealer plays out their hand
        dealer_busted = False
        if not dealer_blackjack:
            dealer_busted = self._dealer_play()

        # Calculate total reward
        total_reward = 0
        for hand, player_busted, player_blackjack in player_results:
            reward = self._calculate_reward(player_busted, dealer_busted,
                                            self.current_bet, hand,
                                            player_blackjack, dealer_blackjack)
            total_reward += reward

        # Update true count
        self.true_count = self.count / max(1, len(self.deck.cards) / 52)

        done = True
        observation = self._get_observation()
        return observation, total_reward, done, {}

    def render(self, mode='human'):
        """Render the current state of the game."""
        for i, hand in enumerate(self.player_hands):
            print(f"Player's hand {i+1}: {hand} (Value: {hand.value})")
        print(f"Dealer's hand: {self.dealer_hand} (Value: {self.dealer_hand.value})")

    # ============================================================
    # Internal Methods
    # ============================================================

    def _deal_initial_cards(self):
        """Deal initial two cards to player and dealer."""
        # Player hand
        player_hand = Hand()
        card = self.deck.deal_card()
        player_hand.add_card(card)
        self._update_count(card)

        card = self.deck.deal_card()
        player_hand.add_card(card)
        self._update_count(card)
        self.player_hands.append(player_hand)

        # Dealer hand
        card = self.deck.deal_card()
        self.dealer_hand.add_card(card)
        self._update_count(card)

        card = self.deck.deal_card()
        self.dealer_hand.add_card(card)
        # Dealer's second card is counted after player finishes

    def _player_play(self, hand):
        """
        Let the player (or hands if split) play according to basic strategy.
        Returns (final_hand, player_busted, player_blackjack).
        """
        player_blackjack = hand.has_blackjack()
        player_busted = False
        hands_to_play = [hand]
        i = 0

        while i < len(hands_to_play):
            current_hand = hands_to_play[i]
            iteration_count = 0
            max_iterations = 10

            # Split Aces: If two cards, forced stand
            if current_hand.is_split_aces and len(current_hand.cards) == 2:
                i += 1
                continue

            while iteration_count < max_iterations:
                iteration_count += 1

                if current_hand.is_six_card_charlie():
                    break  # Automatic win

                if current_hand.is_split_aces and len(current_hand.cards) == 2:
                    # Forced stand on split aces with two cards
                    break

                action = self._basic_strategy_action(current_hand)

                # If split aces with two cards, must stand
                if current_hand.is_split_aces and len(current_hand.cards) == 2:
                    action = 'S'

                if action == 'H':
                    card = self.deck.deal_card()
                    current_hand.add_card(card)
                    self._update_count(card)
                    if current_hand.is_busted():
                        player_busted = True
                        break

                elif action == 'D':
                    if current_hand.can_double():
                        current_hand.doubled = True
                        card = self.deck.deal_card()
                        current_hand.add_card(card)
                        self._update_count(card)
                        if current_hand.is_busted():
                            player_busted = True
                        break
                    else:
                        # If can't double, treat as hit
                        card = self.deck.deal_card()
                        current_hand.add_card(card)
                        self._update_count(card)
                        if current_hand.is_busted():
                            player_busted = True
                            break

                elif action == 'SP':
                    if current_hand.can_split():
                        # Perform the split
                        card1, card2 = current_hand.cards
                        hand1 = Hand(is_split_aces=(card1.rank == 'A'))
                        hand1.add_card(card1)
                        hand1.is_split = True

                        hand2 = Hand(is_split_aces=(card2.rank == 'A'))
                        hand2.add_card(card2)
                        hand2.is_split = True

                        card = self.deck.deal_card()
                        hand1.add_card(card)
                        self._update_count(card)

                        card = self.deck.deal_card()
                        hand2.add_card(card)
                        self._update_count(card)

                        # Replace current hand with the two new hands
                        hands_to_play.pop(i)
                        hands_to_play.insert(i, hand2)
                        hands_to_play.insert(i, hand1)
                        break
                    else:
                        # Can't split, treat as hit
                        card = self.deck.deal_card()
                        current_hand.add_card(card)
                        self._update_count(card)
                        if current_hand.is_busted():
                            player_busted = True
                            break

                elif action == 'S':
                    # Stand
                    break
                else:
                    # Unrecognized action -> stand
                    break
            else:
                # Exceeded max iterations
                break

            i += 1

        return hand, player_busted, player_blackjack

    def _basic_strategy_action(self, hand):
        """Get the action from basic strategy tables (H, S, D, SP)."""
        dealer_upcard = self.dealer_hand.cards[0]
        dealer_value = CARD_VALUES[dealer_upcard.rank]
        if dealer_upcard.rank == 'A':
            dealer_value = 11

        if hand.can_split():
            player_pair = hand.cards[0].rank
            action = self._get_action_from_pair(player_pair, dealer_value)
        else:
            is_soft = (hand.aces >= 1 and hand.value <= 21)
            if is_soft:
                action = self._get_action_from_soft_total(hand.value, dealer_value)
            else:
                action = self._get_action_from_hard_total(hand.value, dealer_value)

        if action not in ['H', 'S', 'D', 'SP']:
            action = 'S'
        return action

    def _get_action_from_hard_total(self, player_total, dealer_value):
        key = ('hard', player_total, dealer_value)
        if key in self.basic_strategy_cache:
            return self.basic_strategy_cache[key]

        player_total = min(player_total, 21)
        try:
            action = self.hard_totals.loc[player_total, str(int(dealer_value))]
        except KeyError:
            action = 'S'
        self.basic_strategy_cache[key] = action
        return action

    def _get_action_from_soft_total(self, player_total, dealer_value):
        key = ('soft', player_total, dealer_value)
        if key in self.basic_strategy_cache:
            return self.basic_strategy_cache[key]

        player_total = min(player_total, 20)
        try:
            action = self.soft_totals.loc[player_total, str(int(dealer_value))]
        except KeyError:
            action = 'S'
        self.basic_strategy_cache[key] = action
        return action

    def _get_action_from_pair(self, pair_rank, dealer_value):
        key = ('pair', pair_rank, dealer_value)
        if key in self.basic_strategy_cache:
            return self.basic_strategy_cache[key]

        rank_map = {'A': 'A', 'K': '10', 'Q': '10', 'J': '10', '10': '10'}
        pair_rank = rank_map.get(pair_rank, pair_rank)

        try:
            action = self.pairs.loc[pair_rank, str(int(dealer_value))]
        except KeyError:
            action = 'H'
        self.basic_strategy_cache[key] = action
        return action

    def _dealer_play(self):
        """
        Dealer draws until value >= 17 (with Aces counted as 11 if possible).
        Returns True if dealer busts, otherwise False.
        """
        while self.dealer_hand.value < 17:
            card = self.deck.deal_card()
            self.dealer_hand.add_card(card)
            self._update_count(card)
            if self.dealer_hand.is_busted():
                return True
        return False

    def _calculate_reward(self, player_busted, dealer_busted, bet, hand,
                          player_blackjack, dealer_blackjack):
        """Calculate the reward for a single player hand after the round."""
        if hand.doubled:
            bet *= 2

        # Six Card Charlie rule
        if hand.is_six_card_charlie():
            return bet

        # Blackjacks
        if player_blackjack and not dealer_blackjack:
            return 1.5 * bet
        elif dealer_blackjack and not player_blackjack:
            return -bet
        elif player_blackjack and dealer_blackjack:
            return 0  # push

        # Normal outcome
        if player_busted:
            return -bet
        elif dealer_busted:
            return bet
        elif hand.value > self.dealer_hand.value:
            return bet
        elif hand.value < self.dealer_hand.value:
            return -bet
        else:
            return 0  # push

    def _update_count(self, card):
        self.count += COUNT_VALUES[card.rank]

    def _get_observation(self):
        """Return the current observation as a state vector."""
        true_count = self.true_count
        percentage_remaining = len(self.deck.cards) / (52 * self.num_decks)
        dealer_upcard = self.dealer_hand.cards[0]
        dealer_visible_value = CARD_VALUES[dealer_upcard.rank]
        if dealer_upcard.rank == 'A':
            dealer_visible_value = 11
        insurance_offered = 0  # Always 0 in this environment

        state = np.array([
            true_count,
            percentage_remaining,
            dealer_visible_value,
            insurance_offered
        ], dtype=np.float32)
        return state
