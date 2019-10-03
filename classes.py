from collections import namedtuple

CandlesResponse = namedtuple(
    'CandlesResponse',
    ['mts', 'open', 'close', 'high', 'lod', 'volume']
)
