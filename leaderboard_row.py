'''
A class for objects to be rendered in the leaderboard
'''


class LeaderboardRow(object):
    def __init__(self, size, email, time, filename, active):
        self.size = size
        self.email = email
        self.time = time
        self.filename = filename
        self.active = active
