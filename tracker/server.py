"""
Web Hit Tracker
"""

from cachetools import TTLCache
from flask import Flask
from flask import make_response
from flask import request


class SimpleTracker:
    """
    This is a simple tracker which tracks all time unique hit counts.
    It does not track time period based minute/day/hour hit rate.

    To get unique hit rates, the unique hits can be persisted with timestamps
    to a data store and then can be queried for hit rate based on time periods.
    """

    def __init__(self):
        # For demo using in memory store
        # In production will read values from disk store
        self.lifetime_unique_hits = self.read_unique_ids()
        self.total_hits = self.read_total_hits()

    # For demo using in memory store
    def read_total_hits(self):
        return 0

    # For demo using in memory store
    def update_total_hits(self):
        self.total_hits += 1

    # For demo using in memory store
    def read_unique_ids(self):
        return set()

    # For demo using in memory store, and the regular python hash set
    # used for memory store will not scale in real world.
    #
    # So a probabilistic data structure like bloom filter
    # should be used in  production that can fit into memory
    # And to span multiple instances across systems.
    #
    # The bloom filter can be backed by a shared cache like Redis
    # which also provides disk persistence.
    # Shared cache can also handle concurrency without disk
    # pressure using periodic snapshots
    def store_unique_ids(self, id):
        self.lifetime_unique_hits.add(id)

    def track_hit(self, req):
        self.update_total_hits()
        resp = make_response()
        if req.cookies.get('t') is None:
            id = get_hash_ids(req)
            resp.set_cookie('t', str(id))
            self.store_unique_ids(id)
        print(self.get_unique_hits(), 'unique hits from total', self.get_total_hits(), 'hits')
        return resp

    def get_unique_hits(self):
        return len(self.lifetime_unique_hits)

    def get_total_hits(self):
        return self.total_hits


class RateTracker:
    """
    A hit rate tracker using fixed memory and a time to live cache with ttl set to
    the time period in seconds we are calculating the rate for

    The memory used = (the time period seconds) * (the expected max concurrent requests per second)

    This will not scale for large concurrent requests and single system
    But the idea could be extended across multiple systems with a shared cache like Redis with ttl sets

    TODO: Explore using a timestamp indexed fixed size (of given time period) queue/array instead of ttl cache
    """

    def __init__(self, period_seconds=60, req_concurrency=100):
        self.seconds = period_seconds
        self.concurrency = req_concurrency
        self.unique = TTLCache(maxsize=(self.seconds * self.concurrency), ttl=self.seconds)
        self.total_hits = 0

    def update_total_hits(self):
        self.total_hits += 1

    def track_hit(self, req):
        self.update_total_hits()
        resp = make_response()
        if req.cookies.get('t') is None:
            id = get_hash_ids(req)
            resp.set_cookie('t', str(id))
            self.unique[id] = 1  # Cache is a dict storing a dummy value
        print(self.get_unique_hits(), 'unique hits per last', self.seconds, 'seconds out of all', self.get_total_hits(),
              'hits so far')
        return resp

    def get_unique_hits(self):
        return self.unique.currsize

    def get_total_hits(self):
        return self.total_hits


class DBTracker:
    """
    TODO: Track all hits to database with timestamps, lookup hit rates for any period as batch/scheduled jobs
    Or send to a stream processing server like Spark through a message queue like Kafka
    to calculate hit rates in near real time.
    """

    def track_hit(self, req):
        print('ERROR: DBTracker is not yet implemented')
        return make_response('DBTracker is not yet implemented', 501)

    def get_unique_hits(self):
        print('ERROR: DBTracker is not yet implemented')
        return 0


def get_hash_ids(req):
    user_agent = req.environ.get('HTTP_USER_AGENT')
    source = req.environ.get('HTTP_X_FORWARDED_FOR')
    if source is None:  # Fallback to remmote addr if no forwarded for
        source = req.environ.get('REMOTE_ADDR')
    return hash(hash(user_agent) + hash(source))  # TODO Optimize


# TODO: use arh parsing to select the tracker
tracker = SimpleTracker()
# tracker = RateTracker()
# tracker = DBTracker()

app = Flask(__name__)


@app.route('/')
def counter():
    return tracker.track_hit(request)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
