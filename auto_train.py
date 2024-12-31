import os
import torch
from agent import train, PolicyNetwork, state_size, action_size, hidden_size, device
from blackjack_game import main as test_blackjack

def auto_train_and_test():
    # Ensure Models directory exists
    models_dir = "Models"
    os.makedirs(models_dir, exist_ok=True)

    iterations = 50

    for iteration in range(iterations):
        print(f"Starting training iteration {iteration + 1}...")
        
        # Train the model
        train()
        print("Training completed.")

        # Test the trained model using blackjack_game.py
        print("Testing the trained model...")
        try:
            average_reward = test_blackjack()  # Ensure this function returns a valid average reward
            if average_reward is None:
                raise ValueError("Test result returned None. Ensure blackjack_game.py returns a numeric value.")
        except Exception as e:
            print(f"Error during testing: {e}")
            average_reward = 0.0
        print(f"Iteration {iteration + 1}: Average reward from testing: {average_reward:.2f}")

        # Determine model filename based on average reward
        model_filename = f"betting_policy_net05{average_reward:.2f}.pth"
        model_path = os.path.join(models_dir, model_filename)

        # Check if model already exists
        if os.path.exists(model_path):
            print(f"Model file '{model_filename}' already exists. Skipping save.")
            continue

        # Save the model
        policy_net = PolicyNetwork(state_size, action_size, hidden_size).to(device)
        policy_net.load_state_dict(torch.load('betting_policy_net.pth', map_location=device))
        torch.save(policy_net.state_dict(), model_path)
        print(f"Model saved as '{model_filename}' in '{models_dir}' directory.")

if __name__ == "__main__":
    auto_train_and_test()
