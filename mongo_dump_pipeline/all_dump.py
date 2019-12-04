__author__ = 'Mayank Tiwari'

import json
import logging.config
import multiprocessing
import time
from functools import partial
from itertools import chain

from bson import json_util
from bson.objectid import ObjectId

from models.game import Game
from util import *
from json import dumps

'''
Loading the Logging library here
'''
with open('./logging_config.yaml', 'r') as f:
    config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)
logger = logging.getLogger(__name__)
'''
Connecting to Mongo DB
'''
config = load_config('./elo_config.yaml')
profile = config["profile"]
logger.info(f'Loaded configuration for Profile: {profile}')


def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]


def calculate(chunk, input):
    client = init_database_mongo(profile, config)
    db = client['chess']
    game_collection = db.get_collection('game')
    # connection = init_database(profile, config)
    # db = connection.get_database('chess')

    chunk_result_list = []
    # loop over the id's in the chunk and do the calculation with each
    for id in chunk:
        # chunk_result_list.append(id)
        # chunk_result_list.append(Game.objects(id=id))
        # print(f'Reading Chunk ID: {id}')
        chunk_result_list.append(
            game_collection.find_one({'_id': ObjectId(id)})
        )
        # print(f'Finished Reading Chunk ID: {id}')
    return chunk_result_list


init_database(profile, config)

# recordCount = Game.objects.count()
document_ids = Game.objects.distinct('_id')
recordCount = len(document_ids)
print(f'Reading {recordCount} objects!')

cpu_count = multiprocessing.cpu_count() * 3
print(f'CPU Count: {cpu_count}')

time2s = time.time()

pool = multiprocessing.Pool(processes=cpu_count)  # spawn processes
calculate_partial = partial(calculate, input=input)  # partial function creation to allow input to be sent to the calculate function
result = pool.map(calculate_partial, list(chunks(document_ids, 1000)))  # creates chunks of 1000 document id's
print(f'Successfully loaded {recordCount} records from the mongo!')
# print(result[0])
pool.close()
pool.join()

time2f = time.time()
print(f'Total time taken: {time2f - time2s} seconds')

result_final = list(chain.from_iterable([r for r in result]))

print(f'Result Size: {len(result_final)}')

# db = connection.get_database('chess')
# game_collection = db.get_collection('game')
# game_collection.find_one({'_id': ObjectId('5dc9e654895e978a56ced7c4')})
with open('data.json', 'w') as outfile:
    json.dump(result_final, outfile, default=json_util.default)
