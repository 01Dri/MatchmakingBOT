import enum


class StatusQueue(enum.Enum):
    DEFAULT = 1
    IN_QUEUE = 2
    IN_VOTING_MAPS = 3
    IN_MATCH = 4
