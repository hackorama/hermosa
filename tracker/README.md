# Hit Tracker

Requires Python 3.7.3+

```
# python3 --version
Python 3.7.3
$ python3 -m venv venv
$ source venv/bin/activate
$ pip3 install -r requirements.txt
```

Run test server ...

```
python3 server.py
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

Run test client connections ...

```
$ rm cookies.txt
$ curl -b cookies.txt -c cookies.txt  -H "X_FORWARDED_FOR: 111" http://127.0.0.1:5000
$ curl -b cookies.txt -c cookies.txt  -H "X_FORWARDED_FOR: 111" http://127.0.0.1:5000
$ curl -b cookies.txt -c cookies.txt  -H "X_FORWARDED_FOR: 111" http://127.0.0.1:5000
$ curl -b cookies.txt -c cookies.txt  -H "X_FORWARDED_FOR: 111" http://127.0.0.1:5000
$ rm cookies.txt
$ curl -b cookies.txt -c cookies.txt  -H "X_FORWARDED_FOR: 222" http://127.0.0.1:5000
```

