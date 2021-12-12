from mailie import Email


def test_structure_of_mail(capsys, render_checker):
    mail = Email(from_addr="test@one.com", to_addrs="two@three.com", html="<b> Hi There! </b>")
    mail.render()
    stdout, stderr = capsys.readouterr()
    lines = render_checker(stdout)
    assert len(lines) == 3
    assert lines[0] == "multipart/alternative"
    assert lines[1] == "text/plain"
    assert lines[2] == "text/html"
