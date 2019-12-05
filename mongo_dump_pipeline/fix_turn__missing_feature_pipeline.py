__author__ = 'Mayank Tiwari'

import logging.config
import multiprocessing
import time
from collections import Counter, defaultdict
from functools import partial

from bson.objectid import ObjectId
from chess import QUEEN, Board, Move

from models.game import Game
from util import *

'''
Loading the Logging library here
'''
with open('../logging_config.yaml', 'r') as f:
    config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)
logger = logging.getLogger(__name__)
'''
Connecting to Mongo DB
'''
config = load_config('../elo_config.yaml')
profile = config["profile"]
logger.info(f'Loaded configuration for Profile: {profile}')


def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]


def featureEngineering(id, game, game_collection):
    counter = 0
    update_dict = {}

    first_check = True
    first_queen_move = True

    features_dict = defaultdict(int)
    # {
    #     'promotion': 0,
    #     'total_checks': 0,
    #     'is_checkmate': 0,
    #     'is_stalemate': 0,
    #     'insufficient_material': 0,
    #     'can_claim_draw': 0
    # }

    board = None
    for moveDBObject in game['moves']:
        # print(f"\tUpdating {move['uci']} -> {move['turn']}")
        board = Board(moveDBObject['fen'])
        uci = moveDBObject['uci']
        move = Move.from_uci(uci)

        moved_piece = board.piece_at(move.from_square)
        captured_piece = board.piece_at(move.to_square)

        if moved_piece == QUEEN and first_queen_move:
            features_dict['queen_moved_at'] = board.fullmove_number
            first_queen_move = False

        if captured_piece == QUEEN:
            features_dict['queen_changed_at'] = board.fullmove_number

        if move.promotion:
            features_dict['promotion'] += 1
        if board.is_check():
            features_dict['total_checks'] += 1
            if first_check:
                features_dict['first_check_at'] = board.fullmove_number
                first_check = False

                # castling
                if uci == 'e1g1':
                    features_dict['white_king_castle'] = board.fullmove_number
                elif uci == 'e1c1':
                    features_dict['white_queen_castle'] = board.fullmove_number
                elif uci == 'e8g8':
                    features_dict['black_king_castle'] = board.fullmove_number
                elif uci == 'e8c8':
                    features_dict['black_queen_castle'] = board.fullmove_number

        # update_dict[f"moves.{counter}.turn"] = counter % 2 == 0
        counter += 1

    if counter > 0:
        if board.is_checkmate():
            features_dict['is_checkmate'] += 1
        if board.is_stalemate():
            features_dict['is_stalemate'] += 1
        if board.is_insufficient_material():
            features_dict['insufficient_material'] += 1
        if board.can_claim_draw():
            features_dict['can_claim_draw'] += 1
        features_dict['total_moves'] = board.fullmove_number

        piece_placement = board.fen().split()[0]
        end_pieces = Counter(x for x in piece_placement if x.isalpha())
        # count number of piece at end position
        features_dict.update({'end_' + piece: cnt for piece, cnt in end_pieces.items()})

        # print(features_dict)
        game_collection.update_one(
            {
                "_id": ObjectId(id)
            },
            {
                "$set": features_dict
            },
            upsert=False
        )


def fixTurnBug(id, game, game_collection):
    counter = 0
    update_dict = {}
    for move in game['moves']:
        # print(f"\tUpdating {move['uci']} -> {move['turn']}")
        update_dict[f"moves.{counter}.turn"] = counter % 2 == 0
        counter += 1

    if counter > 0:
        game_collection.update_one(
            {
                "_id": ObjectId(id)
            },
            {
                "$set": update_dict
            },
            upsert=False
        )


def calculate(chunk, input):
    client = init_database_mongo(profile, config)
    db = client['chess']
    game_collection = db.get_collection('game')
    # connection = init_database(profile, config)
    # db = connection.get_database('chess')

    chunk_result_list = []
    # loop over the id's in the chunk and do the calculation with each
    for id in chunk:
        game = game_collection.find_one({'_id': ObjectId(id)})
        print(f"Updating site: {game['site']}")

        # fixTurnBug(id, game, game_collection)
        featureEngineering(id, game, game_collection)

        chunk_result_list.append(
            id
        )
    return chunk_result_list


init_database(profile, config)

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

# result_final = list(chain.from_iterable([r for r in result]))
# print(f'Result Size: {len(result_final)}')
