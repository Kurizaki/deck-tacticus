import numpy as np
from blackjack_env import BlackjackEnv, Hand, Card, COUNT_VALUES, Deck
from agent import PolicyNetwork, state_size, action_size, hidden_size, device
from blackjack_env import Deck
import torch

def get_card_value(card):
    """Maps a card string to its blackjack value."""
    card = card.upper()
    if card in ['J', 'Q', 'K']:
        return 10
    elif card == 'A':
        return 11
    else:
        return int(card)

def main():
    print("Welcome to the Real-World Blackjack Simulator!")
    print("Type 'exit' at any time to quit. Type 'sh' to reshuffle and reset count.")
    print("Enter your hand as a space-separated list of cards (e.g., 'A 5').")

    # Load the trained policy network
    policy_net = PolicyNetwork(state_size, action_size, hidden_size).to(device)
    policy_net.load_state_dict(torch.load('betting_policy_net.pth', map_location=device))
    policy_net.eval()

    env = BlackjackEnv(num_decks=8)
    count = 0

    while True:
        # Check for reshuffle command
        player_input = input("Your command or hand: ").strip()
        if player_input.lower() == 'exit':
            break
        elif player_input.lower() == 'sh':
            env.deck = Deck(num_decks=env.num_decks)  # Reinitialize the deck
            count = 0  # Reset the count
            print("Deck reshuffled and count reset.")
            continue

        # Step 1: Input player's hand
        player_cards = player_input.split()
        player_hand = Hand()
        for card in player_cards:
            player_hand.add_card(Card(rank=card.strip(), suit=''))

        # Step 2: Input dealer's upcard
        dealer_card_input = input("Enter the dealer's upcard (e.g., '10' or 'A'): ").strip()
        if dealer_card_input.lower() == 'exit':
            break
        dealer_card_value = get_card_value(dealer_card_input)

        # Step 3: Calculate the recommended move using basic strategy
        is_soft = player_hand.aces > 0 and player_hand.value <= 21
        if player_hand.can_split():
            player_pair = player_hand.cards[0].rank
            action = env._get_action_from_pair(player_pair, dealer_card_value)
        elif is_soft:
            action = env._get_action_from_soft_total(player_hand.value, dealer_card_value)
        else:
            action = env._get_action_from_hard_total(player_hand.value, dealer_card_value)

        print(f"Recommended move: {action}")

        # Step 4: Simulate the round based on user inputs
        while action == 'H':
            new_card = input("Enter the new card you drew: ").strip()
            if new_card.lower() == 'exit':
                return
            player_hand.add_card(Card(rank=new_card.strip(), suit=''))
            if player_hand.is_busted():
                print("You busted!")
                break

            is_soft = player_hand.aces > 0 and player_hand.value <= 21
            if is_soft:
                action = env._get_action_from_soft_total(player_hand.value, dealer_card_value)
            else:
                action = env._get_action_from_hard_total(player_hand.value, dealer_card_value)

            print(f"Recommended move: {action}")

        # Input remaining cards in the dealer's hand
        dealer_cards_input = input("Enter the remaining dealer's cards (space-separated): ").strip()
        if dealer_cards_input.lower() == 'exit':
            break
        dealer_cards = dealer_cards_input.split()
        dealer_hand = Hand()
        dealer_hand.add_card(Card(rank=dealer_card_input.strip(), suit=''))
        for card in dealer_cards:
            dealer_hand.add_card(Card(rank=card.strip(), suit=''))

        # Step 5: Update count and calculate true count
        for card in player_hand.cards + dealer_hand.cards:
            count += COUNT_VALUES[card.rank]

        true_count = count / (len(env.deck.cards) / 52)

        # Step 6: Suggest bet for next round based on the policy network
        state = np.array([true_count, len(env.deck.cards) / (52 * env.num_decks), dealer_card_value, 0], dtype=np.float32)
        state = torch.from_numpy(state).float().to(device)
        with torch.no_grad():
            action_probs = policy_net(state)
        bet_action = torch.argmax(action_probs).item()
        bet = bet_action + 1
        print(f"Current count: {count}, True count: {true_count}")
        print(f"Suggested bet for next round: {bet} units")


if __name__ == '__main__':
    main()
