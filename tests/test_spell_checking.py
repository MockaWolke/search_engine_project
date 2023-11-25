import pytest
from search_engine.spelling_fix import (
    fix_spelling,
)  # Replace 'your_module' with the actual name of your Python file


# Test cases
@pytest.mark.parametrize(
    "input_query, expected_output, expected_changed",
    [
        ("This is a test", "This is a test", False),  # No spelling error
        ("Ths is a tst", "This is a test", True),  # Spelling error
        ("Test?", "Test?", False),  # No spelling error, with punctuation
        # Add more test cases as needed
    ],
)
def test_fix_spelling(input_query, expected_output, expected_changed):
    corrected, changed = fix_spelling(input_query)
    assert (
        corrected == expected_output
    ), "The spelling correction did not produce the expected output."
    assert (
        changed == expected_changed
    ), "The function did not correctly identify whether a change was made."
