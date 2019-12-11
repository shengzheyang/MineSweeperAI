# MineSweeperAI
AI agent that solves classic Minesweeper game puzzles.

## Description

This is a course project on Artificial Intelligence.
There are three different difficulty modes:
- Beginner: 8 x 8 tiles with 10 mines. The AI agent can solve it with 70.6%
- Intermediate: 16 x 16 tiles with 40 mines. The AI agent can solve it with 65.5%
- Expert: 16 x 30 tiles with 99 mines. The AI agent can solve it with 8.7%
The success rates are based on 1000 random test boards for each difficulty.

## Logic

MinesweeperAI works its logic in two phases. <br/>
- First phase: Solves the obvious one (e.g. when the number is zero, it's safe to explore all its neighboring nodes) in a BFS manner. Then solve all deterministic ones as Constraint Satisfaction Problems (constraints are given by its neighboring nodes). <br/>
- Second phase: When the deterministic logic inevitably fails to work, we have to break the deadlock with a guess and take the random step. <br/>
Afterwards, the AI will repeat from the first phase to third phase again. <br/>

## Setup

In the worldGenerator/ folder, run the following command to create 1000 random boards for each three different difficulty.
```
./generateTournament.sh
```
<br/>

In the Minesweeper_Python/src/ folder, run the following command to run the AI agent on the boards previously created. After the run, it will show you the final score of how AI agent performs on each diffficulty.
```
python3 Main.py -f ../../WorldGenerator/Problems/ -v
```
<br/>

## Programming Language
Python

## Tools/IDE
PyCharm
