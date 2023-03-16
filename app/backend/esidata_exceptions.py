class UnexpectedDataException(Exception):
    """
    Exception raised for errors related to differences in expected vs actual input

    Attributes:
        expected_input -- Input expected by the developer
        received_input -- Actual input provided by the user
    """
    def __init__(self, expected_input, received_input):
        self.message = f"Expected {expected_input}, got {received_input} instead"
        super().__init__(self.message)
