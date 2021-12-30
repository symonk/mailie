import functools
import operator
import typing


def wraps_conversation(f) -> typing.Any:
    """
    A wrapper for SMTP clients to apply the hooking mechanism around `send(...)` calls.  This supports
    hook invocation before the SMTP conversation has started and after it has been completed.

    # TODO: Make this async aware and await accordingly.
    # TODO: Draft the concept of hooks and entry point for plugins?
    """

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        pre, post = operator.itemgetter("pre", "post")(args[0])
        if pre is not None:
            pre(args[0].message)
        result = f(*args, **kwargs)
        if post is not None:
            post(result)
        return result

    return wrapper
