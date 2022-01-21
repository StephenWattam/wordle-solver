from typing import List
import client as cl

class WordleGame:

    def __init__(self, word, max_guesses=6):
        assert len(word) == 5

        self.word = word.lower()
        self.letters = [x for x in word]

        self.guess_count = 0
        self.incorrect_letters = set()
        self.correct_letters = set()                         # wrong location, right letter
        self.correct_locations = ["_" for _ in self.letters] # correct location
        self.max_guesses = max_guesses

    def finished(self) -> bool:
        return self.guess_count > self.max_guesses or "".join(self.correct_locations) == self.word

    def won(self) -> bool:
        return self.guess_count <= self.max_guesses and "".join(self.correct_locations) == self.word

    def guess(self, guess_word) -> bool:
        assert len(guess_word) == len(self.word)

        self.guess_count += 1
        guess_word = guess_word.lower()
        guess_letters = [x for x in guess_word]

        # Split the guess into letters that match and letters that don't
        unmatched_guess_letters = set()
        for i, letter in enumerate(guess_word):
            if self.word[i] == letter:
                self.correct_locations[i] = letter
            elif letter not in self.word:
                self.incorrect_letters.add(letter)
            else:
                unmatched_guess_letters.add(letter)

        # Build a set of unmatched word letters
        unmatched_word_letters = {self.word[i] for i, x in enumerate(self.correct_locations) if x == "_"}
        # print(f"UNMATCHED from this word: {unmatched_word_letters}")
        # print(f"UNMATCHED from this guess: {unmatched_guess_letters}")
        self.correct_letters = self.correct_letters.union(unmatched_guess_letters).intersection(unmatched_word_letters)

        if "".join(self.correct_letters) == self.word:
            return True
        return False

    def to_unknown_positions_only(self, word: str) -> List[str]:
        """Return a list of characters that are in positions that are not correctly known yet.
        This is important because the "unknown" list shouldn't contain double-counted characters."""
        unmatched_positions = [i for i, b in enumerate(self.correct_locations) if b == "_"]
        return [x for i, x in enumerate(word) if i in unmatched_positions]




def run_game(game: WordleGame, client: cl.WordleClient) -> bool:


    # Start a new game
    client.new_game(game)

    # Play until finish
    while not game.finished():
        guess = client.move()

        if guess is None:
            print(F"CLIENT: Skip move")
            game.guess_count += 1
            continue

        print(f"CLIENT: Guess '{guess}'")
        game.guess(guess)
        print(f"GAME: {game.correct_locations}  (wrong location: {game.correct_letters}, wrong guess: {game.incorrect_letters}")

    # Report win state
    print(f"Win? {game.won()} in {game.guess_count} guesses.")
    return game.won()

