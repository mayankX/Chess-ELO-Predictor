__author__ = 'Mayank Tiwari'

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


outF = open("game_analysis.csv", "w")
writeOutput(
    outF,
    'Event, Is Draw, Has Black Won, Opening, White ELO, Black ELO, Time Control, Termination, Total White Score, Total Black Score, No. White Moves, No. Black Moves, White Avg. Score, Black Avg. Score'
)

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
        game.event + ", " + str(isDraw) + ", " + str(hasBlackWon) + ", " +
        game.opening + ", " + game.whiteElo + ", " + game.blackElo + ", " + game.timeControl + ", " + game.termination + ", " \
        + str(total_white_games) + ", " + str(total_black_games) + ", " + str(white_avg_score) + ", " + str(black_avg_score)
    )
outF.close()