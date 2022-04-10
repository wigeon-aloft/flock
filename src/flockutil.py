import datetime as dt
from tokenize import String

class QueueManager:
    """Manages a group of Queue objects."""

    def __init__(self):
        pass


class Queue:
    """
    Stores information pertaining to an activity queue.
    Contains the game/activity name and the guild members queued for it.
    """

    def __init__(self):
        self._members = []
        self._name = ""
        self.guild = ""
        self._starttime = dt.datetime.now()

    def add_member(self, member_id):
        self._members.append(member_id)

    def remove_member(self, member_id):
        self._members.remove(member_id)

    def clear_members(self):
        self._members = []

    def get_members(self):
        return self._members