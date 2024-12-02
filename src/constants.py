NUM_DECKS = 6
SUITS = ['spades', 'hearts', 'clubs', 'diamonds']
SUIT_EMOJIS = {
    'spades': '♠️',
    'hearts': '❤️',
    'clubs': '♣️',
    'diamonds': '♦️'
}
VALUES = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10] # last three are JQK

# there are a few things any player can do
    # 0 hit (if possible)
    # 1 stay
    # 2 split (if applicable)
    # 3 double (if applicable)
ACTIONS = ['hit', 'stay', 'split', 'double']
DEFAULT_VECTOR = [1, 1, 1, 1]

GOOD_REWARD_VALUE=9
BAD_REWARD_VALUE=3

INCLUDE_DEALER_IN_Q_STATE=True
INCLUDE_SUIT_IN_CARD_VALUE=False
NUM_TRAINING_ITERATIONS=1000

PLAYER_NAME_CHOICES = ['daniel', 'honi', 'sierra', 'oliver', 'alex', 'kathir', 'ben']
DEALER_NAME_CHOICES = ['Dealer-Pablo', 'Dealer-Liz', 'Dealer-Mina', 'Dealer-Jon']

TableRoundStates = {
    'INACTIVE_WAITING': 'inactive_waiting',
    'ACTIVE_DEAL': 'active_deal'
}

PLAYER_FILE_PREFIX='../player_data'

PLAYER_POSSIBLE_ACTIONS = {
    'STAY': 'STAY',
    'HIT': 'HIT',
    'SPLIT': 'SPLIT',
    'DOUBLE': 'DOUBLE'
}