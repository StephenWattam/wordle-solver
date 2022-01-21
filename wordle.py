
# import matplotlib.pyplot as plt

from game import WordleGame, run_game
import client as cl



WORD_FILE = "sgb-words.txt"

print(f"Loading dictionary from {WORD_FILE}")
dictionary = []
with open(WORD_FILE, 'r') as fin:
    for line in fin:
        # print(f" -> {line.strip()}")
        word = line.strip().lower()
        if len(word) != 5:
            continue

        dictionary.append(word)
print(f"Using {len(dictionary)} words")





# -------------------------------------------------------------------------------------------------
wins = 0
losses = 0
guesses = []

for word in dictionary[:1000]:

    # Run game
    game = WordleGame(word, max_guesses=6)
    # client = cl.WordleInteractive()
    # client = cl.RandomDictionarySearchBot(dictionary)
    # client = cl.LetterPositionDictSearchBot(dictionary)
    client = cl.BigramScoringDictSearchBot(dictionary)
    win = run_game(game, client)

    # Accounting
    if win:
        wins += 1
    else:
        losses += 1
    guesses.append(game.guess_count)

print(f"WINS: {wins} / {wins+losses}")


# plt.hist(guesses)
# plt.show()

# import code; code.interact(local=locals())

