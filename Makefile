all: clean continue

continue:
	python3 src/Table.test.py

clean:
	rm -f player_data/test_danny.json