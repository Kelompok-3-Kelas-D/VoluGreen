(function(){
"use strict";
/* ---------- icons (Lucide paths, same set as the mockup) ---------- */
const P={
  leaf:'<path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z"/><path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12"/>',
  sprout:'<path d="M7 20h10"/><path d="M10 20c5.5-2.5.8-6.4 3-10"/><path d="M9.5 9.4c1.1.8 1.8 2.2 2.3 3.7-2 .4-3.5.4-4.8-.3-1.2-.6-2.3-1.9-3-4.2 2.8-.5 4.4 0 5.5.8z"/><path d="M14.1 6a7 7 0 0 0-1.1 4c1.9-.1 3.3-.6 4.3-1.4 1-1 1.6-2.3 1.7-4.6-2.7.1-4 1-4.9 2z"/>',
  mail:'<rect width="20" height="16" x="2" y="4" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>',
  lock:'<rect width="18" height="11" x="3" y="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>',
  eye:'<path d="M2.062 12.348a1 1 0 0 1 0-.696 10.75 10.75 0 0 1 19.876 0 1 1 0 0 1 0 .696 10.75 10.75 0 0 1-19.876 0"/><circle cx="12" cy="12" r="3"/>',
  eyeoff:'<path d="M10.733 5.076a10.744 10.744 0 0 1 11.205 6.575 1 1 0 0 1 0 .696 10.747 10.747 0 0 1-1.444 2.49"/><path d="M14.084 14.158a3 3 0 0 1-4.242-4.242"/><path d="M17.479 17.499a10.75 10.75 0 0 1-15.417-5.151 1 1 0 0 1 0-.696 10.75 10.75 0 0 1 4.446-5.143"/><path d="m2 2 20 20"/>',
  check:'<path d="M20 6 9 17l-5-5"/>',
  arrow:'<path d="M5 12h14"/><path d="m12 5 7 7-7 7"/>',
  heart:'<path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/>',
  building:'<path d="M6 22V4a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v18Z"/><path d="M6 12H4a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2h2"/><path d="M18 9h2a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2h-2"/><path d="M10 6h4"/><path d="M10 10h4"/><path d="M10 14h4"/><path d="M10 18h4"/>',
  shield:'<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/><path d="m9 12 2 2 4-4"/>',
  award:'<path d="m15.477 12.89 1.515 8.526a.5.5 0 0 1-.81.47l-3.58-2.687a1 1 0 0 0-1.197 0l-3.586 2.686a.5.5 0 0 1-.81-.469l1.514-8.526"/><circle cx="12" cy="8" r="6"/>',
  pin:'<path d="M20 10c0 4.993-5.539 10.193-7.399 11.799a1 1 0 0 1-1.202 0C9.539 20.193 4 14.993 4 10a8 8 0 0 1 16 0"/><circle cx="12" cy="10" r="3"/>',
  bell:'<path d="M10.268 21a2 2 0 0 0 3.464 0"/><path d="M3.262 15.326A1 1 0 0 0 4 17h16a1 1 0 0 0 .74-1.673C19.41 13.956 18 12.499 18 8A6 6 0 0 0 6 8c0 4.499-1.411 5.956-2.738 7.326"/>',
  cal:'<path d="M8 2v4"/><path d="M16 2v4"/><rect width="18" height="18" x="3" y="4" rx="2"/><path d="M3 10h18"/>',
  calcheck:'<path d="M8 2v4"/><path d="M16 2v4"/><rect width="18" height="18" x="3" y="4" rx="2"/><path d="M3 10h18"/><path d="m9 16 2 2 4-4"/>',
  pencil:'<path d="M21.174 6.812a1 1 0 0 0-3.986-3.987L3.842 16.174a2 2 0 0 0-.5.83l-1.321 4.352a.5.5 0 0 0 .623.622l4.353-1.32a2 2 0 0 0 .83-.497z"/><path d="m15 5 4 4"/>',
  clock:'<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
  trash:'<path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/>',
  logout:'<path d="m16 17 5-5-5-5"/><path d="M21 12H9"/><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>',
  user:'<path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>',
  phone:'<path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/>',
  at:'<circle cx="12" cy="12" r="4"/><path d="M16 8v5a3 3 0 0 0 6 0v-1a10 10 0 1 0-4 8"/>',
  file:'<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/>',
  upload:'<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><path d="m17 8-5-5-5 5"/><path d="M12 3v12"/>',
  camera:'<path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z"/><circle cx="12" cy="13" r="3"/>',
  menu:'<path d="M4 6h16"/><path d="M4 12h16"/><path d="M4 18h16"/>',
  chev:'<path d="m6 9 6 6 6-6"/>',
  layers:'<path d="m12.83 2.18a2 2 0 0 0-1.66 0L2.6 6.08a1 1 0 0 0 0 1.83l8.58 3.91a2 2 0 0 0 1.66 0l8.58-3.9a1 1 0 0 0 0-1.83Z"/><path d="m22 17.65-9.17 4.16a2 2 0 0 1-1.66 0L2 17.65"/><path d="m22 12.65-9.17 4.16a2 2 0 0 1-1.66 0L2 12.65"/>',
  recycle:'<path d="M7 19H4.815a1.83 1.83 0 0 1-1.57-.881 1.785 1.785 0 0 1-.004-1.784L7.196 9.5"/><path d="M11 19h8.203a1.83 1.83 0 0 0 1.556-.89 1.784 1.784 0 0 0 0-1.775l-1.226-2.12"/><path d="m14 16-3 3 3 3"/><path d="M8.293 13.596 7.196 9.5 3.1 10.598"/><path d="m9.344 5.811 1.093-1.892A1.83 1.83 0 0 1 11.985 3a1.784 1.784 0 0 1 1.546.888l3.943 6.843"/><path d="m13.378 9.633 4.096 1.098 1.097-4.096"/>'
};
const svg=n=>'<svg class="ic" viewBox="0 0 24 24" aria-hidden="true">'+(P[n]||'')+'</svg>';
const paintIcons=root=>root.querySelectorAll('[data-i]').forEach(el=>{ if(!el.dataset.painted){ el.insertAdjacentHTML('afterbegin',svg(el.dataset.i)); el.dataset.painted='1'; }});
const $=(s,r=document)=>r.querySelector(s), $$=(s,r=document)=>[...r.querySelectorAll(s)];
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

/* ---------- state (sample account, in memory) ---------- */
const CATS=['Bersih lingkungan','Urban farming','Penanaman pohon','Bank sampah','Daur ulang'];
const user={name:'Micguel Katili',email:'micguel.katili@gmail.com',phone:'+62 812 3456 7890',city:'Depok, Jawa Barat',
  bio:'Mahasiswa Ilmu Lingkungan. Suka kegiatan akhir pekan yang hasilnya langsung terlihat, terutama urban farming dan bersih sungai.',
  interests:['Bersih lingkungan','Urban farming','Penanaman pohon'],joined:'Februari 2026',avatar:null};
const org={name:'Bank Sampah Hijau Lestari',type:'Bank sampah',email:'halo@hijaulestari.id'};
const docs=[{n:'Akta pendirian.pdf',s:'ok'},{n:'Surat keterangan domisili.pdf',s:'ok'},{n:'Foto kegiatan sebelumnya.zip',s:'wait'}];
let draft=null;

const initials=n=>(n||'?').trim().split(/\s+/).slice(0,2).map(w=>w[0]).join('').toUpperCase();
function avatarHTML(u){ return u.avatar?'<img src="'+u.avatar+'" alt="">':esc(initials(u.name)); }
function tagHTML(list,cls){ return list.map(t=>'<span class="chip '+(cls||'')+'">'+esc(t)+'</span>').join(''); }

function renderUser(){
  $$('[data-bind="name"]').forEach(e=>e.textContent=user.name);
  $$('[data-bind="city"]').forEach(e=>e.textContent=user.city);
  $$('[data-bind="joined"]').forEach(e=>e.textContent='Bergabung sejak '+user.joined);
  $$('[data-bind="bio"]').forEach(e=>e.textContent=user.bio||'Belum ada bio.');
  $$('[data-bind="email"]').forEach(e=>e.textContent=user.email);
  $$('[data-bind="phone"]').forEach(e=>e.textContent=user.phone||'–');
  $$('[data-bind="interests"]').forEach(e=>e.innerHTML=user.interests.length?tagHTML(user.interests):'<span class="muted-sm">Belum memilih kategori.</span>');
  $$('[data-bind="org-name"]').forEach(e=>e.textContent=org.name);
  $$('[data-bind="org-type"]').forEach(e=>e.textContent=org.type);
  $$('[data-bind="org-email"]').forEach(e=>e.textContent=org.email);
  renderAvatars(user);
}
function renderAvatars(u){
  $$('[data-bind="avatar"]').forEach(e=>e.innerHTML=avatarHTML(u));
  $$('.me[data-kind="relawan"]').forEach(e=>e.innerHTML=avatarHTML(u));
}
function renderLive(){
  const d=draft||user;
  $('[data-bind="name-live"]').textContent=d.name||'Nama lengkap';
  $('[data-bind="city-live"]').textContent=d.city||'Kota domisili';
  $('[data-bind="interests-live"]').innerHTML=tagHTML(d.interests,'dark');
  $$('#s-edit [data-bind="avatar"]').forEach(e=>e.innerHTML=avatarHTML(d));
}

/* ---------- app header shells ---------- */
const NAV={
  relawan:[['Beranda','#beranda'],['Jelajahi kegiatan','soon:Jelajahi kegiatan dikerjakan di Modul 2'],['Kegiatan saya','soon:Kegiatan saya dikerjakan di Modul 3'],['Profil','#profil','profil']],
  penyelenggara:[['Dashboard','soon:Dashboard penyelenggara dikerjakan di Modul 4'],['Lowongan','soon:Kelola lowongan dikerjakan di Modul 4'],['Pendaftar','soon:Tinjau pendaftar dikerjakan di Modul 4'],['Profil organisasi','#organisasi','organisasi']]
};
$$('[data-shell]').forEach((h,i)=>{
  const kind=h.dataset.shell, active=h.dataset.active;
  const links=NAV[kind].map(([t,href,key])=>{
    const soon=href.startsWith('soon:');
    return '<a href="'+(soon?'#':href)+'"'+(soon?' data-soon="'+esc(href.slice(5))+'"':'')+(key===active?' aria-current="page"':'')+'>'+t+'</a>';
  }).join('');
  const id='drawer-'+i;
  h.innerHTML='<div class="wrap" style="position:relative">'+
    '<a class="logo" href="#beranda"><span class="logo-mark" data-i="leaf"></span>VoluGreen</a>'+
    (kind==='penyelenggara'?'<span class="chip sm role-chip">Penyelenggara</span>':'')+
    '<nav class="app-nav" aria-label="Navigasi aplikasi">'+links+'</nav>'+
    '<div class="app-tools"><button class="bell" type="button" aria-label="Notifikasi" data-soon="Belum ada notifikasi baru"><span data-i="bell"></span></button>'+
    '<button class="me" type="button" data-kind="'+kind+'" aria-label="Akun"'+(kind==='penyelenggara'?' style="background:var(--yellow-soft)">RK':'>')+'</button>'+
    '<button class="app-menu" type="button" aria-label="Buka menu" data-drawer="'+id+'"><span data-i="menu"></span></button></div>'+
    '<div class="mobile-drawer" id="'+id+'" hidden>'+links+'<a href="#" data-logout>Keluar</a></div></div>';
});
$$('.me').forEach(b=>b.addEventListener('click',()=>{ location.hash=b.dataset.kind==='penyelenggara'?'organisasi':'edit-profil'; }));

/* ---------- toast ---------- */
let tt;
function toast(msg){ $('#toast-msg').textContent=msg; const t=$('#toast'); t.classList.add('show'); clearTimeout(tt); tt=setTimeout(()=>t.classList.remove('show'),2600); }
document.addEventListener('click',e=>{
  const s=e.target.closest('[data-soon]'); if(s){ e.preventDefault(); toast(s.dataset.soon); }
  const lo=e.target.closest('[data-logout]'); if(lo){ e.preventDefault(); location.hash='masuk'; toast('Kamu sudah keluar. Sampai jumpa di aksi berikutnya.'); }
  const d=e.target.closest('[data-drawer]');
  $$('.mobile-drawer').forEach(m=>{ if(!d||m.id!==d.dataset.drawer) m.hidden=true; });
  if(d){ const m=document.getElementById(d.dataset.drawer); m.hidden=!m.hidden; }
  if(!e.target.closest('.jump')){ $('#jump-list').hidden=true; $('#jump-btn').setAttribute('aria-expanded','false'); }
});

/* ---------- router ---------- */
const SCREENS=[['beranda','2a','Masuk · foto penuh + kartu form'],['masuk','2b','Masuk · pilih peran'],['daftar','2c','Daftar · relawan / penyelenggara'],['profil','2d','Profil relawan'],['organisasi','2e','Profil penyelenggara'],['edit-profil','2f','Edit profil']];
$('#jump-list').innerHTML=SCREENS.map(([r,c,t])=>'<li><a href="#'+r+'" data-r="'+r+'"><code>'+c+'</code>'+t+'</a></li>').join('');
$('#jump-btn').addEventListener('click',()=>{ const l=$('#jump-list'); l.hidden=!l.hidden; $('#jump-btn').setAttribute('aria-expanded',String(!l.hidden)); });
function route(){
  const h=(location.hash||'#beranda').slice(1)||'beranda';
  let shown=null;
  $$('.screen').forEach(s=>{ const on=s.dataset.route.split(' ').includes(h); s.hidden=!on; if(on) shown=s; });
  if(!shown){ $('#s-beranda').hidden=false; shown=$('#s-beranda'); }
  $$('.mobile-drawer').forEach(m=>m.hidden=true);
  const key=shown.dataset.route.split(' ')[0];
  $$('#jump-list a').forEach(a=>a.toggleAttribute('aria-current',a.dataset.r===key));
  if(shown.id==='s-edit'){ openTab(['keamanan','notifikasi'].includes(h)?h:'edit-profil'); }
  window.scrollTo(0,0);
}
window.addEventListener('hashchange',route);

/* ---------- helpers ---------- */
const EMAIL=/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
function setErr(id,msg){ const e=$('[data-err="'+id+'"]'); if(e) e.textContent=msg||''; const c=document.getElementById(id)?.closest('.control'); if(c) c.classList.toggle('is-bad',!!msg); return !msg; }
function strength(pw){ if(!pw) return 0; let s=0; if(pw.length>=8) s++; if(/[A-Z]/.test(pw)&&/[a-z]/.test(pw)||/\d/.test(pw)) s++; if(pw.length>=10&&/[^A-Za-z]/.test(pw)) s++; return Math.max(1,s); }
function paintStrength(el,pw){ const lv=pw?strength(pw):0; el.dataset.lv=lv; el.querySelector('b').textContent=['','Lemah','Sedang','Kuat'][lv]; }
$$('[data-eye]').forEach(b=>b.addEventListener('click',()=>{
  const i=document.getElementById(b.dataset.eye), show=i.type==='password'; i.type=show?'text':'password';
  b.innerHTML=svg(show?'eyeoff':'eye'); b.setAttribute('aria-label',show?'Sembunyikan kata sandi':'Tampilkan kata sandi');
}));
$$('input').forEach(i=>i.addEventListener('input',()=>setErr(i.id,'')));
function segment(root,cb){ root.addEventListener('click',e=>{ const b=e.target.closest('button'); if(!b) return; $$('button',root).forEach(x=>x.setAttribute('aria-selected',String(x===b))); cb(b); }); }

/* ---------- 2a quick login ---------- */
$('#f-quick').addEventListener('submit',e=>{
  e.preventDefault();
  const em=$('#q-email').value.trim(), pw=$('#q-pass').value;
  const ok=[setErr('q-email',EMAIL.test(em)?'':'Masukkan email yang valid, contoh nama@email.com.'),setErr('q-pass',pw.length>=8?'':'Kata sandi minimal 8 karakter.')].every(Boolean);
  if(!ok) return;
  user.email=em; renderUser(); location.hash='profil'; toast('Berhasil masuk. Selamat datang, '+user.name.split(' ')[0]+'!');
});

/* ---------- 2b role login ---------- */
let loginRole='relawan';
const ROLE_LABEL={relawan:'Relawan',penyelenggara:'Penyelenggara',admin:'Admin'};
segment($('#login-role'),b=>{ loginRole=b.dataset.role; $('#login-cta').textContent='Masuk sebagai '+ROLE_LABEL[loginRole]; });
$('#f-login').addEventListener('submit',e=>{
  e.preventDefault();
  const em=$('#l-email').value.trim(), pw=$('#l-pass').value;
  const ok=[setErr('l-email',EMAIL.test(em)?'':'Masukkan email yang valid, contoh nama@email.com.'),setErr('l-pass',pw.length>=8?'':'Kata sandi minimal 8 karakter.')].every(Boolean);
  if(!ok) return;
  if(loginRole==='admin'){ toast('Panel admin dikerjakan di Modul 5'); return; }
  if(loginRole==='penyelenggara'){ org.email=em; renderUser(); location.hash='organisasi'; toast('Masuk sebagai penyelenggara'); }
  else { user.email=em; renderUser(); location.hash='profil'; toast('Berhasil masuk sebagai relawan'); }
});

/* ---------- 2c register ---------- */
let regRole='relawan';
const TICKS={relawan:['Cari kegiatan berdasarkan lokasi, kategori, dan waktu','Daftar kegiatan dan pantau status pendaftaranmu','Lihat riwayat partisipasi dan dampak kontribusimu'],
  penyelenggara:['Publikasikan lowongan kegiatan dan atur kuota relawan','Tinjau pendaftar dan konfirmasi kehadiran','Catat dampak kegiatan setelah organisasi diverifikasi admin']};
function paintReg(){
  $('#reg-ticks').innerHTML=TICKS[regRole].map(t=>'<li><span class="t">'+svg('check')+'</span>'+t+'</li>').join('');
  $$('[data-only]').forEach(f=>f.hidden=f.dataset.only!==regRole);
  const org=regRole==='penyelenggara';
  $('#r-name-lbl').textContent=org?'Nama organisasi':'Nama lengkap';
  $('#r-name').placeholder=org?'Contoh: Bank Sampah Hijau Lestari':'Nama sesuai KTM/KTP';
  $('#r-name').autocomplete=org?'organization':'name';
  $('#gratis-sub').textContent=org?'untuk komunitas & organisasi':'untuk semua relawan';
}
segment($('#reg-role'),b=>{ regRole=b.dataset.role; paintReg(); });
$('#r-pass').addEventListener('input',()=>{ paintStrength($('#r-strength'),$('#r-pass').value); checkMatch(); });
$('#r-pass2').addEventListener('input',checkMatch);
function checkMatch(){ const a=$('#r-pass').value,b=$('#r-pass2').value; $('#r-match').hidden=!(b&&a===b); }
$('#r-terms').addEventListener('change',()=>setErr('r-terms',''));
$('#f-reg').addEventListener('submit',e=>{
  e.preventDefault();
  const v=id=>document.getElementById(id).value.trim();
  const isOrg=regRole==='penyelenggara';
  const checks=[
    setErr('r-name',v('r-name').length>=3?'':(isOrg?'Isi nama organisasi.':'Isi nama lengkapmu.')),
    setErr('r-email',EMAIL.test(v('r-email'))?'':'Masukkan email yang valid, contoh nama@email.com.'),
    setErr('r-phone',/^\+?[\d\s-]{9,}$/.test(v('r-phone'))?'':'Nomor HP minimal 9 digit, contoh +62 812 3456 7890.'),
    isOrg||setErr('r-city',v('r-city')?'':'Isi kota domisilimu.'),
    setErr('r-pass',$('#r-pass').value.length>=8?'':'Kata sandi minimal 8 karakter.'),
    setErr('r-pass2',$('#r-pass2').value===$('#r-pass').value&&$('#r-pass2').value?'':'Konfirmasi belum sama dengan kata sandi.'),
    setErr('r-terms',$('#r-terms').checked?'':'Centang persetujuan Syarat & Ketentuan untuk lanjut.')
  ];
  if(!checks.every(Boolean)) return;
  if(isOrg){ org.name=v('r-name'); org.email=v('r-email'); org.type=$('#r-type').value; renderUser(); location.hash='organisasi'; toast('Akun penyelenggara dibuat. Dokumen menunggu verifikasi admin.'); }
  else { Object.assign(user,{name:v('r-name'),email:v('r-email'),phone:v('r-phone'),city:v('r-city'),bio:'',interests:[],joined:'Oktober 2026',avatar:null}); renderUser(); location.hash='edit-profil'; toast('Akun dibuat. Lengkapi profilmu dulu, yuk.'); }
});

/* ---------- 2e documents ---------- */
function renderDocs(){
  $('#docs').innerHTML=docs.map(d=>'<li>'+svg('file')+'<span class="n" title="'+esc(d.n)+'">'+esc(d.n)+'</span><span class="chip sm '+(d.s==='ok'?'ok':'wait')+'">'+(d.s==='ok'?'Diterima':'Ditinjau')+'</span></li>').join('');
}
$('#doc-file').addEventListener('change',e=>{
  const f=e.target.files[0]; if(!f) return;
  if(f.size>10*1024*1024){ toast('Ukuran file maksimal 10 MB'); e.target.value=''; return; }
  docs.push({n:f.name,s:'wait'}); renderDocs(); e.target.value=''; toast(f.name+' terunggah, menunggu ditinjau admin');
});

/* ---------- 2f edit profile ---------- */
function openTab(t){
  $$('#edit-tabs button').forEach(b=>b.setAttribute('aria-selected',String(b.dataset.tab===t)));
  ['edit-profil','keamanan','notifikasi'].forEach(k=>$('#p-'+k).hidden=k!==t);
  if(t==='edit-profil') loadDraft();
}
$('#edit-tabs').addEventListener('click',e=>{ const b=e.target.closest('button'); if(b) location.hash=b.dataset.tab; });
function loadDraft(){
  draft=JSON.parse(JSON.stringify(user));
  $('#e-name').value=draft.name; $('#e-phone').value=draft.phone; $('#e-email').value=draft.email; $('#e-city').value=draft.city; $('#e-bio').value=draft.bio;
  paintInterests(); bioCount(); renderLive(); setErr('e-name','');
}
function paintInterests(){
  $('#e-interests').innerHTML=CATS.map(c=>'<button type="button" class="toggle-chip" aria-pressed="'+draft.interests.includes(c)+'" data-cat="'+esc(c)+'">'+svg('check')+esc(c)+'</button>').join('');
}
$('#e-interests').addEventListener('click',e=>{
  const b=e.target.closest('[data-cat]'); if(!b) return; const c=b.dataset.cat;
  draft.interests=draft.interests.includes(c)?draft.interests.filter(x=>x!==c):CATS.filter(x=>x===c||draft.interests.includes(x));
  b.setAttribute('aria-pressed',String(draft.interests.includes(c))); renderLive();
});
function bioCount(){ $('#bio-count').textContent=$('#e-bio').value.length+'/240'; }
$('#e-name').addEventListener('input',e=>{ draft.name=e.target.value; renderLive(); });
$('#e-phone').addEventListener('input',e=>{ draft.phone=e.target.value; });
$('#e-bio').addEventListener('input',e=>{ draft.bio=e.target.value; bioCount(); });
$('#e-cancel').addEventListener('click',()=>{ location.hash='profil'; });
$('#p-edit-profil').addEventListener('submit',e=>{
  e.preventDefault();
  if(!setErr('e-name',draft.name.trim().length>=3?'':'Nama minimal 3 huruf.')) return;
  draft.name=draft.name.trim(); draft.city=$('#e-city').value.trim()||draft.city;
  Object.assign(user,draft); renderUser(); location.hash='profil'; toast('Perubahan profil tersimpan');
});
$('#avatar-file').addEventListener('change',e=>{
  const f=e.target.files[0]; if(!f) return;
  if(!/^image\/(png|jpe?g)$/.test(f.type)){ toast('Pilih foto JPG atau PNG'); return; }
  if(f.size>2*1024*1024){ toast('Ukuran foto maksimal 2 MB'); return; }
  const r=new FileReader(); r.onload=()=>{ draft.avatar=r.result; renderLive(); toast('Foto siap. Simpan perubahan untuk memakainya.'); }; r.readAsDataURL(f); e.target.value='';
});

/* city lookup: Nominatim when reachable, otherwise a small local list */
const LOCAL=[['Depok','Jawa Barat, Indonesia'],['Depok','Sleman, DI Yogyakarta'],['Depok Jaya','Pancoran Mas, Depok'],['Jakarta Selatan','DKI Jakarta, Indonesia'],['Jakarta Timur','DKI Jakarta, Indonesia'],['Jakarta Pusat','DKI Jakarta, Indonesia'],['Bogor','Jawa Barat, Indonesia'],['Bekasi','Jawa Barat, Indonesia'],['Tangerang Selatan','Banten, Indonesia'],['Bandung','Jawa Barat, Indonesia'],['Yogyakarta','DI Yogyakarta, Indonesia'],['Semarang','Jawa Tengah, Indonesia'],['Surabaya','Jawa Timur, Indonesia'],['Malang','Jawa Timur, Indonesia'],['Denpasar','Bali, Indonesia'],['Makassar','Sulawesi Selatan, Indonesia'],['Medan','Sumatera Utara, Indonesia'],['Palembang','Sumatera Selatan, Indonesia'],['Balikpapan','Kalimantan Timur, Indonesia']];
let results=[], sel=0, timer, src='local';
const cityIn=$('#e-city'), list=$('#city-list');
async function lookup(q){
  try{
    const ctl=new AbortController(); const to=setTimeout(()=>ctl.abort(),2500);
    const r=await fetch('https://nominatim.openstreetmap.org/search?format=json&addressdetails=1&limit=5&countrycodes=id&q='+encodeURIComponent(q),{signal:ctl.signal,headers:{'Accept-Language':'id'}});
    clearTimeout(to); if(!r.ok) throw 0; const j=await r.json();
    src='osm'; return j.map(x=>{ const a=x.address||{}; const n=a.city||a.town||a.county||a.village||x.name||x.display_name.split(',')[0]; return [n,[a.state,a.country].filter(Boolean).join(', ')]; });
  }catch(_){ src='local'; const s=q.toLowerCase(); return LOCAL.filter(([n,d])=>(n+' '+d).toLowerCase().includes(s)).slice(0,5); }
}
function paintList(){
  if(!results.length){ list.hidden=true; cityIn.setAttribute('aria-expanded','false'); return; }
  list.innerHTML=results.map(([n,d],i)=>'<li role="option" id="opt-'+i+'" aria-selected="'+(i===sel)+'" data-i2="'+i+'">'+svg('pin')+'<span><b>'+esc(n)+'</b><small>'+esc(d)+'</small></span></li>').join('')+
    '<li class="src" role="presentation">'+(src==='osm'?'Data lokasi © OpenStreetMap contributors':'Contoh lokasi lokal · Nominatim tidak terjangkau dari halaman ini')+'</li>';
  list.hidden=false; cityIn.setAttribute('aria-expanded','true'); cityIn.setAttribute('aria-activedescendant','opt-'+sel);
}
function pick(i){ const [n,d]=results[i]; const v=n+', '+d.split(',')[0]; cityIn.value=v; draft.city=v; results=[]; paintList(); renderLive(); }
cityIn.addEventListener('input',()=>{ draft.city=cityIn.value; renderLive(); clearTimeout(timer); const q=cityIn.value.trim(); if(q.length<2){ results=[]; paintList(); return; } timer=setTimeout(async()=>{ results=await lookup(q); sel=0; paintList(); },300); });
cityIn.addEventListener('keydown',e=>{
  if(list.hidden) return;
  if(e.key==='ArrowDown'){ e.preventDefault(); sel=(sel+1)%results.length; paintList(); }
  else if(e.key==='ArrowUp'){ e.preventDefault(); sel=(sel-1+results.length)%results.length; paintList(); }
  else if(e.key==='Enter'){ e.preventDefault(); pick(sel); }
  else if(e.key==='Escape'){ results=[]; paintList(); }
});
list.addEventListener('mousedown',e=>{ const li=e.target.closest('[data-i2]'); if(li){ e.preventDefault(); pick(+li.dataset.i2); } });
cityIn.addEventListener('blur',()=>setTimeout(()=>{ results=[]; paintList(); },120));

/* security + notifications */
$('#k-new').addEventListener('input',()=>paintStrength($('#k-strength'),$('#k-new').value));
$('#p-keamanan').addEventListener('submit',e=>{
  e.preventDefault();
  const ok=[setErr('k-old',$('#k-old').value.length>=8?'':'Isi kata sandi saat ini.'),
    setErr('k-new',$('#k-new').value.length>=8?($('#k-new').value===$('#k-old').value?'Kata sandi baru harus berbeda dari yang lama.':''):'Kata sandi baru minimal 8 karakter.'),
    setErr('k-new2',$('#k-new2').value===$('#k-new').value&&$('#k-new2').value?'':'Belum sama dengan kata sandi baru.')].every(Boolean);
  if(!ok) return; e.target.reset(); paintStrength($('#k-strength'),''); toast('Kata sandi diperbarui');
});
$$('.switch').forEach(s=>s.addEventListener('click',()=>{ const on=s.getAttribute('aria-checked')!=='true'; s.setAttribute('aria-checked',String(on)); toast((on?'Aktif: ':'Nonaktif: ')+s.getAttribute('aria-label')); }));

/* ---------- boot ---------- */
const PHOTO=window.VOLUGREEN_PHOTO_URL; $$("img[data-photo]").forEach(i=>i.src=PHOTO);
paintIcons(document); paintReg(); renderDocs(); renderUser(); route();
})();
