"""Core game logic for Exploding Kittens."""

import random
from typing import List, Optional, Tuple
from collections import Counter
from dataclasses import dataclass, field

from cards import Card, CardType, BASE_DECK_CONFIG, DEFUSE_IN_DECK, CAT_CARDS


@dataclass
class Player:
    id: int
    hand: List[Card] = field(default_factory=list)
    alive: bool = True
    
    def has_card(self, card_type: CardType) -> bool:
        return any(c.card_type == card_type for c in self.hand)
    
    def count_card(self, card_type: CardType) -> int:
        return sum(1 for c in self.hand if c.card_type == card_type)
    
    def remove_card(self, card_type: CardType) -> Optional[Card]:
        """Remove and return one card of the given type."""
        for i, card in enumerate(self.hand):
            if card.card_type == card_type:
                return self.hand.pop(i)
        return None
    
    def get_matching_cat_pairs(self) -> List[CardType]:
        """Return cat types that have 2+ cards (can be played as pair)."""
        counts = Counter(c.card_type for c in self.hand if c.card_type in CAT_CARDS)
        return [ct for ct, count in counts.items() if count >= 2]


@dataclass 
class GameState:
    players: List[Player]
    deck: List[Card]  # Top of deck is end of list (deck[-1])
    discard: List[Card] = field(default_factory=list)
    current_player_idx: int = 0
    turns_remaining: int = 1  # For Attack card
    game_over: bool = False
    winner: Optional[int] = None
    
    # For See the Future
    top_three_known_by: Optional[int] = None
    
    def current_player(self) -> Player:
        return self.players[self.current_player_idx]
    
    def other_player(self) -> Player:
        """For 2-player game, get the opponent."""
        return self.players[1 - self.current_player_idx]
    
    def alive_players(self) -> List[Player]:
        return [p for p in self.players if p.alive]
    
    def draw_card(self) -> Card:
        """Draw from top of deck."""
        return self.deck.pop()
    
    def peek_top(self, n: int = 3) -> List[Card]:
        """See top n cards without removing."""
        return self.deck[-n:] if len(self.deck) >= n else self.deck[:]
    
    def insert_card(self, card: Card, position: int):
        """Insert card into deck at position (0 = bottom, len = top)."""
        self.deck.insert(position, card)
    
    def shuffle_deck(self):
        random.shuffle(self.deck)
        self.top_three_known_by = None


class Action:
    """Represents a player action."""
    pass


@dataclass
class PlayCard(Action):
    card_type: CardType
    # For FAVOR: which player to target
    target_player_id: Optional[int] = None
    # For cat pairs: which card type to steal
    steal_card_type: Optional[CardType] = None


@dataclass
class PlayCatPair(Action):
    cat_type: CardType  # Which cat card to play 2 of
    target_player_id: int


@dataclass
class PlayNope(Action):
    """Nope the current action."""
    pass


@dataclass
class Pass(Action):
    """Don't play any card, proceed to draw."""
    pass


@dataclass
class InsertExplodingKitten(Action):
    """After defusing, where to put the EK."""
    position: int  # 0 = bottom, len(deck) = top


class Game:
    def __init__(self, num_players: int = 2, seed: Optional[int] = None):
        if seed is not None:
            random.seed(seed)
        
        self.num_players = num_players
        self.state = self._setup_game()
        self.action_history: List[Tuple[int, Action]] = []
    
    def _setup_game(self) -> GameState:
        # Create players
        players = [Player(id=i) for i in range(self.num_players)]
        
        # Build deck (without EK and Defuses initially)
        deck = []
        for card_type, count in BASE_DECK_CONFIG.items():
            deck.extend([Card(card_type) for _ in range(count)])
        
        # Shuffle and deal 4 cards to each player
        random.shuffle(deck)
        for player in players:
            for _ in range(4):
                player.hand.append(deck.pop())
            # Give each player 1 Defuse
            player.hand.append(Card(CardType.DEFUSE))
        
        # Add remaining Defuses to deck
        for _ in range(DEFUSE_IN_DECK):
            deck.append(Card(CardType.DEFUSE))
        
        # Shuffle again, then add Exploding Kittens
        random.shuffle(deck)
        
        # Add (num_players - 1) Exploding Kittens
        for _ in range(self.num_players - 1):
            deck.append(Card(CardType.EXPLODING_KITTEN))
        
        # Final shuffle
        random.shuffle(deck)
        
        return GameState(players=players, deck=deck)
    
    def get_legal_actions(self, player_id: Optional[int] = None) -> List[Action]:
        """Get all legal actions for the current player."""
        if player_id is None:
            player_id = self.state.current_player_idx
        
        player = self.state.players[player_id]
        actions = []
        
        # Can always pass (then draw)
        actions.append(Pass())
        
        # Action cards
        for card_type in [CardType.ATTACK, CardType.SKIP, CardType.SHUFFLE, 
                         CardType.SEE_THE_FUTURE]:
            if player.has_card(card_type):
                actions.append(PlayCard(card_type))
        
        # Favor requires a target
        if player.has_card(CardType.FAVOR):
            for other in self.state.players:
                if other.id != player_id and other.alive and len(other.hand) > 0:
                    actions.append(PlayCard(CardType.FAVOR, target_player_id=other.id))
        
        # Cat pairs - steal random card from opponent
        for cat_type in player.get_matching_cat_pairs():
            for other in self.state.players:
                if other.id != player_id and other.alive and len(other.hand) > 0:
                    actions.append(PlayCatPair(cat_type, target_player_id=other.id))
        
        # Note: NOPE is reactive, handled separately
        # Note: DEFUSE is automatic when drawing EK
        
        return actions
    
    def get_insert_positions(self) -> List[int]:
        """After defusing, get legal positions to insert EK."""
        return list(range(len(self.state.deck) + 1))
    
    def execute_action(self, action: Action) -> dict:
        """Execute an action and return result info."""
        player = self.state.current_player()
        result = {"action": action, "player": player.id}
        
        if isinstance(action, Pass):
            result["type"] = "pass"
            result.update(self._do_draw())
        
        elif isinstance(action, PlayCard):
            card = player.remove_card(action.card_type)
            self.state.discard.append(card)
            result["type"] = "play_card"
            result["card"] = action.card_type
            
            if action.card_type == CardType.ATTACK:
                self._do_attack()
                result["effect"] = "attack"
            
            elif action.card_type == CardType.SKIP:
                self._do_skip()
                result["effect"] = "skip"
            
            elif action.card_type == CardType.SHUFFLE:
                self.state.shuffle_deck()
                result["effect"] = "shuffle"
            
            elif action.card_type == CardType.SEE_THE_FUTURE:
                top_cards = self.state.peek_top(3)
                self.state.top_three_known_by = player.id
                result["effect"] = "see_future"
                result["seen_cards"] = [c.card_type for c in top_cards]
            
            elif action.card_type == CardType.FAVOR:
                target = self.state.players[action.target_player_id]
                if target.hand:
                    # Target chooses which card to give (for now: random)
                    stolen = target.hand.pop(random.randint(0, len(target.hand) - 1))
                    player.hand.append(stolen)
                    result["effect"] = "favor"
                    result["stolen"] = stolen.card_type
        
        elif isinstance(action, PlayCatPair):
            # Remove 2 cat cards
            player.remove_card(action.cat_type)
            player.remove_card(action.cat_type)
            self.state.discard.append(Card(action.cat_type))
            self.state.discard.append(Card(action.cat_type))
            
            # Steal random card from target
            target = self.state.players[action.target_player_id]
            if target.hand:
                stolen = target.hand.pop(random.randint(0, len(target.hand) - 1))
                player.hand.append(stolen)
                result["type"] = "cat_pair"
                result["stolen"] = stolen.card_type
        
        elif isinstance(action, InsertExplodingKitten):
            # Insert EK back into deck
            ek = Card(CardType.EXPLODING_KITTEN)
            self.state.insert_card(ek, action.position)
            result["type"] = "insert_ek"
            result["position"] = action.position
        
        self.action_history.append((player.id, action))
        self._check_game_over()
        
        return result
    
    def _do_draw(self) -> dict:
        """Handle drawing a card at end of turn."""
        player = self.state.current_player()
        result = {}
        
        if not self.state.deck:
            result["draw"] = None
            self._end_turn()
            return result
        
        card = self.state.draw_card()
        result["draw"] = card.card_type
        
        if card.card_type == CardType.EXPLODING_KITTEN:
            result["exploded"] = True
            if player.has_card(CardType.DEFUSE):
                # Auto-defuse
                defuse = player.remove_card(CardType.DEFUSE)
                self.state.discard.append(defuse)
                result["defused"] = True
                # Need to insert EK back - for now, random position
                # In real game, agent chooses this
                pos = random.randint(0, len(self.state.deck))
                self.state.insert_card(card, pos)
                result["insert_position"] = pos
            else:
                # Player explodes
                player.alive = False
                result["defused"] = False
                self.state.discard.append(card)
        else:
            player.hand.append(card)
            result["exploded"] = False
        
        self._end_turn()
        return result
    
    def _do_attack(self):
        """Attack: end turn without drawing, next player takes 2 turns."""
        next_idx = (self.state.current_player_idx + 1) % self.num_players
        # Find next alive player
        while not self.state.players[next_idx].alive:
            next_idx = (next_idx + 1) % self.num_players
        
        self.state.current_player_idx = next_idx
        self.state.turns_remaining = 2
    
    def _do_skip(self):
        """Skip: end current turn without drawing."""
        self.state.turns_remaining -= 1
        if self.state.turns_remaining <= 0:
            self._advance_player()
            self.state.turns_remaining = 1
    
    def _end_turn(self):
        """End current turn after drawing."""
        self.state.turns_remaining -= 1
        if self.state.turns_remaining <= 0:
            self._advance_player()
            self.state.turns_remaining = 1
    
    def _advance_player(self):
        """Move to next alive player."""
        next_idx = (self.state.current_player_idx + 1) % self.num_players
        while not self.state.players[next_idx].alive:
            next_idx = (next_idx + 1) % self.num_players
        self.state.current_player_idx = next_idx
    
    def _check_game_over(self):
        """Check if game has ended."""
        alive = self.state.alive_players()
        if len(alive) == 1:
            self.state.game_over = True
            self.state.winner = alive[0].id
    
    def is_over(self) -> bool:
        return self.state.game_over
    
    def get_winner(self) -> Optional[int]:
        return self.state.winner
