import json
import logging
import matplotlib.pyplot as plt
import numpy as np


from src.constants import *
from src.Deck import Deck
from src.Player import Player
from src.BlackjackTable import BlackjackTable

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def test_table_population():
    t = BlackjackTable()
    p1 = Player('p1', 1000)
    p2 = Player('p2', 1000)
    t.add_player(p1)
    t.add_player(p2)

    t.print_table_state()


def test_table_setup():
    t = BlackjackTable(3)
    t.print_table_state()

    t.complete_a_round()
    t.print_table_state()


def test_parameterized_round():
    pass


def test_iterate_table_and_graph():
    table = BlackjackTable()
    p1 = Player('test_danny', 1000)
    p2 = Player('test_honi', 1000)
    p1.load_states_from_file()
    table.add_player(p1)
    table.add_player(p2)

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

    # turn to INFO as matplotlib has a lot of debug calls
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
    # test_table_setup()
    test_iterate_table_and_graph() # main driver
