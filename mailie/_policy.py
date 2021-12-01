from email.policy import HTTP
from email.policy import SMTP
from email.policy import SMTPUTF8
from email.policy import default
from email.policy import strict

Policies = {"default": default, "strict": strict, "smtp": SMTP, "smtputf8": SMTPUTF8, "http": HTTP}
