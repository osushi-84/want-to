from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_index_uses_external_css_and_javascript():
    html = (ROOT / "index.html").read_text(encoding="utf-8")

    assert '<link rel="stylesheet" href="./style.css">' in html
    assert '<script src="./script.js"></script>' in html
    assert "<style>" not in html
    assert "<script>" not in html


def test_external_assets_exist_and_contain_main_logic():
    css = (ROOT / "style.css").read_text(encoding="utf-8")
    javascript = (ROOT / "script.js").read_text(encoding="utf-8")

    assert ":root" in css
    assert ".carousel-wrap" in css
    assert "function initCarousel" in javascript
    assert "function initSphere" in javascript
