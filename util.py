__author__ = 'Mayank Tiwari'

import yaml
from mongoengine import connect


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


def load_config(config_file):
    with open(config_file, 'r') as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)


def init_database(profile, config):
    collectionName = config['collection_name']

    mongoConfiguration = config[profile]['mongo']
    mongoAuth = mongoConfiguration['auth']
    host = mongoConfiguration['host']
    port = mongoConfiguration['port']
    if mongoAuth is None or mongoAuth == 'None':
        return connect(collectionName, host=host, port=port)
    else:
        connect(
            collectionName, host=host, port=port,
            username=mongoConfiguration['username'], password=mongoConfiguration['password'],
            authentication_source=mongoConfiguration['authentication_source']
        )
