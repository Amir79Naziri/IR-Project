from parsivar import Normalizer
from parsivar import Tokenizer
from parsivar import FindStems


class Setup:
    def __init__(self):
        self._normalize = Normalizer().normalize
        self._stem = FindStems().convert_to_stem
        self._tokenize = Tokenizer().tokenize_words
        self._data = {}
        self._dictionary = {}
