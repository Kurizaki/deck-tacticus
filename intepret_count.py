#  ____                   __          ______                 __                                  
# /\  _`\                /\ \        /\__  _\               /\ \__  __                           
# \ \ \/\ \     __    ___\ \ \/'\    \/_/\ \/    __      ___\ \ ,_\/\_\    ___   __  __    ____  
#  \ \ \ \ \  /'__`\ /'___\ \ , <       \ \ \  /'__`\   /'___\ \ \/\/\ \  /'___\/\ \/\ \  /',__\ 
#   \ \ \_\ \/\  __//\ \__/\ \ \\`\      \ \ \/\ \L\.\_/\ \__/\ \ \_\ \ \/\ \__/\ \ \_\ \/\__, `\
#    \ \____/\ \____\ \____\\ \_\ \_\     \ \_\ \__/.\_\ \____\\ \__\\ \_\ \____\\ \____/\/\____/
#     \/___/  \/____/\/____/ \/_/\/_/      \/_/\/__/\/_/\/____/ \/__/ \/_/\/____/ \/___/  \/___/ 
# By Kurizaki & Sprudello

import os
import csv
import torch
import numpy as np
from typing import List
from blackjack_env import BlackjackEnv, Hand, Card, COUNT_VALUES, Deck
from agent import PolicyNetwork, STATE_SIZE, ACTION_SIZE, HIDDEN_SIZE, DEVICE

# ============================================================
# Configuration
# ============================================================

LOGGING: bool = False  # Set to False to disable logging to CSV files
MODEL_PATH: str = 'betting_policy_net.pth'
SIMULATION_DIR: str = 'SimulationLogs'

# ============================================================
# Helper Functions
# ============================================================

def get_card_value(card: str) -> int:
    """
    Maps a card string to its blackjack value.
    
    Args:
        card (str): The rank of the card (e.g., 'A', 'K', '5').
    
    Returns:
        int: The blackjack value of the card.
    """
    card = card.upper()
    if card in ['J', 'Q', 'K']:
        return 10
    elif card == 'A':
        return 11
    else:
        try:
            return int(card)
        except ValueError:
            raise ValueError(f"Invalid card rank: {card}")

def save_shoe_state(env: BlackjackEnv, game_number: int, round_number: int) -> None:
    """
    Saves the current shoe (remaining cards) to a CSV file.
    
    Args:
        env (BlackjackEnv): The Blackjack environment instance.
        game_number (int): The current game number.
        round_number (int): The current round number within the game.
    """
    if not LOGGING:
        return

    shoe_filename: str = f"{SIMULATION_DIR}/game_{game_number}_round_{round_number}_shoe.csv"
    with open(shoe_filename, mode='w', newline='', encoding='utf-8') as shoe_file:
        writer = csv.writer(shoe_file)
        writer.writerow(["Card"])
        for card in env.deck.cards:
            writer.writerow([str(card)])

# ============================================================
# Player Class
# ============================================================

class Player:
    """
    Represents a player in the Blackjack game, utilizing a trained policy network
    to make betting decisions based on the current state.
    """
    def __init__(self, name: str = "Player", policy_net: PolicyNetwork = None):
        """
        Initializes the Player instance.
        
        Args:
            name (str): The name of the player.
            policy_net (PolicyNetwork): The trained policy network for making bet decisions.
        """
        self.name: str = name
        self.policy_net: PolicyNetwork = policy_net

    def make_bet_decision(self, state: np.ndarray) -> int:
        """
        Makes a bet decision using the policy network based on the current state.
        
        Args:
            state (np.ndarray): The current state vector.
        
        Returns:
            int: The selected action index (0-4), corresponding to bets of 1-5 units.
        """
        state_tensor: torch.Tensor = torch.from_numpy(state).float().to(DEVICE)
        with torch.no_grad():
            action_probs: torch.Tensor = self.policy_net(state_tensor)
        distribution: torch.distributions.Categorical = torch.distributions.Categorical(action_probs)
        action: int = distribution.sample().item()  # Action in [0..4]
        return action  # 0->bet=1 unit, 4->bet=5 units

# ============================================================
# Main Execution
# ============================================================

def main() -> None:
    """
    Main function to run the Blackjack simulation with Bet AI recommendations.
    """
    print("Welcome to the Real-World Blackjack Simulator!")
    print("Type 'exit' at any time to quit. Type 'sh' to reshuffle and reset count.")
    print("Enter your hand as a space-separated list of cards (e.g., 'A 5').")

    # Ensure SimulationLogs directory exists if logging is active
    if LOGGING and not os.path.exists(SIMULATION_DIR):
        os.makedirs(SIMULATION_DIR)

    # Load the trained policy network
    try:
        policy_net: PolicyNetwork = PolicyNetwork(STATE_SIZE, ACTION_SIZE, HIDDEN_SIZE).to(DEVICE)
        policy_net.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
        policy_net.eval()
    except Exception as e:
        print(f"Error loading the policy network: {e}")
        return

    # Initialize the Blackjack environment
    env: BlackjackEnv = BlackjackEnv(num_decks=8)
    player: Player = Player(policy_net=policy_net)
    count: int = 0  # Running count

    while True:
        # Get player's command or hand
        player_input: str = input("Your command or hand: ").strip()
        if player_input.lower() == 'exit':
            print("Exiting the simulator. Goodbye!")
            break
        elif player_input.lower() == 'sh':
            env.deck = Deck(num_decks=env.num_decks)  # Reinitialize the deck
            count = 0  # Reset the count
            print("Deck reshuffled and count reset.")
            continue

        # Parse player's hand
        try:
            player_cards: List[str] = player_input.split()
            player_hand: Hand = Hand()
            for card_str in player_cards:
                card_rank: str = card_str.strip()
                if not card_rank:
                    continue
                # Assuming default suit as empty string since suit is irrelevant for value calculation
                player_hand.add_card(Card(rank=card_rank, suit=''))
        except ValueError as ve:
            print(f"Error: {ve}")
            continue

        # Get dealer's upcard
        dealer_card_input: str = input("Enter the dealer's upcard (e.g., '10' or 'A'): ").strip()
        if dealer_card_input.lower() == 'exit':
            print("Exiting the simulator. Goodbye!")
            break
        try:
            dealer_card_rank: str = dealer_card_input.strip()
            dealer_card: Card = Card(rank=dealer_card_rank, suit='')
            dealer_value: int = get_card_value(dealer_card_rank)
            env.dealer_hand = Hand()
            env.dealer_hand.add_card(dealer_card)
        except ValueError as ve:
            print(f"Error: {ve}")
            continue

        # Calculate the recommended move using basic strategy
        try:
            is_soft: bool = player_hand.aces > 0 and player_hand.value <= 21
            if player_hand.can_split():
                player_pair: str = player_hand.cards[0].rank
                action: str = env._get_action_from_pair(player_pair, dealer_value)
            elif is_soft:
                action: str = env._get_action_from_soft_total(player_hand.value, dealer_value)
            else:
                action: str = env._get_action_from_hard_total(player_hand.value, dealer_value)
            print(f"Recommended move: {action}")
        except Exception as e:
            print(f"Error determining recommended move: {e}")
            continue

        # Simulate the round based on user inputs
        while action == 'H':
            new_card_input: str = input("Enter the new card you drew: ").strip()
            if new_card_input.lower() == 'exit':
                print("Exiting the simulator. Goodbye!")
                return
            try:
                new_card_rank: str = new_card_input.strip()
                new_card: Card = Card(rank=new_card_rank, suit='')
                player_hand.add_card(new_card)
                if player_hand.is_busted():
                    print("You busted!")
                    break
            except ValueError as ve:
                print(f"Error: {ve}")
                continue

            # Re-evaluate the recommended action after drawing a new card
            try:
                is_soft = player_hand.aces > 0 and player_hand.value <= 21
                if is_soft:
                    action = env._get_action_from_soft_total(player_hand.value, dealer_value)
                else:
                    action = env._get_action_from_hard_total(player_hand.value, dealer_value)
                print(f"Recommended move: {action}")
            except Exception as e:
                print(f"Error determining recommended move: {e}")
                break

        # Get remaining dealer's cards
        dealer_cards_input: str = input("Enter the remaining dealer's cards (space-separated): ").strip()
        if dealer_cards_input.lower() == 'exit':
            print("Exiting the simulator. Goodbye!")
            break
        try:
            dealer_remaining_cards: List[str] = dealer_cards_input.split()
            for card_str in dealer_remaining_cards:
                card_rank: str = card_str.strip()
                if not card_rank:
                    continue
                card: Card = Card(rank=card_rank, suit='')
                env.dealer_hand.add_card(card)
        except ValueError as ve:
            print(f"Error: {ve}")
            continue

        # Update count with all dealt cards
        try:
            for card in player_hand.cards + env.dealer_hand.cards:
                count += COUNT_VALUES.get(card.rank, 0)
        except KeyError as ke:
            print(f"Unknown card rank encountered during count update: {ke}")
            continue

        # Calculate true count
        remaining_cards: int = len(env.deck.cards)
        try:
            true_count: float = count / (remaining_cards / 52)
        except ZeroDivisionError:
            true_count = count  # If no remaining cards, true count equals running count

        # Suggest bet for next round based on the policy network
        try:
            state: np.ndarray = np.array([
                true_count,
                remaining_cards / (52 * env.num_decks),
                dealer_value,
                0  # No insurance offered
            ], dtype=np.float32)
            state_tensor: torch.Tensor = torch.from_numpy(state).float().to(DEVICE)
            with torch.no_grad():
                action_probs: torch.Tensor = policy_net(state_tensor)
            bet_action: int = torch.argmax(action_probs).item()
            bet: int = bet_action + 1
            print(f"Current count: {count}, True count: {true_count:.2f}")
            print(f"Suggested bet for next round: {bet} units\n")
        except Exception as e:
            print(f"Error suggesting bet: {e}")
            continue

if __name__ == '__main__':
    main()
