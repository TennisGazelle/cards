#!/usr/lib/python3

import copy
import json
from random import randint
import random
from string import capwords
from textwrap import indent
from typing import List, Tuple
from xmlrpc.client import Boolean

NUM_DECKS = 6
SUITS = ['spades', 'hearts', 'clubs', 'diamonds']
VALUES = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10] # last three are JQK

# there are a few things any player can do
    # 0 hit (if possible)
    # 1 stay
    # 2 split (if applicable)
    # 3 double (if applicable)
ACTIONS = ['hit', 'stay', 'split', 'double']

GOOD_REWARD_VALUE=1
BAD_REWARD_VALUE=1

class Card:
    def __init__(self, suit: str, value: int) -> None:
        assert(suit in SUITS)
        assert(value in VALUES)
        self.suit = suit
        self.value = value
    
    def __str__(self) -> str:
        # return f'{self.value} of {self.suit}'
        return f'{self.value}'

class Hand:
    def __init__(self, cards: List[Card]) -> None:
        self.cards = cards

    def __str__(self) -> str:
        return f'[{[str(c) for c in self.cards]}]'

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
                        sum -= 10 # remove the first ace, make it a 1
                        isHard = True

                else:
                    # this is the first (or only) ace we see, check for 11 compatibility
                    containsAtLeastOneAce = True
                    if sum + 11 < 21:
                        isHard = False
                        sum += 11
                    else:
                        isHard = True # this one is technically redundant
                        sum += 1
            else:
                sum += x.value
                if containsAtLeastOneAce and sum > 21 and not isHard:
                    sum -= 10 # remove the first ace, make it a 1
                    isHard = True

        return sum, isHard
    
    def sort(self) -> List[Card]:
        sortedCards = copy.deepcopy(self.cards)
        sortedCards.sort(key=lambda c: c.value)
        return Hand(sortedCards)

    def isBlackJack(self) -> bool:
        h = self.sort()
        return len(self.cards) == 2 and h.get(0).value == 1 and h.get(1).value == 10

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

class Deck:
    def __init__(self) -> None:
        deck = []
        for _ in range(NUM_DECKS):
            for s in SUITS:
                for v in VALUES:
                    c = Card(s, v)
                    deck += [c]
        self.deck = deck
        self.index = 0
    
    def shuffle(self) -> None:
        size = len(self.deck)
        # new_indexes = range(size)
        for thisIndex in range(size):
            otherIndex = randint(thisIndex, size-1)

            buffer = self.deck[thisIndex]
            self.deck[thisIndex] = self.deck[otherIndex]
            self.deck[otherIndex] = buffer
    
    def fan(self):
        for c in self.deck:
            print(c)
    
    def next(self):
        c = self.deck[self.index]
        self.index = (self.index + 1) % len(self.deck)
        return c

    def reset(self):
        self.index = 0
        self.shuffle()

def test_shuffleDeck():
    d = Deck()
    d.shuffle()
    d.fan()

def test_prepDeck():
    d = Deck()
    d.shuffle()
    print('prep_deck')
    print(d.next())
    print(d.next())
    print(d.next())

class Player:
    def __init__(self, name: str, chips: int) -> None:
        self._name = name
        self.chips = chips or 1000000 # inf money for dealer
        self._hand = None
        self.states = {}

        self.last_states = []

        self.last_state_key = ''
        self.last_state_action_index = 0

    def __str__(self) -> str:
        return f'{self._name}-${self.chips}-{self._hand}'
    
    def hand(self) -> Hand:
        return self._hand

    def name(self):
        return self._name
    
    def be_dealt(self, c1: Card, c2: Card):
        self._hand = Hand([c1, c2])
    
    def get_one_more_card(self, c):
        self._hand.add_card(c)
    
    def get_q_states(self):
        return self.states

    def pick_q_action(self, dealerCard: Card) -> int: # just numbers 1,2,3,4
        # there are a few things any player can do
            # 0 hit (if possible)
            # 1 stay
            # 2 split (if applicable)
            # 3 double (if applicable)
        # they will be kept as Q-states in an array with probability vectors for each of them
        # the 'action' will be the one that was made, small memory kept
        # if action is good (tbd after this method), memory updated for probability vector

        # is this 'state' in q-table
        key = str(dealerCard) + '-' + str(self._hand.sort())
        if key not in self.states.keys():
            # initialize it, and make it all vectors possible
            self.states[key] = [1, 1, 1, 1]

        # shallow copy to keep track of updates
        tokenVector = self.states[key]
        # mem copy to keep track of most recent q lookup
        self.last_state_key = key
        
        # if i can split, consider index 2 in propability vector
        if self._hand.size() == 2 and self._hand.get(0).value == self._hand.get(1).value:
            pass
        else:
            tokenVector[2] = 0

        # if i can double, consider index 3 in probability vector
        if self._hand.size() == 2 and self._hand.getSum() in (9, 10, 11):
            pass
        else:
            tokenVector[3] = 0
        
        # convert token vector to probability vector
        tokenVectorSum = sum(tokenVector)
        probabilityVector = [float(v)/float(tokenVectorSum) for v in tokenVector]
        shot = random.uniform(0, 1)
        index = 0
        while shot > 0 and index < len(probabilityVector):
            shot -= probabilityVector[index]
            index += 1
        self.last_state_action_index = index-1
        return index-1
    
    def last_action_good(self):
        if self.last_state_key:
            self.states[self.last_state_key][self.last_state_action_index] += GOOD_REWARD_VALUE

    def last_action_bad(self):
        if self.last_state_key:
            self.states[self.last_state_key][self.last_state_action_index] -= BAD_REWARD_VALUE
        
def test_player_q_action():
    p1 = Player('danny', 1000)
    c1, c2, c3 = Card('spades', 1), Card('hearts', 5), Card('diamonds', 8)
    p1.be_dealt(c1, c2)
    print(p1)
    print('action', p1.pick_q_action(c3))

def test_view_player_q_action_states():
    p1 = Player('danny', 1000)
    d = Deck()
    d.shuffle()

    for i in range(1000):
        dealer_card = d.next()
        p1.be_dealt(d.next(), d.next())
        p1.pick_q_action(dealer_card)
        p1.last_action_good()
    
    print(json.dumps(p1.get_q_states(), indent=3))


class Table:
    def __init__(self, numPlayers: int) -> None:
        self.dealer = Player('dealer', 1000000) # inf money
        self.players = [Player(n, 100) for n in ('Danny', 'Honi', 'Sierra')]
        self.rounds = []
        self.current_round = None
        self.deck = Deck()

    def print_table_state(self):
        print(
            f'Dealer:', 
            None if not self.dealer.hand() else f'{self.dealer.hand()}', 
            0 if self.dealer.hand() == None else self.dealer.hand().getSum())
        for p in self.players:
            print(
                f'Player {p.name()}:',
                None if not p.hand() else p.hand(),
                0 if p.hand() == None else p.hand().getSum())

    # start a round
    def deal(self):
        self.deck.reset()

        self.dealer.be_dealt(self.deck.next(), self.deck.next())
        for p in self.players:
            p.be_dealt(self.deck.next(), self.deck.next())


def test_tableSetup():
    t = Table(3)
    t.print_table_state()

    t.deal()
    t.print_table_state()

def test_table_round():
    # init the players and dealer and deck
    dealer = Player('dealer', None)
    p1 = Player('danny', 1000)
    d = Deck()
    d.shuffle()

    # deal to everyone (just straight up, RR not important)
    dealer_showing_card = d.next()
    dealer.be_dealt(dealer_showing_card, d.next())
    p1.be_dealt(d.next(), d.next())

    # main loop for a single player, do this for all players in future
    action = ACTIONS[p1.pick_q_action(dealer_showing_card)]
    p1_sum, _ = p1.hand().getSum()
    print (p1.name(), action, p1_sum, p1.hand())
    while (action != 'stay'):

        # if action is hit
        if action == 'hit':
            p1.get_one_more_card(d.next())
            p1_sum, _ = p1.hand().getSum()

        # todo: if action is double
        if action == 'double':
            pass

        # todo: if action is split
        if action == 'split':
            pass

        # if i bust, call it out and stop
        if p1_sum > 21:
            # bust, call it bad
            p1.last_action_bad()
            print (p1.name(), action, p1_sum, p1.hand())
            # busted!
            print(p1.name(), 'BUST!')
            break

        action = ACTIONS[p1.pick_q_action(dealer_showing_card)]
        print (p1.name(), action, p1_sum, p1.hand())

    # do the mandatory loop for the dealer
    # dealer must hit on soft 17, pushes on 22
    dealer_sum, dealer_sum_is_hard = dealer.hand().getSum()
    print (dealer.name(), dealer_sum, dealer.hand())
    # todo, fix this logic
    while ((dealer_sum < 16 and dealer_sum_is_hard) or (dealer_sum < 17 and not dealer_sum_is_hard)):
        dealer.get_one_more_card(d.next())
        dealer_sum, dealer_sum_is_hard = dealer.hand().getSum()
        print (dealer.name(), dealer_sum, dealer.hand())

    # loop through players and determine their individual winnings (unless global push applies)
    if dealer_sum > 22:
        # dealer loses, everyone wins
        print('dealer lost hand, everyone wins')
        pass
    elif dealer_sum == 22:
        # everyone push
        print('everyone pushes')
        pass
    else:
        # determine individual win or not
        if p1_sum > 21:
            print(p1.name(), 'busted')
        elif dealer_sum > p1_sum:
            print(dealer.name(), 'beats', p1.name())
        elif p1_sum > dealer_sum:
            if p1.hand().isBlackJack():
                print(p1.name(), 'got blackjack')
            else:
                print(p1.name(), 'beats', dealer.name())
        else:
            print(p1.name(), 'pushes individually')

    # determine wins
    # p1.last_action_good()

    # for i in range(10):
    print(json.dumps(p1.get_q_states(), indent=3))


# set of all possible states, with all possible choices at each one and values for each

if __name__ == '__main__':
    # test_getSum()
    # test_shuffleDeck()
    # test_prepDeck()
    # test_sortHand()
    # test_tableSetup()
    # test_isBlackjack()
    # test_player_q_action()
    # test_view_player_q_action_states()
    test_table_round()