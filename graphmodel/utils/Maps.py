import bisect
from collections import defaultdict

from graphmodel.model.SongObjects import SoundEvent

__author__ = 'Adisor'


class HashSet:
    def __init__(self):
        self.set = defaultdict(None)

    def add(self, value):
        self.set[value] = value

    def get(self, index):
        return self.set.keys()[index]

    def values(self):
        return self.set.keys()


total_instructions = 0


# this is really slow because tree becomes unbalanced and implementing rotation algorithms is not trivial
class BadBinarySearchTreeNode:
    def __init__(self, key_comparator):
        self.left = None
        self.right = None
        self.key = None
        self.value = None
        self.key_comparator = key_comparator

    def add(self, key, value):
        if key < 0:
            raise Exception("Key is negative: %s" % key)
        if self.key is None or self.key_comparator(key, self.key) == 0:
            self.key = key
            self.value = value
        else:
            if self.key_comparator(key, self.key) > 0:
                self.add_right(key, value)
            if self.key_comparator(key, self.key) < 0:
                self.add_left(key, value)

    def add_right(self, key, value):
        if self.right is None:
            self.right = BadBinarySearchTreeNode(self.key_comparator)
        self.right.add(key, value)

    def add_left(self, key, value):
        if self.left is None:
            self.left = BadBinarySearchTreeNode(self.key_comparator)
        self.left.add(key, value)

    def get_key_gt(self, key, greater_key=None):
        def constraint_function(key1, key2):
            global total_instructions
            total_instructions += 1
            if key1 is None or key2 is None:
                return False
            return self.key_comparator(key1, key2) > 0

        return self.find_key(self.get_search_comparator_function(constraint_function), key, greater_key)

    def get_key_lt(self, key, smaller_key=None):
        def constraint_function(key1, key2):
            global total_instructions
            total_instructions += 1
            if key1 is None or key2 is None:
                return False
            return self.key_comparator(key1, key2) < 0

        key = self.find_key(self.get_search_comparator_function(constraint_function), key, smaller_key)
        return key

    @staticmethod
    def get_search_comparator_function(constraint_function):
        def compare_function(best_key, potential_key, search_key):
            if best_key is None and constraint_function(potential_key, search_key):
                best_key = potential_key
            if constraint_function(best_key, potential_key) and constraint_function(potential_key, search_key):
                best_key = potential_key
            return best_key

        return compare_function

    def find_key(self, compare_function, search_key, closest_key):
        if self.key is not None:
            closest_key = compare_function(closest_key, self.key, search_key)
            potential_key = None
            if self.right is not None and self.key_comparator(search_key, self.key) > 0:
                potential_key = self.right.find_key(compare_function, search_key, closest_key)
            if self.left is not None and self.key_comparator(search_key, self.key) < 0:
                potential_key = self.left.find_key(compare_function, search_key, closest_key)
            closest_key = compare_function(closest_key, potential_key, search_key)
        return closest_key

    def print_tree(self, level=0):
        print "\t" * level, str(self.key), ":", str(self.value)
        if self.left is not None:
            self.left.print_tree(level + 1)
        if self.right is not None:
            self.right.print_tree(level + 1)


class BadTreeDict:
    def __init__(self, compare_func, default_value=None):
        self.root = BadBinarySearchTreeNode(compare_func)
        self.compare_func = compare_func
        self.default = default_value
        self.items = defaultdict(lambda: None)

    def put(self, key, value):
        if key < 0:
            raise Exception("Key is negative: %s" % key)
        self.items[key] = value
        self.root.add(key, value)

    def get(self, key):
        if key < 0:
            raise Exception("Key is negative: %s" % key)
        if self.items[key] is None:
            self.put(key, self.default())
        return self.items[key]

    def get_key_lt(self, key):
        return self.root.get_key_lt(key)

    def get_key_gt(self, key):
        return self.root.get_key_gt(key)

    def keys(self):
        return self.items.keys()

    def values(self):
        return self.items.values()

    def print_tree(self):
        self.root.print_tree()


class TreeDict:
    def __init__(self, default=None):
        self.keys = []
        self.dict = defaultdict(lambda: None)
        self.default = default

    def put(self, key, value):
        print key, value
        index = bisect.bisect(self.keys, key)
        self.keys = self.keys[:index] + [value] + self.keys[index + 1:]
        self.dict[key] = value

    def get(self, key):
        if self.default is not None:
            self.put(key, self.default())
        return self.dict[key]

    def get_key_lt(self, key):
        index = bisect.bisect_left(self.keys, key)
        if key < len(self.keys):
            key = self.keys[index]
        else:
            return None
        return self.dict[key]

    def get_key_gt(self, key):
        index = bisect.bisect_right(self.keys, key)
        key = self.keys[index]
        return self.dict[key]

    def get_keys(self):
        return self.dict.keys()

    def values(self):
        return self.dict.values()


class HeapDict:
    def __init__(self):
        self.items = []



def test():
    def compare_func(value1, value2):
        return value1 - value2

    treemap = BadTreeDict(int.__cmp__, SoundEvent)
    treemap.put(10, 130)
    treemap.put(5, 1)
    treemap.put(20, 1)
    treemap.put(13, 1)
    treemap.put(15, 1)
    print treemap.get(1)
    print treemap.get(0)
    print treemap.get(2)
    print treemap.values()
    print treemap.keys()
    print "smallest", treemap.get_key_lt(14)
    treemap.print_tree()


def test2():
    treemap = BadTreeDict(int.__cmp__, SoundEvent)
    treemap.put(0, SoundEvent())
    treemap.put(256, SoundEvent())
    treemap.put(512, SoundEvent())
    treemap.put(768, SoundEvent())
    print "smallest", treemap.get_key_lt(256)
    print "smallest", treemap.get_key_lt(512)
    print "smallest", treemap.get_key_lt(768)

# test2()
# test()
