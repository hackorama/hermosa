"""
Web Hit Tracker
"""
import logging as log

from flask import Flask
from flask import jsonify
from flask import request
from flask import make_response

class LifetimeTracker:

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
        self.total_hits +=1

    # For demo using in memory store
    def read_unique_ids(self):
        return set()

    # For demo using in memory store
    # and this regular hash set used will not scale in real world
    # So a probablistic data structure like bloom filter
    # should be used in  production that can fit into memory
    # And to span multiple insatnces across systems
    # the bloom filter can be backed by a shared cache like redis
    # which also provides disk persistance
    def store_unique_ids(self, id):
        self.lifetime_unique_hits.add(id)

    # For demo using in memory store
    def count_unique_ids(self):
        return len(self.lifetime_unique_hits)

    def track(self, req):
        self.update_total_hits()
        resp = make_response()
        if req.cookies.get('t') is None:
            id = get_hash_ids(req)
            resp.set_cookie('t', str(id))
            self.store_unique_ids(id)
        print(self.count_unique_ids(), 'unique hits from total', self.total_hits, 'hits')
        return resp

def get_hash_ids(req):
    user_agent = req.environ.get('HTTP_USER_AGENT')
    source = req.environ.get('HTTP_X_FORWARDED_FOR')
    if source is None: # Fallback to remmote addr if no forwarded for
        source = req.environ.get('REMOTE_ADDR')
    return hash(hash(user_agent) + hash(source)) # TODO Optimize

tracker = LifetimeTracker()
app = Flask(__name__)

@app.route('/')
def counter():
    return tracker.track(request)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
