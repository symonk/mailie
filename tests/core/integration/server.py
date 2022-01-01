import asyncore
import pathlib
import uuid
from smtpd import SMTPServer
from threading import Thread


class BackgroundSMTPServer(Thread):
    def __init__(self, temp_dir=None):
        super().__init__(daemon=True)
        self.messages = []
        self.total = 0
        self.smtp = None
        self.temp_dir = temp_dir or pathlib.Path(__file__).parent.parent.parent.joinpath("test_files")

    def run(self):
        temp_dir = self.temp_dir

        class FakeSMTPServer(SMTPServer):
            def process_message(self, peer, mailfrom, rcpttos, data, **kwargs):
                fname = temp_dir.joinpath(f"{str(uuid.uuid4())}.eml")
                with open(fname, "wb") as f:
                    f.write(data)

        server = FakeSMTPServer(("localhost", 9222), None)
        self.smtp = server
        asyncore.loop()

    def close(self):
        self.smtp.close()
