__author__ = 'Adisor'


class Node:
    def __init__(self, compare_func, value):
        self.left = None
        self.right = None
        self.compare_func = compare_func
        self.value = value

    def insert(self, value):
        if self.compare_func(value, self.value) >= 0:
            if self.right is None:
                self.right = Node(self.compare_func, value)
            else:
                self.right.insert(value)
        if self.compare_func(value, self.value) < 0:
            if self.left is None:
                self.left = Node(self.compare_func, value)
            else:
                self.left.insert(value)

