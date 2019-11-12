__author__ = 'Mayank Tiwari'

import datetime
from chess.pgn import Headers
from mongoengine import *


class PGNMetadata(Document):
    sequenceNumber = IntField()
    sourceFileName = StringField(required=True)
    CreateDate = DateTimeField(default=datetime.datetime.now)
    LastUpdateDate = DateTimeField(default=datetime.datetime.now)

    def __init__(self, sequenceNumber: int, sourceFileName: str, *args, **values):
        super().__init__(*args, **values)
        self.sequenceNumber = sequenceNumber
        self.sourceFileName = sourceFileName


class GameMetadata(Document):
    site = StringField(primary_key=True, unique=True)
    event = StringField(required=True)
    white = StringField(required=True)
    black = StringField(required=True)
    result = StringField(required=True)
    uTCDate = StringField(required=True)
    uTCTime = StringField(required=True)
    whiteElo = StringField(required=True)
    blackElo = StringField(required=True)
    whiteRatingDiff = StringField(required=True)
    blackRatingDiff = StringField(required=True)
    eCO = StringField(required=True)
    opening = StringField(required=True)
    timeControl = StringField(required=True)
    termination = StringField(required=True)
    # PGN File
    pgnMetadata = EmbeddedDocumentField(PGNMetadata)

    def __init__(self, headers: Headers, pgnMetadata: PGNMetadata, *args, **values):
        super().__init__(*args, **values)
        self.event = headers.get("Event")
        self.site = headers.get("Site")
        self.white = headers.get("White")
        self.black = headers.get("Black")
        self.result = headers.get("Result")
        self.uTCDate = headers.get("UTCDate")
        self.uTCTime = headers.get("UTCTime")
        self.whiteElo = headers.get("WhiteElo")
        self.blackElo = headers.get("BlackElo")
        self.whiteRatingDiff = headers.get("WhiteRatingDiff")
        self.blackRatingDiff = headers.get("BlackRatingDiff")
        self.eCO = headers.get("ECO")
        self.opening = headers.get("Opening")
        self.timeControl = headers.get("TimeControl")
        self.termination = headers.get("Termination")
        self.pgnMetadata = pgnMetadata


class MoveMetadata(EmbeddedDocument):
    moveSequenceNumber = IntField(required=True)
    totalMovesInGame = IntField(required=True)
    turn = BooleanField(required=True)
    isMate = BooleanField(default=False)
    # Game Metadata
    gameMetadata = ReferenceField(GameMetadata)


class MoveAnalysis(Document):
    uci = StringField(required=True)
    fen = StringField(required=True)
    encodedMove = StringField(required=True)
    score = IntField(required=True)
    metadata = ListField(EmbeddedDocumentField(MoveMetadata))

    # def __init__(self, uci:str, fen:str, encodedMove:str, score:int,  headers: Headers, pgnMetadata: PGNMetadata, *args, **values):
    #     super().__init__(*args, **values)
