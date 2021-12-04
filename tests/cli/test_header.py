def test_adding_arbitrary_headers(run_mailie):
    result = run_mailie(cmds=["mail", "-f", "a@b.com", "-t", "c@d.com", "--headers", "foo:bar", "-h", "baz:booze"])
    assert result.exit_code == 0
