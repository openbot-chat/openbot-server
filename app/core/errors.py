

class APIException(Exception):
    status: str = 'unknown'
    description: str

    def __init__(self, status: str = 'unknown', description: str = ''):
        super().__init__(description)
        self.status = status



class QuotaExceededError(Exception):
    """
    Custom exception raised when the quota for a provider has been exceeded.
    """
    description = "Quota Exceeded"




class ProviderNotExistsError(Exception):
    def __init__(self, provider: str):
        super().__init__(f"Agent Provider {provider} not exists")