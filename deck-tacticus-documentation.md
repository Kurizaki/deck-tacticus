### Project Documentation
**Group Name:** deck-tacticus
**Members:** Julius Burlet, Keanu Koelewijn  

### Summary Table:

| Date       | Version | Summary                                                         |
| ---------- | ------- | --------------------------------------------------------------- |
| 2024-11-15 | 0.0.1   | Initial setup, requirements for simulation and Bet AI defined.  |

## 1. Inform

### 1.1 Your Project

We are building a Blackjack simulation with a card counting algorithm and Bet AI. The simulation allows theoretical gameplay, which can later integrate the Bet AI for enhanced decision-making.

### 1.2 User Stories

| US-№ | Priority | Type       | Description                                                                                      |
| ---- | -------- | ---------- | ------------------------------------------------------------------------------------------------ |
| 1    | Must     | Functional | As a **player**, I want to simulate Blackjack games to test strategies.                          |
| 2    | Must     | Functional | As a **developer**, I want to implement a card counting algorithm to track the deck.             |
| 3    | Must     | Functional | As a **player**, I want the simulation to support variable deck configurations.                  |
| 4    | Must     | Functional | As a **player**, I want Bet AI to recommend bet sizes based on the game state.                   |
| 5    | Can      | Functional | As a **player**, I want the AI to optimize my moves (Hit, Stand, Double, etc.) in a later phase. |

### 1.3 Test Cases

| TC-№ | Initial State          | Input                               | Expected Output                                                 |
| ---- | ---------------------- | ----------------------------------- | --------------------------------------------------------------- |
| 1.1  | Empty game simulation  | Initialize game with 6 decks        | Game initialized with correct deck composition.                 |
| 1.2  | Cards dealt            | Player and dealer receive cards     | Correct cards dealt to both parties; initial totals calculated. |
| 2.1  | Deck initialized       | Cards played in sequence            | Card counting value updates accurately.                         |
| 3.1  | Bet AI connected       | Provide game state                  | Bet AI returns valid bet recommendation based on state.         |
| 4.1  | Full simulation        | Run a simulated game without AI     | Game runs correctly with accurate rules and results.            |
| 4.2  | Simulation with Bet AI | Run simulation with betting enabled | Bet recommendations adjust dynamically based on game state.     |

### 1.4 Diagrams

- **System Flow Diagram:** Outlines the data flow between simulation, card counting, and Bet AI modules.  
- **Gantt Chart:** Tracks simulation development, card counting implementation, and Bet AI integration.  
- **Architecture Diagram:** Modular view of Blackjack simulation, card counting logic, and Bet AI.  

## 2. Plan

| AP-№ | Deadline   | Responsible | Description                                                          | Planned Time |
| ---- | ---------- | ----------- | -------------------------------------------------------------------- | ------------ |
| 1.A  | 2024-11-01 | Team        | Research Blackjack rules and card counting strategies.               | 4 hours      |
| 1.B  | 2024-11-05 | Keanu      | Implement basic Blackjack rules and game simulation.                 | 8 hours      |
| 2.A  | 2024-11-12 | Julius      | Test and refine simulation for rule accuracy.                        | 6 hours      |
| 3.A  | 2024-11-15 | Team       | Integrate Bet AI into simulation for bet recommendations.            | 8 hours      |
| 4.A  | 2024-11-20 | Team        | Run simulated games with and without Bet AI.                         | 6 hours      |
| 5.A  | 2024-11-25 | Team        | Document findings and prepare for next phase (move optimization AI). | 4 hours      |

**Total Planned Time:** 36 hours

## 3. Decide

- **Simulation:** Core gameplay mechanics must align with Blackjack rules and allow flexible deck configurations.  
- **Card Counting Algorithm:** The simulation will include a Hi-Lo counting system for tracking deck state.  
- **Bet AI Integration:** Bet recommendations will dynamically adjust based on the game state and card count.

## 4 Implement

| AP-№ | Date  | Responsible | Planned Time | Actual Time |
| ---- | ----- | ----------- | ------------ | ----------- |
| 1.A  |       |             |              |             |
| ...  |       |             |              |             |

✍️ Each time you complete a work package, record how long it actually took here.

## 5 Review

### 5.1 Test Log

| TC-№ | Date  | Result   | Tester |
| ---- | ----- | -------- | ------ |
| 1.1  |       |          |        |
| ...  |       |          |        |

✍️ Don’t forget to add a conclusion summarizing the test results.

### 5.2 Exploratory Testing

| BR-№ | Initial State | Input | Expected Output | Actual Output |
| ---- | ------------- | ----- | --------------- | ------------- |
| I    |               |       |                 |               |
| ...  |               |       |                 |               |

✍️ Use Roman numerals for your Bug Reports, i.e., I, II, III, IV, etc.

## 6 Evaluate

✍️ Include a link to your learning report here.
