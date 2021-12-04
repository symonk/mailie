from smtpd import SMTPServer


class FakeSMTPServer(SMTPServer):
    def process_message(self, peer, mailfrom, rcpttos, data, **kwargs):
        pass
