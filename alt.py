__author__ = 'Mayank Tiwari'

from collections import Counter

import chess
import chess.engine
import chess.pgn
import chess.svg
from chess import QUEEN

from util import convertToBB


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
    # pgnFilePath = 'data/test.pgn'
    pgnFilePath = 'data_temp/game1_2.pgn'
    pgn = open(pgnFilePath)
    game = chess.pgn.read_game(pgn)

    engine = chess.engine.SimpleEngine.popen_uci("stockfish")

    prev_eval = 0
    diff = 0
    output_data_string = ''

    # New
    first_check = True
    first_queen_move = True
    features = {}
    # New

    for move in game.mainline_moves():
        # New
        moved_piece = board.piece_at(move.from_square)
        captured_piece = board.piece_at(move.to_square)

        if moved_piece == QUEEN and first_queen_move:
            features['queen_moved_at'] = board.fullmove_number
            first_queen_move = False

        if captured_piece == QUEEN:
            features['queen_changed_at'] = board.fullmove_number

        if move.promotion:
            features['promotion'] += 1
        if board.is_check():
            features['total_checks'] += 1
            if first_check:
                features['first_check_at'] = board.fullmove_number
                first_check = False

                # castling
                uci_repr = move.uci()
                if uci_repr == 'e1g1':
                    features['white_king_castle'] = board.fullmove_number
                elif uci_repr == 'e1c1':
                    features['white_queen_castle'] = board.fullmove_number
                elif uci_repr == 'e8g8':
                    features['black_king_castle'] = board.fullmove_number
                elif uci_repr == 'e8c8':
                    features['black_queen_castle'] = board.fullmove_number
        # New

        board.push(move)

        print("=" * 50)
        print(board)

        limit = chess.engine.Limit(time=0.100)
        # limit = chess.engine.Limit(depth=20)
        result = engine.analyse(board, limit)
        # result = engine.play(board, chess.engine.Limit(time=0.100))
        #
        # info = engine.analyse(board, limit)
        evaluationVal = result.score.relative
        if not evaluationVal.is_mate():
            evaluation = evaluationVal.cp
        else:
            evaluation = evaluationVal.mate()

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

        out_board = convertToBB(board)
        output_data_string = '{0}{1},{2}\n'.format(output_data_string, out_board, evaluation_label)

    # New
    if board.is_checkmate():
        features['is_checkmate'] = 1
    if board.is_stalemate():
        features['is_stalemate'] = 1
    if board.is_insufficient_material():
        features['insufficient_material'] = 1
    if board.can_claim_draw():
        features['can_claim_draw'] = 1
    features['total_moves'] = board.fullmove_number

    piece_placement = board.fen().split()[0]
    end_pieces = Counter(x for x in piece_placement if x.isalpha())

    # count number of piece at end position
    features.update({'end_' + piece: cnt
                     for piece, cnt in end_pieces.items()})
    # New

    # print(output_data_string)
    print(features)
    engine.quit()


test()
