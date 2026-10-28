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

/* ---------- state ---------- */
const profileDataElement=document.getElementById('volugreen-profile-data');
const profileData=profileDataElement?JSON.parse(profileDataElement.textContent):null;
const user={name:'',email:'',phone:'',city:'',joined:''};
const org={name:'',type:'',email:'',phone:'',city:'',description:'',status:'not_submitted'};
if(profileData?.role==='volunteer'){
  Object.assign(user,profileData);
}else if(profileData?.role==='organizer'){
  Object.assign(org,{name:profileData.name,type:profileData.organization_type,email:profileData.email,
    phone:profileData.phone,city:profileData.organization_city,description:profileData.organization_description,
    status:profileData.organization_status});
}

const initials=n=>(n||'?').trim().split(/\s+/).slice(0,2).map(w=>w[0]).join('').toUpperCase();
function renderUser(){
  $$('[data-bind="name"]').forEach(e=>e.textContent=user.name||'Nama belum diisi');
  $$('[data-bind="city"]').forEach(e=>e.textContent=user.city||'Kota belum diisi');
  $$('[data-bind="joined"]').forEach(e=>e.textContent=user.joined?'Bergabung sejak '+user.joined:'');
  $$('[data-bind="email"]').forEach(e=>e.textContent=user.email);
  $$('[data-bind="phone"]').forEach(e=>e.textContent=user.phone||'–');
  $$('[data-bind="org-name"]').forEach(e=>e.textContent=org.name||'Nama organisasi belum diisi');
  $$('[data-bind="org-type"]').forEach(e=>e.textContent=org.type||'Jenis organisasi belum diisi');
  $$('[data-bind="org-email"]').forEach(e=>e.textContent=org.email);
  $$('[data-bind="org-phone"]').forEach(e=>e.textContent=org.phone||'Nomor belum diisi');
  $$('[data-bind="org-city"]').forEach(e=>e.textContent=org.city||'Lokasi belum diisi');
  $$('[data-bind="org-description"]').forEach(e=>e.textContent=org.description||'Deskripsi organisasi belum diisi.');
  $$('[data-bind="org-status"]').forEach(e=>{e.textContent=org.status==='verified'?'Terverifikasi':org.status==='rejected'?'Perlu perbaikan':org.status==='pending'?'Menunggu verifikasi':'Belum diajukan';e.className='chip '+(org.status==='verified'?'ok':org.status==='rejected'?'wait':'yellow');});
  const orgNotice=$('#org-review-title');
  if(orgNotice) orgNotice.textContent=org.status==='verified'?'Profil organisasi terverifikasi':org.status==='rejected'?'Profil organisasi perlu diperbaiki':org.status==='pending'?'Profil organisasi sedang ditinjau admin':'Ajukan profil organisasi agar admin dapat meninjaunya';
  const stepIndex=org.status==='not_submitted'?1:org.status==='verified'?3:2;
  $$('[data-org-step]').forEach((step,index)=>{
    const done=org.status==='verified'||index<stepIndex;
    const current=org.status!=='verified'&&index===stepIndex;
    step.classList.toggle('done',done); step.classList.toggle('now',current);
    if(current) step.setAttribute('aria-current','step'); else step.removeAttribute('aria-current');
    const dot=step.querySelector('.dot'); if(dot) dot.innerHTML=done?svg('check'):'';
  });
  const reviewStep=$('[data-org-step="review"]');
  if(reviewStep) reviewStep.lastChild.textContent=org.status==='rejected'?'Perlu perbaikan':'Ditinjau admin';
  renderAvatars(user);
}
function renderAvatars(u){ $$('[data-bind="avatar"]').forEach(e=>e.textContent=initials(u.name)||'–'); }

/* ---------- app header shells ---------- */
const NAV={
  relawan:[['Beranda','#beranda'],['Jelajahi kegiatan','#kegiatan','kegiatan'],['Profil','#profil','profil']],
  penyelenggara:[['Ringkasan',window.VOLUGREEN_ORGANIZER_URL+'#ringkasan'],['Kegiatan',window.VOLUGREEN_ORGANIZER_URL+'#lowongan'],['Laporan dampak',window.VOLUGREEN_ORGANIZER_URL+'#dampak'],['Profil organisasi','#organisasi','organisasi']]
};
$$('[data-shell]').forEach((h,i)=>{
  const kind=h.dataset.shell, active=h.dataset.active;
  const links=NAV[kind].map(([t,href,key])=>{
    return '<a href="'+href+'"'+(key===active?' aria-current="page"':'')+'>'+t+'</a>';
  }).join('');
  const id='drawer-'+i;
  h.innerHTML='<div class="wrap" style="position:relative">'+
    '<a class="logo" href="#beranda"><span class="logo-mark" data-i="leaf"></span>VoluGreen</a>'+
    (kind==='penyelenggara'?'<span class="chip sm role-chip">Penyelenggara</span>':'')+
    '<nav class="app-nav" aria-label="Navigasi aplikasi">'+links+'</nav>'+
    '<div class="app-tools"><a class="me" href="'+window.VOLUGREEN_PROFILE_SETTINGS_URL+'" aria-label="Pengaturan akun">'+esc(initials(kind==='penyelenggara'?org.name:user.name)||'–')+'</a>'+
    '<button class="app-menu" type="button" aria-label="Buka menu" data-drawer="'+id+'"><span data-i="menu"></span></button></div>'+
    '<div class="mobile-drawer" id="'+id+'" hidden>'+links+'<a href="'+window.VOLUGREEN_LOGOUT_URL+'">Keluar</a></div></div>';
});

document.addEventListener('click',e=>{
  const d=e.target.closest('[data-drawer]');
  $$('.mobile-drawer').forEach(m=>{ if(!d||m.id!==d.dataset.drawer) m.hidden=true; });
  if(d){ const m=document.getElementById(d.dataset.drawer); m.hidden=!m.hidden; }
});

/* ---------- router ---------- */
function route(){
  let h=(location.hash||'#beranda').slice(1)||'beranda';
  if(['profil','organisasi'].includes(h)&&!profileData){ window.location.assign(window.VOLUGREEN_LOGIN_URL); return; }
  if(h==='profil'&&profileData?.role==='organizer'){ location.replace('#organisasi'); return; }
  if(h==='organisasi'&&profileData?.role==='volunteer'){ location.replace('#profil'); return; }
  let shown=null;
  $$('.screen').forEach(s=>{ const on=s.dataset.route.split(' ').includes(h); s.hidden=!on; if(on) shown=s; });
  if(!shown){ $('#s-beranda').hidden=false; shown=$('#s-beranda'); }
  $$('.mobile-drawer').forEach(m=>m.hidden=true);
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

/* ---------- 2b role login ---------- */
let loginRole='relawan';
const ROLE_LABEL={relawan:'Relawan',penyelenggara:'Penyelenggara'};
segment($('#login-role'),b=>{ loginRole=b.dataset.role; $('#login-cta').textContent='Masuk sebagai '+ROLE_LABEL[loginRole]; });
$('#f-login').addEventListener('submit',e=>{
  const em=$('#l-email').value.trim(), pw=$('#l-pass').value;
  const ok=[setErr('l-email',EMAIL.test(em)?'':'Masukkan email yang valid, contoh nama@email.com.'),setErr('l-pass',pw.length>=8?'':'Kata sandi minimal 8 karakter.')].every(Boolean);
  if(!ok){ e.preventDefault(); return; }
  $('#spa-login-role').value=loginRole==='penyelenggara'?'organizer':'volunteer';
});

/* ---------- 2c register ---------- */
let regRole=$('#spa-reg-role').value==='organizer'?'penyelenggara':'relawan';
const TICKS={relawan:['Buat akun relawan menggunakan email, nomor HP, dan kota domisili.'],
  penyelenggara:['Kirim informasi organisasi untuk ditinjau admin.','Kelola draft kegiatan dan pantau status tinjauannya.','Catat dampak setelah kegiatan terbit dan selesai.']};
function paintReg(){
  $('#reg-ticks').innerHTML=TICKS[regRole].map(t=>'<li><span class="t">'+svg('check')+'</span>'+t+'</li>').join('');
  $$('#reg-role button').forEach(b=>b.setAttribute('aria-selected',String(b.dataset.role===regRole)));
  $$('[data-only]').forEach(f=>f.hidden=!f.dataset.only.split(' ').includes(regRole));
  const org=regRole==='penyelenggara';
  $('#r-name-lbl').textContent=org?'Nama organisasi':'Nama lengkap';
  $('#r-name').placeholder=org?'Nama organisasi':'Nama sesuai KTM/KTP';
  $('#r-name').autocomplete=org?'organization':'name';
  const cityLabel=$('#r-city-lbl');
  if(cityLabel) cityLabel.textContent=org?'Kota organisasi':'Kota domisili';
  $('#r-city').placeholder=org?'Masukkan kota organisasi':'Masukkan kota domisili';
  $('#gratis-sub').textContent=org?'untuk komunitas & organisasi':'untuk semua relawan';
}
segment($('#reg-role'),b=>{ regRole=b.dataset.role; paintReg(); });
$('#r-pass').addEventListener('input',()=>{ paintStrength($('#r-strength'),$('#r-pass').value); checkMatch(); });
$('#r-pass2').addEventListener('input',checkMatch);
function checkMatch(){ const a=$('#r-pass').value,b=$('#r-pass2').value; $('#r-match').hidden=!(b&&a===b); }
$('#r-terms').addEventListener('change',()=>setErr('r-terms',''));
$('#f-reg').addEventListener('submit',e=>{
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
  if(!checks.every(Boolean)){ e.preventDefault(); return; }
  $('#spa-reg-role').value=isOrg?'organizer':'volunteer';
});

/* ---------- boot ---------- */
const PHOTO=window.VOLUGREEN_PHOTO_URL; $$("img[data-photo]").forEach(i=>i.src=PHOTO);
paintIcons(document); paintReg(); renderUser(); route();
})();
