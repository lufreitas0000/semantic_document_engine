"""
End-to-End tests for the Streamlit Interface.
"""
import pytest
from unittest.mock import patch, MagicMock
from streamlit.testing.v1 import AppTest

@pytest.mark.anyio
@patch("httpx.post") # Block the Ingest network call
@patch("httpx.get")  # Block the Search network call
def test_streamlit_search_ui_renders_and_fetches_data(mock_get, mock_post):
    # 1. Configure GET mock (Search)
    mock_get_response = MagicMock()
    mock_get_response.status_code = 200
    mock_get_response.json.return_value = {
        "query": "physics",
        "results": [
            {
                "id": "1234-5678",
                "title": "Simulated Physics Paper",
                "abstract": "This is a simulated abstract.",
                "distance": 0.1234
            }
        ]
    }
    mock_get_response.raise_for_status.return_value = None
    mock_get.return_value = mock_get_response

    # Configure POST mock (Ingest) just in case!
    mock_post_response = MagicMock()
    mock_post_response.status_code = 200
    mock_post_response.json.return_value = {"message": "Success", "papers_ingested": 5}
    mock_post_response.raise_for_status.return_value = None
    mock_post.return_value = mock_post_response

    # 2. Instantiate the Streamlit simulation
    at = AppTest.from_file("frontend/app.py")
    at.run()

    # 3. Safely find the EXACT inputs and buttons by their labels
    # This prevents the "IndexError" and clicks the correct tab
    search_input = next(widget for widget in at.text_input if "conceptual question" in widget.label)
    search_button = next(widget for widget in at.button if widget.label == "Search")

    # 4. Simulate a human typing and clicking
    search_input.input("physics").run()
    search_button.click().run()

    # 5. Mathematically prove the UI rendered the mocked data
    assert not at.exception # Prove the app didn't crash

    if not at.expander:
        pytest.fail(f"UI rendered an error instead of expanders: {[e.value for e in at.error]}")

    assert "Simulated Physics Paper" in at.expander[0].label
    assert "0.1234" in at.expander[0].label
