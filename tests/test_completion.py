"""配信データによる完了表示を、実際の JavaScript を実行して検証する。"""

import json
from pathlib import Path
import subprocess

import pytest


ROOT = Path(__file__).resolve().parents[1]


def render_items(items):
    script = (ROOT / "script.js").read_text(encoding="utf-8")
    harness = r"""
const vm = require('node:vm');
const input = JSON.parse(require('node:fs').readFileSync(0, 'utf8'));
// 初期化時の通信を止め、DOM 表示関数を同じカードに対して実行する。
const context = vm.createContext({ fetch: () => new Promise(() => {}) });
vm.runInContext(input.script, context);
const classes = new Set();
const card = {
  innerHTML: '',
  classList: { toggle: (name, enabled) => enabled ? classes.add(name) : classes.delete(name) }
};
const results = input.items.map(item => {
  context.renderCarouselItem(card, item);
  return { html: card.innerHTML, completed: classes.has('is-complete') };
});
process.stdout.write(JSON.stringify(results));
"""
    result = subprocess.run(
        ["node", "-e", harness],
        input=json.dumps({"script": script, "items": items}),
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
        timeout=10,
    )
    return json.loads(result.stdout)


@pytest.mark.parametrize("completed", [True, False, None, "true"])
def test_only_boolean_true_shows_completion(completed):
    result = render_items([{"e": "🏕️", "t": "キャンプ", "completed": completed}])[0]
    assert result["completed"] is (completed is True)
    assert ('class="cr-completed"' in result["html"]) is (completed is True)
    assert ("✓ 完了" in result["html"]) is (completed is True)


def test_existing_items_without_completion_remain_incomplete():
    result = render_items([{"e": "⚽", "t": "サッカー"}])[0]
    assert not result["completed"]
    assert "cr-completed" not in result["html"]
    assert "サッカー" in result["html"]


def test_recycled_card_does_not_keep_previous_completion():
    results = render_items([
        {"e": "🏕️", "t": "キャンプ", "completed": True},
        {"e": "🎯", "t": "サバゲー", "completed": False},
        {"e": "🎵", "t": "楽器演奏", "completed": True},
    ])
    assert [result["completed"] for result in results] == [True, False, True]
    assert "完了" not in results[1]["html"]
    assert "キャンプ" not in results[1]["html"]
    assert "サバゲー" in results[1]["html"]
    assert "楽器演奏" in results[2]["html"]


def test_item_text_is_escaped():
    result = render_items([{"e": "<img>", "t": '<script>"&', "completed": True}])[0]
    assert "<img>" not in result["html"]
    assert "<script>" not in result["html"]
    assert "&lt;script&gt;&quot;&amp;" in result["html"]


def test_try_items_have_boolean_completion_in_served_data():
    data = json.loads((ROOT / "data.json").read_text(encoding="utf-8"))
    assert data["tryItems"]
    assert all(type(item["completed"]) is bool for item in data["tryItems"])
