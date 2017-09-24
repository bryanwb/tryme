"""tryme - error handling for humans"""

from .tryme import Try, Failure, Success, Again, Stop, Maybe, Some, Nothing, try_out, to_console, tick_counter, retry


__all__ = [
    'Try',
    'Failure',
    'Success',
    'Again',
    'Stop',
    'Maybe',
    'Some',
    'Nothing',
    'try_out',
    'to_console',
    'tick_counter',
    'retry'
]

VERSION = '0.0.5'
