"""Unit tests for the pure helper functions and HTTP routes in app.py.

These exist primarily to give the pre-push quality gate (see
.githooks/pre-push) something real to run. Following the project's TDD
steering rules, new behavior added to app.py should come with tests here
covering the normal case, edge cases, and error cases.
"""

from __future__ import annotations

import pytest

from app import app as flask_app
from app import hex_to_rgb, lerp, resolve_font_path, shift_hue

# --- hex_to_rgb --------------------------------------------------------------

def test_hex_to_rgb_parses_six_digit_hex_with_hash():
    assert hex_to_rgb("#ffd60a") == (255, 214, 10)


def test_hex_to_rgb_parses_six_digit_hex_without_hash():
    assert hex_to_rgb("ffd60a") == (255, 214, 10)


def test_hex_to_rgb_expands_three_digit_shorthand():
    assert hex_to_rgb("#fff") == (255, 255, 255)


def test_hex_to_rgb_returns_fallback_for_invalid_length():
    assert hex_to_rgb("#12345", fallback=(1, 2, 3)) == (1, 2, 3)


def test_hex_to_rgb_returns_fallback_for_non_hex_characters():
    assert hex_to_rgb("#zzzzzz", fallback=(1, 2, 3)) == (1, 2, 3)


def test_hex_to_rgb_returns_default_fallback_for_empty_input():
    assert hex_to_rgb("") == (0, 0, 0)


def test_hex_to_rgb_returns_default_fallback_for_none_input():
    assert hex_to_rgb(None) == (0, 0, 0)


# --- lerp ---------------------------------------------------------------

def test_lerp_at_t_zero_returns_start_value():
    assert lerp(0, 100, 0.0) == 0


def test_lerp_at_t_one_returns_end_value():
    assert lerp(0, 100, 1.0) == 100


def test_lerp_at_midpoint_returns_average():
    assert lerp(0, 100, 0.5) == 50


# --- shift_hue ------------------------------------------------------------

def test_shift_hue_with_zero_delta_returns_same_color():
    assert shift_hue((10, 20, 30), 0.0) == (10, 20, 30)


def test_shift_hue_full_turn_returns_to_original_color():
    rgb = (255, 0, 0)
    shifted = shift_hue(rgb, 1.0)
    assert shifted == rgb


def test_shift_hue_half_turn_changes_a_saturated_color():
    rgb = (255, 0, 0)
    shifted = shift_hue(rgb, 0.5)
    assert shifted != rgb


# --- resolve_font_path ------------------------------------------------------

def test_resolve_font_path_returns_none_for_unknown_font():
    assert resolve_font_path("Definitely Not A Real Font") is None


# --- HTTP routes -------------------------------------------------------------

@pytest.fixture
def client():
    flask_app.config.update(TESTING=True)
    return flask_app.test_client()


def test_health_endpoint_returns_ok_status(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["status"] == "ok"
    assert "effects" in body
    assert "patterns" in body
    assert "borders" in body


def test_index_route_returns_html(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"<html" in resp.data.lower() or b"<!doctype" in resp.data.lower()


def test_generate_route_returns_png(client):
    resp = client.get("/generate?text=TEST")
    assert resp.status_code == 200
    assert resp.mimetype == "image/png"


def test_generate_gif_route_returns_gif(client):
    resp = client.get("/generate.gif?text=TEST&frames=12")
    assert resp.status_code == 200
    assert resp.mimetype == "image/gif"
