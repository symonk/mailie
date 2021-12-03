def test_version_execution(run_mailie):
    result = run_mailie("--help")
    assert result.exit_code == 0
    assert "--show-completion" in result.output
