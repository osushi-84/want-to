"""実際の JavaScript で、リサイズ後の描画と操作状態を検証する。"""

import json
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]
HARNESS = r"""
const assert = require('node:assert/strict');
const vm = require('node:vm');
const input = JSON.parse(require('node:fs').readFileSync(0, 'utf8'));

function element() {
  let values = {};
  const property = name => name.replace(/[A-Z]/g, c => '-' + c.toLowerCase());
  const style = new Proxy({}, {
    get(_, key) {
      return key === 'cssText' ? Object.entries(values).map(([k,v]) => `${k}:${v}`).join(';') : values[property(key)] || '';
    },
    set(_, key, value) {
      if (key === 'cssText') {
        values = Object.fromEntries(value.split(';').filter(s => s.includes(':')).map(s => {
          const colon = s.indexOf(':');
          return [s.slice(0, colon).trim(), s.slice(colon + 1).trim()];
        }));
      } else values[property(key)] = String(value);
      return true;
    }
  });
  return {
    style, children: [], events: {}, innerHTML: '', textContent: '',
    classList: {toggle() {}},
    appendChild(child) { this.children.push(child); },
    addEventListener(name, fn) { (this.events[name] ||= []).push(fn); },
    emit(name, event = {}) { (this.events[name] || []).forEach(fn => fn(event)); }
  };
}

function environment(width, height, mode = 'sphere') {
  const root = element(), win = element(), frames = [], observers = [];
  Object.assign(root, {clientWidth: width, clientHeight: height});
  win.innerWidth = width;
  const context = vm.createContext({
    fetch: () => new Promise(() => {}), window: win,
    document: {getElementById: () => root, createElement: element},
    requestAnimationFrame: fn => frames.push(fn),
    IntersectionObserver: class {
      constructor(fn) { this.fn = fn; }
      observe(target) { this.fn([{target, isIntersecting: true}]); }
      disconnect() {}
    },
    ResizeObserver: class {
      constructor(fn) { this.fn = fn; observers.push(this); }
      observe(target) { this.target = target; }
    }
  });
  vm.runInContext(input.script, context);
  if (mode === 'sphere') context.initSphere(input.data.artists);
  else context.initCarousel('carouselWrap', input.data.tryItems);
  return {
    root, win,
    frame() {
      const pending = frames.splice(0);
      assert.equal(pending.length, 1, 'リサイズで描画ループが増減しない');
      pending.forEach(fn => fn());
    },
    resize(w, h, viewport) {
      Object.assign(root, {clientWidth: w, clientHeight: h});
      if (viewport !== undefined) { win.innerWidth = viewport; win.emit('resize'); }
      observers.forEach(observer => observer.fn([{
        target: observer.target, contentRect: {width: w, height: h}
      }]));
    }
  };
}

const hold = env => env.root.emit('mousedown', {clientX: 100, clientY: 100});
function rotateAndHold(env) {
  for (let i = 0; i < 20; i++) env.frame();
  hold(env);
  env.win.emit('mousemove', {clientX: 180, clientY: 140, cancelable: true, preventDefault() {}});
  env.frame();
  hold(env);
}
function sameSphere(actual, expected) {
  assert.equal(actual.root.children.length, expected.root.children.length);
  actual.root.children.forEach((tag, i) => {
    assert.equal(tag.textContent, expected.root.children[i].textContent);
    for (const name of ['left', 'top', 'fontSize', 'opacity', 'zIndex']) {
      const a = parseFloat(tag.style[name]), b = parseFloat(expected.root.children[i].style[name]);
      assert(Number.isFinite(a) && Number.isFinite(b));
      assert(Math.abs(a - b) < 1e-8, `${name}: ${a} != ${b}`);
    }
  });
}

if (input.case === 'sphere') {
  for (const [width, height] of [[320, 520], [520, 960], [960, 280]]) {
    const actual = environment(960, 520), expected = environment(width, height);
    [actual, expected].forEach(env => {
      rotateAndHold(env);
      env.root.children[0].emit('mouseenter');
    });
    const tags = [...actual.root.children];
    actual.resize(width, height); // window resize を伴わないコンテナ変更も対象。
    actual.frame(); expected.frame();
    tags.forEach((tag, i) => assert.equal(actual.root.children[i], tag));
    sameSphere(actual, expected);
    assert.equal(actual.root.children[0].style.zIndex, '9999');
    [actual, expected].forEach(env => {
      env.root.children[0].emit('mouseleave');
      env.win.emit('mouseup');
      env.frame();
    });
    sameSphere(actual, expected);
  }
} else if (input.case === 'zero') {
  const actual = environment(0, 0), expected = environment(640, 360);
  const tags = [...actual.root.children];
  for (let i = 0; i < 3; i++) actual.frame();
  tags.forEach(tag => assert(!/NaN|Infinity/.test(tag.style.cssText)));
  actual.resize(640, 360); actual.frame();
  sameSphere(actual, expected);
  [actual, expected].forEach(hold);
  for (const [width, height] of [[0, 360], [640, 0], [0, 0]]) {
    const styles = tags.map(tag => tag.style.cssText);
    actual.resize(width, height);
    for (let i = 0; i < 3; i++) actual.frame();
    assert.deepEqual(tags.map(tag => tag.style.cssText), styles);
    actual.resize(640, 360); actual.frame(); expected.frame();
    tags.forEach((tag, i) => assert.equal(actual.root.children[i], tag));
    sameSphere(actual, expected);
  }
} else if (input.case === 'carousel') {
  const actual = environment(1024, 520, 'carousel');
  rotateAndHold(actual);
  const stage = actual.root.children[0], cards = [...stage.children];
  const contents = cards.map(card => card.innerHTML), angle = stage.style.transform, widths = {};
  for (const width of [640, 639, 641, 640, 1024]) {
    const expected = environment(width, 520, 'carousel');
    rotateAndHold(expected);
    actual.resize(width, 520, width); actual.frame(); expected.frame();
    assert.equal(actual.root.children.length, 1);
    assert.equal(actual.root.children[0], stage);
    assert.equal(stage.children.length, cards.length);
    assert.equal(stage.style.transform, angle);
    assert.deepEqual(cards.map(card => card.innerHTML), contents);
    for (const name of ['width', 'height', 'transform']) {
      assert.equal(stage.style[name], expected.root.children[0].style[name]);
    }
    cards.forEach((card, i) => {
      assert.equal(stage.children[i], card);
      for (const name of ['width', 'height', 'left', 'top', 'transform', 'opacity']) {
        assert.equal(card.style[name], expected.root.children[0].children[i].style[name]);
      }
    });
    widths[width] = cards[0].style.width;
  }
  assert.equal(widths[640], widths[639], '640 px はモバイル側に含める');
  assert.notEqual(widths[641], widths[640]);
}
"""


def run_resize_case(case, script=None):
    result = subprocess.run(
        ["node", "-e", HARNESS],
        input=json.dumps({
            "case": case,
            "script": script if script is not None else (ROOT / "script.js").read_text(encoding="utf-8"),
            "data": json.loads((ROOT / "data.json").read_text(encoding="utf-8")),
        }),
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=10,
    )
    assert result.returncode == 0, result.stderr


def test_sphere_resize_preserves_geometry_and_interaction():
    run_resize_case("sphere")


def test_sphere_recovers_from_zero_dimensions():
    run_resize_case("zero")


def test_carousel_resize_preserves_cards_and_rotation_at_mobile_boundary():
    run_resize_case("carousel")
