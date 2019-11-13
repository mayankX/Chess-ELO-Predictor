__author__ = 'Mayank Tiwari'

import logging
import logging.config
import os
import sys

import chess
import chess.engine
import chess.pgn
import chess.svg

# if __name__ == '__main__':
#     __import__('imp').load_source('root', os.path.abspath(os.path.join(os.path.split(__file__)[0], *(['..'] + ['__init__.py']))))

ROOT_DIR = os.path.abspath(os.path.join(os.path.split(__file__)[0], '..'))
sys.path.append(ROOT_DIR)

from models.game import *
from util import *

'''
Loading the Logging library here
'''
# logging.basicConfig(level=logging.INFO, filename='app.log', filemode='w', format='%(asctime)s - %(levelname)s - %(message)s')
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
init_database(profile, config)


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
    limit = chess.engine.Limit(time=0.200)
    # limit = chess.engine.Limit(depth=18)

    '''
    Beginning to parse the files and load it into the warehouse
    '''
    counter = 0
    while True:
        counter = counter + 1
        game = chess.pgn.read_game(pgn)
        if game is None:
            break

        headers = game.headers
        # print(headers)

        site = headers.get("Site")
        logging.info(f'Processing [{counter}] game... ID: {site}')
        # if Game.site_exists(site=site):
        if Game.objects(site=site).count() != 0:
            logger.info("-> Skipping Already Processed File...")
            continue

        dbGameObject = Game(headers, Metadata(counter, filename))
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
            fen = str(board.fen())
            dbGameObject.moves.append(Move(uci, fen, encodedMove, evaluation, prev_eval, turn, isMate))

            # print(f'DIFF: {diff}, Eval: {evaluation}, Prev: {prev_eval}, Label: {"Bad" if evaluation_label == "B" else "Good"}')
            prev_eval = evaluation

        logger.info(f'Finished processing [{counter}] game... Saving outcome to database...')
        try:
            dbGameObject.save(cascade=True)
        except BaseException as e:
            logger.error(f'Error saving record: {site}', str(e))

    engine.quit()


# parse_pgn('lichess_db_standard_rated_2014-01.pgn')
def parse_all_pgn(location='./data'):
    logger.info(f'Parsing PGN files from Location: {location} for Game Analysis...')
    for dirname, _, filenames in os.walk(location):
        for filename in filenames:
            if filename.endswith('.pgn'):
                # filePath = os.path.join(dirname, filename)
                # print(filePath)
                parse_pgn(dirname, filename)


# parse_all_pgn('./data')
'''D
from mongo_pipeline import *
parse_all_pgn('./data')
'''
parse_all_pgn()
