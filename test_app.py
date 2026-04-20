"""Tests for NutriGPT app endpoints and critical functionality."""
import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)


# --- Static asset endpoints ---

def test_logo_png_returns_image():
    r = client.get("/logo.png")
    assert r.status_code == 200
    assert r.headers["content-type"] == "image/png"
    assert r.content[:4] == b"\x89PNG"


def test_icon_192_redirects_to_logo():
    r = client.get("/icon-192.png", follow_redirects=False)
    assert r.status_code == 302
    assert r.headers["location"] == "/logo.png"


def test_icon_512_redirects_to_logo():
    r = client.get("/icon-512.png", follow_redirects=False)
    assert r.status_code == 302
    assert r.headers["location"] == "/logo.png"


def test_anim_9_16_returns_video():
    r = client.get("/anim-9-16.mp4")
    assert r.status_code == 200
    assert "video/mp4" in r.headers["content-type"]


def test_anim_4_3_returns_video():
    r = client.get("/anim-4-3.mp4")
    assert r.status_code == 200
    assert "video/mp4" in r.headers["content-type"]


def test_anim_1_1_returns_video():
    r = client.get("/anim-1-1.mp4")
    assert r.status_code == 200
    assert "video/mp4" in r.headers["content-type"]


# --- PWA manifest ---

def test_manifest_uses_logo_png():
    r = client.get("/manifest.json")
    assert r.status_code == 200
    data = r.json()
    assert data["icons"][0]["src"] == "/logo.png"


def test_manifest_fields():
    r = client.get("/manifest.json")
    data = r.json()
    assert data["name"] == "NutriGPT"
    assert data["display"] == "standalone"


# --- Service worker ---

def test_sw_js_returns_javascript():
    r = client.get("/sw.js")
    assert r.status_code == 200
    assert "javascript" in r.headers["content-type"]
    assert r.headers["cache-control"] == "no-cache, no-store"


# --- Main HTML page ---

def test_homepage_returns_html():
    r = client.get("/")
    assert r.status_code == 200
    assert "text/html" in r.headers["content-type"]


def test_homepage_has_logo_img():
    r = client.get("/")
    assert b'<img src="/logo.png"' in r.content


def test_homepage_has_splash_element():
    r = client.get("/")
    assert b'id="splash"' in r.content
    assert b'id="splash-video"' in r.content


def test_app_js_has_splash_js():
    r = client.get("/app.js")
    assert r.status_code == 200
    assert b"_splashVideo" in r.content
    assert b"anim-9-16.mp4" in r.content
    assert b"anim-4-3.mp4" in r.content


def test_homepage_apple_touch_icon_uses_logo():
    r = client.get("/")
    assert b'rel="apple-touch-icon" href="/logo.png"' in r.content


# --- Chat API ---

def test_chat_endpoint_exists():
    r = client.post("/api/chat", json={"mensaje": "hola", "contexto": {}})
    assert r.status_code == 200
    assert "respuesta" in r.json()


def test_chat_empty_message_handled():
    r = client.post("/api/chat", json={"mensaje": "", "contexto": {}})
    assert r.status_code == 200


# --- Calorie lookup API ---

def test_calories_endpoint_known_food():
    r = client.get("/api/calories?food=arroz")
    assert r.status_code == 200
    data = r.json()
    assert "found" in data


def test_calories_endpoint_unknown_food():
    r = client.get("/api/calories?food=xyzunknownfood99")
    assert r.status_code == 200
    data = r.json()
    assert data["found"] is False
