__author__ = 'Adisor'


class DictIterator(object):
    def __init__(self, iterable_dict):
        self.iterable_dict = iterable_dict
        self.current_index = 0

    def has_next(self):
        return self.current_index < len(self.iterable_dict) - 1

    def has_previous(self):
        return self.current_index > 0

    def current_value(self):
        return self.iterable_dict[self.current_key()]

    def current_key(self):
        return self.iterable_dict.keys()[self.current_index]

    def go_next(self):
        self.current_index += 1
        return self.current_key()

    def go_previous(self):
        self.current_index -= 1
        return self.current_key()

    def is_empty(self):
        return len(self.iterable_dict) == 0
