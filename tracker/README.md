# Hit Tracker

> Requires Python 3.7.3+

## Quick start demo

### Using Docker

```
$ docker build -t tracker .
$ docker run -p 5000:5000 tracker
...
 * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
```

### Or using venv

Setup venv and dependencies (flask and cachetools from requirements.txt)

```
$ python3 --version
Python 3.7.3
$ python3 -m venv venv
$ source venv/bin/activate
$ pip3 install -r requirements.txt
$ python3 server.py
...
 * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)

```

### Run test server ...

```
$ python3 server.py
 * Serving Flask app "server" (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
 * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
1 unique hits from total 1 hits
1 unique hits from total 2 hits
1 unique hits from total 3 hits
1 unique hits from total 4 hits
2 unique hits from total 5 hits
```

### Run test client connections ...

```
$ rm cookies.txt
$ curl -b cookies.txt -c cookies.txt  -H "X_FORWARDED_FOR: 111" http://127.0.0.1:5000
$ curl -b cookies.txt -c cookies.txt  -H "X_FORWARDED_FOR: 111" http://127.0.0.1:5000
$ curl -b cookies.txt -c cookies.txt  -H "X_FORWARDED_FOR: 111" http://127.0.0.1:5000
$ curl -b cookies.txt -c cookies.txt  -H "X_FORWARDED_FOR: 111" http://127.0.0.1:5000
$ rm cookies.txt
$ curl -b cookies.txt -c cookies.txt  -H "X_FORWARDED_FOR: 222" http://127.0.0.1:5000
```

### Try different implementations, by updating the code

```
# vi server.py
...
133 # TODO: use arg parsing to select the tracker
134 tracker = SimpleTracker()
135 # tracker = RateTracker()
136 # tracker = DBTracker()
...
```

> TODO: Args processing to select the implementation

## Implementation Notes

### Simple Tracker

`SimpleTracker().track(request)`

This is a simple tracker which tracks all time unique hit counts.
It does not track time period based minute/day/hour hit rate.

To get unique hit rates, the unique hits can be persisted with timestmap
to a data store and then can be queried for hit rate based on time periods.

For demo using in memory store, and the regular hash set used
for memory store will not scale in real world.

So a probabilistic data structure like bloom filter
should be used in  production that can fit into memory
And to span multiple instances across systems.

The bloom filter can be backed by a shared cache like Redis
which also provides disk persistence.
Shared cache can also handle concurrency without disk
pressure using periodic snapshots

### Hit Rate Tracker

`RateTracker().track(request)`

A hit rate tracker using fixed memory and a time to live cache with ttl set to
the time period in seconds we are calculating the rate for

The memory used = (the time period seconds) * (the expected max concurrent requests per second)

This will not scale for large concurrent requests and single system
But the idea could be extended across multiple systems with a shared cache like Redis with ttl sets

> TODO: Explore using a timestamp indexed fixed size (of given time period) queue/array instead of ttl cache

## DB (batched) and/or Stream processing (real time) Tracker

`DBTracker().track(request)`

> TODO: Track all hits to database with timestamps, lookup hit rates for any period as batch/scheduled jobs.
>Or send to a stream processing server like Spark through a message queue like Kafka
to calculate hit rates in near real time.

### Other notes

Simple demo examples used are on single thread when using multiple threads then the
the data updates should be synchronised at code/cache/db layer as needed.

When scaling out to multiple server instances if there is no shared cache layer individual nodes can calculate hit rate which can be combined in a map reduce fashion.

### Memory/Disk Storage

As we can see in the different implementations approaches above depending on how you want
to use the hit counter you can use in memory store for counter rate for smaller time period
which can be aggregated for other time periods.

When using memory based solution the design should make sure fixed memory usage by
leveraging moving window streaming approaches and/or probabilistic data structures
like bloom filters if minor affect on accuracy can be tolerated.

In memory store can be extended across instances across nodes by using a shared in memory cache.

If the hit counter is used as part of an extensive click stream analytics then storing them into
a time series style distributed data store or data late or data warehouse can then be analysed
for any time slices using batch jobs to get much more click stream insight that just a simple hit
counter.

In addition using stream processor pipeline can get real time click stream analytics without waiting
for batch aggregation analytics data.

When using disk based storage for analytics, the storage can be optimised by purge policies based
on purge policies after analytics are done and/or compression and long term archiving storage strategies.
