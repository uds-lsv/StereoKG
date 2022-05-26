"""
Refer:
https://github.com/Aunsiels/CSK/tree/master/quasimodo
"""

import inflect
import statement_from_question as q2s

class InflectAccessor:

    def __init__(self):
        self._conversions_singular = dict()
        self._conversions_plural = dict()
        self._plural_engine = inflect.engine()
        self._proper_name = set()

    def to_singular(self, word):
        if word in self._conversions_singular:
            return self._conversions_singular[word]
        singular = self._plural_engine.singular_noun(word)
        if not singular or word in q2s.NON_PLURAL or word.endswith("sis") or \
                word in self._proper_name:
            self._conversions_singular[word] = word
        else:
            self._conversions_singular[word] = singular
        return self._conversions_singular[word]

    def to_plural(self, word):
        if word in self._conversions_plural:
            return self._conversions_plural[word]
        plural = self._plural_engine.plural(word)
        self._conversions_plural[word] = plural
        return plural