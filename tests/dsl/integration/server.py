import asyncore
from smtpd import SMTPServer
from threading import Thread


class BackgroundSMTPServer(Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.messages = []
        self.total = 0
        self.smtp = None

    def run(self):
        class FakeSMTPServer(SMTPServer):
            def process_message(self, peer, mailfrom, rcpttos, data, **kwargs):
                with open("myemail.eml", "wb") as f:
                    f.write(data)

        server = FakeSMTPServer(("localhost", 9222), None)
        self.smtp = server
        asyncore.loop()

    def close(self):
        self.smtp.close()
