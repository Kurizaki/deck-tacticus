import subprocess
import time

# Parameters for automation
start_episodes = 10000  # Start number of episodes
max_episodes = 150000   # Maximum number of episodes
episode_step = 10000    # Step size for increasing episodes
log_file = "training_results.txt"  # Log file for results
training_script = "agent.py"  # The updated training script

# Initialize the log file
with open(log_file, "w") as log:
    log.write("Episodes\tAverageReward\tDuration(s)\n")

# Loop through different episode settings
for episodes in range(start_episodes, max_episodes + 1, episode_step):
    print(f"Starting training with {episodes} episodes...")
    start_time = time.time()
    
    # Run the training script with the current number of episodes
    result = subprocess.run(
        ["python3", training_script, "--num_episodes", str(episodes)],
        capture_output=True,
        text=True
    )
    
    end_time = time.time()
    duration = end_time - start_time

    # Process the results
    if result.returncode == 0:
        output = result.stdout.strip()
        try:
            avg_reward = None
            # Extract the last reported "Average Reward" from the output
            # The training script prints lines like:
            # "Episode X, Average Reward: YYYYY"
            for line in output.split("\n"):
                if "Average Reward:" in line:
                    parts = line.split("Average Reward:")
                    if len(parts) > 1:
                        # The value after "Average Reward:" might be something like " 0.1234"
                        avg_reward_str = parts[1].split(",")[0].strip()  # Just in case there's a comma
                        avg_reward = float(avg_reward_str)
            
            if avg_reward is not None:
                with open(log_file, "a") as log:
                    log.write(f"{episodes}\t{avg_reward:.4f}\t{duration:.2f}\n")
            else:
                print(f"Warning: Could not extract Average Reward for {episodes} episodes.")
        except Exception as e:
            print(f"Error processing results for {episodes} episodes: {e}")
    else:
        print(f"Error running script for {episodes} episodes.")
        with open(log_file, "a") as log:
            log.write(f"{episodes}\tERROR\t{duration:.2f}\n")