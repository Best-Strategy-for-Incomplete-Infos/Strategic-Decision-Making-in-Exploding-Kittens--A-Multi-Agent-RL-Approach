"""Agent implementations for Exploding Kittens."""

from abc import ABC, abstractmethod
from typing import List
import random

from game import Game, Action, Pass, PlayCard, PlayCatPair, GameState
from cards import CardType


class Agent(ABC):
    """Base class for Exploding Kittens agents."""
    
    def __init__(self, player_id: int):
        self.player_id = player_id
    
    @abstractmethod
    def choose_action(self, game: Game, legal_actions: List[Action]) -> Action:
        """Choose an action from legal actions."""
        pass
    
    @abstractmethod
    def choose_insert_position(self, game: Game, max_position: int) -> int:
        """Choose where to insert Exploding Kitten after defusing."""
        pass
    
    def choose_card_to_give(self, game: Game) -> CardType:
        """When targeted by Favor, choose which card to give."""
        # Default: give random card
        hand = game.state.players[self.player_id].hand
        return random.choice(hand).card_type


class RandomAgent(Agent):
    """Agent that plays randomly."""
    
    def choose_action(self, game: Game, legal_actions: List[Action]) -> Action:
        return random.choice(legal_actions)
    
    def choose_insert_position(self, game: Game, max_position: int) -> int:
        return random.randint(0, max_position)


class PassiveAgent(Agent):
    """Agent that always passes (only draws cards)."""
    
    def choose_action(self, game: Game, legal_actions: List[Action]) -> Action:
        # Always pass if possible
        for action in legal_actions:
            if isinstance(action, Pass):
                return action
        return random.choice(legal_actions)
    
    def choose_insert_position(self, game: Game, max_position: int) -> int:
        # Put EK on top (opponent draws it next)
        return max_position


class AggressiveAgent(Agent):
    """Agent that prioritizes offensive cards (Attack, Favor, cat pairs)."""
    
    def choose_action(self, game: Game, legal_actions: List[Action]) -> Action:
        # Priority: Attack > Cat Pair > Favor > Skip > others > Pass
        
        # First, look for Attack
        for action in legal_actions:
            if isinstance(action, PlayCard) and action.card_type == CardType.ATTACK:
                return action
        
        # Then cat pairs (steal cards)
        for action in legal_actions:
            if isinstance(action, PlayCatPair):
                return action
        
        # Then Favor
        for action in legal_actions:
            if isinstance(action, PlayCard) and action.card_type == CardType.FAVOR:
                return action
        
        # Skip if we have extra turns to burn
        if game.state.turns_remaining > 1:
            for action in legal_actions:
                if isinstance(action, PlayCard) and action.card_type == CardType.SKIP:
                    return action
        
        # Otherwise just pass and draw
        for action in legal_actions:
            if isinstance(action, Pass):
                return action
        
        return random.choice(legal_actions)
    
    def choose_insert_position(self, game: Game, max_position: int) -> int:
        # Put EK near top so opponent likely draws it
        if max_position >= 2:
            return max_position - 1  # Second from top
        return max_position


class DefensiveAgent(Agent):
    """Agent that prioritizes survival (Skip, Shuffle, See the Future)."""
    
    def choose_action(self, game: Game, legal_actions: List[Action]) -> Action:
        player = game.state.players[self.player_id]
        deck_size = len(game.state.deck)
        
        # If deck is small and we don't have defuse, be careful
        has_defuse = player.has_card(CardType.DEFUSE)
        danger = deck_size <= 5 and not has_defuse
        
        if danger:
            # Prioritize: Skip > Attack > Shuffle > See Future
            for action in legal_actions:
                if isinstance(action, PlayCard) and action.card_type == CardType.SKIP:
                    return action
            for action in legal_actions:
                if isinstance(action, PlayCard) and action.card_type == CardType.ATTACK:
                    return action
        
        # Use See the Future if we haven't recently
        if game.state.top_three_known_by != self.player_id:
            for action in legal_actions:
                if isinstance(action, PlayCard) and action.card_type == CardType.SEE_THE_FUTURE:
                    return action
        
        # Shuffle if we saw EK in top 3
        if game.state.top_three_known_by == self.player_id:
            top_cards = game.state.peek_top(3)
            if any(c.card_type == CardType.EXPLODING_KITTEN for c in top_cards):
                for action in legal_actions:
                    if isinstance(action, PlayCard) and action.card_type == CardType.SHUFFLE:
                        return action
                for action in legal_actions:
                    if isinstance(action, PlayCard) and action.card_type == CardType.SKIP:
                        return action
        
        # Default: pass
        for action in legal_actions:
            if isinstance(action, Pass):
                return action
        
        return random.choice(legal_actions)
    
    def choose_insert_position(self, game: Game, max_position: int) -> int:
        # Put EK at bottom (safest for us later)
        return 0
