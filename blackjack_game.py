#  ____                   __          ______                 __                                  
# /\  _`\                /\ \        /\__  _\               /\ \__  __                           
# \ \ \/\ \     __    ___\ \ \/'\    \/_/\ \/    __      ___\ \ ,_\/\_\    ___   __  __    ____  
#  \ \ \ \ \  /'__`\ /'___\ \ , <       \ \ \  /'__`\   /'___\ \ \/\/\ \  /'___\/\ \/\ \  /',__\ 
#   \ \ \_\ \/\  __//\ \__/\ \ \\`\      \ \ \/\ \L\.\_/\ \__/\ \ \_\ \ \/\ \__/\ \ \_\ \/\__, `\
#    \ \____/\ \____\ \____\\ \_\ \_\     \ \_\ \__/.\_\ \____\\ \__\\ \_\ \____\\ \____/\/\____/
#     \/___/  \/____/\/____/ \/_/\/_/      \/_/\/__/\/_/\/____/ \/__/ \/_/\/____/ \/___/  \/___/ 
# By Kurizaki & Sprudello

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import numpy as np
from blackjack_env import BlackjackEnv

# ============================================================
# Configuration and Hyperparameters
# ============================================================

# State representation: [true_count, percentage_remaining, dealer_upcard_value, insurance_flag]
STATE_SIZE: int = 4

# Number of possible bet actions: 5 (0-4) corresponding to bets of 1-5 units
ACTION_SIZE: int = 5

# Neural network parameters
HIDDEN_SIZE: int = 128
LEARNING_RATE: float = 1e-4
GAMMA: float = 1.0  # Not used as each episode is one step
NUM_EPISODES: int = 300_000

# Exploration parameters for epsilon-greedy policy
EPSILON_START: float = 1.0
EPSILON_END: float = 0.01
EPSILON_DECAY: float = 0.999

# Device configuration: use GPU if available
DEVICE: torch.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Training on device: {DEVICE}")

# ============================================================
# Policy Network Definition
# ============================================================

class PolicyNetwork(nn.Module):
    """
    Neural network approximating the policy for betting in Blackjack.
    
    Architecture:
        - Input layer: state_size
        - Hidden layers: two layers with hidden_size units and tanh activation
        - Output layer: action_size units with softmax activation to output probabilities
    """
    def __init__(self, state_size: int, action_size: int, hidden_size: int = 128):
        super(PolicyNetwork, self).__init__()
        self.fc1: nn.Linear = nn.Linear(state_size, hidden_size)
        self.fc2: nn.Linear = nn.Linear(hidden_size, hidden_size)
        self.action_head: nn.Linear = nn.Linear(hidden_size, action_size)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass through the network.
        
        Args:
            x (torch.Tensor): Input state tensor.
        
        Returns:
            torch.Tensor: Action probabilities.
        """
        x = torch.tanh(self.fc1(x))
        x = torch.tanh(self.fc2(x))
        action_logits: torch.Tensor = self.action_head(x)
        action_probs: torch.Tensor = F.softmax(action_logits, dim=-1)
        return action_probs

# ============================================================
# Training Function
# ============================================================

def train():
    """
    Train the PolicyNetwork using reinforcement learning on the Blackjack environment.
    The network learns to recommend bet sizes based on the current game state.
    """
    # Initialize environment and policy network
    env: BlackjackEnv = BlackjackEnv(num_decks=8)
    policy_net: PolicyNetwork = PolicyNetwork(STATE_SIZE, ACTION_SIZE, HIDDEN_SIZE).to(DEVICE)
    optimizer: optim.Optimizer = optim.Adam(policy_net.parameters(), lr=LEARNING_RATE)

    total_rewards: list = []
    epsilon: float = EPSILON_START

    for episode in range(1, NUM_EPISODES + 1):
        # Reset environment and get initial state
        state: np.ndarray = env.reset()
        state_tensor: torch.Tensor = torch.from_numpy(state).float().to(DEVICE)

        # Compute action probabilities from the policy network
        action_probs: torch.Tensor = policy_net(state_tensor)

        # Epsilon-greedy action selection for betting
        if np.random.rand() < epsilon:
            # Explore: choose a random action
            action: torch.Tensor = torch.tensor([np.random.choice(ACTION_SIZE)], device=DEVICE)
        else:
            # Exploit: choose the best action based on policy
            distribution: torch.distributions.Categorical = torch.distributions.Categorical(action_probs)
            action: torch.Tensor = distribution.sample()

        # Translate action index to bet amount (0-4 -> 1-5 units)
        bet_action: int = action.item()

        # Execute the action in the environment
        next_state, reward, done, info = env.step(bet_action)
        total_reward: float = reward

        # Compute the loss: negative log probability weighted by the reward
        log_prob: torch.Tensor = torch.log(action_probs[action])
        loss: torch.Tensor = -log_prob * total_reward

        # Perform backpropagation and update the policy network
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        # Record the reward for tracking performance
        total_rewards.append(total_reward)

        # Decay epsilon to reduce exploration over time
        epsilon = max(EPSILON_END, epsilon * EPSILON_DECAY)

        # Print progress every 1000 episodes
        if episode % 1000 == 0:
            avg_reward: float = np.mean(total_rewards[-1000:])
            print(f"Episode {episode}, Average Reward: {avg_reward:.4f}, Epsilon: {epsilon:.4f}")

    # Save the trained policy network
    torch.save(policy_net.state_dict(), 'betting_policy_net.pth')
    print("Training completed and model saved.")

# ============================================================
# Entry Point
# ============================================================

if __name__ == '__main__':
    train()
