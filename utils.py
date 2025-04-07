"""Utilities, miscellaneous."""


class ProcessError(Exception):
    """Custom exception with an optional message."""

    def __init__(self, message: str = "Unexpected error!") -> None:
        """Create ProcessError instance."""
        self.message = message
        super().__init__(self.message)
