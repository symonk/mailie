import typing


class Response:
    # Todo: Simple for now; add per email data later etc.
    def __init__(self, result: typing.Dict[typing.Any, typing.Any]) -> None:
        self.result = result
