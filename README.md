# car-example

This repository contains code for a blog post about using MongoDB directly.

## Using the Code

First, [run a local BigchainDB node using our handy make commands](https://docs.bigchaindb.com/projects/contributing/en/latest/dev-setup-coding-and-contribution-process/run-node-with-docker-compose.html)

Assuming you're using Python 3.6...

Install some Python packages:
```text
pip install -r requirements.txt
```

Then generate some fake data about some custom cars and the ownership history of each one, and write all that data to the local BigchainDB node:
```text
python populate_db.py
```

