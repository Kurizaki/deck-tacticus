# Setup

## Dependencies

- Python 3.12.8
- pytorch ([with CUDA support](https://pytorch.org/)) You can copy the required pip install command from here

  !!!Important for Windows users, you have to install the CUDA Toolkit to run everything via your NVIDIA GPU!!!
- numpy
- pandas
- gym

## Anaconda

Download and install Anaconda

There is a deck-tacticus-env.yml import this to a new environment in anaconda, and you should be ready to go.

Create environment via console: `conda env create -f deck-tacticus-env.yml`

Activate environment via console: `conda activate deck-tacticus`

You should be ready to go.

## Run the different scrips

You can run files via a runner, or via console with `python file-name.py`


`agent.py` Trains a new agent

`blackjack_game.py` Tests the model in a real world like scenario.

`intepret_count.py` You want to try it in the real world? Run this.


