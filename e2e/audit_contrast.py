"""
Auditoría de contraste (WCAG) de pantallas, en modo claro u oscuro y con sesión opcional.

Uso:  python e2e/audit_contrast.py <light|dark> <email|-> <ruta1,ruta2,...> [shots]
Ej.:  python e2e/audit_contrast.py light admin@test.co /admin,/admin/reservas shots
"""

import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

theme, email, paths = sys.argv[1], sys.argv[2], sys.argv[3].split(",")
shots = len(sys.argv) > 4 and sys.argv[4] == "shots"
OUT = Path(__file__).parent / "out"
OUT.mkdir(exist_ok=True)

JS = r"""
() => {
  const parse = c => { const m = c.match(/rgba?\(([^)]+)\)/); if(!m) return null; const p = m[1].split(',').map(parseFloat); return {r:p[0],g:p[1],b:p[2],a:p.length>3?p[3]:1}; };
  const lum = c => { const f = v => { v/=255; return v<=0.03928? v/12.92 : Math.pow((v+0.055)/1.055,2.4); }; return 0.2126*f(c.r)+0.7152*f(c.g)+0.0722*f(c.b); };
  const bgOf = el => {
    const layers = [];
    for (let n = el; n; n = n.parentElement) {
      const cs = getComputedStyle(n); const c = parse(cs.backgroundColor);
      if (cs.backgroundImage !== 'none' && !cs.backgroundImage.startsWith('url(')) return {complex:true};
      if (c && c.a > 0) { layers.push(c); if (c.a >= 0.99) break; }
    }
    let base = {r:255,g:255,b:255};
    for (let i = layers.length-1; i>=0; i--) { const l = layers[i]; base = {r:l.r*l.a+base.r*(1-l.a), g:l.g*l.a+base.g*(1-l.a), b:l.b*l.a+base.b*(1-l.a)}; }
    return base;
  };
  const res = {};
  document.querySelectorAll('body *').forEach(el => {
    const hasText = [...el.childNodes].some(n => n.nodeType===3 && n.textContent.trim().length>0);
    if (!hasText) return;
    const cs = getComputedStyle(el);
    if (cs.visibility==='hidden' || cs.display==='none' || parseFloat(cs.opacity)===0) return;
    const r = el.getBoundingClientRect(); if (r.width===0||r.height===0) return;
    const clip = cs.webkitTextFillColor === 'rgba(0, 0, 0, 0)' || cs.color === 'rgba(0, 0, 0, 0)';
    if (clip) return;                      // texto con degradado (background-clip:text)
    const fg = parse(cs.color); const bg = bgOf(el); if (!fg || bg.complex) return;
    const L1 = lum(fg), L2 = lum(bg); const ratio = (Math.max(L1,L2)+0.05)/(Math.min(L1,L2)+0.05);
    if (ratio < 3) {
      let chain = [], n = el; for (let i=0; i<3 && n && n.tagName!=='BODY'; i++, n = n.parentElement) chain.push(n.tagName.toLowerCase() + (typeof n.className==='string' && n.className ? '.' + n.className.split(' ').filter(c=>c && !c.startsWith('ng-')).slice(0,2).join('.') : ''));
      const key = chain.join(' < ');
      res[key] = res[key] || {n:0, ratio: ratio.toFixed(2), fg: cs.color, bg: `rgb(${Math.round(bg.r)},${Math.round(bg.g)},${Math.round(bg.b)})`, text: el.textContent.trim().slice(0,28)};
      res[key].n++;
    }
  });
  return res;
}
"""

with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={"width": 1366, "height": 900})
    ctx.add_init_script(f"localStorage.setItem('barbergo-theme','{theme}')")
    pg = ctx.new_page()
    if email != "-":
        pg.goto("http://localhost:4200/login", wait_until="networkidle")
        pg.fill("#email", email)
        pg.fill("#password", "Password123!")
        pg.click("button.auth-submit")
        pg.wait_for_function("() => !location.pathname.startsWith('/login')")
    total = 0
    for path in paths:
        pg.goto("http://localhost:4200" + path, wait_until="networkidle")
        time.sleep(1.8)
        for y in range(0, 5000, 600):
            pg.mouse.wheel(0, 600)
            time.sleep(0.1)
        pg.evaluate("window.scrollTo(0,0)")
        time.sleep(0.6)
        r = pg.evaluate(JS)
        total += len(r)
        print(f"== [{theme}] {path}: {len(r)} grupos con bajo contraste")
        for k, v in sorted(r.items(), key=lambda x: -x[1]["n"])[:14]:
            print(f"   x{v['n']:<3} {v['ratio']:>5}  {k}  fg={v['fg']} bg={v['bg']}  «{v['text']}»")
        if shots:
            pg.screenshot(path=str(OUT / f"audit_{theme}_{path.strip('/').replace('/', '_') or 'home'}.png"), full_page=True)
    b.close()
print("TOTAL grupos:", total)
