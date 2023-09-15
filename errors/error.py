class ImproperlyConfigured(Exception):
    """Raises when a environment variable is missing"""

    def __init__(self, variable_name):
        self.variable_name = variable_name
        self.message = f'Set the {variable_name} environment variable.'
        super().__init__(self.message)


class BadBookError(Exception):
    """Raises when it is not possible to parse this file"""

    def __init__(self):
        self.message = f"Can't parse this file"
        super().__init__(self.message)
