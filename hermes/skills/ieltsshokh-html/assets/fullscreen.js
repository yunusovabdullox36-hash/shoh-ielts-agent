/* IELTSSHOKH full screen module (shared by Reading and Writing).
   Same look as F11 (no tabs, no address bar) in Chrome and Edge, via the Fullscreen API.
   - ShkhFS.enter() must run inside a click handler (browser rule: needs a user gesture).
   - ShkhFS.arm() after the test starts: if full screen is lost, a small "Return to full screen" pill appears.
   - F11 is NOT intercepted: the browser's own F11 always works (Chrome and Edge), the header button uses the API.
   - Esc is locked while in API full screen where supported (hold Esc to leave), so an accidental Esc does not leave the exam.
   Buttons: any element with [data-shkh-fs]. Body gets class is-fs while in full screen. */
(function () {
  var d = document, de = d.documentElement, armed = false, toast = null, pendingUntil = 0, noteT = 0;
  var el = function () { return d.fullscreenElement || d.webkitFullscreenElement || null; };
  var can = !!(d.fullscreenEnabled || d.webkitFullscreenEnabled);
  /* browser F11 fullscreen: Chrome/Edge/Firefox report display-mode: fullscreen */
  function nativeFS() { try { return matchMedia('(display-mode: fullscreen)').matches; } catch (e) { return false; } }
  var on = function () { return !!el() || nativeFS(); };
  function lockEsc() { try { navigator.keyboard && navigator.keyboard.lock && navigator.keyboard.lock(['Escape']).catch(function () {}); } catch (e) {} }
  function unlockEsc() { try { navigator.keyboard && navigator.keyboard.unlock && navigator.keyboard.unlock(); } catch (e) {} }
  function enter() {
    if (!can || el()) return;
    var f = de.requestFullscreen || de.webkitRequestFullscreen;
    pendingUntil = Date.now() + 2000; /* do not flash the pill while the browser is switching */
    try {
      var p = f.call(de, { navigationUI: 'hide' });
      if (p && p.then) p.then(lockEsc, fail); else lockEsc();
    } catch (e) { fail(e); }
  }
  function fail(e) { pendingUntil = 0; showToast('The browser blocked full screen' + (e && e.message ? ' (' + e.message + ')' : '') + '. Press F11 instead.'); }
  function exit() {
    unlockEsc();
    var x = d.exitFullscreen || d.webkitExitFullscreen;
    if (el() && x) { try { var p = x.call(d); if (p && p.catch) p.catch(function () {}); } catch (e) {} }
  }
  function toggle() {
    if (el()) { exit(); if (nativeFS()) note('Browser full screen is still on. Press F11 to leave it.'); }
    else if (nativeFS()) note('You are in browser full screen. Press F11 to leave it.');
    else enter();
  }
  function hideToast() { if (toast) { toast.remove(); toast = null; } }
  function showToast(msg) {
    if (!armed || !can) return;
    if (!msg && (on() || Date.now() < pendingUntil)) return;
    if (!toast) {
      toast = d.createElement('div'); toast.className = 'shkh-fs-toast'; toast.setAttribute('role', 'status');
      toast.innerHTML = '<span></span><button type="button" data-act="go">Return to full screen</button><button type="button" data-act="no" aria-label="Dismiss">&times;</button>';
      toast.addEventListener('click', function (e) {
        var a = e.target.closest('button'); if (!a) return;
        if (a.dataset.act === 'go') { enter(); }
        hideToast();
      });
      d.body.appendChild(toast);
    }
    toast.firstChild.textContent = msg || 'Full screen is off';
  }
  function note(msg) {
    var n = d.createElement('div'); n.className = 'shkh-fs-toast'; n.setAttribute('role', 'status'); n.innerHTML = '<span></span>';
    n.firstChild.textContent = msg; n.style.paddingRight = '16px'; d.body.appendChild(n);
    clearTimeout(noteT); noteT = setTimeout(function () { n.remove(); }, 3500);
  }
  function paint() {
    var f = on();
    d.body.classList.toggle('is-fs', f);
    [].forEach.call(d.querySelectorAll('[data-shkh-fs]'), function (b) {
      b.hidden = !can;
      var t = f ? 'Exit full screen (F11)' : 'Full screen (F11)';
      b.title = t; b.setAttribute('aria-label', t); b.setAttribute('aria-pressed', f ? 'true' : 'false');
    });
    if (f) { pendingUntil = 0; hideToast(); } else if (armed) showToast();
  }
  d.addEventListener('click', function (e) { var b = e.target.closest && e.target.closest('[data-shkh-fs]'); if (b) toggle(); });
  ['fullscreenchange', 'webkitfullscreenchange'].forEach(function (ev) { d.addEventListener(ev, function () { if (!el()) unlockEsc(); paint(); }); });
  addEventListener('resize', paint);
  if (d.readyState === 'loading') d.addEventListener('DOMContentLoaded', paint); else paint();
  window.ShkhFS = { enter: enter, exit: exit, toggle: toggle, isOn: on, arm: function () { armed = true; setTimeout(paint, 2200); } };
})();
