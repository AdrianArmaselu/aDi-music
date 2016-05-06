__author__ = 'Adisor'


class FrameSelectionPolicy(object):
    def __init__(self):
        pass

    HIGHEST_COUNT = 0
    RANDOM = 1
    PROB = 2  # Probabilistic
    EXPERIMENTAL = 3


frame_selection_policy = FrameSelectionPolicy.HIGHEST_COUNT
