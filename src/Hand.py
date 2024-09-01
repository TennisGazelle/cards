import copy
from typing import List, Tuple

from src.Card import Card

class Hand:
    def __init__(self, cards: List[Card]) -> None:
        self.cards = cards

    def __str__(self) -> str:
        return f'{[str(c) for c in self.cards]}'

    def size(self) -> int:
        return len(self.cards)

    def get(self, index) -> int:
        assert index < len(self.cards)
        return self.cards[index]

    def add_card(self, c: Card):
        self.cards.append(c)

    def getSum(self) -> Tuple[int, bool]:
        if not self.cards or len(self.cards) == 0:
            return 0

        sum = 0
        isHard = True
        containsAtLeastOneAce = False
        for x in self.cards:
            # print(sum)
            # if it's an ace, check to see if its hard
            if x.value == 1:
                if containsAtLeastOneAce:
                    # there can only be at most one ace that's hard
                    # the first one seen (if previously) could still be reduced if we overflow, if we can (i.e. if notisHard)
                    # we can only ever add one, but if needed, we should reduce the first one
                    sum += 1
                    if sum > 21 and not isHard:
                        sum -= 10  # remove the first ace, make it a 1
                        isHard = True

                else:
                    # this is the first (or only) ace we see, check for 11 compatibility
                    containsAtLeastOneAce = True
                    if sum + 11 < 21:
                        isHard = False
                        sum += 11
                    else:
                        isHard = True  # this one is technically redundant
                        sum += 1
            else:
                sum += x.value
                if containsAtLeastOneAce and sum > 21 and not isHard:
                    sum -= 10  # remove the first ace, make it a 1
                    isHard = True

        return sum, isHard

    def sort(self) -> List[Card]:
        sortedCards = copy.deepcopy(self.cards)
        sortedCards.sort(key=lambda c: c.value)
        return Hand(sortedCards)

    def isBlackJack(self) -> bool:
        h = self.sort()
        return len(self.cards) == 2 and h.get(0).value == 1 and h.get(1).value == 10
