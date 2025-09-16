import pytest  # type: ignore
from bs4 import BeautifulSoup  # type: ignore
from vectorize.process_html import HTMLProcessor


@pytest.fixture(scope="module", autouse=True)
def fake_html():
    return """
    <html>
      <body>
        <div class="keep">
          <p>Paragraph 1</p>
          <p>Paragraph 2</p>
        </div>
        <div class="ignore-me">
          <p>Paragraph 3</p>
        </div>
        <table id="valid-table">
          <tr><td>Workout A</td></tr>
        </table>
        <table id="invalid-table">
          <tr><td>Workout B</td></tr>
        </table>
      </body>
    </html>
    """


@pytest.fixture(scope="module", autouse=True)
def fake_config():
    return {
        "input_paths": [],
        "tables": True,
        "table_structure": {
            "table_selector": "table",
            "row_selector": "tr",
            "day_columns_selector": "tr",
            "day_cells": "td",
            "invalid_table_ids": ["invalid-table"]
        },
        "classes-ignore": ["ignore-me"],
        "output_path_root": "output/test/"
    }


@pytest.fixture(scope="module", autouse=True)
def processor(fake_config):
    return HTMLProcessor(fake_config)


def test_get_paragraphs(processor, fake_html, fake_config):
    soup = BeautifulSoup(fake_html, 'html.parser')
    paragraphs = processor.get_paragraphs(soup, fake_config["classes-ignore"])
    assert paragraphs == ["Paragraph 1", "Paragraph 2"]
    assert "Paragraph 3" not in paragraphs


def test_flatten_weeks(processor):
    weeks = [
        {"desc": "Week 1 \n", "days": [
            {"day": "Mon", "workout": "5 mile run"}, {"day": "Tue", "workout": "rest"}]}
    ]
    flat_weeks = processor.flatten_weeks(weeks)
    flat_week = flat_weeks[0]
    expected = "Week 1 \nMon:5 mile run \nTue:rest \n"
    assert flat_week == expected
