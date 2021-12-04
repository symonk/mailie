from email.parser import Parser
from smtpd import SMTPServer


class FakeSMTPServer(SMTPServer):
    total = 0
    files = []

    def process_message(self, peer, mailfrom, rcpttos, data, **kwargs):
        _ = Parser().parsestr(data)
        # TODO: Finish this off.
        ...
