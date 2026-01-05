"""Smart heuristic agent that mimics human-level play.

Key insights for Exploding Kittens strategy:
1. Card counting: track where EK might be
2. Defuse management: protect your defuse, know if opponent has one
3. Tempo control: use Attack/Skip to avoid drawing
4. Information advantage: See the Future is extremely powerful
5. Resource denial: steal cards to weaken opponent
"""

import random
from typing import List, Dict, Optional, Tuple
from collections import Counter

from game import Game, GameState, Action, Pass, PlayCard, PlayCatPair
from cards import Card, CardType, CAT_CARDS
from agents import Agent


class SmartAgent(Agent):
    """
    Human-like agent using strategic heuristics.
    
    Strategy principles:
    1. Never draw if you can avoid it (especially without defuse)
    2. Use information cards early
    3. Attack when opponent is weak
    4. Save defuse as last resort
    5. Count cards to estimate EK probability
    """
    
    def __init__(self, player_id: int, aggression: float = 0.5):
        super().__init__(player_id)
        self.aggression = aggression  # 0 = defensive, 1 = aggressive
    
    def choose_action(self, game: Game, legal_actions: List[Action]) -> Action:
        player = game.state.players[self.player_id]
        opponent = game.state.players[1 - self.player_id]
        
        # Game state analysis
        deck_size = len(game.state.deck)
        my_hand_size = len(player.hand)
        opp_hand_size = len(opponent.hand)
        
        has_defuse = player.has_card(CardType.DEFUSE)
        opp_has_defuse = self._estimate_opponent_defuse(game)
        
        ek_prob = self._estimate_ek_probability(game)
        i_know_top = game.state.top_three_known_by == self.player_id
        
        # Check if EK is in top cards (if we know)
        ek_on_top = False
        ek_position = -1
        if i_know_top and deck_size > 0:
            top_cards = game.state.peek_top(3)
            for i, card in enumerate(reversed(top_cards)):
                if card.card_type == CardType.EXPLODING_KITTEN:
                    ek_on_top = True
                    ek_position = i  # 0 = very top
                    break
        
        # CRITICAL: Small deck = high danger, MUST avoid drawing
        if deck_size <= 3 and not has_defuse:
            # Survival is top priority!
            for action in legal_actions:
                if isinstance(action, PlayCard) and action.card_type == CardType.ATTACK:
                    return action
            for action in legal_actions:
                if isinstance(action, PlayCard) and action.card_type == CardType.SKIP:
                    return action
            for action in legal_actions:
                if isinstance(action, PlayCard) and action.card_type == CardType.SHUFFLE:
                    return action
        
        # CRITICAL: If EK is on top and we'll draw it
        if ek_on_top and ek_position == 0:
            # Must avoid drawing!
            for action in legal_actions:
                if isinstance(action, PlayCard) and action.card_type == CardType.SKIP:
                    return action
            for action in legal_actions:
                if isinstance(action, PlayCard) and action.card_type == CardType.ATTACK:
                    return action
            for action in legal_actions:
                if isinstance(action, PlayCard) and action.card_type == CardType.SHUFFLE:
                    return action
        
        # HIGH DANGER: Low deck, no defuse
        danger_level = self._calculate_danger(ek_prob, has_defuse, deck_size)
        
        if danger_level > 0.5:  # Lowered threshold
            action = self._survival_action(game, legal_actions, ek_on_top)
            if action:
                return action
        
        # OPPORTUNITY: Attack when opponent is vulnerable
        if not opp_has_defuse and deck_size <= 10:
            for action in legal_actions:
                if isinstance(action, PlayCard) and action.card_type == CardType.ATTACK:
                    return action
        
        # INFORMATION: Use See the Future if we don't know deck state
        if not i_know_top and deck_size > 3 and deck_size <= 15:
            for action in legal_actions:
                if isinstance(action, PlayCard) and action.card_type == CardType.SEE_THE_FUTURE:
                    return action
        
        # TEMPO: Attack to force opponent to draw more
        if has_defuse and deck_size <= 15 and random.random() < self.aggression:
            for action in legal_actions:
                if isinstance(action, PlayCard) and action.card_type == CardType.ATTACK:
                    return action
        
        # RESOURCE DENIAL: Steal cards if opponent has more
        if opp_hand_size > my_hand_size + 2:
            # Use Favor
            for action in legal_actions:
                if isinstance(action, PlayCard) and action.card_type == CardType.FAVOR:
                    return action
            # Use cat pairs
            for action in legal_actions:
                if isinstance(action, PlayCatPair):
                    return action
        
        # SHUFFLE: If we know EK is coming soon
        if i_know_top and ek_on_top and ek_position <= 2:
            for action in legal_actions:
                if isinstance(action, PlayCard) and action.card_type == CardType.SHUFFLE:
                    return action
        
        # SKIP: Use extra skips to burn Attack turns
        if game.state.turns_remaining > 1:
            for action in legal_actions:
                if isinstance(action, PlayCard) and action.card_type == CardType.SKIP:
                    return action
        
        # LOW PRIORITY: Use cat pairs for card advantage
        if my_hand_size >= 6 and opp_hand_size > 0:
            cat_pairs = [a for a in legal_actions if isinstance(a, PlayCatPair)]
            if cat_pairs and random.random() < 0.3:
                return random.choice(cat_pairs)
        
        # DEFAULT: Pass and draw
        for action in legal_actions:
            if isinstance(action, Pass):
                return action
        
        return random.choice(legal_actions)
    
    def _estimate_ek_probability(self, game: Game) -> float:
        """Estimate probability of drawing EK."""
        deck_size = len(game.state.deck)
        if deck_size == 0:
            return 0.0
        
        # Count EK in discard (used by defuse)
        ek_in_discard = sum(1 for c in game.state.discard 
                          if c.card_type == CardType.EXPLODING_KITTEN)
        
        # In 2-player, 1 EK total
        ek_remaining = 1 - ek_in_discard
        
        if ek_remaining <= 0:
            return 0.0
        
        return ek_remaining / deck_size
    
    def _estimate_opponent_defuse(self, game: Game) -> bool:
        """Estimate if opponent likely has a defuse."""
        opponent = game.state.players[1 - self.player_id]
        
        # Count defuses in discard
        defuse_in_discard = sum(1 for c in game.state.discard 
                               if c.card_type == CardType.DEFUSE)
        
        # In 2-player: each starts with 1, 2 in deck = 4 total
        # If opponent has drawn many cards and defuse not in discard,
        # they probably have one
        
        if defuse_in_discard >= 2:
            # At least some defuses are gone
            return len(opponent.hand) > 3
        
        # Assume they have one if they haven't used it
        return True
    
    def _calculate_danger(self, ek_prob: float, has_defuse: bool, deck_size: int) -> float:
        """Calculate current danger level (0-1)."""
        if has_defuse:
            return ek_prob * 0.3  # Much less dangerous with defuse
        
        # No defuse - danger scales with EK probability
        base_danger = ek_prob
        
        # Extra danger if deck is small
        if deck_size <= 5:
            base_danger *= 1.5
        elif deck_size <= 10:
            base_danger *= 1.2
        
        return min(1.0, base_danger)
    
    def _survival_action(self, game: Game, legal_actions: List[Action], 
                        ek_on_top: bool) -> Optional[Action]:
        """Find best action to survive dangerous situation."""
        # Priority when in danger:
        # 1. Skip (avoid drawing)
        # 2. Attack (make opponent draw instead)
        # 3. Shuffle (if we know EK is near top)
        # 4. See Future (gain information)
        
        for action in legal_actions:
            if isinstance(action, PlayCard) and action.card_type == CardType.SKIP:
                return action
        
        for action in legal_actions:
            if isinstance(action, PlayCard) and action.card_type == CardType.ATTACK:
                return action
        
        if ek_on_top:
            for action in legal_actions:
                if isinstance(action, PlayCard) and action.card_type == CardType.SHUFFLE:
                    return action
        
        for action in legal_actions:
            if isinstance(action, PlayCard) and action.card_type == CardType.SEE_THE_FUTURE:
                return action
        
        return None
    
    def choose_insert_position(self, game: Game, max_position: int) -> int:
        """
        Strategic EK placement after defusing.
        
        Key insight: Put it where opponent will likely draw it,
        but not so obvious that they can predict and use Shuffle.
        """
        if max_position == 0:
            return 0
        
        opponent = game.state.players[1 - self.player_id]
        opp_has_skip = opponent.has_card(CardType.SKIP)
        opp_has_attack = opponent.has_card(CardType.ATTACK)
        opp_has_shuffle = opponent.has_card(CardType.SHUFFLE)
        opp_has_stf = opponent.has_card(CardType.SEE_THE_FUTURE)
        
        # If opponent can see future, don't put on top
        # If opponent has shuffle, position doesn't matter much
        
        if opp_has_shuffle:
            # Random position since they might shuffle anyway
            return random.randint(0, max_position)
        
        if opp_has_stf:
            # Put 4+ cards deep to avoid their peek
            if max_position >= 4:
                return max_position - random.randint(4, min(6, max_position))
            return random.randint(0, max_position)
        
        if opp_has_skip or opp_has_attack:
            # They can avoid top card, put 2nd or 3rd
            if max_position >= 2:
                return max_position - random.randint(1, 2)
        
        # Default: put near top
        if max_position >= 2:
            return max_position - 1
        return max_position
    
    def choose_card_to_give(self, game: Game) -> CardType:
        """When targeted by Favor, give least valuable card."""
        player = game.state.players[self.player_id]
        
        # Never give Defuse if possible
        non_defuse = [c for c in player.hand if c.card_type != CardType.DEFUSE]
        if non_defuse:
            # Priority to give: Cat cards > Nope > action cards
            cat_cards = [c for c in non_defuse if c.card_type in CAT_CARDS]
            if cat_cards:
                # Give singleton cats (can't use for pairs)
                counts = Counter(c.card_type for c in cat_cards)
                singletons = [ct for ct, count in counts.items() if count == 1]
                if singletons:
                    return random.choice(singletons)
                return random.choice(cat_cards).card_type
            
            return random.choice(non_defuse).card_type
        
        # Have to give Defuse :(
        return CardType.DEFUSE


class ExpertAgent(SmartAgent):
    """
    Even smarter agent with deeper analysis.
    """
    
    def __init__(self, player_id: int):
        super().__init__(player_id, aggression=0.6)
    
    def choose_action(self, game: Game, legal_actions: List[Action]) -> Action:
        # First check for obvious plays using parent logic
        player = game.state.players[self.player_id]
        opponent = game.state.players[1 - self.player_id]
        deck_size = len(game.state.deck)
        
        has_defuse = player.has_card(CardType.DEFUSE)
        ek_prob = self._estimate_ek_probability(game)
        
        i_know_top = game.state.top_three_known_by == self.player_id
        
        # EXPERT INSIGHT 1: Card counting for EK position
        # If we've tracked cards, we might know EK position even without STF
        
        # EXPERT INSIGHT 2: Combo plays
        # Attack + putting EK on top = opponent draws EK twice
        if has_defuse and deck_size <= 5:
            for action in legal_actions:
                if isinstance(action, PlayCard) and action.card_type == CardType.ATTACK:
                    return action
        
        # EXPERT INSIGHT 3: Bait opponent's defuse
        # If they have defuse and deck is small, attack to force them to use it
        if self._estimate_opponent_defuse(game) and deck_size <= 8:
            for action in legal_actions:
                if isinstance(action, PlayCard) and action.card_type == CardType.ATTACK:
                    return action
        
        # EXPERT INSIGHT 4: Information denial
        # Use Shuffle after opponent uses See the Future
        if game.state.top_three_known_by == (1 - self.player_id):
            for action in legal_actions:
                if isinstance(action, PlayCard) and action.card_type == CardType.SHUFFLE:
                    if random.random() < 0.7:  # Not always, to be unpredictable
                        return action
        
        # EXPERT INSIGHT 5: Resource management
        # Don't waste cards early, save for endgame
        if deck_size > 20 and len(player.hand) <= 4:
            # Conservative play early
            for action in legal_actions:
                if isinstance(action, Pass):
                    return action
        
        # Fall back to parent logic
        return super().choose_action(game, legal_actions)
    
    def choose_insert_position(self, game: Game, max_position: int) -> int:
        """Expert EK placement with mind games."""
        if max_position <= 1:
            return max_position
        
        # Count how many cards opponent will draw before us
        turns = game.state.turns_remaining
        
        # If opponent has Attack, assume they'll use it
        opponent = game.state.players[1 - self.player_id]
        if opponent.has_card(CardType.ATTACK):
            # They'll probably attack, so we draw next
            # Put EK deep
            if max_position >= 3:
                return random.randint(0, max_position // 2)
        
        # Default expert placement: 2-3 cards from top
        if max_position >= 3:
            return max_position - random.randint(2, 3)
        return max_position - 1


if __name__ == "__main__":
    from simulate import run_simulation, print_stats
    from agents import RandomAgent, AggressiveAgent, DefensiveAgent
    
    print("=" * 60)
    print("TESTING SMART AGENTS")
    print("=" * 60)
    
    # Test Smart Agent
    print("\n[Test 1] SmartAgent vs Random (500 games)")
    stats = run_simulation([SmartAgent, RandomAgent], num_games=500, seed_start=42)
    print_stats(stats)
    
    print("\n[Test 2] SmartAgent vs Aggressive (500 games)")
    stats = run_simulation([SmartAgent, AggressiveAgent], num_games=500, seed_start=42)
    print_stats(stats)
    
    print("\n[Test 3] SmartAgent vs Defensive (500 games)")
    stats = run_simulation([SmartAgent, DefensiveAgent], num_games=500, seed_start=42)
    print_stats(stats)
    
    # Test Expert Agent
    print("\n[Test 4] ExpertAgent vs Random (500 games)")
    stats = run_simulation([ExpertAgent, RandomAgent], num_games=500, seed_start=42)
    print_stats(stats)
    
    print("\n[Test 5] ExpertAgent vs SmartAgent (500 games)")
    stats = run_simulation([ExpertAgent, SmartAgent], num_games=500, seed_start=42)
    print_stats(stats)
    
    # Head to head comparison
    print("\n[Test 6] ExpertAgent vs Aggressive (500 games)")
    stats = run_simulation([ExpertAgent, AggressiveAgent], num_games=500, seed_start=42)
    print_stats(stats)
    
    # Symmetric test (both ways)
    print("\n[Test 7] SmartAgent vs SmartAgent (1000 games) - Position Analysis")
    stats = run_simulation([SmartAgent, SmartAgent], num_games=1000, seed_start=42)
    print_stats(stats)
