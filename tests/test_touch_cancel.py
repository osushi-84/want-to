"""タッチ中断後にドラッグ状態が残らないことを検証する。"""

import json
from pathlib import Path
import subprocess

import pytest


ROOT = Path(__file__).resolve().parents[1]
HARNESS = r"""
const assert = require('node:assert/strict');
const vm = require('node:vm');
const input = JSON.parse(require('node:fs').readFileSync(0, 'utf8'));

function element() {
  return {
    children: [], events: {}, style: {}, classList: {toggle() {}},
    appendChild(child) { this.children.push(child); },
    addEventListener(name, fn) { (this.events[name] ||= []).push(fn); },
    emit(name, event = {}) { (this.events[name] || []).forEach(fn => fn(event)); }
  };
}

function environment(mode) {
  const root = element(), win = element(), frames = [];
  Object.assign(root, {clientWidth: 800, clientHeight: 500});
  win.innerWidth = 800;
  const context = vm.createContext({
    fetch: () => new Promise(() => {}), window: win,
    document: {getElementById: () => root, createElement: element},
    requestAnimationFrame: fn => frames.push(fn),
    IntersectionObserver: class {
      constructor(fn) { this.fn = fn; }
      observe() { this.fn([{isIntersecting: true}]); }
      disconnect() {}
    },
    ResizeObserver: class { observe() {} }
  });
  vm.runInContext(input.script, context);
  if (mode === 'carousel') context.initCarousel('carouselWrap', input.data.tryItems);
  else context.initSphere(input.data.artists);
  return {
    root, win,
    frame() {
      const pending = frames.splice(0);
      assert.equal(pending.length, 1);
      pending[0]();
    }
  };
}

function visibleState(env, mode) {
  if (mode === 'carousel') return env.root.children[0].style.transform;
  return env.root.children.map(tag => tag.style.cssText).join('|');
}

const actual = environment(input.mode);
actual.frame();

actual.root.emit('touchstart', {touches: [{clientX: 100, clientY: 100}]});
actual.win.emit('touchcancel');
let prevented = false;
actual.win.emit('touchmove', {
  touches: [{clientX: 300, clientY: 250}], cancelable: true,
  preventDefault() { prevented = true; }
});

actual.frame();
assert.equal(prevented, false, '中断後のタッチ操作を捕捉しない');
const resumedState = visibleState(actual, input.mode);
actual.frame();
assert.notEqual(visibleState(actual, input.mode), resumedState,
  '中断後は自動回転へ戻る');
"""


def run_touch_cancel_case(mode, script=None):
    result = subprocess.run(
        ["node", "-e", HARNESS],
        input=json.dumps({
            "mode": mode,
            "script": script if script is not None else (ROOT / "script.js").read_text(encoding="utf-8"),
            "data": json.loads((ROOT / "data.json").read_text(encoding="utf-8")),
        }),
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=10,
    )
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize("mode", ["carousel", "sphere"])
def test_touch_cancel_releases_drag(mode):
    run_touch_cancel_case(mode)
