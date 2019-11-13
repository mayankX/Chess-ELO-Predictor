__author__ = 'Mayank Tiwari'

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
        result = headers.get("Result")

        isDraw = result == "1/2-1/2"
        hasBlackWon = False
        if not isDraw:
            hasBlackWon = result == "0-1"

        logging.info(f'Processing [{counter}] game... ID: {site}')

        gameMetadata = GameMetadata.objects.filter(site=site).first()
        if gameMetadata is None:
            gameMetadata = GameMetadata.save(GameMetadata(headers, PGNMetadata(counter, filename)))

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
            piecePlacement = str(board.fen()).split(' ')[0]
            if isDraw:
                score = 0
            else:
                if hasBlackWon:
                    score = -1 if turn else 1
                else:
                    score = 1 if turn else -1

            boardState = BoardState.get_by_id(piecePlacement)
            moveMetadata = MoveMetadata(counter, totalMoves, turn, board.is_checkmate(), board.is_check(), fen, uci, gameMetadata)
            if boardState is None:
                boardState = BoardState(piecePlacement, encodedMove, score, [moveMetadata]).save()
                logger.info('\tBoard State & Move metadata saved successfully in DB!')
            else:
                if BoardState.objects.filter(Q(id=boardState.id) & Q(moveMetadata__gameMetadata=gameMetadata.id)).count() != 0:
                    logger.info('\t====>Skipping already analyzed game...')
                    continue

                BoardState.objects(id=boardState.id).update_one(inc__score=score, push__moveMetadata=moveMetadata)
                logger.info('\tBoard State Updated with Move metadata')

            logger.info(f'\tSaved/Updated board state   ID: {boardState.id}')

        logger.info(f'Finished processing [{counter}] game... Saving outcome to database...')

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
parse_all_pgn()
