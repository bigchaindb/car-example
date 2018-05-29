"""
A script to populate a BigchainDB database with a bunch of data
for a blog post to illustrate various MongoDB queries.
The data is for fictional custom cars designed by Sergio Tillenham.
"""

import json
import pytz
import random
import datetime

from faker import Faker
from bson import json_util  # Install using: pip install pymongo
from bigchaindb_driver import BigchainDB
from bigchaindb_driver.crypto import generate_keypair
from haikunator import Haikunator


color_list = ['teal', 'almond', 'aluminum', 'obsidian', 'caramel',
              'tawny', 'canary', 'coffee', 'coral', 'cream', 'lilac']
bdb_root_url = 'http://localhost:9984'
num_cars = 25

# Generate Sergio Tillenham's keypair
sergio = generate_keypair()

bdb = BigchainDB(bdb_root_url)
secure_random = random.SystemRandom()
haikunator = Haikunator()
fake = Faker()
now_unaware = datetime.datetime.utcnow()  # now_unaware.tzinfo is None
now = now_unaware.replace(tzinfo=pytz.UTC)  # now.tzinfo is UTC

# External loop.
# Each iteration is for a different car.

for car_number in range(num_cars):
    print('Generating data for car number {}'.format(car_number))
    print('----------------------------------')
    car_name = haikunator.haikunate(token_length=0, delimiter=' ').title()
    # Make sure the datetime_created is in the UTC time zone.
    datetime_created = fake.date_time_between(start_date='-30y',
                                              end_date='-3y',
                                              tzinfo=pytz.UTC)
    serialized_datetime_created = json.dumps(datetime_created,
                                             default=json_util.default)
    # serialized_datetime_created is a string that looks something like
    # '{"$date": 1526650426444}'
    # and after JSON serialization of that it looks like
    # "{\"$date\": 1526650609774}"
    car_dict = {
        'data': {
            'type': 'car',
            'name': car_name,
            'color': secure_random.choice(color_list),
            'datetime_created': serialized_datetime_created,
            'designer': 'Sergio Tillenham'
        }
    }
    print('CREATE tx asset: {}'.format(car_dict))
    create_tx_metadata = {
        'notes': 'The CREATE transaction for one particular car (an asset).'
    }
    print('CREATE tx metadata: {}'.format(create_tx_metadata))
    # Prepare the CREATE transaction.
    # Note that the creator (Sergio) is also the initial owner.
    prepared_create_tx = bdb.transactions.prepare(
        operation='CREATE',
        signers=sergio.public_key,
        asset=car_dict,
        metadata=create_tx_metadata
    )
    fulfilled_create_tx = bdb.transactions.fulfill(
        prepared_create_tx,
        private_keys=sergio.private_key
    )
    sent_create_tx = bdb.transactions.send(fulfilled_create_tx)
    print('CREATE transaction id: {}'.format(fulfilled_create_tx['id']))
    asset_id_of_car = fulfilled_create_tx['id']

    # Generate a random datetime for the sale.
    # Generate a random time delta from 0 to 2 years (730 days)
    # and add that to datetime_created
    # Remember to serialize the result.
    time_to_sale = datetime.timedelta(days=random.randint(1, 730))
    sale_datetime = datetime_created + time_to_sale
    serialized_sale_datetime = json.dumps(sale_datetime,
                                          default=json_util.default)

    # Generate some data about the first owner
    first_owner_name = fake.name()
    first_owner = generate_keypair()

    asset_to_transfer = {'id': asset_id_of_car}

    transfer_tx_metadata = {
        'notes': 'The first transfer, from Sergio to the first owner.',
        'new_owner': first_owner_name,
        'transfer_time': serialized_sale_datetime
    }
    print('First TRANSFER tx metadata: {}'.format(transfer_tx_metadata))
    output = fulfilled_create_tx['outputs'][0]
    transfer_input = {
        'fulfills': {
            'transaction_id': fulfilled_create_tx['id'],
            'output_index': 0
        },
        'owners_before': [sergio.public_key],
        'fulfillment': output['condition']['details']
    }
    prepared_transfer_tx = bdb.transactions.prepare(
        operation='TRANSFER',
        asset=asset_to_transfer,
        metadata=transfer_tx_metadata,
        inputs=transfer_input,
        recipients=first_owner.public_key
    )
    fulfilled_transfer_tx = bdb.transactions.fulfill(
        prepared_transfer_tx,
        private_keys=sergio.private_key
    )
    sent_transfer_tx = bdb.transactions.send(fulfilled_transfer_tx)
    print('First TRANSFER tx id: {}'.format(fulfilled_transfer_tx['id']))

    prev_sale_datetime = sale_datetime
    prev_owner = first_owner
    prev_tx = fulfilled_transfer_tx

    # Internal loop.
    # Each iteration transfers the car to a new owner.
    while True:
        # Generate the datetime of the next sale
        time_between_sales = datetime.timedelta(days=random.randint(1, 3650))
        sale_datetime = prev_sale_datetime + time_between_sales
        serialized_sale_datetime = json.dumps(sale_datetime,
                                              default=json_util.default)
        
        # If the next sale happens in the future, then exit this internal loop
        # and go on to the next car.
        if sale_datetime > now:
            break

        # Generate some data about the new owner
        new_owner_name = fake.name()
        new_owner = generate_keypair()

        # Generate a TRANSFER transaction to transfer the car to the new owner
        transfer_tx_metadata = {
            'notes': None,
            'new_owner': new_owner_name,
            'transfer_time': serialized_sale_datetime
        }
        print('Next TRANSFER tx metadata: {}'.format(transfer_tx_metadata))
        output = prev_tx['outputs'][0]
        transfer_input = {
            'fulfills': {
                'transaction_id': prev_tx['id'],
                'output_index': 0
            },
            'owners_before': [prev_owner.public_key],
            'fulfillment': output['condition']['details']
        }
        prepared_transfer_tx = bdb.transactions.prepare(
            operation='TRANSFER',
            asset=asset_to_transfer,
            metadata=transfer_tx_metadata,
            inputs=transfer_input,
            recipients=new_owner.public_key
        )
        fulfilled_transfer_tx = bdb.transactions.fulfill(
            prepared_transfer_tx,
            private_keys=prev_owner.private_key
        )
        sent_transfer_tx = bdb.transactions.send(fulfilled_transfer_tx)
        print('Next TRANFER transaction id: {}'.format(fulfilled_transfer_tx['id']))

        prev_sale_datetime = sale_datetime
        prev_owner = new_owner
        prev_tx = fulfilled_transfer_tx

    print('We are done generating fake data about that car.\n\n')

print('We are done generating all fake data.')
