# Strategic Decision Making in Exploding Kittens: A Multi-Agent RL Approach
Exploding Kittens Optimal Strategy Simulator

A Monte Carlo simulation framework for discovering optimal decision-making strategies in the card game Exploding Kittens.

Overview

This project uses extensive Monte Carlo simulation (100,000+ iterations per decision point) to identify optimal actions across 64 distinct game states. The resulting policy achieves significant competitive advantages:
PlayersBaselinePolicy Win Rate Edge
50.0%     59.2%     +9.2%
33.3%     39.4%     +6.1%
25.0%     29.8%     +4.8%

Key Strategic Findings

1. Attack > Skip (When Escaping Known Bomb)
When See Future reveals a bomb on top, Attack is superior to Skip (56.4% vs 52.1% win rate). This counterintuitive finding arises from resource depletion—forcing opponents to use their Defuse cards early significantly reduces their endgame survival.

3. Always Counter-Attack
When under attack (facing 2+ required draws), counter-attacking with your own Attack card achieves 68.5% win rate vs. 41.3% for Skip. The principle of tempo—forcing opponents into bad positions—outweighs passive defense.

5. Defuse as Insurance
Players with Defuse should continue drawing even at 30% bomb probability. Save escape cards for reactive situations. Players without Defuse should escape aggressively at high risk (>30%).

7. Early Game Conservation
In the early game (deck >70% remaining), simply draw. Attack card value increases exponentially as the deck shrinks. Card advantage is the primary predictor of endgame success.

9. Endgame Principles

With Defuse: Draw confidently
Without Defuse: Use any escape card
Against opponent with Defuse: Consider Shuffle to reset state

1. Bomb Visible (12 triggers)
When See Future reveals bomb position.

BOMB_TOP_SKIP_DEFUSE → ATTACK
BOMB_TOP_SKIP_NO_DEFUSE → SKIP
BOMB_2ND_HAS_ACTIONS → DRAW

2. Bomb Unknown (16 triggers)
When bomb location is uncertain, categorized by risk level.

UNKNOWN_LOW_* → DRAW
UNKNOWN_HIGH_NO_DEFUSE → SKIP/ATTACK

3. See Future Decision (6 triggers)
Whether to use See Future card.

Low/Med risk + escape → DRAW
High risk → SEE_FUTURE

4. Under Attack (11 triggers)
When facing multiple required draws.

Have Attack → ATTACK (always)
No Attack, have Skip → SKIP

5. Defused (4 triggers)
Bomb placement after using Defuse.

Generally → PLACE_TOP (needs more simulation)

6. Proactive (5 triggers)
Whether to attack without immediate threat.

Early game → DRAW (conserve)
Late game → Consider ATTACK

7. Endgame (10 triggers)
Two-player final confrontation.

Have Defuse → DRAW
No Defuse → Use escape cards

Methodology
Two-Pass Refinement

Pass 1: Find initial best actions with no prior policy
Pass 2: Refine using Pass 1 policy as baseline, improving coherence

Simulation Protocol
For each trigger-action pair:

Generate random games until target trigger is reached
Execute test action
Continue game to completion using learned policy
Record win/loss outcome
Repeat 10,000+ times

Opponent Model
Opponents use semi-intelligent baseline strategy:

Respond to visible bombs
Escape at high risk
Random otherwise

Limitations

Opponent Model: Analysis against optimized opponents may differ
Defused Triggers: Rare event, insufficient samples
Simplified Mechanics: Nope and Favor cards simplified
No Card Counting: Opponent hand inference not modeled
No Psychology: Bluffing and table presence not captured

Future Work

 Forced simulation for Defused triggers
 Player-count specific policy training
 Neural network value function
 Self-play reinforcement learning
 Human player validation studies
 Mixed strategy / Nash equilibrium analysis

Acknowledgments

Game design: Elan Lee, Matthew Inman, Shane Small
Simulation methodology inspired by poker AI research
Monte Carlo methods for imperfect information games
