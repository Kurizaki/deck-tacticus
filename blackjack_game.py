import os
import csv
import torch
import numpy as np
from blackjack_env import BlackjackEnv, Hand
from agent import PolicyNetwork, state_size, action_size, hidden_size, device

LOGGING = False  # Set to False to disable logging to CSV files

class Player:
    """Represents a player in the game."""
    def __init__(self, name="Player", policy_net=None):
        self.name = name
        self.policy_net = policy_net

    def make_bet_decision(self, state):
        """Makes a bet decision using the policy network based on current state."""
        state = torch.from_numpy(state).float().to(device)
        with torch.no_grad():
            action_probs = self.policy_net(state)
        m = torch.distributions.Categorical(action_probs)
        action = m.sample().item()  # action in [0..9]
        return action  # 0->bet=1 unit, 9->bet=10 units

def save_shoe_state(env, game_number, round_number):
    """Saves the current shoe (remaining cards) to a CSV file."""
    if not LOGGING:
        return
    # File name for the shoe state at the start of this round
    shoe_filename = f"SimulationLogs/game_{game_number}_round_{round_number}_shoe.csv"
    with open(shoe_filename, mode='w', newline='', encoding='utf-8') as shoe_file:
        writer = csv.writer(shoe_file)
        writer.writerow(["Card"])
        for card in env.deck.cards:
            writer.writerow([str(card)])

def main():
    # Ensure SimulationLogs directory exists if logging is active
    if LOGGING and not os.path.exists('SimulationLogs'):
        os.makedirs('SimulationLogs')

    # Load the trained policy network
    policy_net = PolicyNetwork(state_size, action_size, hidden_size).to(device)
    policy_net.load_state_dict(torch.load('betting_policy_net.pth', map_location=device))
    policy_net.eval()

    env = BlackjackEnv(num_decks=8)
    player = Player(policy_net=policy_net)

    num_games = 1000       # Number of separate "games" (sessions)
    rounds_per_game = 250  # Rounds per game session
    game_profits = []

    for game in range(num_games):
        total_profit = 0

        # Only open a CSV log if LOGGING is True
        if LOGGING:
            log_filename = f"SimulationLogs/game_{game+1}.csv"
            logfile = open(log_filename, mode='w', newline='', encoding='utf-8')
            writer = csv.writer(logfile)
            # Write header row
            writer.writerow([
                "Game", "Round", "Bet", "Reward", 
                "PlayerCards", "PlayerValue",
                "DealerCards", "DealerValue", 
                "TrueCount", "Outcome"
            ])

        for round_num in range(rounds_per_game):
            # Reset the environment for a new round
            state = env.reset()

            # Save the current shoe before making a decision if logging is active
            save_shoe_state(env, game+1, round_num+1)

            # The agent decides how much to bet based on the current state
            bet_action = player.make_bet_decision(state)
            bet = bet_action + 1

            # Step through the environment
            next_state, reward, done, info = env.step(bet_action)
            total_profit += reward

            # Gather details after the round finishes
            player_cards = [str(card) for card in env.player_hands[0].cards]
            dealer_cards = [str(card) for card in env.dealer_hand.cards]
            player_value = env.player_hands[0].value
            dealer_value = env.dealer_hand.value

            # Determine outcome from reward
            if reward > 0:
                outcome = "Win"
            elif reward < 0:
                outcome = "Loss"
            else:
                outcome = "Push"

            current_true_count = env.true_count

            # Write this round's details to the game's CSV if logging is active
            if LOGGING:
                writer.writerow([
                    game+1, 
                    round_num+1, 
                    bet, 
                    reward,
                    ";".join(player_cards), 
                    player_value,
                    ";".join(dealer_cards), 
                    dealer_value, 
                    f"{current_true_count:.2f}",
                    outcome
                ])

        if LOGGING:
            logfile.close()

        game_profits.append(total_profit)
        
        if (game + 1) % 100 == 0:
            # Print results every game
            print(f"Game {game+1}: Profit/Loss = {total_profit} units")

    # After all games, print some statistics
    average_profit = sum(game_profits) / num_games
    median_profit = np.median(game_profits)
    highest_profit = max(game_profits)
    lowest_profit = min(game_profits)

    print("\n--- Summary ---")
    print(f"Average profit/loss per game: {average_profit:.2f} units")
    print(f"Median profit: {median_profit:.2f} units")
    print(f"Highest profit: {highest_profit} units")
    print(f"Lowest profit: {lowest_profit} units")

    return average_profit  # Return average profit for compatibility with auto_train_and_test

if __name__ == '__main__':
    main()
