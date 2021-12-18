from email.policy import HTTP
from email.policy import SMTP
from email.policy import SMTPUTF8
from email.policy import EmailPolicy
from email.policy import default
from email.policy import strict

POLICIES = {"default": default, "strict": strict, "smtp": SMTP, "smtputf8": SMTPUTF8, "http": HTTP}


def policy_factory(policy_type: str = "default") -> EmailPolicy:
    """
    Returns an immutable email policy instance based on the policy_type.
    :param policy_type: The policy type to perform the lookup for
    :returns: The EmailPolicy instance.
    """
    return POLICIES.get(policy_type, default)
