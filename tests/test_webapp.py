from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest

from quant_app.webapp import create_app


def _fake_history(ticker, as_of=None):
    rng = np.random.default_rng(abs(hash(ticker)) % (2**32))
    n = 260
    base = {"AAPL": 180, "MSFT": 300, "VTI": 230, "BND": 70}[ticker]
    walk = np.cumsum(rng.normal(0, base * 0.01, n))
    closes = base + walk
    return pd.DataFrame({"Close": closes}, index=pd.date_range("2025-01-01", periods=n))


@pytest.fixture
def client(tmp_path):
    app = create_app(
        holdings_path="config/holdings.csv",
        config_path="config/config.yaml",
        reports_dir=str(tmp_path),
    )
    app.testing = True
    with patch("quant_app.pipeline.get_price_history", side_effect=_fake_history):
        with app.test_client() as c:
            yield c


def test_dashboard_renders_holdings(client):
    response = client.get("/")
    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert "Portfolio Dashboard" in body
    assert "AAPL" in body
    assert "Total value" in body


def test_history_empty_state(client):
    response = client.get("/history")
    assert response.status_code == 200
    assert "No reports yet" in response.get_data(as_text=True)


def test_history_detail_rejects_path_traversal(client):
    response = client.get("/history/..%2f..%2fetc%2fpasswd")
    assert response.status_code == 404


def test_history_detail_rejects_bad_filename_pattern(client):
    response = client.get("/history/not-a-report.txt")
    assert response.status_code == 404
