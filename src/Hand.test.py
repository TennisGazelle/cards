from src.Card import Card
from src.Hand import Hand

def test_getSum():
    c1 = Card('spades', 1)
    c2 = Card('hearts', 1)
    c3 = Card('spades', 6)
    h = Hand([c1, c2, c3])

    sum, isHard = h.getSum()
    print(h, 'sum:', sum, 'hard' if isHard else 'soft')
    assert(sum == 18)
    assert(isHard == False)

    c1 = Card('spades', 1)
    c2 = Card('hearts', 1)
    c3 = Card('diamonds', 10)
    c4 = Card('clubs', 1)
    h = Hand([c1, c2, c3, c4])

    sum, isHard = h.getSum()
    print(h, 'sum:', sum, 'hard' if isHard else 'soft')
    assert(sum == 13)
    assert(isHard == True)

def test_sortHand():
    c1 = Card('diamonds', 5)
    c2 = Card('hearts', 1)
    c3 = Card('spades', 4)
    h = Hand([c1, c2, c3])
    print(h)
    print(h.sort())

def test_isBlackjack():
    c1 = Card('diamonds', 1)
    c2 = Card('spades', 10)
    h = Hand([c1, c2])
    print(h)
    print(h.isBlackJack())
    assert(h.isBlackJack())