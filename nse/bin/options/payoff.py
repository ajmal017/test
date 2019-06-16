class payoff(list):
    """
    Class payoff
    """
    def __init__(self):
        self.otmstrike = list[1]
        self.itmstrike = list[2]
        self.frame = list[0]

    def __getitem__(self, item):
        return item