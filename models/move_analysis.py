__author__ = 'Mayank Tiwari'

import datetime

from mongoengine import *


class PGNMetadata(EmbeddedDocument):
    sequenceNumber = IntField()
    sourceFileName = StringField(required=True)
    CreateDate = DateTimeField(default=datetime.datetime.now)
    LastUpdateDate = DateTimeField(default=datetime.datetime.now)

    def __init__(self, sequenceNumber: int, sourceFileName: str, *args, **values):
        super().__init__(*args, **values)
        self.sequenceNumber = sequenceNumber
        self.sourceFileName = sourceFileName


class GameMetadata(Document):
    site = StringField(required=True)
    event = StringField(required=True)
    white = StringField(required=True)
    black = StringField(required=True)
    result = StringField(required=True)
    uTCDate = StringField(required=True)
    uTCTime = StringField(required=True)
    whiteElo = StringField(required=True)
    blackElo = StringField(required=True)
    whiteRatingDiff = StringField()
    blackRatingDiff = StringField()
    eCO = StringField(required=True)
    opening = StringField(required=True)
    timeControl = StringField(required=True)
    termination = StringField(required=True)
    # PGN File
    pgnMetadata = EmbeddedDocumentField(PGNMetadata)

    def __init__(self, *args, **values):
        super().__init__(*args, **values)

    def __init__(self, headers=None, pgnMetadata=None, *args, **values):
        super().__init__(*args, **values)
        if headers is not None:
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

    # def get_by_id(cls, id):
    #     return cls.objects.filter(site=id).first()


class MoveMetadata(EmbeddedDocument):
    moveSequenceNumber = IntField(required=True)
    totalMovesInGame = IntField(required=True)
    turn = BooleanField(required=True)
    isCheckMate = BooleanField(default=False)
    isCheck = BooleanField(default=False)
    fen = StringField(required=True)
    uci = StringField(required=True)
    # Game Metadata
    gameMetadata = ReferenceField(GameMetadata)

    def __init__(self, moveSequenceNumber: int, totalMovesInGame: int, turn: bool, isCheckMate: bool, isCheck: bool, fen: str, uci: str, gameMetadata: GameMetadata, *args,
                 **values):
        super().__init__(*args, **values)
        self.moveSequenceNumber = moveSequenceNumber
        self.totalMovesInGame = totalMovesInGame
        self.turn = turn
        self.isCheckMate = isCheckMate
        self.isCheck = isCheck
        self.fen = fen
        self.uci = uci
        self.gameMetadata = gameMetadata


class BoardState(Document):
    piecePlacement = StringField(required=True)
    encodedState = StringField(required=True)
    score = IntField(required=True)
    # Metadata
    moveMetadata = ListField(EmbeddedDocumentField(MoveMetadata))

    def __init__(self, piecePlacement: str, encodedState: str, score: int, moveMetadata: ListField(EmbeddedDocumentField(MoveMetadata)), *args, **values):
        super().__init__(*args, **values)
        self.piecePlacement = piecePlacement
        self.encodedState = encodedState
        self.score = score
        self.moveMetadata = moveMetadata

    @classmethod
    def get_by_id(cls, id):
        return cls.objects.filter(piecePlacement=id).first()
