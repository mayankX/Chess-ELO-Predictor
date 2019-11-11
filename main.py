import chess
import asyncio
import chess.pgn
import chess.engine


def convertLetterToNumber(letter):
    if letter == 'K':
        return '100000000000'
    if letter == 'Q':
        return '010000000000'
    if letter == 'R':
        return '001000000000'
    if letter == 'B':
        return '000100000000'
    if letter == 'N':
        return '000010000000'
    if letter == 'P':
        return '000001000000'
    if letter == 'k':
        return '000000100000'
    if letter == 'q':
        return '000000010000'
    if letter == 'r':
        return '000000001000'
    if letter == 'b':
        return '000000000100'
    if letter == 'n':
        return '000000000010'
    if letter == 'p':
        return '000000000001'
    if letter == '1':
        return '000000000000'
    if letter == '2':
        return '000000000000000000000000'
    if letter == '3':
        return '000000000000000000000000000000000000'
    if letter == '4':
        return '000000000000000000000000000000000000000000000000'
    if letter == '5':
        return '000000000000000000000000000000000000000000000000000000000000'
    if letter == '6':
        return '000000000000000000000000000000000000000000000000000000000000000000000000'
    if letter == '7':
        return '000000000000000000000000000000000000000000000000000000000000000000000000000000000000'
    if letter == '8':
        return '000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'
    if letter == '/':
        return ''


def convertToBB(board):
    bitBoard = ''
    board = str(board.fen()).split(' ')[0]
    for letter in board:
        bitBoard = bitBoard + convertLetterToNumber(letter)
    # bitBoard = bitBoard[1:-1]
    return bitBoard


def indefinite_analysis(engine):
    with engine.analysis(chess.Board()) as analysis:
        for info in analysis:
            print(info.get("score"), info.get("pv"))

            # Arbitrary stop condition.
            if info.get("seldepth", 0) > 20:
                break


def test_async():
    async def main():
        transport, engine = await chess.engine.popen_uci("stockfish")

        board = chess.Board()
        while not board.is_game_over():
            result = await engine.play(board, chess.engine.Limit(time=0.100))
            board.push(result.move)
            print("=" * 50)
            print(board)

        await engine.quit()

    asyncio.set_event_loop_policy(chess.engine.EventLoopPolicy())
    asyncio.run(main())