from random import randint

from src.constants import *
from src.Card import Card

class Deck:
    def __init__(self, num_decks=NUM_DECKS) -> None:
        deck = []
        for _ in range(num_decks):
            for s in SUITS:
                for v in VALUES:
                    c = Card(s, v)
                    deck += [c]
        self.deck = deck
        self.index = 0

    def len(self):
        return len(self.deck)

    def shuffle(self) -> None:
        size = len(self.deck)
        # new_indexes = range(size)
        for thisIndex in range(size):
            otherIndex = randint(thisIndex, size - 1)
            # swap this and other
            buffer = self.deck[thisIndex]
            self.deck[thisIndex] = self.deck[otherIndex]
            self.deck[otherIndex] = buffer

    def fan(self):
        line = ''
        for c in self.deck:
            line += f'{c} '
        print(line)

    # as opposed to the deck iterator's __next_ function,
    # this will shuffle the deck if it needs to wrap around the deck
    def next(self):
        c = self.deck[self.index]
        self.index = (self.index + 1) % len(self.deck)
        if self.index == 0:
            self.shuffle()
        return c

    # def __next__(self):
    #     c = self.deck[self._index]
    #     if self._index < len(cards):
    #         # result = cards[self._index]
    #         self._index += 1;
    #         return c
    #     return StopIteration

    def reset(self):
        self.index = 0
        self.shuffle()

    # def cards(self) -> List:
    #     return self.cards

    def __iter__(self):
        return DeckIterator(self)


class DeckIterator:
    def __init__(self, deck: Deck) -> None:
        self.deck = deck
        self._index = 0

    def __next__(self):
        if self._index < len(self.deck.deck):
            result = self.deck.deck[self._index]
            self._index += 1;
            return result
        raise StopIteration

