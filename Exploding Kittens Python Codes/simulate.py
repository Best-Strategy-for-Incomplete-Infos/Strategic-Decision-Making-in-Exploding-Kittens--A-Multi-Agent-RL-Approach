"""Simulation runner for Exploding Kittens experiments."""

import time
from typing import List, Dict, Tuple, Optional, Type
from collections import defaultdict
from dataclasses import dataclass
import random

from game import Game, Pass
from agents import Agent, RandomAgent, PassiveAgent, AggressiveAgent, DefensiveAgent


@dataclass
class GameResult:
    winner: int
    num_turns: int
    final_deck_size: int
    player_hands: List[int]  # Hand sizes at end


def run_single_game(
    agents: List[Agent],
    seed: Optional[int] = None,
    verbose: bool = False
) -> GameResult:
    """Run a single game and return result."""
    game = Game(num_players=len(agents), seed=seed)
    turn_count = 0
    max_turns = 1000  # Safety limit
    
    while not game.is_over() and turn_count < max_turns:
        current_id = game.state.current_player_idx
        agent = agents[current_id]
        
        legal_actions = game.get_legal_actions()
        action = agent.choose_action(game, legal_actions)
        
        if verbose:
            player = game.state.current_player()
            print(f"Turn {turn_count}: Player {current_id} "
                  f"(hand: {len(player.hand)}, deck: {len(game.state.deck)})")
            print(f"  Action: {action}")
        
        result = game.execute_action(action)
        
        if verbose and "draw" in result:
            print(f"  Drew: {result.get('draw')}")
            if result.get("exploded"):
                if result.get("defused"):
                    print(f"  DEFUSED! Inserted at position {result.get('insert_position')}")
                else:
                    print(f"  EXPLODED! Player {current_id} is out!")
        
        turn_count += 1
    
    return GameResult(
        winner=game.get_winner() if game.get_winner() is not None else -1,
        num_turns=turn_count,
        final_deck_size=len(game.state.deck),
        player_hands=[len(p.hand) for p in game.state.players]
    )


def run_simulation(
    agent_classes: List,  # Can be Type[Agent] or callable returning Agent
    num_games: int = 1000,
    verbose_every: int = 0,
    seed_start: Optional[int] = None
) -> Dict:
    """Run multiple games and collect statistics."""
    
    wins = defaultdict(int)
    total_turns = 0
    results = []
    
    start_time = time.time()
    
    for i in range(num_games):
        # Create fresh agents for each game
        agents = []
        for j, cls in enumerate(agent_classes):
            if callable(cls) and not isinstance(cls, type):
                # It's a factory function
                agent = cls()
                agent.player_id = j
                agents.append(agent)
            else:
                # It's a class
                agents.append(cls(player_id=j))
        
        seed = seed_start + i if seed_start is not None else None
        verbose = verbose_every > 0 and i % verbose_every == 0
        
        result = run_single_game(agents, seed=seed, verbose=verbose)
        results.append(result)
        
        if result.winner >= 0:
            wins[result.winner] += 1
        total_turns += result.num_turns
        
        if (i + 1) % 100 == 0:
            elapsed = time.time() - start_time
            print(f"Completed {i + 1}/{num_games} games ({elapsed:.1f}s)")
    
    elapsed = time.time() - start_time
    
    # Calculate statistics
    stats = {
        "num_games": num_games,
        "elapsed_seconds": elapsed,
        "wins_by_player": dict(wins),
        "win_rates": {p: w / num_games for p, w in wins.items()},
        "avg_turns": total_turns / num_games,
        "agent_types": [cls.__name__ for cls in agent_classes],
    }
    
    # First player advantage
    if 0 in wins and 1 in wins:
        stats["first_player_win_rate"] = wins[0] / num_games
        stats["second_player_win_rate"] = wins[1] / num_games
    
    return stats


def print_stats(stats: Dict):
    """Pretty print simulation statistics."""
    print("\n" + "=" * 50)
    print("SIMULATION RESULTS")
    print("=" * 50)
    print(f"Games played: {stats['num_games']}")
    print(f"Time: {stats['elapsed_seconds']:.2f} seconds")
    print(f"Avg turns per game: {stats['avg_turns']:.1f}")
    print()
    print("Agent matchup:")
    for i, agent_type in enumerate(stats['agent_types']):
        print(f"  Player {i}: {agent_type}")
    print()
    print("Win rates:")
    for player, rate in stats['win_rates'].items():
        wins = stats['wins_by_player'][player]
        print(f"  Player {player}: {rate*100:.1f}% ({wins} wins)")
    print()
    if "first_player_win_rate" in stats:
        print(f"First player advantage: {stats['first_player_win_rate']*100:.1f}%")
    print("=" * 50)


def compare_agents(
    agent_pairs: List[Tuple[Type[Agent], Type[Agent]]],
    num_games_per_pair: int = 1000
) -> Dict:
    """Compare multiple agent pairs."""
    all_results = {}
    
    for agent1, agent2 in agent_pairs:
        name = f"{agent1.__name__} vs {agent2.__name__}"
        print(f"\nRunning: {name}")
        
        # Run in both orders to account for first player advantage
        stats_1_first = run_simulation([agent1, agent2], num_games_per_pair // 2)
        stats_2_first = run_simulation([agent2, agent1], num_games_per_pair // 2)
        
        # Combine results (swap player indices for second run)
        total_games = num_games_per_pair
        agent1_wins = stats_1_first['wins_by_player'].get(0, 0) + \
                      stats_2_first['wins_by_player'].get(1, 0)
        agent2_wins = stats_1_first['wins_by_player'].get(1, 0) + \
                      stats_2_first['wins_by_player'].get(0, 0)
        
        all_results[name] = {
            "agent1": agent1.__name__,
            "agent2": agent2.__name__,
            "agent1_wins": agent1_wins,
            "agent2_wins": agent2_wins,
            "agent1_win_rate": agent1_wins / total_games,
            "agent2_win_rate": agent2_wins / total_games,
        }
    
    return all_results


if __name__ == "__main__":
    print("=" * 50)
    print("EXPLODING KITTENS SIMULATION")
    print("=" * 50)
    
    # Test 1: Random vs Random (baseline)
    print("\n[Test 1] Random vs Random")
    stats = run_simulation([RandomAgent, RandomAgent], num_games=1000, seed_start=42)
    print_stats(stats)
    
    # Test 2: Random vs Passive
    print("\n[Test 2] Random vs Passive")
    stats = run_simulation([RandomAgent, PassiveAgent], num_games=1000, seed_start=42)
    print_stats(stats)
    
    # Test 3: Random vs Aggressive
    print("\n[Test 3] Random vs Aggressive")
    stats = run_simulation([RandomAgent, AggressiveAgent], num_games=1000, seed_start=42)
    print_stats(stats)
    
    # Test 4: Random vs Defensive
    print("\n[Test 4] Random vs Defensive")
    stats = run_simulation([RandomAgent, DefensiveAgent], num_games=1000, seed_start=42)
    print_stats(stats)
    
    # Test 5: Aggressive vs Defensive
    print("\n[Test 5] Aggressive vs Defensive")
    stats = run_simulation([AggressiveAgent, DefensiveAgent], num_games=1000, seed_start=42)
    print_stats(stats)
    
    # Test 6: Run verbose single game
    print("\n[Test 6] Single game (verbose)")
    print("-" * 50)
    agents = [RandomAgent(0), RandomAgent(1)]
    result = run_single_game(agents, seed=12345, verbose=True)
    print(f"\nWinner: Player {result.winner}")
    print(f"Total turns: {result.num_turns}")
