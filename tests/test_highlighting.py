import pytest


from search_engine.highlight import highlight_result_page
from search_engine import check_helper_api


def test_if_api_active():
    assert check_helper_api() == True


def test_highligting():
    result = highlight_result_page(
        [
            (
                "https://en.wikipedia.org/wiki/Seco_Herrerano",
                "title",
                {"apple", "chocolate"},
                {"apple", "chocolate"},
            )
        ]
    )

    expcted_result = [
        (
            "https://en.wikipedia.org/wiki/Seco_Herrerano",
            "title",
            {"apple", "chocolate"},
            [
                ("or", False),
                ("molasses", False),
                ("Tea", False),
                ("Various", False),
                ("starches", False),
                ("by", False),
                ("ingredientsFruit", False),
                ("Apple", True),
                ("Cashew", False),
                ("apple", True),
            ],
        )
    ]

    assert result == expcted_result, f"{result}"
