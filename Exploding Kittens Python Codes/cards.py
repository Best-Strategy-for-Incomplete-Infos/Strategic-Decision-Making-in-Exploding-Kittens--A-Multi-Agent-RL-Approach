"""Card definitions for Exploding Kittens."""

from enum import Enum, auto
from dataclasses import dataclass


class CardType(Enum):
    # Special cards
    EXPLODING_KITTEN = auto()
    DEFUSE = auto()
    
    # Action cards
    ATTACK = auto()
    SKIP = auto()
    FAVOR = auto()
    SHUFFLE = auto()
    SEE_THE_FUTURE = auto()
    NOPE = auto()
    
    # Cat cards (for combos)
    CAT_TACOCAT = auto()
    CAT_CATTERMELON = auto()
    CAT_HAIRY_POTATO = auto()
    CAT_BEARD_CAT = auto()
    CAT_RAINBOW_CAT = auto()


# Cards that can be played as actions
ACTION_CARDS = {
    CardType.ATTACK,
    CardType.SKIP,
    CardType.FAVOR,
    CardType.SHUFFLE,
    CardType.SEE_THE_FUTURE,
    CardType.NOPE,
}

# Cat cards (no individual effect, used for combos)
CAT_CARDS = {
    CardType.CAT_TACOCAT,
    CardType.CAT_CATTERMELON,
    CardType.CAT_HAIRY_POTATO,
    CardType.CAT_BEARD_CAT,
    CardType.CAT_RAINBOW_CAT,
}


# Base game deck configuration (without Exploding Kittens and Defuses)
BASE_DECK_CONFIG = {
    CardType.ATTACK: 4,
    CardType.SKIP: 4,
    CardType.FAVOR: 4,
    CardType.SHUFFLE: 4,
    CardType.SEE_THE_FUTURE: 5,
    CardType.NOPE: 5,
    CardType.CAT_TACOCAT: 4,
    CardType.CAT_CATTERMELON: 4,
    CardType.CAT_HAIRY_POTATO: 4,
    CardType.CAT_BEARD_CAT: 4,
    CardType.CAT_RAINBOW_CAT: 4,
}

# Defuse cards in deck (not dealt to players)
DEFUSE_IN_DECK = 2  # For 2-3 players, 2 extra defuses in deck


@dataclass
class Card:
    card_type: CardType
    
    def __repr__(self):
        return f"{self.card_type.name}"
    
    def is_cat(self) -> bool:
        return self.card_type in CAT_CARDS
    
    def is_action(self) -> bool:
        return self.card_type in ACTION_CARDS
