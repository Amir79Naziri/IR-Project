from hazm import *


class Setup:
    def __init__(self):
        self._normalize = Normalizer().normalize
        self._stem = Stemmer().stem
        self._tokenize = word_tokenize
        self._data = {}
        self._dictionary = {}
