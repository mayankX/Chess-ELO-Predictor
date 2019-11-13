__author__ = 'Mayank Tiwari'

import logging
import logging.config
import os
import sys

import chess
import chess.engine
import chess.pgn
import chess.svg

ROOT_DIR = os.path.abspath(os.path.join(os.path.split(__file__)[0], '..'))
sys.path.append(ROOT_DIR)

from models.move_analysis import *
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

        site = headers.get("Site")
        logging.info(f'Processing [{counter}] game... ID: {site}')

        gameMetadata = GameMetadata.get_by_id(site)
        if gameMetadata is None:
            gameMetadata = GameMetadata(headers, PGNMetadata())
            continue

        # dbGameObject = Game(headers, Metadata(counter, filename))

        board = chess.Board()
        moves = list(game.mainline_moves())
        totalMoves = len(moves)
        for index, move in enumerate(moves):
            board.push(move)
            uci = move.uci()
            print(f'{index + 1}/{totalMoves} Analyzing Move {uci} for Game: {counter}...')

            turn = board.turn
            encodedMove = convertToBB(board)
            fen = str(board.fen())

        logger.info(f'Finished processing [{counter}] game... Saving outcome to database...')
        # dbGameObject.save(cascade=True)

    engine.quit()


def parse_all_pgn(location='./data'):
    logger.info(f'Parsing PGN files from Location: {location} for Move Analysis...')
    for dirname, _, filenames in os.walk(location):
        for filename in filenames:
            if filename.endswith('.pgn'):
                parse_pgn(dirname, filename)


'''
from mongo_pipeline import *
parse_all_pgn('./data')
'''
# parse_all_pgn()
