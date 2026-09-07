/* ════════════════════════════
   CAROUSEL
════════════════════════════ */
function escapeHTML(value) {
  return String(value).replace(/[&<>"']/g, char => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;'
  }[char]));
}

function updateCounts(data) {
  document.getElementById('yariCount').textContent = data.yariItems.length;
  document.getElementById('tryCount').textContent = data.tryItems.length;
  document.getElementById('artistCount').textContent = data.artists.length;
  document.getElementById('artistBadge').textContent = `${data.artists.length} artists`;
}

function renderCarouselItem(card, item) {
  const completed = item.completed === true;
  card.classList.toggle('is-complete', completed);
  card.innerHTML = `<span class="cr-ic">${escapeHTML(item.e)}</span><span class="cr-tx">${escapeHTML(item.t)}</span>` +
    (completed ? '<span class="cr-completed">✓ 完了</span>' : '');
}

function initCarousel(wrapId, data) {
  const wrap = document.getElementById(wrapId);
  const n = data.length;
  if (n === 0) return;
  const isMobile = window.innerWidth < 640;
  const cardW = isMobile ? 62 : 85, cardH = isMobile ? 46 : 62;
  const radius = isMobile ? 260 : 600;
  const SLOTS = 24;                        // 常に24枚固定
  const step = 360 / SLOTS;

  const stage = document.createElement('div');
  stage.className = 'cr-stage';
  stage.style.cssText = `width:${cardW}px;height:${cardH}px;`;

  let nextIdx = SLOTS;                     // 次に表示するデータのインデックス

  const cards = Array.from({length: SLOTS}, (_, i) => {
    const it = data[i % n];
    const card = document.createElement('div');
    card.className = 'cr-card';
    card.style.cssText =
      `width:${cardW}px;height:${cardH}px;`+
      `left:${-cardW/2}px;top:${-cardH/2}px;`+
      `transform:rotateY(${step * i}deg) translateZ(${radius}px);`;
    renderCarouselItem(card, it);
    stage.appendChild(card);
    return { el: card, baseAngle: step * i, inBack: false };
  });
  wrap.appendChild(stage);

  const AUTO = 0.04;
  let ang = 0, vel = 0, dragging = false, lastX = 0;

  const onDown = e => { dragging = true; lastX = e.touches ? e.touches[0].clientX : e.clientX; vel = 0; };
  const onMove = e => {
    if (!dragging) return;
    if (e.cancelable) e.preventDefault();
    const x = e.touches ? e.touches[0].clientX : e.clientX;
    const dx = x - lastX;
    vel = dx * 0.15; ang += dx * 0.10; lastX = x;
  };
  const onUp = () => { dragging = false; };

  wrap.addEventListener('mousedown',  onDown);
  wrap.addEventListener('touchstart', onDown, {passive:true});
  window.addEventListener('mousemove',  onMove);
  window.addEventListener('touchmove',  onMove, {passive:false});
  window.addEventListener('mouseup',  onUp);
  window.addEventListener('touchend', onUp);

  (function tick() {
    if (!dragging) {
      if (Math.abs(vel) > 0.05) { ang += vel; vel *= 0.92; }
      else { ang += AUTO; vel = 0; }
    }
    stage.style.transform = `rotateY(${ang}deg)`;
    cards.forEach(c => {
      const eff = ((c.baseAngle + ang) % 360 + 360) % 360;
      c.el.style.opacity = Math.max(0, Math.cos(eff * Math.PI / 180)).toFixed(3);

      // 裏側に入った瞬間にコンテンツを差し替え
      const nowInBack = eff > 90 && eff < 270;
      if (nowInBack && !c.inBack) {
        const it = data[nextIdx % n];
        nextIdx++;
        renderCarouselItem(c.el, it);
      }
      c.inBack = nowInBack;
    });
    requestAnimationFrame(tick);
  })();
}
/* ════════════════════════════
   SPHERE
════════════════════════════ */
function initSphere(artists) {
  const wrap = document.getElementById('sphereWrap');
  if (artists.length === 0) return;

  /* IntersectionObserver で表示されてから起動 */
  const observer = new IntersectionObserver(entries => {
    if (!entries[0].isIntersecting) return;
    observer.disconnect();
    start();
  }, { threshold: 0.1 });
  observer.observe(wrap);

  function start() {
    const W = wrap.clientWidth, H = wrap.clientHeight;
    const R = Math.min(W, H) * 0.36;
    const fov = 600;
    const φ = (1 + Math.sqrt(5)) / 2;

    const pts = artists.map((name, i) => {
      const θ = Math.acos(1 - 2*(i+.5)/artists.length);
      const λ = 2*Math.PI*i/φ;
      return {
        ox: R*Math.sin(θ)*Math.cos(λ),
        oy: R*Math.sin(θ)*Math.sin(λ),
        oz: R*Math.cos(θ),
        name
      };
    });

    const tags = pts.map((p, i) => {
      const hue = Math.round((i / artists.length) * 360);
      const color = `hsl(${hue},70%,72%)`;
      const el = document.createElement('div');
      el.className = 'sp-tag';
      el.textContent = p.name;
      el.addEventListener('click', () => {
        if (dragDist > 5) return;
        window.open(`https://www.google.com/search?q=${encodeURIComponent(p.name + ' ライブ チケット')}`, '_blank');
      });
      el.addEventListener('mouseenter', () => { hoveredEl = el; });
      el.addEventListener('mouseleave', () => { hoveredEl = null; });
      wrap.appendChild(el);
      return {el, ox:p.ox, oy:p.oy, oz:p.oz, color};
    });

    let ay = 0, ax = 0;
    let vy = 0.0018, vx = 0.0004;
    let dragging = false, lastX = 0, lastY = 0, dragDist = 0, hoveredEl = null;

    const onDown = e => {
      dragging = true;
      lastX = e.touches ? e.touches[0].clientX : e.clientX;
      lastY = e.touches ? e.touches[0].clientY : e.clientY;
      dragDist = 0;
      vy = 0; vx = 0;
    };
    const onMove = e => {
      if (!dragging) return;
      if (e.cancelable) e.preventDefault();
      const x = e.touches ? e.touches[0].clientX : e.clientX;
      const y = e.touches ? e.touches[0].clientY : e.clientY;
      dragDist += Math.hypot(x - lastX, y - lastY);
      vy = (x - lastX) * 0.004;
      vx = (y - lastY) * 0.004;
      ay += vy; ax += vx;
      lastX = x; lastY = y;
    };
    const onUp = () => { dragging = false; };

    wrap.addEventListener('mousedown',  onDown);
    wrap.addEventListener('touchstart', onDown, {passive:true});
    window.addEventListener('mousemove',  onMove);
    window.addEventListener('touchmove',  onMove, {passive:false});
    window.addEventListener('mouseup',  onUp);
    window.addEventListener('touchend', onUp);

    (function tick() {
      if (!dragging) {
        vy += (0.0018 - vy) * 0.02;  /* 慣性後にオートに戻る */
        vx += (0.0004 - vx) * 0.02;
      }
      ay += vy; ax += vx;
      const cX=Math.cos(ax), sX=Math.sin(ax);
      const cY=Math.cos(ay), sY=Math.sin(ay);

      const projected = tags.map(({el, ox, oy, oz, color}) => {
        const x1 = ox*cY - oz*sY, z1 = ox*sY + oz*cY;
        const y2 = oy*cX - z1*sX, z2 = oy*sX + z1*cX;
        const s = fov / (fov + z2);
        return {el, px: W/2 + x1*s, py: H/2 + y2*s, s, z: z2};
      });
      projected.sort((a,b) => a.z - b.z);

      projected.forEach(({el, px, py, s, z, color}, i) => {
        const t  = 1 - (z + R) / (2 * R);
        const op = t * t * (3 - 2 * t);
        const hov = el === hoveredEl;
        const fs = (0.6 + s * 0.5) * (hov ? 1.22 : 1);
        el.style.cssText =
          `left:${px}px;top:${py}px;`+
          `transform:translate(-50%,-50%);`+
          `opacity:${(hov ? Math.max(op, 0.95) : op).toFixed(3)};`+
          `font-size:${fs.toFixed(2)}rem;`+
          `color:${hov ? '#fff' : color};`+
          `text-shadow:${hov ? `0 0 16px ${color}, 0 0 5px ${color}` : 'none'};`+
          `z-index:${hov ? 9999 : i};`;
      });
      requestAnimationFrame(tick);
    })();
  }
}

async function init() {
  const response = await fetch('./data.json');
  if (!response.ok) {
    throw new Error(`data.jsonを読み込めませんでした: ${response.status}`);
  }

  const data = await response.json();
  updateCounts(data);
  initCarousel('yariWrap', data.yariItems);
  initCarousel('carouselWrap', data.tryItems);
  initSphere(data.artists);
}

init().catch(error => {
  console.error(error);
  document.getElementById('artistBadge').textContent = 'load error';
});
