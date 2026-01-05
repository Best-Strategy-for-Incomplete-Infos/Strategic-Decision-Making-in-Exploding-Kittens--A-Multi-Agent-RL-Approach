"""Monte Carlo Tree Search agent for Exploding Kittens.

Uses Information Set MCTS (determinization) to handle hidden information:
- Sample possible game states consistent with current observation
- Run MCTS on each determinized state
- Aggregate results across samples
"""

import random
import math
import copy
from typing import List, Dict, Optional, Tuple
from collections import defaultdict
from dataclasses import dataclass, field

from game import Game, GameState, Action, Pass, PlayCard, PlayCatPair, Player
from cards import Card, CardType, CAT_CARDS, BASE_DECK_CONFIG
from agents import Agent


@dataclass
class MCTSNode:
    """Node in the MCTS tree."""
    state_hash: str
    parent: Optional['MCTSNode'] = None
    action: Optional[Action] = None  # Action that led to this node
    children: Dict[str, 'MCTSNode'] = field(default_factory=dict)
    visits: int = 0
    wins: float = 0.0
    
    def ucb1(self, exploration: float = 1.41) -> float:
        """Upper Confidence Bound for Trees."""
        if self.visits == 0:
            return float('inf')
        exploitation = self.wins / self.visits
        exploration_term = exploration * math.sqrt(math.log(self.parent.visits) / self.visits)
        return exploitation + exploration_term
    
    def best_child(self, exploration: float = 1.41) -> 'MCTSNode':
        """Select child with highest UCB1 value."""
        return max(self.children.values(), key=lambda c: c.ucb1(exploration))
    
    def most_visited_child(self) -> 'MCTSNode':
        """Select most visited child (for final action selection)."""
        return max(self.children.values(), key=lambda c: c.visits)


def action_to_key(action: Action) -> str:
    """Convert action to hashable string key."""
    if isinstance(action, Pass):
        return "pass"
    elif isinstance(action, PlayCard):
        return f"play_{action.card_type.name}_{action.target_player_id}"
    elif isinstance(action, PlayCatPair):
        return f"pair_{action.cat_type.name}_{action.target_player_id}"
    return str(action)


def clone_game(game: Game) -> Game:
    """Deep copy a game state."""
    new_game = Game.__new__(Game)
    new_game.num_players = game.num_players
    new_game.action_history = list(game.action_history)
    
    # Deep copy state
    new_game.state = GameState(
        players=[
            Player(
                id=p.id,
                hand=[Card(c.card_type) for c in p.hand],
                alive=p.alive
            ) for p in game.state.players
        ],
        deck=[Card(c.card_type) for c in game.state.deck],
        discard=[Card(c.card_type) for c in game.state.discard],
        current_player_idx=game.state.current_player_idx,
        turns_remaining=game.state.turns_remaining,
        game_over=game.state.game_over,
        winner=game.state.winner,
        top_three_known_by=game.state.top_three_known_by
    )
    return new_game


def determinize_game(game: Game, observer_id: int) -> Game:
    """
    Create a determinized copy of the game from observer's perspective.
    
    Hidden information (opponent's hand, deck order) is randomized
    while maintaining consistency with what observer knows.
    """
    det_game = clone_game(game)
    
    # Collect all cards that observer doesn't know the location of
    unknown_cards = []
    
    # Add opponent's hand cards to unknown pool
    for player in det_game.state.players:
        if player.id != observer_id and player.alive:
            unknown_cards.extend(player.hand)
            player.hand = []
    
    # Add deck cards to unknown pool (except top 3 if observer saw them)
    observer_knows_top = (det_game.state.top_three_known_by == observer_id)
    
    if observer_knows_top and len(det_game.state.deck) >= 3:
        # Keep top 3, randomize rest
        top_three = det_game.state.deck[-3:]
        rest = det_game.state.deck[:-3]
        unknown_cards.extend(rest)
        det_game.state.deck = []
    else:
        unknown_cards.extend(det_game.state.deck)
        det_game.state.deck = []
    
    # Shuffle unknown cards
    random.shuffle(unknown_cards)
    
    # Redistribute to opponents
    for player in det_game.state.players:
        if player.id != observer_id and player.alive:
            # Give them same number of cards as original
            original_hand_size = len(game.state.players[player.id].hand)
            for _ in range(original_hand_size):
                if unknown_cards:
                    player.hand.append(unknown_cards.pop())
    
    # Rest goes to deck
    det_game.state.deck = unknown_cards
    
    # Put back top 3 if observer knew them
    if observer_knows_top and len(game.state.deck) >= 3:
        det_game.state.deck.extend(top_three)
    
    return det_game


def simulate_random_playout(game: Game, max_moves: int = 200) -> Optional[int]:
    """
    Play out game randomly from current state.
    Returns winner's player_id or None if no winner.
    """
    moves = 0
    while not game.is_over() and moves < max_moves:
        legal_actions = game.get_legal_actions()
        if not legal_actions:
            break
        
        # Random action selection with slight bias toward good moves
        action = random.choice(legal_actions)
        game.execute_action(action)
        moves += 1
    
    return game.get_winner()


def simulate_with_heuristics(game: Game, player_id: int, max_moves: int = 200) -> Optional[int]:
    """
    Smarter playout using basic heuristics.
    """
    moves = 0
    while not game.is_over() and moves < max_moves:
        current_player = game.state.current_player_idx
        legal_actions = game.get_legal_actions()
        
        if not legal_actions:
            break
        
        # Simple heuristic-based selection
        action = select_heuristic_action(game, legal_actions)
        game.execute_action(action)
        moves += 1
    
    return game.get_winner()


def select_heuristic_action(game: Game, legal_actions: List[Action]) -> Action:
    """Select action using simple heuristics."""
    player = game.state.current_player()
    deck_size = len(game.state.deck)
    has_defuse = player.has_card(CardType.DEFUSE)
    
    # If deck is small and no defuse, prioritize skip/attack
    if deck_size <= 3 and not has_defuse:
        for action in legal_actions:
            if isinstance(action, PlayCard):
                if action.card_type in [CardType.SKIP, CardType.ATTACK]:
                    return action
    
    # If we know top cards have EK, shuffle or skip
    if game.state.top_three_known_by == player.id:
        top_cards = game.state.peek_top(3)
        if any(c.card_type == CardType.EXPLODING_KITTEN for c in top_cards[:1]):
            # EK is on top!
            for action in legal_actions:
                if isinstance(action, PlayCard):
                    if action.card_type in [CardType.SHUFFLE, CardType.SKIP, CardType.ATTACK]:
                        return action
    
    # Use See the Future if we don't know deck state
    if game.state.top_three_known_by != player.id:
        for action in legal_actions:
            if isinstance(action, PlayCard) and action.card_type == CardType.SEE_THE_FUTURE:
                if random.random() < 0.3:  # Don't always use it
                    return action
    
    # Attack is generally good
    for action in legal_actions:
        if isinstance(action, PlayCard) and action.card_type == CardType.ATTACK:
            if random.random() < 0.4:
                return action
    
    # Cat pairs to steal cards
    for action in legal_actions:
        if isinstance(action, PlayCatPair):
            if random.random() < 0.3:
                return action
    
    # Default: random from remaining
    return random.choice(legal_actions)


class MCTSAgent(Agent):
    """
    MCTS-based agent using determinization for imperfect information.
    """
    
    def __init__(
        self, 
        player_id: int,
        num_simulations: int = 500,
        num_determinizations: int = 20,
        exploration: float = 1.41,
        use_heuristics: bool = True
    ):
        super().__init__(player_id)
        self.num_simulations = num_simulations
        self.num_determinizations = num_determinizations
        self.exploration = exploration
        self.use_heuristics = use_heuristics
    
    def choose_action(self, game: Game, legal_actions: List[Action]) -> Action:
        if len(legal_actions) == 1:
            return legal_actions[0]
        
        # Aggregate action values across determinizations
        action_values: Dict[str, List[float]] = defaultdict(list)
        
        for _ in range(self.num_determinizations):
            # Create determinized game
            det_game = determinize_game(game, self.player_id)
            
            # Run MCTS on this determinization
            root = MCTSNode(state_hash="root")
            
            sims_per_det = self.num_simulations // self.num_determinizations
            for _ in range(sims_per_det):
                self._mcts_iteration(det_game, root, legal_actions)
            
            # Collect win rates for each action
            for action_key, child in root.children.items():
                if child.visits > 0:
                    action_values[action_key].append(child.wins / child.visits)
        
        # Select action with best average value
        best_action_key = None
        best_avg_value = -1
        
        for action_key, values in action_values.items():
            if values:
                avg_value = sum(values) / len(values)
                if avg_value > best_avg_value:
                    best_avg_value = avg_value
                    best_action_key = action_key
        
        # Map back to action object
        if best_action_key:
            for action in legal_actions:
                if action_to_key(action) == best_action_key:
                    return action
        
        # Fallback
        return random.choice(legal_actions)
    
    def _mcts_iteration(
        self, 
        game: Game, 
        root: MCTSNode,
        legal_actions: List[Action]
    ):
        """One iteration of MCTS: select, expand, simulate, backpropagate."""
        sim_game = clone_game(game)
        node = root
        path = [node]
        
        # Selection: traverse tree using UCB1
        while node.children and not sim_game.is_over():
            node = node.best_child(self.exploration)
            path.append(node)
            
            if node.action:
                sim_game.execute_action(node.action)
        
        # Expansion: add children if not terminal
        if not sim_game.is_over() and node.visits > 0:
            current_legal = sim_game.get_legal_actions() if node != root else legal_actions
            for action in current_legal:
                action_key = action_to_key(action)
                if action_key not in node.children:
                    child = MCTSNode(
                        state_hash=action_key,
                        parent=node,
                        action=action
                    )
                    node.children[action_key] = child
            
            # Select one child to simulate
            if node.children:
                action_key = random.choice(list(node.children.keys()))
                node = node.children[action_key]
                path.append(node)
                if node.action:
                    sim_game.execute_action(node.action)
        
        # Simulation: playout to terminal state
        if self.use_heuristics:
            winner = simulate_with_heuristics(sim_game, self.player_id)
        else:
            winner = simulate_random_playout(sim_game)
        
        # Backpropagation: update statistics
        result = 1.0 if winner == self.player_id else 0.0
        for node in path:
            node.visits += 1
            node.wins += result
    
    def choose_insert_position(self, game: Game, max_position: int) -> int:
        """
        Choose where to insert Exploding Kitten after defusing.
        Strategy: put it where opponent is most likely to draw it.
        """
        # Simple heuristic: put near top but not on top
        # (opponent might have Skip/Attack)
        if max_position <= 1:
            return max_position
        elif max_position <= 3:
            return max_position - 1
        else:
            # Put it 2-4 cards from top
            return max_position - random.randint(2, min(4, max_position))


class FastMCTSAgent(Agent):
    """
    Faster MCTS with fewer simulations, good for bulk testing.
    """
    
    def __init__(self, player_id: int, num_simulations: int = 100):
        super().__init__(player_id)
        self.num_simulations = num_simulations
    
    def choose_action(self, game: Game, legal_actions: List[Action]) -> Action:
        if len(legal_actions) == 1:
            return legal_actions[0]
        
        # Simple: run random playouts for each action, pick best
        action_scores = {}
        
        sims_per_action = max(5, self.num_simulations // len(legal_actions))
        
        for action in legal_actions:
            wins = 0
            for _ in range(sims_per_action):
                # Determinize and simulate
                det_game = determinize_game(game, self.player_id)
                det_game.execute_action(action)
                
                winner = simulate_with_heuristics(det_game, self.player_id)
                if winner == self.player_id:
                    wins += 1
            
            action_scores[action_to_key(action)] = wins / sims_per_action
        
        # Select best
        best_key = max(action_scores, key=action_scores.get)
        for action in legal_actions:
            if action_to_key(action) == best_key:
                return action
        
        return random.choice(legal_actions)
    
    def choose_insert_position(self, game: Game, max_position: int) -> int:
        if max_position <= 2:
            return max_position
        return max_position - random.randint(1, 3)


if __name__ == "__main__":
    # Quick test
    from simulate import run_single_game, run_simulation, print_stats
    from agents import RandomAgent, AggressiveAgent
    
    print("Testing MCTS Agent...")
    print("=" * 50)
    
    # Single game test
    print("\n[Test] Single game: MCTS vs Random (verbose)")
    agents = [MCTSAgent(0, num_simulations=200, num_determinizations=10), RandomAgent(1)]
    result = run_single_game(agents, seed=42, verbose=True)
    print(f"Winner: Player {result.winner}")
    
    # Bulk test
    print("\n[Test] 100 games: MCTS vs Random")
    stats = run_simulation(
        [lambda: MCTSAgent(0, num_simulations=200, num_determinizations=10), RandomAgent],
        num_games=100
    )
    print_stats(stats)
    
    print("\n[Test] 100 games: MCTS vs Aggressive")
    stats = run_simulation(
        [lambda: MCTSAgent(0, num_simulations=200, num_determinizations=10), AggressiveAgent],
        num_games=100
    )
    print_stats(stats)
