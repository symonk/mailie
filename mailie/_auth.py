class Auth:
    """
    Base class for authentication schemes.
    """

    def auth(self):
        ...

    def synchronous_auth(self):
        ...

    async def asynchronous_auth(self):
        ...
