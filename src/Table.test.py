import json
import logging
import matplotlib.pyplot as plt
import numpy as np


from src.constants import *
from src.Deck import Deck
from src.Player import Player
from src.Table import Table

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def test_table_population():
    t = Table()
    p1 = Player('p1', 1000)
    p2 = Player('p2', 1000)
    t.add_player(p1)
    t.add_player(p2)

    t.print_table_state()


def test_tableSetup():
    t = Table(3)
    t.print_table_state()

    t.deal()
    t.print_table_state()


# def test_parameterized_round():


def test_table_round():
    # init the players and dealer and deck
    dealer = Player('dealer', None)
    p1 = Player('danny', 1000)
    d = Deck()
    d.shuffle()

    # for the table to have scope into multiple hands a user
    # might choose to make (potential new q state on what to do)
    # all players minimum have one 'table' hand which is shared
    # between dealer and them

    # eventually the player will hold an array of 'hands' that
    # can be shared with the table for part ownership (i.e. minimum bets validated,
    # free bet or other conditions apply for side bets, etc)

    # this round must iterate per hand, per player on table

    # cache for now, remove later
    ##
    ## start removal
    ##

    p1.load_states_from_file()

    ##
    ## end removal
    ##

    for round_index in range(1000):
        # deal to everyone (just straight up, RR not important)
        dealer_showing_card = d.next()
        dealer.be_dealt(dealer_showing_card, d.next())
        p1.be_dealt(d.next(), d.next())

        # main loop for a single player, do this for all players in future
        ## start loop ##

        action = ACTIONS[p1.pick_and_stage_q_action(dealer_showing_card)]
        p1_sum, _ = p1.hand().getSum()
        print(p1.getName(), action, p1_sum, p1.getName())
        while (action != 'stay'):

            # if action is hit
            if action == 'hit':
                p1.hit(d.next())
                p1_sum, _ = p1.hand().getSum()

            # todo: if action is double
            if action == 'double':
                p1.hit(d.next())
                p1_sum, _ = p1.hand().getSum()
                action = 'stay'
                continue

            # todo: if action is split, make temp second hand for player
            if action == 'split':
                # interpreting 'splitting' as staying for now, skip
                action = 'stay'
                continue

            # if i bust, call it out and stop
            if p1_sum > 21:
                # bust, call it bad
                p1.last_action_bad()
                print(p1.getName(), action, p1_sum, p1.hand())
                # busted!
                print(p1.getName(), 'BUST!')
                break

            action = ACTIONS[p1.pick_and_stage_q_action(dealer_showing_card)]
            print(p1.getName(), action, p1_sum, p1.hand())

        # do the mandatory loop for the dealer
        # dealer must hit on soft 17, pushes on 22
        dealer_sum, dealer_sum_is_hard = dealer.hand().getSum()
        print(dealer.getName(), dealer_sum, dealer.hand())
        # todo, fix this logic
        while ((dealer_sum < 16 and dealer_sum_is_hard) or (dealer_sum < 17 and not dealer_sum_is_hard)):
            dealer.hit(d.next())
            dealer_sum, dealer_sum_is_hard = dealer.hand().getSum()
            print(dealer.getName(), dealer_sum, dealer.hand())

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
                print(p1.getName(), 'busted')
                p1.last_action_bad()
            elif dealer_sum > p1_sum:
                print(dealer.getName(), 'beats', p1.getName())
                p1.last_action_bad()
            elif p1_sum > dealer_sum:
                if p1.hand().isBlackJack():
                    print(p1.getName(), 'got blackjack')
                    p1.last_action_good()
                else:
                    print(p1.getName(), 'beats', dealer.getName())
                    p1.last_action_good()
            else:
                print(p1.getName(), 'pushes individually')
        ## end player loop ##

    # cache for now, remove later
    ##
    ## start removal
    ##

    p1.save_states()

    ##
    ## end removal
    ##

    print(json.dumps(p1.get_q_states(), indent=3))
    print('q states:', len(p1.get_q_states().keys()))


def test_iterate_table_and_graph():
    table = Table()
    p1 = Player('test_danny', 1000)
    p2 = Player('test_honi', 1000)
    p1.load_states_from_file()
    table.add_player(p1)

    chips, wins, losses, win_rate, q_state_size = [], [], [], [], []
    starting_index = p1.get_metadata()['hands_seen']
    for i in range(1, NUM_TRAINING_ITERATIONS):
        table.complete_a_round()

        metadata = p1.get_metadata()

        # populate tables
        chips.append(metadata['chips'])
        wins.append(metadata['score']['wins'])
        losses.append(metadata['score']['losses'])
        win_rate.append(float(metadata['score']['wins']) / float(starting_index + i))
        q_state_size.append(metadata['num_states'])

        # print(wins, losses, q_state_size, metadata)

    p1.save_states()
    # standardize this and move to the top later
    # import matplotlib.pyplot as plt
    # import numpy as np

    # Some example data to display
    x = np.array(range(starting_index, starting_index + len(wins)))
    y_chips = np.array(chips)
    y_wins = np.array(wins)
    y_losses = np.array(losses)
    y_rate = np.array(win_rate)
    y_size = np.array(q_state_size)

    # x = np.linspace(0, 2 * np.pi, 400)
    # y = np.sin(x ** 2)

    # print(x)
    # print(y_wins)
    # print(y_losses)
    # print(y_size)

    logging.basicConfig(level=logging.INFO)

    fig, axs = plt.subplots(4)
    fig.suptitle('wins v losses, win ratio, unique q states, player chip count')
    axs[0].plot(x, y_wins)
    axs[0].plot(x, y_losses)
    # axs[1].plot(x, y_losses)
    axs[1].plot(x, y_rate)
    axs[2].plot(x, y_size)
    axs[3].plot(x, y_chips)
    plt.show()


def test_generate_all_q_states():
    # these are only q starting states
    deck = Deck(1)
    deck2 = Deck(1)
    dealerDeck = Deck(1)
    # deck.shuffle()
    unique_states = set()
    for card1 in deck:
        for card2 in deck2:
            for dealerCard in dealerDeck:
                if card1.value <= card2.value:
                    unique_states.add(f'{dealerCard}-[[\'{card1}\', \'{card2}\']]')
    print(len(unique_states))

    return (list(unique_states))

if __name__ == '__main__':
    test_iterate_table_and_graph() # main driver
