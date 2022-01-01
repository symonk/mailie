def test_structure_of_mail(capsys, html_multi_attach_mail):
    html_multi_attach_mail.tree_view()
    stdout, stderr = capsys.readouterr()
    lines = stdout.strip().split("\n")
    assert len(lines) == 7
    assert lines[0] == "multipart/mixed"
    assert lines[1] == "-multipart/alternative"
    assert lines[2] == "--text/plain"
    assert lines[3] == "--text/html"
    assert lines[4] == "-image/png"
    assert lines[5] == "-image/png"
    assert lines[6] == "-image/png"
