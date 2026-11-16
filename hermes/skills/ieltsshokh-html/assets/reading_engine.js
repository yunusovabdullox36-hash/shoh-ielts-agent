/* ================= DATA (filled by build_reading.py) ================= */
const ANS = __ANS__;
const ACCEPT = __ACCEPT__;
const QNUMS = __QNUMS__;
const GROUPS = __GROUPS__;
const PAIR = __PAIR__;      // first number of each "choose TWO" card -> "A,D"
const KW = __KW__;
const FB = __FB__;
const ICON = __ICONS__;
const TYPE = {};
const responses = {};
let submitted = false;
const groupOf = n => GROUPS.findIndex(g => n >= g[0] && n <= g[1]);
const pairKey = n => { for (const k in PAIR){ const a=+k, c=PAIR[k].split(',').length; if(n>=a && n<a+c) return a; } return null; };   // choose TWO / THREE cards
function cardFor(n){ return document.querySelector('.q-card[data-qs~="'+n+'"]') || document.querySelector('.q-card[data-q="'+n+'"]'); }

/* ================= INIT ================= */
document.querySelectorAll('.q-card').forEach(c=>{
  (c.dataset.qs ? c.dataset.qs.split(' ') : [c.dataset.q]).forEach(q=>{ TYPE[q]=c.dataset.type; });
});
document.querySelectorAll('.tfng-btn,.multi-opt,.chip-opt,.mc-opt').forEach(el=>{
  el.addEventListener('keydown',e=>{ if(e.key==='Enter'||e.key===' '){ e.preventDefault(); el.click(); } });
});
function wasHighlighting(){ return window.getSelection().toString().trim().length>0; }
// single-choice: paragraph/person matching chips and MCQ options
[['chip','.chip-opt'],['mc','.mc-opt']].forEach(([type,sel])=>{
  document.querySelectorAll('.q-card[data-type="'+type+'"]').forEach(card=>{
    card.querySelectorAll(sel).forEach(opt=>{
      opt.addEventListener('click',()=>{
        if(submitted||wasHighlighting()) return;
        card.querySelectorAll(sel).forEach(o=>o.classList.remove('selected'));
        opt.classList.add('selected');
        responses[card.dataset.q]=opt.dataset.opt;
        updateState();
      });
    });
  });
});
// choose TWO
document.querySelectorAll('.q-card[data-type="multi"]').forEach(card=>{
  card.querySelectorAll('.multi-opt').forEach(opt=>{
    opt.addEventListener('click',()=>{
      if(submitted||wasHighlighting()) return;
      const already=opt.classList.contains('selected');
      if(!already && card.querySelectorAll('.multi-opt.selected').length>=(+card.dataset.n||2)) return;
      opt.classList.toggle('selected');
      const picked=[...card.querySelectorAll('.multi-opt.selected')].map(o=>o.dataset.opt).sort();
      if(picked.length) responses[card.dataset.q]=picked.join(','); else delete responses[card.dataset.q];
      updateState();
    });
  });
});
// TRUE/FALSE/NOT GIVEN and YES/NO/NOT GIVEN
document.querySelectorAll('.q-card[data-type="tfng"]').forEach(card=>{
  card.querySelectorAll('.tfng-btn').forEach(btn=>{
    btn.addEventListener('click',()=>{
      if(submitted) return;
      card.querySelectorAll('.tfng-btn').forEach(b=>b.classList.remove('sel-t','sel-f','sel-ng'));
      const v=btn.dataset.val;
      btn.classList.add((v==='TRUE'||v==='YES')?'sel-t':(v==='FALSE'||v==='NO')?'sel-f':'sel-ng');
      responses[card.dataset.q]=v;
      updateState();
    });
  });
});
// gap fill
document.querySelectorAll('.q-card[data-type="text"]').forEach(card=>{
  const inp=card.querySelector('.ti-input');
  inp.addEventListener('input',()=>{
    if(submitted) return;
    if(inp.value.trim()) responses[card.dataset.q]=inp.value; else delete responses[card.dataset.q];
    updateState();
  });
  inp.addEventListener('keydown',e=>{ if(e.key==='Enter') e.preventDefault(); });
});

/* ================= FOOTER / NAV ================= */
const ftc=document.getElementById('ft-center');
QNUMS.forEach(n=>{
  const p=document.createElement('button');
  p.className='fpill'; p.textContent=n; p.dataset.q=n;
  p.onclick=()=>scrollToQ(n);
  ftc.appendChild(p);
});
let curIdx=0, curP=0;
function setPassage(i){
  curP=i;
  document.querySelectorAll('.psec').forEach((e,k)=>e.classList.toggle('on',k===i));
  document.querySelectorAll('.qgroup').forEach((e,k)=>e.classList.toggle('on',k===i));
  document.querySelectorAll('.ptab').forEach((e,k)=>e.classList.toggle('on',k===i));
  document.querySelectorAll('.fpill').forEach(p=>{ p.style.display = groupOf(+p.dataset.q)===i ? '' : 'none'; });
  document.getElementById('passage-panel').scrollTop=0;
  document.getElementById('questions-panel').scrollTop=0;
  if(groupOf(QNUMS[curIdx])!==i) curIdx=QNUMS.indexOf(GROUPS[i][0]);
  markActive();
}
function scrollToQ(n){
  if(groupOf(n)!==curP) setPassage(groupOf(n));
  curIdx=QNUMS.indexOf(n);
  const card=cardFor(n);
  if(card) card.scrollIntoView({behavior:'smooth',block:'center'});
  markActive();
}
function navQ(d){ curIdx=Math.max(0,Math.min(QNUMS.length-1,curIdx+d)); scrollToQ(QNUMS[curIdx]); }
function markActive(){
  document.querySelectorAll('.fpill').forEach(p=>p.classList.toggle('active',+p.dataset.q===QNUMS[curIdx]));
  document.getElementById('nav-prev').disabled=curIdx===0;
  document.getElementById('nav-next').disabled=curIdx===QNUMS.length-1;
}
function isAnswered(n){
  const pk=pairKey(n);
  if(pk!==null){ const r=responses[pk]; const len=r?r.split(',').length:0; return len>=(n-pk+1); }
  return responses[n]!==undefined;
}
function updateState(){
  let ans=0;
  QNUMS.forEach(n=>{
    const p=document.querySelector('.fpill[data-q="'+n+'"]');
    if(isAnswered(n)){ p.classList.add('answered'); ans++; } else p.classList.remove('answered');
  });
  document.getElementById('progress-bar').style.width=(ans/QNUMS.length*100)+'%';
}

/* ================= TIMER ================= */
let secs=__MINUTES__*60, tInt=null, tHidden=false;
function startTimer(){
  tInt=setInterval(()=>{ secs--; renderTimer(); if(secs<=0){ clearInterval(tInt); if(!submitted) doSubmit(); } },1000);
}
function renderTimer(){
  const el=document.getElementById('timer');
  if(tHidden){ el.textContent='••:••'; return; }
  const m=Math.floor(secs/60), s=secs%60;
  el.textContent=(m<10?'0':'')+m+':'+(s<10?'0':'')+s;
  el.classList.toggle('warn',secs<=300&&secs>60);
  el.classList.toggle('danger',secs<=60);
}
function toggleTimer(){ tHidden=!tHidden; renderTimer(); }
/* full screen: see fullscreen.js (ShkhFS); Start click is the user gesture the browser requires */
function startTest(){ ShkhFS.enter(); ShkhFS.arm(); document.getElementById('welcome-overlay').style.display='none'; startTimer(); markActive(); }
function toggleDark(){ document.body.classList.toggle('dark'); document.body.classList.toggle('light'); }

__HL__
/* ================= GRADING ================= */
function grade(n){
  const pk=pairKey(n);
  if(pk!==null){
    const user=responses[pk]?responses[pk].split(','):[];
    const right=PAIR[pk].split(',');
    const hits=user.filter(x=>right.indexOf(x)>=0).length;
    let state;
    const idx=n-pk;   // i-th question of the card is right when at least i+1 picks are right (total = number of right picks)
    state=user.length<=idx?'skipped':(hits>=idx+1?'correct':'wrong');
    return {user:user.length?user.join(', '):undefined, ok:state==='correct', state};
  }
  const user=responses[n];
  const ok = TYPE[n]==='text' ? (user!==undefined && ACCEPT[n].indexOf(String(user).trim().toLowerCase().replace(/\s+/g,' '))>=0) : user===ANS[n];
  return {user, ok, state: user===undefined?'skipped':(ok?'correct':'wrong')};
}

/* ================= SUBMIT ================= */
function askSubmit(){
  const un=QNUMS.filter(n=>!isAnswered(n)).length;
  if(confirm(un>0?('You have '+un+' unanswered question(s). Submit anyway?'):'Submit your answers?')) doSubmit();
}
function doSubmit(){
  if(submitted) return;
  submitted=true; clearInterval(tInt);
  let cor=0,wr=0,sk=0; const per=GROUPS.map(()=>0);
  QNUMS.forEach(n=>{
    const g=grade(n);
    if(g.state==='correct'){ cor++; per[groupOf(n)]++; } else if(g.state==='wrong') wr++; else sk++;
    const p=document.querySelector('.fpill[data-q="'+n+'"]');
    p.classList.remove('answered');
    p.classList.add(g.state==='correct'?'correct':g.state==='wrong'?'wrong':'skipped-pill');
    document.querySelectorAll('.ans-ev[data-q="'+n+'"]').forEach(sp=>{
      sp.classList.add('hl-answer');
      const tag=document.createElement('span'); tag.className='hl-qtag'; tag.textContent=n;
      sp.parentNode.insertBefore(tag,sp);
    });
  });
  document.querySelectorAll('.q-card').forEach(card=>{
    const n=+card.dataset.q;
    if(TYPE[n]==='multi'){
      const gs=PAIR[n].split(',').map((_,i)=>grade(n+i));
      const cls=gs.every(g=>g.ok)?'correct':(gs[0].state==='skipped'?'skipped':'wrong');
      card.classList.add(cls); revealMulti(card,n,cls);
    }else{
      const g=grade(n);
      card.classList.add(g.state); revealCard(card,n,g.user,ANS[n],g.state);
    }
  });
  document.querySelectorAll('.ti-input').forEach(el=>el.disabled=true);
  document.querySelectorAll('.chip-opt,.multi-opt,.mc-opt').forEach(el=>el.classList.add('disabled'));
  document.querySelectorAll('.tfng-btn').forEach(el=>el.disabled=true);
  buildAnalysis();
  showResult(cor,wr,sk,per);
}
function revealMulti(card,n,cls){
  const right=PAIR[n].split(','); const user=responses[n]?responses[n].split(','):[];
  card.querySelectorAll('.multi-opt').forEach(o=>{
    if(right.indexOf(o.dataset.opt)>=0) o.classList.add('correct-opt');
    else if(user.indexOf(o.dataset.opt)>=0) o.classList.add('wrong-opt');
  });
  const m=document.createElement('div'); m.className='q-result-tag '+cls; m.style.marginTop='10px';
  m.textContent = cls==='correct' ? 'Correct — '+right.join(', ') : (user.length?'Your answer: '+user.join(', ')+' · Correct: '+right.join(', '):'Skipped — answer: '+right.join(', '));
  card.appendChild(m);
}
function revealCard(card,n,user,right,cls){
  const type=TYPE[n];
  const tag=document.createElement('span');
  tag.className='q-result-tag '+cls;
  tag.textContent = cls==='correct'?'Correct':cls==='skipped'?'Skipped — answer: '+right:'Your answer: '+user+' · Correct: '+right;
  if(type==='text'){
    const inp=card.querySelector('.ti-input'); if(inp) inp.classList.add(cls);
    if(cls!=='correct'){ const fix=document.createElement('span'); fix.className='ti-fix'; fix.innerHTML=ICON.check+right; card.appendChild(fix); }
  }else if(type==='chip'||type==='mc'){
    const sel=type==='chip'?'.chip-opt':'.mc-opt';
    card.querySelectorAll(sel).forEach(o=>{
      if(o.dataset.opt===right) o.classList.add('correct-opt');
      if(o.dataset.opt===user && user!==right) o.classList.add('wrong-opt');
    });
    if(type==='chip'){ tag.style.marginLeft='4px'; card.querySelector('.q-row-chip').appendChild(tag); }
    else card.querySelector('.q-row').appendChild(tag);
  }else if(type==='tfng'){
    card.querySelectorAll('.tfng-btn').forEach(o=>{
      if(o.dataset.val===right) o.classList.add('correct-mark');
      if(o.dataset.val===user && user!==right) o.classList.add('wrong-mark');
    });
    card.querySelector('.q-row').appendChild(tag);
  }
}

/* ================= RESULT MODAL ================= */
function bandOf(c){
  const t=[[39,9],[37,8.5],[35,8],[33,7.5],[30,7],[27,6.5],[23,6],[19,5.5],[15,5],[13,4.5],[10,4],[8,3.5],[6,3],[4,2.5]];
  for(const [m,b] of t) if(c>=m) return b; return 2;
}
function showResult(cor,wr,sk,per){
  const total=QNUMS.length; const pct=Math.round(cor/total*100);
  document.getElementById('rb-score').textContent=cor+'/'+total;
  document.getElementById('rb-pct').textContent=pct+'%';
  document.getElementById('rb-cor').textContent=cor;
  document.getElementById('rb-wr').textContent=wr;
  document.getElementById('rb-sk').textContent=sk;
  if(GROUPS.length>1) document.getElementById('rb-secs').innerHTML=GROUPS.map((g,i)=>'<div class="rb-sec"><b>'+per[i]+'/'+(g[1]-g[0]+1)+'</b>Passage '+(i+1)+'</div>').join('');
  const badge=document.getElementById('perf-badge');
  let lvl,cls;
  if(pct>=85){lvl='Excellent';cls='e';} else if(pct>=65){lvl='Good';cls='g';} else if(pct>=45){lvl='Fair';cls='f';} else {lvl='Keep practising';cls='p';}
  badge.textContent=lvl; badge.className='perf-badge '+cls;
  const band = total===40 ? ' — approx. Academic Reading Band '+bandOf(cor).toFixed(1) : '';
  document.getElementById('band-feedback').innerHTML='<b>'+cor+' out of '+total+' correct ('+pct+'%)'+band+'.</b> Read the analysis slowly: every answer is pinned to an exact line in the passage and its paraphrase.';
  document.getElementById('result-modal').classList.add('show');
}
function closeResult(){ document.getElementById('result-modal').classList.remove('show'); }
function reviewAnswers(){
  closeResult();
  const a=document.getElementById('analysis-section'); a.classList.add('show'); a.scrollIntoView({behavior:'smooth'});
}

/* ================= ANALYSIS ================= */
function buildAnalysis(){
  const escapeUserText = value => String(value).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  const kb=document.getElementById('kw-body');
  const list=document.getElementById('fb-list');
  QNUMS.forEach(n=>{
    const gi=GROUPS.findIndex(g=>g[0]===n);
    if(gi>=0 && GROUPS.length>1){
      const tr=document.createElement('tr'); tr.innerHTML='<td colspan="3" style="background:var(--card);font-weight:800;text-align:left;color:var(--blue)">Passage '+(gi+1)+'</td>'; kb.appendChild(tr);
      const h=document.createElement('div'); h.className='a-pass'; h.textContent='Passage '+(gi+1)+' · Q'+GROUPS[gi][0]+'–'+GROUPS[gi][1]; list.appendChild(h);
    }
    const tr=document.createElement('tr');
    tr.innerHTML='<td>'+n+'</td><td>'+KW[n][0]+'</td><td class="pw">'+KW[n][1]+'</td>';
    kb.appendChild(tr);
    const f=FB[n]; const g=grade(n);
    const got = g.state==='skipped' ? '<span class="fb-verd nv">Skipped</span>' :
      (g.ok ? '<span class="fb-verd tv">'+ICON.check+'You: '+escapeUserText(g.user)+'</span>' : '<span class="fb-verd fv">'+ICON.x+'You: '+escapeUserText(g.user)+'</span>');
    const card=document.createElement('div'); card.className='fb-card';
    card.innerHTML=
      '<div class="fb-header"><span class="fb-qn">'+n+'</span><span class="fb-stmt">'+f.stmt+'</span>'+
      '<span class="fb-verd ans">'+f.verd+'</span><span class="fb-caret">'+ICON.chev+'</span></div>'+
      '<div class="fb-body"><div style="margin:8px 0 4px;font-size:.8rem">'+got+'</div>'+
      '<div class="evidence-block"><div class="evidence-label">Evidence in the passage</div>'+f.ev+'</div>'+
      '<div class="fb-explain">'+f.ex+'</div>'+
      '<div class="kw-inline">'+ICON.key+'<span class="qw">'+KW[n][0]+'</span> &nbsp;→&nbsp; <span class="pw">'+KW[n][1]+'</span></div></div>';
    card.querySelector('.fb-header').addEventListener('click',()=>card.classList.toggle('open'));
    list.appendChild(card);
  });
}

document.getElementById('questions-panel').addEventListener('scroll',()=>{
  let best=curIdx;
  for(let n=GROUPS[curP][0];n<=GROUPS[curP][1];n++){
    const c=cardFor(n);
    if(c){ const r=c.getBoundingClientRect(); if(r.top<window.innerHeight*0.5) best=QNUMS.indexOf(n); }
  }
  if(best!==curIdx){ curIdx=best; markActive(); }
});
setPassage(0);
