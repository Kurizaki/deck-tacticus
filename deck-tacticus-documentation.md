### Project Documentation

**Group Name:** deck-tacticus  
**Members:** Julius Burlet, Keanu Koelewijn

### Summary Table:

| Date       | Version | Summary                                                                               |
| ---------- | ------- | ------------------------------------------------------------------------------------- |
| 2024-11-15 | 0.0.1   | Initial setup, requirements for simulation and Bet AI defined.                        |
| 2024-11-22 | 0.0.2   | Basic Blackjack environment implemented. Card and Deck classes integrated.            |
| 2024-12-06 | 0.0.3   | Policy network for Bet AI developed and integrated with simulation for betting logic. |
| 2024-12-13 | 0.1.0   | Logging, training scripts, and result analysis implemented.                           |

## 1. Inform

### 1.1 Our Project

We are building a comprehensive Blackjack simulation with integrated card counting and Bet AI. The simulation supports multiple-deck Blackjack, applies a Hi-Lo counting strategy, and uses a policy network to recommend optimal bet sizes. This system addresses user stories related to simulating the game, tracking the deck, supporting multiple decks, and recommending bets dynamically.

### 1.2 User Stories

**Note:** Each work package corresponds to one or more user stories, reflecting end-user needs. These user stories define our incremental development path.

| US-№ | Priority | Type       | Description                                                                                     |
| ---- | -------- | ---------- | ----------------------------------------------------------------------------------------------- |
| 1    | Must     | Functional | As a **player**, I want to simulate Blackjack games to test strategies (Game simulation).       |
| 2    | Must     | Functional | As a **developer**, I want to implement a card counting algorithm to track the deck (Counting). |
| 3    | Must     | Functional | As a **player**, I want to support variable deck configurations (Multi-deck capability).        |
| 4    | Must     | Functional | As a **player**, I want Bet AI to recommend bet sizes based on the game state (Bet AI).         |
| 5    | Can      | Functional | As a **player**, I want future AI for move optimization (Hit/Stand/Double) (Future expansion).  |

### 1.3 Test Cases

| TC-№ | Linked US  | Initial State             | Input                                | Expected Output                                    |
| ---- | ---------- | ------------------------- | ------------------------------------ | -------------------------------------------------- |
| 1.1  | US-1, US-3 | Empty simulation          | Initialize game with N decks         | Correct deck composition & shuffle                 |
| 1.2  | US-1       | Cards dealt to player     | Player/dealer receive cards          | Accurate initial deal & value calculation          |
| 2.1  | US-2       | Deck in play              | Multiple cards dealt in sequence     | Running and true counts update correctly           |
| 3.1  | US-4       | Bet AI integrated         | Provide game state to policy network | Policy network returns valid bet recommendations   |
| 3.2  | US-4       | Multiple rounds simulated | Run simulation with Bet AI           | Bet recommendations improve as training progresses |
| 4.1  | US-1, US-4 | Logged simulation         | Run long simulation                  | Results logged; can analyze performance            |
| 4.2  | US-1, US-3 | Edge cases (low cards)    | Deck nearly depleted                 | Deck rebuilds, count resets, no errors             |

### 1.4 Diagrams

- **System Flow Diagram:** Shows how the simulation, card counting, and Bet AI modules interact.
- **Gantt Chart:** Tracks completion of user stories (work packages) over time.
- **Architecture Diagram:** Depicts the modular structure of environment, cards, counting, and AI.

## 2. Plan

**User stories as Work Packages:**

| US-№ | Deadline   | Responsible | Description (Work Package)                                              | Planned Time |
| ---- | ---------- | ----------- | ----------------------------------------------------------------------- | ------------ |
| 1    | 2024-11-22 | Keanu       | Implement base Blackjack rules & multi-deck simulation                  | 8 hours      |
| 2    | 2024-11-22 | Julius      | Integrate card counting algorithm & ensure accurate true count          | 6 hours      |
| 3    | 2024-12-06 | Keanu       | Extend the simulation to support variable deck configurations           | 4 hours      |
| 4    | 2024-12-13 | Team        | Implement initial Bet AI (policy network) and integrate into simulation | 8 hours      |
| 5    | TBD        | Team        | Move optimization AI (Hit/Stand/Double) planned for a later phase       | TBD          |

**Total Planned Time so far:** 26 hours

## 3. Decide

- Develop the basic simulation (US-1) before advanced AI (US-4).
- Use the Hi-Lo counting method (US-2).
- Support multi-deck configurations from the start (US-3).
- Choose PyTorch + CUDA for Bet AI training (US-4).
- Move optimization (US-5) is postponed until the betting system is proven.

## 4. Implement

**Track Actual Times:**

| US-№ | Date       | Responsible | Planned Time | Actual Time |
| ---- | ---------- | ----------- | ------------ | ----------- |
| 1    | 2024-11-15 | Keanu       | 8h           | 5h          |
| 2    | 2024-11-15 | Julius      | 6h           | 4.5h        |
| 3    | 2024-11-22 | Team        | 4h           | 2h          |
| 4    | 2024-12-13 | Team        | 8h           | 13.5h       |
| 5    | Future     | Team        | TBD          | TBD         |

## 5. Review

### 5.1 Test Log

| TC-№ | US-№ | Date       | Result | Tester |
| ---- | ---- | ---------- | ------ | ------ |
| 1.1  | 1,3  | 2024-12-13 | Pass   | Julius |
| 1.2  | 1    | 2024-12-13 | Pass   | Keanu  |
| 2.1  | 2    | 2024-12-13 | Pass   | Julius |
| 3.1  | 4    | 2024-12-13 | Pass   | Team   |
| 3.2  | 4    | 2024-12-13 | Pass   | Team   |
| 4.1  | 1,4  | 2024-12-13 | Pass   | Team   |
| 4.2  | 1,3  | 2024-12-13 | Pass   | Team   |

All critical user story-related tests have passed.

## 6. Evaluate

- US-1, US-2, US-3, US-4 met.
- Bet AI shows improved betting decisions over time.
- Logging and analysis support refinement.
- Future: Implement US-5 for move optimization.

**Learning Report:** (Link pending)

- Keanu

- Julius

## 7. Project Report History

- **15.11.2024 Report:** Defined project goals, requirements, initial "Inform" and "Plan" sections. Allocated tasks. Decided to implement base simulation (US-1) before AI (US-4).

- **22.11.2024 Report:** Completed US-1 (basic rules), US-2 (counting), and US-3 (multi-deck). Identified and chose AI frameworks (US-4 in progress).

- **29.11.2024 Report:** Continued working on US-4 (Bet AI integration, training model). Delay due to environment setup for GPU training.

- **06.12.2024 Report:** Completed US-4 (model integration). Started simulations and training with Bet AI. Results logged and analyzed.

- **13.12.2024 Report:** Completed simulations, plausibility checks, and documentation. Preparing for potential future US-5.
