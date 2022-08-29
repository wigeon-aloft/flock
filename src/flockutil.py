from tokenize import String
import random
import string
import datetime as dt

class QueueManager:
    """Manages a group of Queue objects."""

    def __init__(self):
        self._queues = []

    def create_queue(self, author, name=""):
        """Creates a new queue and adds it to the queue list."""

        # Generate name for the queue if not provided
        qname = name
        if qname == "":
            qname = Queue.generate_queue_name()
            # Keep generating new queue names until one is found that doesn't exist
            while self.check_queue_name_exists(qname):
                qname = Queue.generate_queue_name()
        
        # Create the new queue and add to list
        queue = Queue(creator=author.id, guild=author.guild, name=qname)
        
        # Add queue creator to queue
        queue.add_member(author.id)

        # Add queue to queue list
        self._queues.append(queue)
        
        return queue

    def get_queues(self):
        return self._queues

    def delete_queue(self, queue_name):
        """Removes an existing queue from the queue list. Takes the name of a queue as a string."""
        queue_removed = None

        # Check if the queue exists
        queue = self.find_queue_by_name(queue_name)

        if queue:
            self._queues.remove(queue)
        
        return queue_removed

    def find_queue_by_id(self, qid=""):
        """Returns queue that matches the given ID."""
        queue = None

        # Get queue for given ID
        if len(self._queues) != 0:
            for q in self._queues:
                if str(id(q)) == qid:
                    queue = q
                    break
        return queue

    def find_queue_by_name(self, name=""):
        """Returns queue that matches the given name."""
        queue = None

        if len(self._queues) != 0 and name != "":
            for q in self._queues:
                if (q.get_name() == name):
                    queue = q
                    break
        return queue

    def check_queue_name_exists(self, name):
        """Checks if the given queue name already belongs to an existing queue."""
        if len(self._queues) > 0 and name != "":
            for q in self._queues:
                if q.name == name:
                    return True
        return False

    def get_user_queues(self, user):
        """Returns a list of queues that a user is currently in."""
        user_queues = []
        for queue in self._queues:
            if user.id in queue.get_members():
                user_queues.append(queue)
        return user_queues


class Queue:
    """
    Stores information pertaining to an activity queue.
    Contains the game/activity name and the guild members queued for it.
    """

    def __init__(self, members=[], creator="", name="",  guild="", starttime=dt.datetime.now() + dt.timedelta(minutes=30)):
        """Parametrised constructor"""

        self.DATETIME_FORMAT = "%Y/%m/%d %H:%M:%S"  
        self._members = members                     # List of Discord UIDs of people currently queued for activity
        self._creator = creator                     # Discord UID of the user who created the queue
        self._name = name                           # Name of the queue
        self._guild = guild                         # Guild that the queue belongs to
        self._createdtime = dt.datetime.now()       # Queue created time
        self._lastmodified = dt.datetime.now()      # Last time queue was modified
        self._starttime = starttime                 # Activity start time - defaults to 30 mins after the lobby is created.

    @staticmethod
    def generate_queue_name():
        """Generates a random 6 character queue name."""
        return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(6))

    def _update_lastmodified(self):
        self._lastmodified = dt.datetime.now()

    def add_member(self, member_id):
        if member_id not in self._members:
            self._members.append(member_id)
        else:
            raise ValueError("{} is already in queue.")

    def remove_member(self, member_id):
        self._members.remove(member_id)

    def clear_members(self):
        self._members = []

    def get_members(self):
        return self._members

    def get_name(self):
        return self._name

    def get_formatted_starttime(self):
        """Returns the Queue's start time formatted using the Queue's datetime format."""
        return self._starttime.strftime(self.DATETIME_FORMAT)

    def format_current_queue():
        pass

    def get_time_until_start(self):
        """Returns a datetime object indicating the time until the activity starts."""
        return self._starttime - dt.datetime.now()
