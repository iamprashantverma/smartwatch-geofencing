from enum import Enum

class Severity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class Status(str, Enum):
    OK = "OK"
    FLAGGED = "FLAGGED"


class ZoneEvent(str, Enum):
    ENTRY = "ENTRY"
    EXIT = "EXIT"
    STAY = "STAY"