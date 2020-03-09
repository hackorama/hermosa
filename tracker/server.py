"""
Team XP REST API web server
"""
import logging as log

from flask import Flask
from flask import jsonify
from flask import request
from flask import make_response

class LifetimeTracker:

    def __init__(self):
        self.lifetime_unique_hits = self.read_unique_ids()
        self.total_hits = self.read_total_hits()

    def read_total_hits(self):
        return 0

    def update_total_hits(self):
        self.total_hits +=1

    def read_unique_ids(self):
        return set()

    def store_unique_ids(self, id):
        self.lifetime_unique_hits.add(id)

    def count_unique_ids(self):
        return len(self.lifetime_unique_hits)

    def track(self, req):
        self.update_total_hits()
        resp = make_response()
        if req.cookies.get('t') is None:
            id = self.get_hash_ids(req)
            resp.set_cookie('t', str(id))
            self.store_unique_ids(id)
        print(self.count_unique_ids(), ' / ', self.total_hits)
        return resp

    def get_hash_ids(self, req):
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
