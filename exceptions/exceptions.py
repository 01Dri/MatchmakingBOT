class InvalidRankPlayerException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return {self.message}


class CrowdedQueueException(Exception):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return {self.message}


class NotFoundPlayerException(Exception):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return {self.message}
