import random
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field
from collections import defaultdict
import math

class Game:
    def __init__(self, num_players: int):
        self.num_players = num_players
        self.hands: List[Dict[str, int]] = []  # hand[player_id][card_type] = count
        self.deck_size = 0
        self.bombs_in_deck = 0
        self.current_idx = 0
        self.turns_left = 1
        self.alive = []  # list of alive player ids
        self.winner: Optional[int] = None
    
    def setup(self):
        # Simplified: track counts not individual cards
        self.hands = []
        for i in range(self.num_players):
            self.hands.append({
                'defuse': 1,
                'skip': random.randint(0, 2),
                'attack': random.randint(0, 2),
                'shuffle': random.randint(0, 2),
                'see': random.randint(0, 2),
                'nope': random.randint(0, 2),
                'other': random.randint(2, 5)
            })
        
        # Deck: remaining cards after dealing
        total_action = 4 + 4 + 4 + 5 + 4 + 5  # skip, attack, shuffle, see, favor, nope
        total_cat = 20
        dealt = sum(sum(h.values()) - 1 for h in self.hands)  # -1 for defuse
        self.deck_size = total_action + total_cat - dealt + 2  # +2 defuse in deck
        self.bombs_in_deck = self.num_players - 1
        self.deck_size += self.bombs_in_deck
        
        self.alive = list(range(self.num_players))
        self.current_idx = 0
        self.turns_left = 1
        self.winner = None
    
    def copy(self) -> 'Game':
        g = Game(self.num_players)
        g.hands = [h.copy() for h in self.hands]
        g.deck_size = self.deck_size
        g.bombs_in_deck = self.bombs_in_deck
        g.current_idx = self.current_idx
        g.turns_left = self.turns_left
        g.alive = self.alive.copy()
        g.winner = self.winner
        return g
    
    def is_over(self) -> bool:
        return self.winner is not None
    
    def bomb_prob(self) -> float:
        if self.deck_size <= 0:
            return 0
        return self.bombs_in_deck / self.deck_size
    
    def current_player(self) -> int:
        return self.alive[self.current_idx % len(self.alive)]
    
    def hand(self, player_id: int) -> Dict[str, int]:
        return self.hands[player_id]
    
    def has_card(self, player_id: int, card: str) -> bool:
        return self.hands[player_id].get(card, 0) > 0
    
    def use_card(self, player_id: int, card: str) -> bool:
        if self.has_card(player_id, card):
            self.hands[player_id][card] -= 1
            return True
        return False
    
    def add_card(self, player_id: int, card: str):
        self.hands[player_id][card] = self.hands[player_id].get(card, 0) + 1
    
    def total_cards(self, player_id: int) -> int:
        return sum(self.hands[player_id].values())
    
    def next_player(self):
        self.turns_left -= 1
        if self.turns_left <= 0:
            self.current_idx = (self.current_idx + 1) % len(self.alive)
            self.turns_left = 1
    
    def eliminate(self, player_id: int):
        if player_id in self.alive:
            self.alive.remove(player_id)
            if len(self.alive) == 1:
                self.winner = self.alive[0]
            elif self.current_idx >= len(self.alive):
                self.current_idx = 0
    
    def draw(self, player_id: int) -> str:
        """Draw a card. Returns what was drawn."""
        if self.deck_size <= 0:
            return 'empty'
        
        # Probability of bomb
        if random.random() < self.bomb_prob():
            # Drew bomb
            if self.has_card(player_id, 'defuse'):
                self.use_card(player_id, 'defuse')
                # Bomb goes back - deck size stays same, bombs stay same
                return 'bomb_defused'
            else:
                self.bombs_in_deck -= 1
                self.deck_size -= 1
                self.eliminate(player_id)
                return 'bomb_exploded'
        else:
            # Drew safe card
            self.deck_size -= 1
            # Random card type
            r = random.random()
            if r < 0.1:
                self.add_card(player_id, 'skip')
            elif r < 0.2:
                self.add_card(player_id, 'attack')
            elif r < 0.3:
                self.add_card(player_id, 'shuffle')
            elif r < 0.4:
                self.add_card(player_id, 'see')
            elif r < 0.5:
                self.add_card(player_id, 'nope')
            elif r < 0.55:
                self.add_card(player_id, 'defuse')
            else:
                self.add_card(player_id, 'other')
            return 'safe'
    
    def play_skip(self, player_id: int) -> bool:
        if self.use_card(player_id, 'skip'):
            self.turns_left -= 1
            if self.turns_left <= 0:
                self.next_player()
                self.turns_left = 1
            return True
        return False
    
    def play_attack(self, player_id: int) -> bool:
        if self.use_card(player_id, 'attack'):
            old_idx = self.current_idx
            self.current_idx = (self.current_idx + 1) % len(self.alive)
            self.turns_left = self.turns_left + 1 if self.turns_left > 0 else 2
            return True
        return False
    
    def play_shuffle(self, player_id: int) -> bool:
        if self.use_card(player_id, 'shuffle'):
            return True
        return False

def extract_features(game: Game, player_id: int) -> List[float]:
    
    h = game.hand(player_id)
    
    deck_size = game.deck_size
    bombs = game.bombs_in_deck
    bomb_prob = game.bomb_prob()
    players_alive = len(game.alive)
    
    my_defuse = h.get('defuse', 0)
    my_skip = h.get('skip', 0)
    my_attack = h.get('attack', 0)
    my_shuffle = h.get('shuffle', 0)
    my_see = h.get('see', 0)
    my_nope = h.get('nope', 0)
    my_total = game.total_cards(player_id)
    
    all_totals = [game.total_cards(p) for p in game.alive]
    avg_cards = sum(all_totals) / len(all_totals) if all_totals else 0
    max_cards = max(all_totals) if all_totals else 0
    min_cards = min(all_totals) if all_totals else 0
    
    am_weakest = 1.0 if my_total == min_cards else 0.0
    am_strongest = 1.0 if my_total == max_cards else 0.0
    
    is_my_turn = 1.0 if game.current_player() == player_id else 0.0
    turns_left = game.turns_left if is_my_turn else 0
    
    survival_odds = 1.0 - bomb_prob if my_defuse == 0 else 1.0 - (bomb_prob ** 2)
    action_cards = my_skip + my_attack + my_shuffle
    escape_options = my_skip + my_attack
    
    # Game phase (0 = early, 1 = late)
    game_phase = 1.0 - (deck_size / 40.0) if deck_size < 40 else 0.0
    
    # Endgame flag
    is_endgame = 1.0 if players_alive == 2 and bombs == 1 else 0.0
    
    features = [
        # State features (normalized)
        deck_size / 40.0,
        bombs / 4.0,
        bomb_prob,
        players_alive / 5.0,
        
        # My resources
        min(my_defuse, 2) / 2.0,
        min(my_skip, 3) / 3.0,
        min(my_attack, 3) / 3.0,
        min(my_shuffle, 2) / 2.0,
        min(my_see, 2) / 2.0,
        min(my_nope, 3) / 3.0,
        my_total / 15.0,
        
        # Relative
        am_weakest,
        am_strongest,
        (my_total - avg_cards) / 10.0,
        
        # Turn
        is_my_turn,
        turns_left / 3.0,
        
        # Derived
        survival_odds,
        action_cards / 6.0,
        escape_options / 4.0,
        game_phase,
        is_endgame,
        
        # Interactions
        bomb_prob * (1 - min(my_defuse, 1)),  # Risk if no defuse
        bomb_prob * escape_options,  # Can escape?
        game_phase * action_cards,  # Late game with cards
    ]
    
    return features


def feature_names() -> List[str]:
    return [
        'deck_size', 'bombs', 'bomb_prob', 'players_alive',
        'my_defuse', 'my_skip', 'my_attack', 'my_shuffle', 'my_see', 'my_nope', 'my_total',
        'am_weakest', 'am_strongest', 'cards_vs_avg',
        'is_my_turn', 'turns_left',
        'survival_odds', 'action_cards', 'escape_options', 'game_phase', 'is_endgame',
        'risk_no_defuse', 'escape_ability', 'late_game_cards'
    ]



class ValueFunction:
    """Linear value function: V(s) = weights · features"""
    
    def __init__(self, num_features: int):
        self.weights = [0.0] * num_features
        self.bias = 0.5  # Prior: 50% win rate
    
    def predict(self, features: List[float]) -> float:
        """Predict win probability."""
        v = self.bias
        for w, f in zip(self.weights, features):
            v += w * f
        # Clip to [0, 1]
        return max(0.0, min(1.0, v))
    
    def update(self, features: List[float], target: float, lr: float = 0.01):
        """Update weights toward target."""
        pred = self.predict(features)
        error = target - pred
        
        self.bias += lr * error
        for i in range(len(self.weights)):
            self.weights[i] += lr * error * features[i]
    
    def batch_train(self, data: List[Tuple[List[float], float]], epochs: int = 100, lr: float = 0.01):
        """Train on batch of (features, outcome) pairs."""
        for epoch in range(epochs):
            random.shuffle(data)
            total_error = 0
            for features, target in data:
                pred = self.predict(features)
                error = target - pred
                total_error += error ** 2
                
                self.bias += lr * error
                for i in range(len(self.weights)):
                    self.weights[i] += lr * error * features[i]
            
            if epoch % 20 == 0:
                mse = total_error / len(data)
                print(f"  Epoch {epoch}: MSE = {mse:.4f}")
    
    def print_weights(self, names: List[str]):
        """Print weights with feature names."""
        pairs = list(zip(names, self.weights))
        pairs.sort(key=lambda x: abs(x[1]), reverse=True)
        
        print("\nFeature Weights (sorted by importance):")
        print("-" * 40)
        for name, weight in pairs:
            print(f"  {name:20}: {weight:+.4f}")



def random_action(game: Game, player_id: int):
    """Random player logic."""
    h = game.hand(player_id)
    
    # If high risk and have escape, use it
    if game.bomb_prob() > 0.3:
        if h.get('attack', 0) > 0 and random.random() < 0.5:
            game.play_attack(player_id)
            return
        if h.get('skip', 0) > 0 and random.random() < 0.5:
            game.play_skip(player_id)
            return
    
    # Sometimes use attack randomly
    if h.get('attack', 0) > 0 and random.random() < 0.2:
        game.play_attack(player_id)
        return
    
    # Draw
    result = game.draw(player_id)
    if result != 'bomb_exploded':
        game.next_player()


def value_action(game: Game, player_id: int, vf: ValueFunction):
    """Choose action that maximizes expected value."""
    
    h = game.hand(player_id)
    best_action = 'draw'
    best_value = -1
    
    # Evaluate each action
    actions = ['draw']
    if h.get('skip', 0) > 0:
        actions.append('skip')
    if h.get('attack', 0) > 0:
        actions.append('attack')
    if h.get('shuffle', 0) > 0:
        actions.append('shuffle')
    
    for action in actions:
        g = game.copy()
        pid = player_id
        
        if action == 'draw':
            # Expected value after draw
            # Simulate multiple outcomes
            values = []
            for _ in range(20):
                g2 = g.copy()
                result = g2.draw(pid)
                if result == 'bomb_exploded':
                    values.append(0.0)
                else:
                    g2.next_player()
                    if not g2.is_over():
                        values.append(vf.predict(extract_features(g2, pid)))
                    else:
                        values.append(1.0 if g2.winner == pid else 0.0)
            value = sum(values) / len(values)
        
        elif action == 'skip':
            g.play_skip(pid)
            if not g.is_over():
                value = vf.predict(extract_features(g, pid))
            else:
                value = 1.0 if g.winner == pid else 0.0
        
        elif action == 'attack':
            g.play_attack(pid)
            if not g.is_over():
                value = vf.predict(extract_features(g, pid))
            else:
                value = 1.0 if g.winner == pid else 0.0
        
        elif action == 'shuffle':
            g.play_shuffle(pid)
            # Still need to draw after shuffle
            values = []
            for _ in range(20):
                g2 = g.copy()
                result = g2.draw(pid)
                if result == 'bomb_exploded':
                    values.append(0.0)
                else:
                    g2.next_player()
                    if not g2.is_over():
                        values.append(vf.predict(extract_features(g2, pid)))
                    else:
                        values.append(1.0 if g2.winner == pid else 0.0)
            value = sum(values) / len(values)
        
        if value > best_value:
            best_value = value
            best_action = action
    
    # Execute best action
    if best_action == 'draw':
        result = game.draw(player_id)
        if result != 'bomb_exploded':
            game.next_player()
    elif best_action == 'skip':
        game.play_skip(player_id)
    elif best_action == 'attack':
        game.play_attack(player_id)
    elif best_action == 'shuffle':
        game.play_shuffle(player_id)
        result = game.draw(player_id)
        if result != 'bomb_exploded':
            game.next_player()


def simulate_game(num_players: int, vf: Optional[ValueFunction] = None, 
                  my_id: int = 0, collect_data: bool = False) -> Tuple[int, List]:
    """
    Simulate one game.
    Returns (winner_id, [(features, outcome), ...])
    """
    game = Game(num_players)
    game.setup()
    
    states = []  # (player_id, features) at each turn
    
    for _ in range(200):  # Max turns
        if game.is_over():
            break
        
        pid = game.current_player()
        
        # Collect state before action
        if collect_data:
            features = extract_features(game, pid)
            states.append((pid, features))
        
        # Choose action
        if vf is not None and pid == my_id:
            value_action(game, pid, vf)
        else:
            random_action(game, pid)
    
    winner = game.winner
    
    # Convert states to training data
    data = []
    if collect_data:
        for pid, features in states:
            outcome = 1.0 if pid == winner else 0.0
            data.append((features, outcome))
    
    return winner, data


def generate_training_data(num_games: int, num_players: int) -> List[Tuple[List[float], float]]:
    """Generate training data from random games."""
    all_data = []
    
    for i in range(num_games):
        if i % 1000 == 0:
            print(f"  Generating game {i}/{num_games}...")
        
        _, data = simulate_game(num_players, vf=None, collect_data=True)
        all_data.extend(data)
    
    return all_data


def evaluate_vf(vf: ValueFunction, num_games: int, num_players: int) -> float:
    """Evaluate value function by playing games."""
    wins = 0
    my_id = 0
    
    for _ in range(num_games):
        winner, _ = simulate_game(num_players, vf=vf, my_id=my_id, collect_data=False)
        if winner == my_id:
            wins += 1
    
    return wins / num_games

def main():
    print("=" * 70)
    print("Value Function Learning for Exploding Kittens")
    print("=" * 70)
    
    num_players = 3
    num_features = len(feature_names())
    
    # Phase 1: Generate training data
    print("\n[Phase 1] Generating training data...")
    training_data = generate_training_data(5000, num_players)
    print(f"  Generated {len(training_data)} state-outcome pairs")
    
    # Phase 2: Train value function
    print("\n[Phase 2] Training value function...")
    vf = ValueFunction(num_features)
    vf.batch_train(training_data, epochs=100, lr=0.005)
    
    # Print learned weights
    vf.print_weights(feature_names())
    
    # Phase 3: Evaluate
    print("\n[Phase 3] Evaluating...")
    
    print("\nBaseline (random vs random):")
    baseline = 1.0 / num_players
    print(f"  Expected: {baseline*100:.1f}%")
    
    print("\nValue function vs random opponents:")
    win_rate = evaluate_vf(vf, 2000, num_players)
    print(f"  Win rate: {win_rate*100:.1f}%")
    print(f"  Advantage: {(win_rate - baseline)*100:+.1f}%")
    
    # Phase 4: Iterative improvement
    print("\n[Phase 4] Self-improvement iterations...")
    
    for iteration in range(3):
        print(f"\n--- Iteration {iteration + 1} ---")
        
        # Generate data with current policy
        new_data = []
        for _ in range(2000):
            _, data = simulate_game(num_players, vf=vf, my_id=0, collect_data=True)
            new_data.extend(data)
        
        # Combine with old data (keep some history)
        combined = training_data[-10000:] + new_data
        
        # Retrain
        print("  Retraining...")
        vf.batch_train(combined, epochs=50, lr=0.003)
        
        # Evaluate
        win_rate = evaluate_vf(vf, 1000, num_players)
        print(f"  Win rate: {win_rate*100:.1f}%")
        
        training_data = combined
    
    # Final evaluation
    print("\n" + "=" * 70)
    print("Final Evaluation")
    print("=" * 70)
    
    for np in [2, 3, 4]:
        baseline = 1.0 / np
        win_rate = evaluate_vf(vf, 2000, np)
        print(f"\n{np} Players:")
        print(f"  Baseline: {baseline*100:.1f}%")
        print(f"  Win rate: {win_rate*100:.1f}%")
        print(f"  Advantage: {(win_rate - baseline)*100:+.1f}%")
    
    # Print final weights
    print("\n" + "=" * 70)
    print("Final Learned Weights")
    print("=" * 70)
    vf.print_weights(feature_names())


if __name__ == "__main__":
    main()
