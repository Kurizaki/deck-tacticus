import random
import numpy as np
import gym
from gym import spaces
import pandas as pd
import logging

# Set up logging
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


class Card:
    """Represents a single playing card."""
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit
        self.value = CARD_VALUES[self.rank]

    def __str__(self):
        return f"{self.rank}{self.suit}"


class Deck:
    """Represents a shoe containing multiple decks."""
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


class Hand:
    """Represents a hand of cards."""
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
        while self.value > 21 and self.aces:
            self.value -= 10
            self.aces -= 1

    def is_busted(self):
        return self.value > 21

    def has_blackjack(self):
        return self.value == 21 and len(self.cards) == 2 and not self.is_split

    def is_six_card_charlie(self):
        return len(self.cards) == 6 and not self.is_busted()

    def can_double(self):
        return len(self.cards) == 2 and not self.is_split_aces

    def can_split(self):
        # Split if both cards have the same blackjack value
        return (len(self.cards) == 2 and
                CARD_VALUES[self.cards[0].rank] == CARD_VALUES[self.cards[1].rank])

    def __str__(self):
        return ', '.join(str(card) for card in self.cards)


class BlackjackEnv(gym.Env):
    """Custom Blackjack environment with no insurance option."""
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
        # [True count, Percentage of cards remaining, Dealer's visible card value, (No insurance)]
        self.observation_space = spaces.Box(low=np.array([-10, 0, 1, 0]),
                                            high=np.array([10, 1, 11, 0]),
                                            dtype=np.float32)

        # Load basic strategy tables
        self.hard_totals = pd.read_csv('hard_totals.csv', index_col='PlayerTotal')
        self.soft_totals = pd.read_csv('soft_totals.csv', index_col='PlayerTotal')
        self.pairs = pd.read_csv('pairs.csv', index_col='Pair')

        self.basic_strategy_cache = {}

    def minimum_deck_size(self):
        return int(0.25 * 52 * self.num_decks)

    def reset(self):
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
        """Take a bet action and play out the round."""
        # Convert action to bet amount
        self.current_bet = action + 1

        # Player plays
        player_results = []
        for hand in self.player_hands:
            results = self._player_play(hand)
            player_results.append(results)

        # Update count with dealer's hidden card
        self._update_count(self.dealer_hand.cards[1])

        # Check dealer blackjack
        dealer_blackjack = self.dealer_hand.has_blackjack()

        # Dealer plays if no dealer blackjack
        dealer_busted = False
        if not dealer_blackjack:
            dealer_busted = self._dealer_play()

        # Determine reward (no insurance)
        total_reward = 0
        for hand, player_busted, player_blackjack in player_results:
            reward = self._calculate_reward(player_busted, dealer_busted, self.current_bet, hand, player_blackjack, dealer_blackjack)
            total_reward += reward

        # Update true count
        self.true_count = self.count / max(1, len(self.deck.cards) / 52)

        done = True
        observation = self._get_observation()
        return observation, total_reward, done, {}

    def render(self, mode='human'):
        for i, hand in enumerate(self.player_hands):
            print(f"Player's hand {i+1}: {hand} (Value: {hand.value})")
        print(f"Dealer's hand: {self.dealer_hand} (Value: {self.dealer_hand.value})")

    def _deal_initial_cards(self):
        # Player
        player_hand = Hand()
        card = self.deck.deal_card()
        player_hand.add_card(card)
        self._update_count(card)
        card = self.deck.deal_card()
        player_hand.add_card(card)
        self._update_count(card)
        self.player_hands.append(player_hand)

        # Dealer
        card = self.deck.deal_card()
        self.dealer_hand.add_card(card)
        self._update_count(card)

        card = self.deck.deal_card()
        self.dealer_hand.add_card(card)
        # Dealer's second card is hidden until revealed in counting

    def _player_play(self, hand):
        player_blackjack = hand.has_blackjack()
        player_busted = False
        hands_to_play = [hand]
        i = 0

        while i < len(hands_to_play):
            current_hand = hands_to_play[i]
            iteration_count = 0
            max_iterations = 10

            # If split aces and 2 cards, must stand
            if current_hand.is_split_aces and len(current_hand.cards) == 2:
                i += 1
                continue

            while iteration_count < max_iterations:
                iteration_count += 1

                if current_hand.is_six_card_charlie():
                    break  # Automatic win

                if current_hand.is_split_aces and len(current_hand.cards) == 2:
                    # Forced stand
                    break

                action = self._basic_strategy_action(current_hand)

                # If split aces and we have two cards, no actions:
                if current_hand.is_split_aces and len(current_hand.cards) == 2:
                    # stand automatically
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
                        # treat as hit
                        card = self.deck.deal_card()
                        current_hand.add_card(card)
                        self._update_count(card)
                        if current_hand.is_busted():
                            player_busted = True
                            break
                elif action == 'SP':
                    if current_hand.can_split():
                        # Split
                        card1 = current_hand.cards[0]
                        card2 = current_hand.cards[1]

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

                        hands_to_play.pop(i)
                        hands_to_play.insert(i, hand2)
                        hands_to_play.insert(i, hand1)
                        break
                    else:
                        # treat as hit
                        card = self.deck.deal_card()
                        current_hand.add_card(card)
                        self._update_count(card)
                        if current_hand.is_busted():
                            player_busted = True
                            break
                elif action == 'S':
                    break
                else:
                    # Unrecognized action, stand
                    break
            else:
                # If loop hits max iterations
                break

            i += 1

        return hand, player_busted, player_blackjack

    def _basic_strategy_action(self, hand):
        dealer_upcard = self.dealer_hand.cards[0]
        dealer_value = CARD_VALUES[dealer_upcard.rank]
        dealer_value = 11 if dealer_upcard.rank == 'A' else dealer_value

        if hand.can_split():
            player_pair = hand.cards[0].rank
            action = self._get_action_from_pair(player_pair, dealer_value)
        else:
            is_soft = hand.aces >= 1 and hand.value <= 21
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
        # Dealer draws to 16, stands on all 17s
        while self.dealer_hand.value < 17:
            card = self.deck.deal_card()
            self.dealer_hand.add_card(card)
            self._update_count(card)
            if self.dealer_hand.is_busted():
                return True
        return False

    def _calculate_reward(self, player_busted, dealer_busted, bet, hand, player_blackjack, dealer_blackjack):
        if hand.doubled:
            bet *= 2

        # Six Card Charlie
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
        true_count = self.true_count
        percentage_remaining = len(self.deck.cards) / (52 * self.num_decks)
        dealer_visible_value = CARD_VALUES[self.dealer_hand.cards[0].rank]
        dealer_visible_value = 11 if self.dealer_hand.cards[0].rank == 'A' else dealer_visible_value
        # No insurance offered now, so 0
        insurance_offered = 0

        state = np.array([true_count, percentage_remaining, dealer_visible_value, insurance_offered], dtype=np.float32)
        return state
