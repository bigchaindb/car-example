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

## Exploring the Archived Data

The data generated for the blog post was saved using `mongodump --db bigchain --out car_example_data`. The `car_example_data/` directory was then uploaded to this repository so you can explore it. To do that, first [start a new MongoDB instance](https://docs.mongodb.com/manual/tutorial/manage-mongodb-processes/) and then run `mongorestore car_example_data/`
