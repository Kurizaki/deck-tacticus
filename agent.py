# agent.py
 

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import numpy as np
from blackjack_env import BlackjackEnv


#BASEMODEL
# Hyperparameters
state_size = 4         # [true_count, percentage_remaining, dealer_upcard_value, 0(no_insurance)]
action_size = 5        # Only 5 bet actions (0-4) corresponding to bets of 1-5 units
hidden_size = 128
learning_rate = 1e-4
gamma = 1.0            # Each episode is essentially one step
num_episodes = 350_000  # Increase the number of episodes for better results

# Exploration parameters
epsilon_start = 1.0
epsilon_end = 0.01
epsilon_decay = 0.999

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Training on device: {device}")

class PolicyNetwork(nn.Module):
    #Neural network approximating the policy.
    def __init__(self, state_size, action_size, hidden_size=128):
        super(PolicyNetwork, self).__init__()
        self.fc1 = nn.Linear(state_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.action_head = nn.Linear(hidden_size, action_size)

    def forward(self, x):
        x = torch.tanh(self.fc1(x))
        x = torch.tanh(self.fc2(x))
        action_logits = self.action_head(x)
        action_probs = F.softmax(action_logits, dim=-1)
        return action_probs

def train():
    env = BlackjackEnv(num_decks=8)
    policy_net = PolicyNetwork(state_size, action_size, hidden_size).to(device)
    optimizer = optim.Adam(policy_net.parameters(), lr=learning_rate)

    total_rewards = []
    epsilon = epsilon_start

    for episode in range(1, num_episodes + 1):
        state = env.reset()
        state = torch.from_numpy(state).float().to(device)

        # Compute action probabilities
        action_probs = policy_net(state)

        # Epsilon-greedy action selection for bet
        if np.random.rand() < epsilon:
            action = torch.tensor([np.random.choice(action_size)], device=device)
        else:
            m = torch.distributions.Categorical(action_probs)
            action = m.sample()

        # Perform action in the environment
        # action in [0..4] -> bet = action + 1 in [1..5]
        bet_action = action.item()  # This corresponds to bet = action + 1
        next_state, reward, done, info = env.step(bet_action)
        total_reward = reward

        # Compute loss
        log_prob = torch.log(action_probs[action])
        loss = -log_prob * total_reward

        # Update policy network
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        total_rewards.append(total_reward)

        # Decay epsilon
        epsilon = max(epsilon_end, epsilon * epsilon_decay)

        # Print progress every 1000 episodes
        if episode % 10000 == 0:
            avg_reward = sum(total_rewards[-10000:]) / 10000
            print(f"Episode {episode}, Average Reward: {avg_reward:.4f}, Epsilon: {epsilon:.4f}")

    # Save the trained model
    torch.save(policy_net.state_dict(), 'betting_policy_net.pth')
    print("Training completed and model saved.")


if __name__ == '__main__':
    train()