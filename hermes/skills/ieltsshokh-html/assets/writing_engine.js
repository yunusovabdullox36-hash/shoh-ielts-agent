/* IELTSSHOKH Writing engine (Reading-template skin). Placeholders are filled by build_writing.py. */
const TEST = __TEST__;
const KIT = __KIT__;
const IC = __ICONS__;
const LOGO = __LOGO__;
const MODES = { full: { parts: [1, 2], secs: 3600 }, t1: { parts: [1], secs: 1200 }, t2: { parts: [2], secs: 2400 } };
const KEY = 'shkh-writing:' + TEST.id;
const $ = s => document.querySelector(s);
const $$ = s => [].slice.call(document.querySelectorAll(s));
const essay = $('#essay'), plan = $('#plan');
let S = null, timerId = null, saveT = null, tHidden = false;

/* ---------- theme (same switch as the Reading test) ---------- */
function toggleDark() {
  const d = !document.body.classList.contains('dark');
  document.body.classList.toggle('dark', d); document.body.classList.toggle('light', !d);
  try { localStorage.setItem('shkh-theme', d ? 'dark' : 'light'); } catch (e) {}
}
try { if (localStorage.getItem('shkh-theme') === 'dark') { document.body.classList.add('dark'); document.body.classList.remove('light'); } } catch (e) {}

/* ---------- state ---------- */
const fresh = (mode, practice) => ({ mode, practice, texts: { 1: '', 2: '' }, plans: { 1: '', 2: '' }, remaining: MODES[mode].secs, spent: { 1: 0, 2: 0 }, current: MODES[mode].parts[0], submitted: false, savedAt: 0 });
function store(o) { try { localStorage.setItem(KEY, JSON.stringify(o)); return true; } catch (e) { return false; } }
function loadStore() { try { return JSON.parse(localStorage.getItem(KEY) || 'null'); } catch (e) { return null; } }
function save() {
  if (!S) return;
  S.texts[S.current] = essay.value; S.plans[S.current] = plan.value; S.savedAt = Date.now();
  if (store(S)) $('#saved-t').textContent = 'Saved ' + new Date().toTimeString().slice(0, 5);
}
function saveSoon() { clearTimeout(saveT); saveT = setTimeout(save, 700); }

/* ---------- text stats ---------- */
const words = t => (t.trim().match(/[A-Za-z0-9'’%-]+/g) || []).length;
const paras = t => t.split(/\n\s*\n|\n/).filter(p => p.trim().length > 0).length;
const sentences = t => (t.match(/[^.!?]+[.!?]+/g) || (t.trim() ? [t] : [])).filter(s => s.trim().split(/\s+/).length > 2).length;
function updateStats() {
  const n = S.current, t = essay.value, w = words(t), min = TEST.tasks[n].min, done = w >= min;
  $('#wc').textContent = w; $('#wmin').textContent = min;
  $('#pc').textContent = paras(t); $('#sc').textContent = sentences(t);
  $('#wbar i').style.width = Math.min(w / min * 100, 100).toFixed(1) + '%'; $('#wbar').classList.toggle('done', done);
  const l = $('#wc-l'); l.textContent = done ? 'Target reached' : (min - w) + ' words to go'; l.classList.toggle('ok', done);
  S.texts[n] = t;
  [1, 2].forEach(p => $('.ptab[data-part="' + p + '"]').classList.toggle('done', words(S.texts[p]) >= TEST.tasks[p].min));
}

/* ---------- timer ---------- */
const fmt = s => String(Math.floor(s / 60)).padStart(2, '0') + ':' + String(s % 60).padStart(2, '0');
function renderTimer() {
  const el = $('#timer');
  if (tHidden) { el.textContent = '••:••'; return; }
  el.textContent = fmt(Math.max(S.remaining, 0));
  el.classList.toggle('warn', S.remaining <= 600 && S.remaining > 300);
  el.classList.toggle('danger', S.remaining <= 300);
  $('#progress-bar').style.width = ((MODES[S.mode].secs - S.remaining) / MODES[S.mode].secs * 100).toFixed(2) + '%';
}
function toggleTimer() { tHidden = !tHidden; renderTimer(); }
function tick() {
  if (S.submitted) return;
  S.remaining--; S.spent[S.current]++; renderTimer();
  if (S.remaining % 5 === 0) save();
  if (S.remaining <= 0) { clearInterval(timerId); submit(true); }
}

/* ---------- parts ---------- */
function switchPart(n) {
  if (!MODES[S.mode].parts.includes(n)) return;
  S.texts[S.current] = essay.value; S.plans[S.current] = plan.value;
  S.current = n;
  $$('.task-view').forEach(v => v.classList.toggle('on', v.id === 'prompt-' + n));
  $('#hd-sub').textContent = 'Academic · Writing Task ' + n + ' · ' + TEST.tasks[n].min + '+ words';
  $$('.ptab').forEach(b => b.classList.toggle('on', +b.dataset.part === n));
  essay.value = S.texts[n] || ''; plan.value = S.plans[n] || '';
  renderKit(); updateStats(); save();
  $('#passage-panel').scrollTop = 0;
}

/* ---------- start / resume ---------- */
let chosenMode = 'full';
$$('.w-mode').forEach(b => b.addEventListener('click', () => { $$('.w-mode').forEach(x => x.classList.remove('on')); b.classList.add('on'); chosenMode = b.dataset.mode; }));
function begin(state) {
  ShkhFS.enter(); ShkhFS.arm(); /* the click is the user gesture the browser requires */
  S = state;
  $('#welcome-overlay').style.display = 'none';
  $$('.ptab').forEach(b => b.classList.toggle('hidden', !MODES[S.mode].parts.includes(+b.dataset.part)));
  $('#kit-btn').classList.toggle('show', !!S.practice);
  const tag = $('#mode-tag'); tag.className = 'w-tag' + (S.practice ? ' prac' : ''); tag.textContent = S.practice ? 'Practice mode' : 'Exam mode';
  const cur = S.current; S.current = MODES[S.mode].parts[0];
  essay.value = S.texts[S.current] || '';
  switchPart(cur); renderTimer();
  timerId = setInterval(tick, 1000);
  essay.focus();
}
function startTest() { begin(fresh(chosenMode, $('#practice').checked)); }
const prev = loadStore();
if (prev && !prev.submitted && prev.remaining > 0 && (prev.texts[1] || prev.texts[2])) {
  const r = $('#resume-btn'); r.classList.remove('hidden'); r.textContent = 'Resume draft, ' + fmt(prev.remaining) + ' left';
  r.addEventListener('click', () => begin(prev));
}

/* ---------- input ---------- */
essay.addEventListener('input', () => { updateStats(); saveSoon(); });
plan.addEventListener('input', saveSoon);
$$('.ptab').forEach(b => b.addEventListener('click', () => switchPart(+b.dataset.part)));
document.addEventListener('keydown', e => {
  if ((e.ctrlKey || e.metaKey) && (e.key === '1' || e.key === '2') && S && !S.submitted) { e.preventDefault(); switchPart(+e.key); }
  if (e.key === 'Escape') { closeKit(); $('#confirm').classList.remove('show'); $('#result-modal').classList.remove('show'); }
});
let fz = 1;
function setFz(v) { fz = Math.min(1.4, Math.max(.85, v)); document.documentElement.style.setProperty('--wfs', fz + 'rem'); }
$('#fs-up').addEventListener('click', () => setFz(fz + .08));
$('#fs-down').addEventListener('click', () => setFz(fz - .08));
(() => { /* resizable divider, same handle as Reading */
  const h = $('#resize-handle'), L = $('#passage-panel'), P = $('#layout'); let on = false;
  h.addEventListener('pointerdown', e => { on = true; h.classList.add('dragging'); h.setPointerCapture(e.pointerId); });
  h.addEventListener('pointermove', e => { if (!on) return; const r = P.getBoundingClientRect(); L.style.flex = '0 0 ' + Math.min(72, Math.max(28, (e.clientX - r.left) / r.width * 100)) + '%'; });
  const stop = () => { on = false; h.classList.remove('dragging'); };
  h.addEventListener('pointerup', stop); h.addEventListener('pointercancel', stop);
})();

/* ---------- toolkit ---------- */
const escA = s => s.replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;');
function renderKit() {
  if (!S) return;
  $('#kit-body').innerHTML = KIT[S.current].map(([g, items]) => '<div class="kit-grp"><h4>' + g + '</h4>' + items.map(([p, h]) =>
    '<button class="chip" data-p="' + escA(p) + '">' + escA(p) + (h ? '<small>' + h + '</small>' : '') + '</button>').join('') + '</div>').join('');
}
$('#kit-body').addEventListener('click', e => {
  const c = e.target.closest('.chip'); if (!c || S.submitted) return;
  const p = c.dataset.p, s = essay.selectionStart, en = essay.selectionEnd, v = essay.value;
  const pre = v.slice(0, s), pad = pre && !/\s$/.test(pre) ? ' ' : '';
  essay.value = pre + pad + p + v.slice(en);
  const pos = (pre + pad + p).length; essay.focus(); essay.setSelectionRange(pos, pos);
  updateStats(); saveSoon();
});
function closeKit() { $('#kit').classList.remove('open'); document.body.classList.remove('kit-open'); }
$('#kit-btn').addEventListener('click', () => { const o = $('#kit').classList.toggle('open'); document.body.classList.toggle('kit-open', o); });
$('#kit-close').addEventListener('click', closeKit);
$$('[data-close]').forEach(b => b.addEventListener('click', () => $('#' + b.dataset.close).classList.remove('show')));

const esc = s => s.replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
/* ---------- submit (two steps: score modal, then review) ---------- */
function askSubmit() {
  if (!S || S.submitted) return;
  save();
  $('#cf-rows').innerHTML = MODES[S.mode].parts.map(p => {
    const w = words(S.texts[p]), ok = w >= TEST.tasks[p].min;
    return '<div class="cf-row"><span>' + TEST.tasks[p].title + '</span><span class="' + (ok ? 'ok' : 'low') + '">' + (ok ? IC.check : IC.warn) + w + ' / ' + TEST.tasks[p].min + '</span></div>';
  }).join('');
  $('#confirm').classList.add('show');
}
$('#cf-yes').addEventListener('click', () => { $('#confirm').classList.remove('show'); submit(false); });
function submit(timeUp) {
  if (S.submitted) return;
  S.texts[S.current] = essay.value; S.plans[S.current] = plan.value;
  S.submitted = true; clearInterval(timerId); store(S);
  essay.disabled = true; plan.disabled = true; closeKit();
  $('#res-h').textContent = timeUp ? 'Time is up. Writing submitted' : 'Writing submitted';
  $('#res-cards').innerHTML = MODES[S.mode].parts.map(p => {
    const w = words(S.texts[p]);
    return '<div class="rb-hero"><div class="rb-hero-band"><div class="rb-hero-score">' + w + '</div><div class="rb-hero-label">' + (w === 1 ? 'word' : 'words') + '</div></div><div class="rb-hero-right"><div class="rb-hero-desc"><b>' + TEST.tasks[p].title + '</b></div><div class="res-meta">Minimum ' + TEST.tasks[p].min + ' words, ' + fmt(S.spent[p]) + ' spent</div></div></div>';
  }).join('');
  $('#result-modal').classList.add('show');
}
function closeResult() { $('#result-modal').classList.remove('show'); }
function reviewAnswers() { closeResult(); openReview(MODES[S.mode].parts[0]); }

/* ---------- review ---------- */
function openReview(n) {
  const task = TEST.tasks[n], txt = S.texts[n] || '', w = words(txt);
  $('#rv-tabs').innerHTML = MODES[S.mode].parts.map(p => '<button class="rv-tab' + (p === n ? ' on' : '') + '" data-p="' + p + '">Task ' + p + '</button>').join('');
  $('#rv-grid').innerHTML =
    '<div class="rv-card"><h3>' + IC.pen + 'Your response<span>' + w + ' words</span></h3><p class="rv-sub">Your teacher will check this.</p>' +
    '<div class="rv-q">' + esc(task.question) + '</div>' +
    '<div class="rv-text">' + (txt.trim() ? esc(txt) : '<span class="empty">Not written</span>') + '</div></div>' +
    '<div class="rv-card"><h3>' + IC.book + 'Band 8.0 model answer</h3><p class="rv-sub">Highlighted phrases are the structures that lift the band.</p>' +
    '<div class="model">' + task.model + '</div>' +
    '<div class="vocab">' + task.vocab.map(([e, u]) => '<div><b>' + esc(e) + '</b><span>' + esc(u) + '</span></div>').join('') + '</div></div>';
  $('#review').classList.add('show'); $('#review').scrollTop = 0;
  $$('#rv-tabs .rv-tab').forEach(b => b.addEventListener('click', () => openReview(+b.dataset.p)));
}
$('#rv-close').addEventListener('click', () => $('#review').classList.remove('show'));
$('#rv-new').addEventListener('click', () => { try { localStorage.removeItem(KEY); } catch (e) {} location.reload(); });

/* ---------- PDF (white page, centred sh|kh mark, black type, thin grey rules: same style as the IELTSSHOKH Grammar Level Test PDF) ---------- */
function logoInfo() {
  return new Promise(res => {
    const img = new Image();
    img.onload = () => res({ src: LOGO, w: img.naturalWidth, h: img.naturalHeight });
    img.onerror = () => res(null);
    img.src = LOGO;
  });
}
const pdfSafe = s => (s || '').replace(/[‘’]/g, "'").replace(/[“”]/g, '"').replace(/[–—]/g, '-').replace(/…/g, '...').replace(/[^\x09\x0A\x0D\x20-\x7E\xA0-\xFF]/g, '');
const stripTags = h => h.replace(/<\/p>\s*<p>/g, '\n\n').replace(/<[^>]+>/g, '');
async function downloadPDF() {
  if (!S) return;
  const name = 'IELTSSHOKH_' + TEST.label.replace(/\s+/g, '_') + '_' + new Date().toISOString().slice(0, 10);
  const written = p => (S.texts[p] || '').trim() ? S.texts[p] : 'Not written';
  if (!window.jspdf) {
    const body = MODES[S.mode].parts.map(p => TEST.tasks[p].title + '\n' + TEST.tasks[p].question + '\n\n' + written(p)).join('\n\n------\n\n');
    const a = document.createElement('a'); a.href = URL.createObjectURL(new Blob([body], { type: 'text/plain' })); a.download = name + '.txt'; a.click(); return;
  }
  const { jsPDF } = window.jspdf, doc = new jsPDF({ unit: 'mm', format: 'a4', compress: true }), logo = await logoInfo();
  const INK = [20, 20, 20], MUTE = [110, 110, 110], RULE = [200, 200, 200];
  let y = 0;
  const head = () => {
    if (logo) { const h = 15, w = h * logo.w / logo.h; doc.addImage(logo.src, 'PNG', 105 - w / 2, 8, w, h, 'shkh-logo'); }
    doc.setDrawColor.apply(doc, RULE); doc.setLineWidth(0.25); doc.line(20, 26, 190, 26);
    y = 38;
  };
  const page = () => { doc.addPage(); head(); };
  const need = h => { if (y + h > 276) page(); };
  const h1 = t => { need(14); doc.setTextColor.apply(doc, INK); doc.setFont('helvetica', 'bold'); doc.setFontSize(14); doc.text(t, 20, y); y += 8; };
  const label = t => { need(9); doc.setTextColor.apply(doc, MUTE); doc.setFont('helvetica', 'bold'); doc.setFontSize(8.5); doc.text(t.toUpperCase(), 20, y); y += 5.5; };
  const para = (t, size, style, color) => {
    doc.setFont('helvetica', style || 'normal'); doc.setFontSize(size || 11); doc.setTextColor.apply(doc, color || INK);
    pdfSafe(t).split(/\n/).forEach(line => {
      if (!line.trim()) { y += 3; return; }
      doc.splitTextToSize(line, 170).forEach(l => { need(6); doc.text(l, 20, y); y += (size || 11) * 0.5; });
    });
    y += 3;
  };
  head();
  doc.setTextColor.apply(doc, INK); doc.setFont('helvetica', 'bold'); doc.setFontSize(20); doc.text(TEST.label.toUpperCase(), 105, y, { align: 'center' }); y += 8;
  doc.setFont('helvetica', 'italic'); doc.setFontSize(10); doc.setTextColor.apply(doc, MUTE);
  doc.text('Academic Writing  -  ' + ({ full: 'Full test', t1: 'Task 1 only', t2: 'Task 2 only' }[S.mode]) + (S.practice ? ' (practice)' : ' (exam)'), 105, y, { align: 'center' }); y += 6;
  doc.setFont('helvetica', 'bold'); doc.setTextColor.apply(doc, INK);
  doc.text(MODES[S.mode].parts.length + (MODES[S.mode].parts.length > 1 ? ' tasks' : ' task') + '  -  ' + MODES[S.mode].secs / 60 + ' minutes', 105, y, { align: 'center' }); y += 8;
  doc.setDrawColor.apply(doc, INK); doc.setLineWidth(0.3); doc.rect(20, y, 170, 12);
  doc.setFont('helvetica', 'normal'); doc.setFontSize(10);
  doc.text('Name: ______________________', 25, y + 7.5); doc.text('Date: ' + new Date().toLocaleDateString('en-GB'), 105, y + 7.5);
  doc.text('Time used: ' + fmt(MODES[S.mode].secs - S.remaining), 150, y + 7.5); y += 22;
  MODES[S.mode].parts.forEach((p, i) => {
    if (i > 0) page();
    const t = TEST.tasks[p], w = words(S.texts[p] || '');
    h1(t.title.toUpperCase());
    label('Question'); para(t.question, 10.5, 'italic', MUTE);
    label('Words: ' + w + ' / ' + t.min + '    Time used: ' + fmt(S.spent[p]));
    y += 2; label('Your response'); para(written(p), 11);
  });
  MODES[S.mode].parts.forEach(p => {
    page(); const t = TEST.tasks[p];
    h1('BAND 8.0 MODEL: TASK ' + p); para(stripTags(t.model), 11);
    label('Key vocabulary'); t.vocab.forEach(([e, u]) => { para(e + ': ' + u, 10); y -= 1.5; });
  });
  const N = doc.getNumberOfPages();
  for (let i = 1; i <= N; i++) {
    doc.setPage(i); doc.setDrawColor.apply(doc, RULE); doc.setLineWidth(0.25); doc.line(20, 284, 190, 284);
    doc.setFont('helvetica', 'normal'); doc.setFontSize(8.5); doc.setTextColor.apply(doc, MUTE);
    doc.text('t.me/ieltsshokh', 20, 289); doc.text('IELTSSHOKH', 105, 289, { align: 'center' }); doc.text('Page ' + i, 190, 289, { align: 'right' });
  }
  doc.save(name + '.pdf');
}
$('#pdf-btn').addEventListener('click', downloadPDF);
