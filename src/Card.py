from src.constants import *

class Card:
    def __init__(self, suit: str, value: int) -> None:
        assert (suit in SUITS)
        assert (value in VALUES)
        self.suit = suit
        self.value = value

    def __str__(self) -> str:
        # return f'{self.value} of {self.suit}'
        return f'{self.value}' + (SUIT_EMOJIS[self.suit] if INCLUDE_SUIT_IN_CARD_VALUE else '')