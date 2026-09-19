from importlib.util import find_spec


def test_isolated_preference_api_when_requested() -> None:
    # Given: preference recording must be independent of the session review command.
    # When: a consumer discovers the dedicated API.
    result = find_spec("logo_helper.preference_gallery")
    # Then: the blind comparison renderer is available as its own module.
    assert result is not None
