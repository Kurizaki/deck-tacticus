#  ____                   __          ______                 __                                  
# /\  _`\                /\ \        /\__  _\               /\ \__  __                           
# \ \ \/\ \     __    ___\ \ \/'\    \/_/\ \/    __      ___\ \ ,_\/\_\    ___   __  __    ____  
#  \ \ \ \ \  /'__`\ /'___\ \ , <       \ \ \  /'__`\   /'___\ \ \/\/\ \  /'___\/\ \/\ \  /',__\ 
#   \ \ \_\ \/\  __//\ \__/\ \ \\`\      \ \ \/\ \L\.\_/\ \__/\ \ \_\ \ \/\ \__/\ \ \_\ \/\__, `\
#    \ \____/\ \____\ \____\\ \_\ \_\     \ \_\ \__/.\_\ \____\\ \__\\ \_\ \____\\ \____/\/\____/
#     \/___/  \/____/\/____/ \/_/\/_/      \/_/\/__/\/_/\/____/ \/__/ \/_/\/____/ \/___/  \/___/ 
# By Kurizaki & Sprudello

import subprocess
import time

# ============================================================
# Configuration Parameters
# ============================================================

START_EPISODES = 10_000     # Starting number of episodes
MAX_EPISODES = 150_000      # Maximum number of episodes
EPISODE_STEP = 10_000       # Step size for increasing the number of episodes
LOG_FILE = "training_results.txt"
TRAINING_SCRIPT = "agent.py"

# ============================================================
# Helper Function to Parse Average Reward
# ============================================================

def parse_average_reward(output: str) -> float:
    """
    Parse the average reward from the training script's output.
    The script prints lines like:
    "Episode X, Average Reward: YYYYY"
    We find the last occurrence of "Average Reward:" and return the associated value.
    """
    avg_reward = None
    for line in output.split("\n"):
        if "Average Reward:" in line:
            parts = line.split("Average Reward:")
            if len(parts) > 1:
                # Extract the numeric part after "Average Reward:"
                avg_reward_str = parts[1].split(",")[0].strip()
                avg_reward = float(avg_reward_str)
    return avg_reward

# ============================================================
# Main Loop
# ============================================================

# Initialize the log file with headers
with open(LOG_FILE, "w") as log_file:
    log_file.write("Episodes\tAverageReward\tDuration(s)\n")

# Iterate over different episode counts
for episodes in range(START_EPISODES, MAX_EPISODES + 1, EPISODE_STEP):
    print(f"Starting training with {episodes} episodes...")
    start_time = time.time()

    # Run the training script with the current number of episodes
    result = subprocess.run(
        ["python3", TRAINING_SCRIPT, "--num_episodes", str(episodes)],
        capture_output=True,
        text=True
    )

    duration = time.time() - start_time

    # Handle the results
    if result.returncode == 0:
        avg_reward = parse_average_reward(result.stdout.strip())
        if avg_reward is not None:
            # Log the successful run
            with open(LOG_FILE, "a") as log_file:
                log_file.write(f"{episodes}\t{avg_reward:.4f}\t{duration:.2f}\n")
        else:
            print(f"Warning: Could not extract Average Reward for {episodes} episodes.")
    else:
        print(f"Error running script for {episodes} episodes.")
        with open(LOG_FILE, "a") as log_file:
            log_file.write(f"{episodes}\tERROR\t{duration:.2f}\n")
