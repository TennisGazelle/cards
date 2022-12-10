all:
	rm -f player_data/test_danny.json && python3 blackjack_qlearning.py

continue:
	python3 blackjack_qlearning.py