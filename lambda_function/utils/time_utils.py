import datetime
import json
from .logger import setup_logging

# Setting up logging
logger = setup_logging()

def seconds_to_minutes(seconds: int) -> float:
    if not isinstance(seconds, int) or seconds < 0:
        raise ValueError("Input seconds should be a non-negative integer.")
    
    return seconds / 60.0

class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime.datetime):
            return o.isoformat()

        return super(DateTimeEncoder, self).default(o)