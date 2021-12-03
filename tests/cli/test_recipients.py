def test_single_recipient(run_mailie):
    result = run_mailie(cmds=["mail", "-f", "one@two.com", "-t", "foo@bar.com", "-s", "nice", "-m", "one"])
    assert result.exit_code == 0


def test_recipients_from_file(run_mailie, tmp_path):
    sub = tmp_path / "examples"
    sub.mkdir()
    file = sub / "example.csv"
    file.write_text("one@two.com,two@three.com")
    result = run_mailie(cmds=["mail", "-f", "a@b.com", f"-t {str(file)}", "-s", "foo", "-m", "bar"])
    print(result.output)
    assert result.exit_code == 0
