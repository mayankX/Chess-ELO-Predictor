__author__ = 'Mayank Tiwari'

from mongoengine import *
import os
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
# connect('chess', host='localhost', port=27017)
connect('chess', host='35.196.240.61', port=27017, username='root', password='P@ssword123', authentication_source='admin')


def parse_pgn(dirname: str, filename: str):
    filePath = os.path.join(dirname, filename)
    logger.info(f'Starting to Parse PGN File: {filePath}')

    '''
    Reading the Chess PGN file
    '''
    # pgn = open('data/%s' % fileName)
    pgn = open(filePath)

    '''
    Loading the chess processing engine
    '''
    engine = chess.engine.SimpleEngine.popen_uci("stockfish")
    # limit = chess.engine.Limit(time=0.100)
    limit = chess.engine.Limit(depth=20)
    metadata = Metadata(filename)

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

        dbGameObject = Game(headers, metadata)
        # for k, v in headers.items():
        #     print(f'{k} -> {v}')

        prev_eval = 0
        board = chess.Board()
        moves = list(game.mainline_moves())
        totalMoves = len(moves)
        for index, move in enumerate(moves):
            board.push(move)
            uci = move.uci()
            print(f'{index + 1}/{totalMoves} Analyzing Move {uci} for Game: {counter}...')
            result = engine.analyse(board, limit)

            evaluationVal = result.score.relative
            isMate = evaluationVal.is_mate()
            if not isMate:
                evaluation = evaluationVal.cp
            else:
                evaluation = evaluationVal.mate()

            turn = board.turn
            # if turn:
            #     diff = prev_eval - evaluation
            #     if diff > 0.3:
            #         evaluation_label = "B"  # badmove
            #     else:
            #         evaluation_label = "G"  # goodmove
            # else:
            #     evaluation *= -1
            #     diff = evaluation - prev_eval
            #     if diff > 0.3:
            #         evaluation_label = "B"  # badmove
            #     else:
            #         evaluation_label = "G"  # goodmove

            encodedMove = convertToBB(board)
            fen = board.fen().__str__()
            dbGameObject.moves.append(Move(uci, fen, encodedMove, evaluation, prev_eval, turn, isMate))

            # print(f'DIFF: {diff}, Eval: {evaluation}, Prev: {prev_eval}, Label: {"Bad" if evaluation_label == "B" else "Good"}')
            prev_eval = evaluation

        logger.info(f'Finished processing [{counter}] game... Saving outcome to database...')
        dbGameObject.save(cascade=True)
        counter = counter + 1

    engine.quit()


# parse_pgn('lichess_db_standard_rated_2014-01.pgn')
def parse_all_pgn(location):
    for dirname, _, filenames in os.walk(location):
        for filename in filenames:
            if filename.endswith('.pgn'):
                # filePath = os.path.join(dirname, filename)
                # print(filePath)
                parse_pgn(dirname, filename)


# parse_all_pgn('./data')
'''
from mongo_pipeline import *
parse_all_pgn('./data')
'''
