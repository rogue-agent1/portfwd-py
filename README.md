# portfwd-py
TCP port forwarder/proxy.
```bash
python portfwd.py 8080 localhost:3000        # Forward 8080 → 3000
python portfwd.py 5433 db.example.com:5432 -v  # Proxy with logging
```
## Zero dependencies. Python 3.6+.
