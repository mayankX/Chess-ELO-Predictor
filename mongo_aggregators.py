__author__ = 'Mayank Tiwari'

import errno
import os
from datetime import datetime

now = datetime.now()

import logging.config

from models.game import *
from util import *

# ROOT_DIR = os.path.abspath(os.path.join(os.path.split(__file__)[0], '..'))
# sys.path.append(ROOT_DIR)

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


def writeOutput(file, line):
    logging.info(line)
    file.write(line)
    file.write("\n")


# SEPARATOR = ", "
SEPARATOR = "|"

timestampString = now.strftime("%m_%d_%Y_%H_%M_%S")
outputFileName = f"dump/game_analysis_{timestampString}.psv"

if not os.path.exists(os.path.dirname(outputFileName)):
    try:
        os.makedirs(os.path.dirname(outputFileName))
    except OSError as exc:  # Guard against race condition
        if exc.errno != errno.EEXIST:
            raise

outF = open(outputFileName, "w")
writeOutput(
    outF,
    'Event' + SEPARATOR + 'Is Draw' + SEPARATOR + 'Has Black Won' + SEPARATOR + 'Opening' + SEPARATOR + 'White ELO' + SEPARATOR + 'Black ELO' + SEPARATOR + 'Time Control'
    + SEPARATOR + 'Termination' + SEPARATOR + 'Total White Score' + SEPARATOR + 'Total Black Score' + SEPARATOR + 'No. White Moves' + SEPARATOR + 'No. Black Moves' + SEPARATOR +
    'White Avg. Score' + SEPARATOR + 'Black Avg. Score'
)
logging.info('Beginning to process data from MongoDB...')
for game in Game.objects.all():
    isDraw = game.result == "1/2-1/2"
    hasBlackWon = False
    if not isDraw:
        hasBlackWon = game.result == "0-1"

    white_score_sum = 0
    black_score_sum = 0
    total_white_games = 0
    total_black_games = 0
    for move in game.moves:
        if move.turn:
            total_white_games = total_white_games + 1
            white_score_sum = white_score_sum + move.score
        else:
            total_black_games = total_black_games + 1
            black_score_sum = black_score_sum + move.score
    white_avg_score = 0 if total_white_games == 0 else round(white_score_sum / total_white_games, 2)
    black_avg_score = 0 if total_black_games == 0 else round(black_score_sum / total_black_games, 2)

    writeOutput(
        outF,
        game.event + SEPARATOR + str(isDraw) + SEPARATOR + str(hasBlackWon) + SEPARATOR +
        game.opening + SEPARATOR + game.whiteElo + SEPARATOR + game.blackElo + SEPARATOR + game.timeControl + SEPARATOR + game.termination + SEPARATOR \
        + str(white_score_sum) + SEPARATOR + str(black_score_sum) + SEPARATOR + str(total_white_games) + SEPARATOR + str(total_black_games) + SEPARATOR \
        + str(white_avg_score) + SEPARATOR + str(black_avg_score)
    )
outF.close()
logging.info('Finished processing data from MongoDB!')
