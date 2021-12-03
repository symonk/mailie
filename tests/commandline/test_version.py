from mailie import VERSION


def test_dash_dash_versions(run_mailie):
    result = run_mailie("--version")
    assert result.exit_code == 0
    assert f"Mailie version: {VERSION}\n" == result.output
