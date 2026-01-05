"""Deep Q-Learning agent for Exploding Kittens.

Uses a neural network to approximate Q(s, a) and learns through self-play.
"""

import random
import math
import numpy as np
from typing import List, Dict, Optional, Tuple
from collections import deque
from dataclasses import dataclass

from game import Game, GameState, Action, Pass, PlayCard, PlayCatPair, Player
from cards import Card, CardType, CAT_CARDS, ACTION_CARDS, BASE_DECK_CONFIG
from agents import Agent


# All possible action types
ACTION_TYPES = [
    "pass",
    "attack", "skip", "shuffle", "see_future", "favor", "nope",
    "pair_tacocat", "pair_cattermelon", "pair_hairy_potato", 
    "pair_beard_cat", "pair_rainbow_cat"
]
NUM_ACTIONS = len(ACTION_TYPES)

# Card type to index mapping
CARD_TYPE_TO_IDX = {ct: i for i, ct in enumerate(CardType)}
NUM_CARD_TYPES = len(CardType)


def state_to_vector(game: Game, player_id: int) -> np.ndarray:
    """
    Convert game state to feature vector from player's perspective.
    
    Features:
    - Own hand: count of each card type (15 dims)
    - Deck size (1 dim)
    - Discard pile: count of each card type (15 dims)
    - Opponent's hand size (1 dim)
    - Turns remaining (1 dim)
    - Whether we have defuse (1 dim)
    - Whether we know top 3 (1 dim)
    - Top card is EK (if known) (1 dim)
    - Game progress (deck_remaining / initial_deck) (1 dim)
    
    Total: ~38 dimensions
    """
    player = game.state.players[player_id]
    opponent = game.state.players[1 - player_id]
    
    features = []
    
    # Own hand composition (15 dims)
    hand_counts = np.zeros(NUM_CARD_TYPES)
    for card in player.hand:
        hand_counts[CARD_TYPE_TO_IDX[card.card_type]] += 1
    # Normalize by max possible
    features.extend(hand_counts / 10.0)
    
    # Deck size (normalized)
    features.append(len(game.state.deck) / 50.0)
    
    # Discard pile composition (15 dims)
    discard_counts = np.zeros(NUM_CARD_TYPES)
    for card in game.state.discard:
        discard_counts[CARD_TYPE_TO_IDX[card.card_type]] += 1
    features.extend(discard_counts / 10.0)
    
    # Opponent's hand size (normalized)
    features.append(len(opponent.hand) / 20.0)
    
    # Turns remaining
    features.append(game.state.turns_remaining / 3.0)
    
    # Have defuse
    features.append(1.0 if player.has_card(CardType.DEFUSE) else 0.0)
    
    # Know top 3
    know_top = game.state.top_three_known_by == player_id
    features.append(1.0 if know_top else 0.0)
    
    # Top card is EK (if known)
    if know_top and game.state.deck:
        top_is_ek = game.state.deck[-1].card_type == CardType.EXPLODING_KITTEN
        features.append(1.0 if top_is_ek else 0.0)
    else:
        features.append(0.0)
    
    # Danger level: P(draw EK) estimate
    num_ek_remaining = sum(1 for c in game.state.deck 
                          if c.card_type == CardType.EXPLODING_KITTEN)
    if game.state.deck:
        features.append(num_ek_remaining / len(game.state.deck))
    else:
        features.append(0.0)
    
    return np.array(features, dtype=np.float32)


def action_to_index(action: Action) -> int:
    """Convert action to index."""
    if isinstance(action, Pass):
        return 0
    elif isinstance(action, PlayCard):
        mapping = {
            CardType.ATTACK: 1,
            CardType.SKIP: 2,
            CardType.SHUFFLE: 3,
            CardType.SEE_THE_FUTURE: 4,
            CardType.FAVOR: 5,
            CardType.NOPE: 6,
        }
        return mapping.get(action.card_type, 0)
    elif isinstance(action, PlayCatPair):
        mapping = {
            CardType.CAT_TACOCAT: 7,
            CardType.CAT_CATTERMELON: 8,
            CardType.CAT_HAIRY_POTATO: 9,
            CardType.CAT_BEARD_CAT: 10,
            CardType.CAT_RAINBOW_CAT: 11,
        }
        return mapping.get(action.cat_type, 0)
    return 0


def index_to_action_type(index: int) -> str:
    """Convert index back to action type string."""
    return ACTION_TYPES[index] if index < len(ACTION_TYPES) else "pass"


class SimpleNN:
    """
    Simple neural network using only numpy.
    Architecture: input -> hidden1 -> hidden2 -> output
    """
    
    def __init__(self, input_dim: int, hidden_dim: int, output_dim: int):
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.output_dim = output_dim
        
        # Xavier initialization
        self.w1 = np.random.randn(input_dim, hidden_dim) * np.sqrt(2.0 / input_dim)
        self.b1 = np.zeros(hidden_dim)
        self.w2 = np.random.randn(hidden_dim, hidden_dim) * np.sqrt(2.0 / hidden_dim)
        self.b2 = np.zeros(hidden_dim)
        self.w3 = np.random.randn(hidden_dim, output_dim) * np.sqrt(2.0 / hidden_dim)
        self.b3 = np.zeros(output_dim)
    
    def forward(self, x: np.ndarray) -> np.ndarray:
        """Forward pass."""
        # Layer 1
        h1 = np.maximum(0, x @ self.w1 + self.b1)  # ReLU
        # Layer 2
        h2 = np.maximum(0, h1 @ self.w2 + self.b2)  # ReLU
        # Output layer (no activation for Q-values)
        out = h2 @ self.w3 + self.b3
        return out
    
    def predict(self, x: np.ndarray) -> np.ndarray:
        """Predict Q-values for a state."""
        if x.ndim == 1:
            x = x.reshape(1, -1)
        return self.forward(x)
    
    def update(self, states: np.ndarray, targets: np.ndarray, 
               actions: np.ndarray, lr: float = 0.001):
        """Simple gradient descent update."""
        batch_size = states.shape[0]
        
        # Forward pass with caching
        h1_pre = states @ self.w1 + self.b1
        h1 = np.maximum(0, h1_pre)
        h2_pre = h1 @ self.w2 + self.b2
        h2 = np.maximum(0, h2_pre)
        q_values = h2 @ self.w3 + self.b3
        
        # Only update Q-value for taken action
        q_selected = q_values[np.arange(batch_size), actions]
        td_error = q_selected - targets
        
        # Backward pass
        dout = np.zeros_like(q_values)
        dout[np.arange(batch_size), actions] = td_error / batch_size
        
        # Gradient for w3, b3
        dw3 = h2.T @ dout
        db3 = np.sum(dout, axis=0)
        
        # Backprop through layer 2
        dh2 = dout @ self.w3.T
        dh2[h2_pre <= 0] = 0  # ReLU gradient
        
        dw2 = h1.T @ dh2
        db2 = np.sum(dh2, axis=0)
        
        # Backprop through layer 1
        dh1 = dh2 @ self.w2.T
        dh1[h1_pre <= 0] = 0
        
        dw1 = states.T @ dh1
        db1 = np.sum(dh1, axis=0)
        
        # Gradient clipping
        max_grad = 1.0
        for grad in [dw1, db1, dw2, db2, dw3, db3]:
            np.clip(grad, -max_grad, max_grad, out=grad)
        
        # Update weights
        self.w3 -= lr * dw3
        self.b3 -= lr * db3
        self.w2 -= lr * dw2
        self.b2 -= lr * db2
        self.w1 -= lr * dw1
        self.b1 -= lr * db1
        
        return np.mean(td_error ** 2)
    
    def copy_from(self, other: 'SimpleNN'):
        """Copy weights from another network."""
        self.w1 = other.w1.copy()
        self.b1 = other.b1.copy()
        self.w2 = other.w2.copy()
        self.b2 = other.b2.copy()
        self.w3 = other.w3.copy()
        self.b3 = other.b3.copy()
    
    def save(self, filepath: str):
        """Save weights to file."""
        np.savez(filepath, 
                 w1=self.w1, b1=self.b1,
                 w2=self.w2, b2=self.b2, 
                 w3=self.w3, b3=self.b3)
    
    def load(self, filepath: str):
        """Load weights from file."""
        data = np.load(filepath)
        self.w1 = data['w1']
        self.b1 = data['b1']
        self.w2 = data['w2']
        self.b2 = data['b2']
        self.w3 = data['w3']
        self.b3 = data['b3']


@dataclass
class Experience:
    state: np.ndarray
    action: int
    reward: float
    next_state: np.ndarray
    done: bool


class ReplayBuffer:
    """Experience replay buffer."""
    
    def __init__(self, capacity: int = 50000):
        self.buffer = deque(maxlen=capacity)
    
    def add(self, exp: Experience):
        self.buffer.append(exp)
    
    def sample(self, batch_size: int) -> List[Experience]:
        return random.sample(self.buffer, min(batch_size, len(self.buffer)))
    
    def __len__(self):
        return len(self.buffer)


class DQNAgent(Agent):
    """Deep Q-Network agent."""
    
    def __init__(
        self, 
        player_id: int,
        epsilon: float = 0.1,
        trained_network: Optional[SimpleNN] = None
    ):
        super().__init__(player_id)
        self.epsilon = epsilon
        
        # State dimension from state_to_vector (15 + 1 + 15 + 1 + 1 = 33)
        self.state_dim = 33
        
        if trained_network:
            self.network = trained_network
        else:
            self.network = SimpleNN(self.state_dim, 128, NUM_ACTIONS)
    
    def choose_action(self, game: Game, legal_actions: List[Action]) -> Action:
        # Epsilon-greedy
        if random.random() < self.epsilon:
            return random.choice(legal_actions)
        
        # Get Q-values
        state = state_to_vector(game, self.player_id)
        q_values = self.network.predict(state)[0]
        
        # Mask illegal actions
        legal_indices = {action_to_index(a) for a in legal_actions}
        
        # Select best legal action
        best_q = float('-inf')
        best_action = legal_actions[0]
        
        for action in legal_actions:
            idx = action_to_index(action)
            if q_values[idx] > best_q:
                best_q = q_values[idx]
                best_action = action
        
        return best_action
    
    def choose_insert_position(self, game: Game, max_position: int) -> int:
        # Put EK near top to trap opponent
        if max_position <= 2:
            return max_position
        return max_position - random.randint(1, 3)


def train_dqn(
    num_episodes: int = 5000,
    batch_size: int = 64,
    gamma: float = 0.99,
    epsilon_start: float = 1.0,
    epsilon_end: float = 0.05,
    epsilon_decay: float = 0.995,
    learning_rate: float = 0.001,
    target_update_freq: int = 100,
    save_path: Optional[str] = None
) -> SimpleNN:
    """Train DQN through self-play."""
    
    state_dim = 33
    
    # Networks
    policy_net = SimpleNN(state_dim, 128, NUM_ACTIONS)
    target_net = SimpleNN(state_dim, 128, NUM_ACTIONS)
    target_net.copy_from(policy_net)
    
    # Replay buffer
    buffer = ReplayBuffer(capacity=50000)
    
    epsilon = epsilon_start
    total_rewards = []
    
    for episode in range(num_episodes):
        game = Game(num_players=2)
        
        # Create agents using current network
        agents = [
            DQNAgent(0, epsilon=epsilon, trained_network=policy_net),
            DQNAgent(1, epsilon=epsilon, trained_network=policy_net)
        ]
        
        episode_experiences = [[], []]  # Experiences for each player
        
        # Play one game
        while not game.is_over():
            current_id = game.state.current_player_idx
            agent = agents[current_id]
            
            state = state_to_vector(game, current_id)
            legal_actions = game.get_legal_actions()
            action = agent.choose_action(game, legal_actions)
            action_idx = action_to_index(action)
            
            # Execute action
            game.execute_action(action)
            
            next_state = state_to_vector(game, current_id)
            done = game.is_over()
            
            # Immediate reward (small penalty for each turn to encourage efficiency)
            reward = -0.01
            
            episode_experiences[current_id].append({
                'state': state,
                'action': action_idx,
                'next_state': next_state,
                'done': done
            })
        
        # Assign final rewards based on outcome
        winner = game.get_winner()
        for player_id in range(2):
            final_reward = 1.0 if winner == player_id else -1.0
            
            for i, exp in enumerate(episode_experiences[player_id]):
                # Discounted reward from end of game
                steps_to_end = len(episode_experiences[player_id]) - i - 1
                reward = final_reward * (gamma ** steps_to_end)
                
                buffer.add(Experience(
                    state=exp['state'],
                    action=exp['action'],
                    reward=reward,
                    next_state=exp['next_state'],
                    done=exp['done']
                ))
        
        total_rewards.append(1 if winner == 0 else 0)
        
        # Training step
        if len(buffer) >= batch_size:
            batch = buffer.sample(batch_size)
            
            states = np.array([e.state for e in batch])
            actions = np.array([e.action for e in batch])
            rewards = np.array([e.reward for e in batch])
            next_states = np.array([e.next_state for e in batch])
            dones = np.array([e.done for e in batch], dtype=np.float32)
            
            # Compute targets
            next_q = target_net.predict(next_states)
            max_next_q = np.max(next_q, axis=1)
            targets = rewards + gamma * max_next_q * (1 - dones)
            
            # Update network
            loss = policy_net.update(states, targets, actions, lr=learning_rate)
        
        # Update target network
        if episode % target_update_freq == 0:
            target_net.copy_from(policy_net)
        
        # Decay epsilon
        epsilon = max(epsilon_end, epsilon * epsilon_decay)
        
        # Logging
        if (episode + 1) % 100 == 0:
            recent_winrate = sum(total_rewards[-100:]) / 100
            print(f"Episode {episode + 1}/{num_episodes}, "
                  f"Epsilon: {epsilon:.3f}, "
                  f"Recent P0 winrate: {recent_winrate:.2%}, "
                  f"Buffer: {len(buffer)}")
    
    # Save trained network
    if save_path:
        policy_net.save(save_path)
        print(f"Model saved to {save_path}")
    
    return policy_net


if __name__ == "__main__":
    print("=" * 60)
    print("TRAINING DQN AGENT")
    print("=" * 60)
    
    # Train
    trained_net = train_dqn(
        num_episodes=2000,
        batch_size=64,
        save_path="dqn_model.npz"
    )
    
    # Test against baselines
    from simulate import run_simulation, print_stats
    from agents import RandomAgent, AggressiveAgent
    
    print("\n" + "=" * 60)
    print("TESTING TRAINED DQN AGENT")
    print("=" * 60)
    
    # Test vs Random
    print("\n[Test] DQN vs Random (100 games)")
    stats = run_simulation(
        [lambda: DQNAgent(0, epsilon=0.0, trained_network=trained_net), RandomAgent],
        num_games=100
    )
    print_stats(stats)
    
    # Test vs Aggressive
    print("\n[Test] DQN vs Aggressive (100 games)")
    stats = run_simulation(
        [lambda: DQNAgent(0, epsilon=0.0, trained_network=trained_net), AggressiveAgent],
        num_games=100
    )
    print_stats(stats)
