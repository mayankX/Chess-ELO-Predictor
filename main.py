import chess
import asyncio
import chess.pgn
import chess.engine


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