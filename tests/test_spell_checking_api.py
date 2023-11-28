import pytest
from search_engine.spelling_fix import query_model
from search_engine import check_helper_api


def test_if_api_active():
    assert check_helper_api() == True


# Test cases
@pytest.mark.parametrize(
    "input_query, expected_output, expected_changed",
    [
        ("This is a test", "This is a test.", False),  # No spelling error
        ("Ths is a tst", "This is a test.", True),  # Spelling error
        ("Test?", "Test?", False),  # No spelling error, with punctuation
        # Add more test cases as needed
    ],
)
def test_fix_spelling(input_query, expected_output, expected_changed):
    corrected = query_model(input_query)
    assert (
        corrected == expected_output
    ), f"The spelling correction did produce '{corrected}' insteead of '{expected_output}'"
