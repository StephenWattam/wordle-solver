
from typing import Optional, List, Set

import re
import random

class WordleClient:

    def __init__(self):
        self.game = None

    def new_game(self, game) -> None:
        self.game = game

    def move(self) -> Optional[str]:
        pass






class WordleInteractive(WordleClient):
    """Offer an interactive CLI word entry"""

    def move(self) -> Optional[str]:
        assert self.game is not None

        guess = input("Enter a 5-letter word: ").strip().lower()
        print(f"GUESS: {guess}")
        return guess



class RandomDictionarySearchBot(WordleClient):

    def __init__(self, wordlist: List[str]):
        super().__init__()

        self.dictionary = {w for w in wordlist if len(w) == 5}
        print(f"{len(self.dictionary)} items in solver wordlist")

    def new_game(self, game) -> None:
        super().new_game(game)
        self.old_guesses = set()

    def move(self) -> Optional[str]:
        candidates = self._get_candidates()

        # Skip if we don't have any clue!
        if len(candidates) == 0:
            return None

        # Pick a random candidate
        # TODO: use ngram frequency to pick most likely, though we don't know
        #       the distribution used by the wordle game so this may be less than perfect
        guess = random.choice(list(candidates))
        self.old_guesses.add(guess)
        return guess

    def _get_candidates(self) -> Set[str]:
        """Calculate all possible words given the in-position characters
        and out-of-position characters up to this point."""

        # Build a regex based on the existing matches, then
        # select one at random
        candidates = self.dictionary - self.old_guesses

        # 1 --- find words fitting known locations in the dictionary
        rx = "^"
        for letter in self.game.correct_locations:
            if letter == "_":
                rx += r"[a-z]"
            else:
                rx += f"{letter}"
        rx += "$"
        pattern = re.compile(rx)
        print(f"Intermediate RX: {rx}")

        candidates = {x for x in candidates if pattern.fullmatch(x)}
        print(f"Found {len(candidates)} candidate words after filtering known positions")

        # 2 --- discard words if they have the previously-tried letters in them
        for letter in self.game.incorrect_letters:
            candidates = [x for x in candidates if letter not in x]
        print(f"Found {len(candidates)} candidate words after filtering known failed guesses")

        # 3 --- find words where the unknown positions have the known-valid letters
        unmatched_positions = [i for i, b in enumerate(self.game.correct_locations) if b == "_"]
        def to_unknown_positions_only(word: str) -> List[str]:
            return [x for i, x in enumerate(word) if i in unmatched_positions]
        for letter in self.game.correct_letters:
            # print(f"-> {to_unknown_positions_only(candidates[0])} must contain {letter}")
            candidates = [x for x in candidates if letter in to_unknown_positions_only(x)]
        print(f"Found {len(candidates)} candidate words after filtering known letters")

        return candidates





class LetterPositionDictSearchBot(RandomDictionarySearchBot):
    """Looks up words from a dictionary, then ranks them by how likely
    letters are to appear in a given position in the word.

    This strategy usually loses to the random bot, presumably because letters
    are not independent of one another.  A bigram scoring bot would probably work better.
    """

    def __init__(self, wordlist: List[str]):
        super().__init__(wordlist)

        ALPHABET = [x for x in "abcdefghijklmnopqrstuvwxyz"]
        self.weights_by_position = {x: {letter: 0.0 for letter in ALPHABET}
                                    for x in range(5)}

        # Count totals, sum = 1
        for word in self.dictionary:
            for i, letter in enumerate(word):
                self.weights_by_position[i][letter] += 1 / len(self.dictionary)

    def move(self) -> Optional[str]:
        candidates = self._get_candidates()

        # Skip if we don't have any clue!
        if len(candidates) == 0:
            return None

        # Weight candidate words by the sum of their letter weights
        def score_word(word: str) -> float:
            return sum([self.weights_by_position[i][letter] for i, letter in enumerate(word)])
        sorted_scores = sorted([(score_word(word), word) for word in candidates], key=lambda x: x[0], reverse=True)

        print(f"Sorted scores max: {sorted_scores[0]}, min: {sorted_scores[-1]}")
        self.old_guesses.add(sorted_scores[0][1])
        return sorted_scores[0][1]






class BigramScoringDictSearchBot(RandomDictionarySearchBot):
    """Selects words from a dictionary as RandomDictionarySearchBot, then
    ranks them based on bigram probabilities."""

    def __init__(self, wordlist: List[str]):
        super().__init__(wordlist)

        ALPHABET = [x for x in "abcdefghijklmnopqrstuvwxyz"]
        self.bigram_weights = {x: {y: 0.0 for y in ALPHABET}
                               for x in ALPHABET}

        # Count totals, sum = 1
        for word in self.dictionary:
            for a, b in zip(word, word[:1]):
                self.bigram_weights[a][b] += 1

    def move(self) -> Optional[str]:
        candidates = self._get_candidates()

        # Skip if we don't have any clue!
        if len(candidates) == 0:
            return None

        # Weight candidate words by the sum of their letter weights
        def score_word(word: str) -> float:
            return sum([self.bigram_weights[a][b] for a, b in zip(word, word[:1])])
        sorted_scores = sorted([(score_word(word), word) for word in candidates],\
                               key=lambda x: x[0], reverse=True)

        print(f"Sorted scores max: {sorted_scores[0]}, min: {sorted_scores[-1]}")
        self.old_guesses.add(sorted_scores[0][1])
        return sorted_scores[0][1]






# TODO: policy that attempts maximally-informative guess in early guess, and maximally-likely guess
#       later on

