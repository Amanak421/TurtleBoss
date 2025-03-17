class ProcessError(Exception):
    """Custom exception with an optional message."""
    def __init__(self, message="Unexpected error!"):
        self.message = message
        super().__init__(self.message)
