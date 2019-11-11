__author__ = 'Mayank Tiwari'

from mongoengine import *
import chess
import asyncio
import chess.pgn
import chess.engine
import chess.svg

import logging
import logging.config
import yaml

from main import convertToBB
from models.game import *

'''
Loading the Logging library here
'''
# logging.basicConfig(level=logging.INFO, filename='app.log', filemode='w', format='%(asctime)s - %(levelname)s - %(message)s')
with open('logging_config.yaml', 'r') as f:
    config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)
logger = logging.getLogger(__name__)

'''
Connecting to Mongo DB
'''
connect('chess', host='localhost', port=27017)

'''
Reading the Chess PGN file
'''
pgn = open('data/lichess_db_standard_rated_2014-01.pgn')

'''
Loading the chess processing engine
'''
engine = chess.engine.SimpleEngine.popen_uci("stockfish")
limit = chess.engine.Limit(time=0.100)
# limit = chess.engine.Limit(depth=25)

'''
Beginning to parse the files and load it into the warehouse
'''
counter = 1
while True:
    game = chess.pgn.read_game(pgn)
    if game is None:
        break

    headers = game.headers
    # print(headers)

    logging.info(f'Processing [{counter}] game...')

    dbGameObject = Game(headers)
    # for k, v in headers.items():
    #     print(f'{k} -> {v}')

    prev_eval = 0
    board = chess.Board()
    for move in game.mainline_moves():
        result = engine.analyse(board, limit)
        evaluation = result.score.relative.cp

        turn = board.turn
        if turn:
            diff = prev_eval - evaluation
            if diff > 0.3:
                evaluation_label = "B"  # badmove
            else:
                evaluation_label = "G"  # goodmove
        else:
            evaluation *= -1
            diff = evaluation - prev_eval
            if diff > 0.3:
                evaluation_label = "B"  # badmove
            else:
                evaluation_label = "G"  # goodmove

        board.push(move)
        encodedMove = convertToBB(board)
        fen = board.fen().__str__()
        dbGameObject.moves.append(Move(move.uci(), fen, encodedMove, evaluation, prev_eval, turn))

        # print(f'DIFF: {diff}, Eval: {evaluation}, Prev: {prev_eval}, Label: {"Bad" if evaluation_label == "B" else "Good"}')
        prev_eval = evaluation

    logger.info(f'Finished processing [{counter}] game... Saving outcome to database...')
    dbGameObject.save(cascade=True)
    counter = counter + 1

engine.quit()
