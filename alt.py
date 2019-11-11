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

from main import convertToBB

def game_analysis():
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


def read_multiple_games():
    pgn = open('data/game1_2.pgn')

    while True:
        print("-" * 50)
        # board = chess.Board()
        game = chess.pgn.read_game(pgn)
        if game is None:
            break

        headers = game.headers
        # print(headers)
        for k, v in headers.items():
            print(f'{k} -> {v}')


# read_multiple_games()
def test():
    board = chess.Board()
    pgn = open('data/test.pgn')
    game = chess.pgn.read_game(pgn)

    engine = chess.engine.SimpleEngine.popen_uci("stockfish")

    prev_eval = 0
    diff = 0
    output_data_string = ''

    for move in game.mainline_moves():
        print("=" * 50)
        print(board)

        limit = chess.engine.Limit(time=0.100)
        # limit = chess.engine.Limit(depth=20)
        result = engine.analyse(board, limit)
        # result = engine.play(board, chess.engine.Limit(time=0.100))
        #
        # info = engine.analyse(board, limit)
        evaluation = result.score.relative.cp
        print("=" * 50)

        if board.turn:
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

        print(f'DIFF: {diff}, Eval: {evaluation}, Prev: {prev_eval}, Label: {"Bad" if evaluation_label == "B" else "Good"}')
        prev_eval = evaluation

        board.push(move)
        out_board = convertToBB(board)
        output_data_string = '{0}{1},{2}\n'.format(output_data_string, out_board, evaluation_label)

    print(output_data_string)

    engine.quit()

test()