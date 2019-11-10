__author__ = 'Mayank Tiwari'

import chess
import asyncio
import chess.pgn
import chess.engine
import chess.svg

from stockfish import Stockfish

import base64
import numpy as np  # linear algebra
import pandas as pd  # data processing, CSV file I/O (e.g. pd.read_csv)

engine = chess.engine.SimpleEngine.popen_uci("stockfish")
# test_fen = 'r1bq2n1/pp3kbQ/2n2p2/3p1P2/3Pp2p/2P5/PP4P1/RNB1KB1R w KQ - 0 14'
test_fen = 'r1bq2n1/pp3kbQ/2n2p1B/3p1P2/3Pp2p/2P5/PP4P1/RN2KB1R b KQ - 1 14'
test_board = chess.Board(test_fen)

if test_board.turn:
    print('White to move')
else:
    print('black to move')

# with pd.option_context("display.max_rows", None, "display.max_columns", None):
with engine.analysis(test_board) as analysis:
    for index, info in enumerate(analysis):
        #         print(info.get("score"), info.get("pv"))
        #         print(f'{index} => {info.get("score")}, PV: {info.get("pv")}')
        print(f'{index} => {info.get("score")}')
        # print
        # str(board.san(el)), 'eval = ', round(handler.info["score"][1].cp / 100.0, 2)

        # Arbitrary stop condition.
        if info.get("seldepth", 0) > 30:
            break
engine.quit()
