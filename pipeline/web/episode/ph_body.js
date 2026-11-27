import * as THREE from 'three';
import {GLTFLoader} from 'gltf';
import {EXRLoader} from 'exr';
import {Muxer, ArrayBufferTarget} from 'mp4muxer';
import {EffectComposer} from 'pp/EffectComposer'; import {RenderPass} from 'pp/RenderPass'; import {BokehPass} from 'pp/BokehPass';
import {UnrealBloomPass} from 'pp/UnrealBloomPass'; import {OutputPass} from 'pp/OutputPass';
const K=window.EP, $=id=>document.getElementById(id), L=K.look;
const opt={fps:24,style:'smooth',res:1080};
document.querySelectorAll('.seg').forEach(g=>g.addEventListener('click',e=>{const b=e.target.closest('button');if(!b)return;
  g.querySelectorAll('button').forEach(x=>x.setAttribute('aria-pressed',x===b));opt[g.dataset.k]=+b.dataset.v;}));
const say=(t,err)=>{$('msg').textContent=t;$('msg').className=err?'err':''};
const LOADS={};
const load=src=>LOADS[src]??=new Promise((ok,no)=>{const s=document.createElement('script');s.src=src;s.onload=ok;s.onerror=()=>no(new Error('Gagal memuat '+src+' (pastikan folder data/ ada di samping file HTML ini)'));document.head.appendChild(s);});
let tLoad=0;
say('Memuat aset…');
__TONE__
const r=new THREE.WebGLRenderer({antialias:true,preserveDrawingBuffer:true,powerPreference:'high-performance'});
r.setPixelRatio(1); r.toneMapping=THREE.CustomToneMapping; r.toneMappingExposure=1; r.shadowMap.enabled=true; r.shadowMap.type=THREE.PCFSoftShadowMap;
const out=document.createElement('canvas'), octx=out.getContext('2d'); $('frame').appendChild(out);
const gl=r.getContext(), dbg=gl.getExtension('WEBGL_debug_renderer_info'); $('gpu').textContent=dbg?gl.getParameter(dbg.UNMASKED_RENDERER_WEBGL):gl.getParameter(gl.RENDERER);
const gltf=new GLTFLoader(), exr=new EXRLoader(), tl=new THREE.TextureLoader(), pm=new THREE.PMREMGenerator(r);
const scene=new THREE.Scene(); const cam=new THREE.PerspectiveCamera(40,9/16,0.1,500);
// pasca-proses ala film pendek: kedalaman ruang (latar blur lembut) + bloom halus
const comp=new EffectComposer(r); comp.addPass(new RenderPass(scene,cam));
const bokeh=new BokehPass(scene,cam,{focus:3,aperture:0.0012,maxblur:0.006}); comp.addPass(bokeh);
const bloom=new UnrealBloomPass(new THREE.Vector2(540,960),0.28,0.6,0.9); comp.addPass(bloom); comp.addPass(new OutputPass());
let focusDist=3; const draw3d=()=>{ bokeh.uniforms.focus.value=focusDist; comp.render(); };
const tile=i=>new THREE.Vector2((i%4)*0.25,(3-Math.floor(i/4))*0.25);
const lerp=(a,b,u)=>a+(b-a)*u, D=Math.PI/180;
// ---------- media: footage, audio, font
await load('data/media.js'); const MED=window.MEDIA;
const font=new FontFace('DejaVuSub',`url(${MED.font})`,{weight:'700'}); await font.load(); document.fonts.add(font);
const font2=new FontFace('OswaldSub',`url(${MED.font2})`,{weight:'200 700'}); await font2.load(); document.fonts.add(font2);
// footage TV = deretan JPEG (30 fps) yang di-decode langsung; tidak ada seek video per frame
const FR={}; for(const k in MED.frames){ FR[k]=await Promise.all(MED.frames[k].map(u=>fetch(u).then(r=>r.blob()))); }
async function frameBitmap(k,t){ const arr=FR[k]; const i=Math.max(0,Math.min(arr.length-1,Math.round(t*30))); return createImageBitmap(arr[i]); }
// ---------- layar TV & ponsel (kanvas)
const tvC=document.createElement('canvas'); tvC.width=1024; tvC.height=576; const tvX=tvC.getContext('2d'); const tvTex=new THREE.CanvasTexture(tvC); tvTex.colorSpace=THREE.SRGBColorSpace; tvTex.flipY=false;
const PH={}; for(const w of ['nayla','dimas']){ const c=document.createElement('canvas'); c.width=360; c.height=640; const t=new THREE.CanvasTexture(c); t.colorSpace=THREE.SRGBColorSpace; t.flipY=false; PH[w]={c,x:c.getContext('2d'),t,last:''}; }
let lucPause=document.createElement('canvas'); lucPause.width=1024; lucPause.height=576; { const bm=await createImageBitmap(await (await fetch(MED.pause)).blob()); lucPause.getContext('2d').drawImage(bm,0,0,1024,576); bm.close(); }
async function drawTV(t){
  const e=K.tv.find(([a,b])=>t>=a&&t<b); const x=tvX, W=1024, H=576;
  if(!e){ x.fillStyle='#000'; x.fillRect(0,0,W,H); tvTex.needsUpdate=true; return null; }
  const [a,b,k,off]=e;
  if(k==='unduh'){ const g=x.createLinearGradient(0,0,W,H); g.addColorStop(0,'#0b1d4a'); g.addColorStop(1,'#1d4fa8'); x.fillStyle=g; x.fillRect(0,0,W,H);
    x.fillStyle='#fff'; x.font='700 44px DejaVuSub'; x.textAlign='left'; x.fillText('Mengunduh game…',90,230);
    x.fillStyle='rgba(255,255,255,.25)'; x.fillRect(90,280,844,26); x.fillStyle='#fff'; x.fillRect(90,280,844*0.99,26); x.font='700 36px DejaVuSub'; x.fillText('99%',90,360);
    x.font='28px DejaVuSub'; x.fillStyle='rgba(255,255,255,.7)'; x.fillText('Sisa waktu: menghitung…',90,410); }
  else if(k==='pause'){
    x.drawImage(lucPause,0,0); x.fillStyle='rgba(0,0,0,.55)'; x.fillRect(0,0,W,H); x.fillStyle='#fff'; x.font='700 64px DejaVuSub'; x.textAlign='center'; x.fillText('PAUSE',W/2,H/2+20); }
  else { const v=await frameBitmap(k,t-a); const vw=v.width, vh=v.height, s=Math.max(W/vw,H/vh); x.fillStyle='#000'; x.fillRect(0,0,W,H);
    if(vw/vh<1.4){ const s2=H/vh; x.drawImage(v,(W-vw*s2)/2,0,vw*s2,H); } else x.drawImage(v,(W-vw*s)/2,(H-vh*s)/2,vw*s,vh*s); v.close(); }
  tvTex.needsUpdate=true; return k;
}
function drawPhone(t){
  for(const w of ['nayla','dimas']){ const P=PH[w]; const e=K.phone.find(([a,b,who])=>who===w&&t>=a&&t<b); const name=e?e[3]:'home';
    if(P.last===name) continue; P.last=name; const x=P.x, W=360, H=640;
    const g=x.createLinearGradient(0,0,0,H); g.addColorStop(0,w==='nayla'?'#f7b2c9':'#3a6fb0'); g.addColorStop(1,w==='nayla'?'#8f6bd1':'#14213d'); x.fillStyle=g; x.fillRect(0,0,W,H);
    x.fillStyle='#fff'; x.textAlign='center'; x.font='700 22px DejaVuSub'; x.fillText('17.04',W/2,34);
    if(name==='home'||name==='notif'){ x.font='700 72px DejaVuSub'; x.fillText('17.04',W/2,170);
      const cols=['#ff6b6b','#ffd93d','#6bcb77','#4d96ff','#c77dff','#ff9f1c','#2ec4b6','#e71d36'];
      for(let i=0;i<8;i++){ x.fillStyle=cols[i]; const cx=50+(i%4)*87, cy=400+Math.floor(i/4)*95; x.beginPath(); x.roundRect(cx-30,cy-30,60,60,16); x.fill(); } }
    if(name==='notif'){ x.fillStyle='rgba(255,255,255,.92)'; x.beginPath(); x.roundRect(14,60,W-28,104,22); x.fill(); x.fillStyle='#111'; x.textAlign='left';
      x.font='700 18px DejaVuSub'; x.fillText('KabarGame · sekarang',34,92); x.font='700 23px DejaVuSub'; x.fillText('GTA 6 sudah rilis!',34,124); x.font='19px DejaVuSub'; x.fillText('Main sekarang di PS5',34,150); }
    if(name==='berita'){ x.fillStyle='#fff'; x.fillRect(0,48,W,H); x.fillStyle='#c0392b'; x.fillRect(0,48,W,56); x.fillStyle='#fff'; x.textAlign='left'; x.font='700 26px DejaVuSub'; x.fillText('KabarGame',18,86);
      x.fillStyle='#111'; x.font='700 27px DejaVuSub'; ['GTA 6 Resmi Rilis','di PS5 dan Xbox','Series X|S'].forEach((l,i)=>x.fillText(l,18,148+i*34));
      if(lucPause) x.drawImage(lucPause,18,262,W-36,(W-36)*9/16); else { x.fillStyle='#ccc'; x.fillRect(18,262,W-36,182); }
      x.fillStyle='#555'; for(let i=0;i<5;i++) x.fillRect(18,470+i*26,(W-36)*(i===4?0.6:1),12); }
    if(name==='beli'){ x.fillStyle='#fff'; x.fillRect(0,48,W,H); x.fillStyle='#2ecc71'; x.beginPath(); x.arc(W/2,220,70,0,7); x.fill();
      x.strokeStyle='#fff'; x.lineWidth=14; x.beginPath(); x.moveTo(W/2-34,222); x.lineTo(W/2-8,248); x.lineTo(W/2+36,196); x.stroke();
      x.fillStyle='#111'; x.textAlign='center'; x.font='700 28px DejaVuSub'; x.fillText('Pembelian berhasil',W/2,350); x.font='22px DejaVuSub'; x.fillStyle='#444'; x.fillText('Grand Theft Auto VI',W/2,392); x.fillText('Siap diunduh ke konsol',W/2,424); }
    P.t.needsUpdate=true; }
}
// ---------- lingkungan (dibagi antar segmen) & segmen
const ENV={}, SEG=[];
function makeDU(n){ return {n,dPos:{value:[...Array(n)].map(()=>new THREE.Vector3())},dCol:{value:[...Array(n)].map(()=>new THREE.Vector3())},dDir:{value:[...Array(n)].map(()=>new THREE.Vector3(0,-1,0))},dCone:{value:[...Array(n)].map(()=>new THREE.Vector2(-2,-1))}}; }
function withDyn(m,DU){ const N=DU.n; m.onBeforeCompile=sh=>{ Object.assign(sh.uniforms,{dPos:DU.dPos,dCol:DU.dCol,dDir:DU.dDir,dCone:DU.dCone});
  sh.vertexShader='varying vec3 vWP; varying vec3 vWN;\n'+sh.vertexShader.replace('#include <begin_vertex>','#include <begin_vertex>\nvWP=(modelMatrix*vec4(transformed,1.0)).xyz; vWN=normalize(mat3(modelMatrix)*normal);');
  sh.fragmentShader=`varying vec3 vWP; varying vec3 vWN; uniform vec3 dPos[${N}]; uniform vec3 dCol[${N}]; uniform vec3 dDir[${N}]; uniform vec2 dCone[${N}];\n`+sh.fragmentShader.replace('// modulation',`
   vec3 Nw=normalize(vWN); if(!gl_FrontFacing) Nw=-Nw;
   for(int i=0;i<${N};i++){ vec3 Lv=dPos[i]-vWP; float d2=max(dot(Lv,Lv),1e-3); vec3 Ld=Lv*inversesqrt(d2);
     float sp=dCone[i].x<-1.5?1.0:smoothstep(dCone[i].x,dCone[i].y,dot(-Ld,dDir[i]));
     reflectedLight.indirectDiffuse+=dCol[i]*max(dot(Nw,Ld),0.0)/d2*sp*RECIPROCAL_PI; }
   // modulation`); }; m.customProgramCacheKey=()=>'dyn'+N; return m; }
async function buildEnv(key){
  await load(`data/env_${key}.js`); const E=window['ENV_'+key]; delete window['ENV_'+key]; const env=await gltf.loadAsync(E.env);
  const LM={},AL={};
  for(const g in E.lm){ const t=await exr.loadAsync(E.lm[g]); t.channel=1; t.repeat.set(1,-1); t.offset.set(0,1); t.colorSpace=THREE.LinearSRGBColorSpace; t.minFilter=THREE.LinearMipmapLinearFilter; t.generateMipmaps=true; t.needsUpdate=true; LM[g]=t; }
  for(const g in E.al){ const t=await tl.loadAsync(E.al[g]); t.flipY=false; t.channel=1; t.colorSpace=THREE.SRGBColorSpace; t.anisotropy=4; AL[g]=t; }
  const probe=await exr.loadAsync(E.probe), sky=await exr.loadAsync(E.sky); probe.mapping=sky.mapping=THREE.EquirectangularReflectionMapping;
  const DU=makeDU(4), emis={};
  env.scene.traverse(o=>{ if(!o.isMesh) return; o.castShadow=true;
    const g=(o.name.match(/ENV_([A-Z])/)||(o.parent&&o.parent.name.match(/ENV_([A-Z])/))||[])[1];
    const conv=m=>{ if(m.name==='tv_layar') return new THREE.MeshBasicMaterial({map:tvTex,color:new THREE.Color(2.2,2.2,2.2)});
      const e=E.emissive[m.name];
      if(e){ const v=e.frames[0], mm=new THREE.MeshBasicMaterial({color:new THREE.Color(v[0]*v[3],v[1]*v[3],v[2]*v[3])}); (emis[m.name]??=[]).push(mm); return mm; }
      const proc=E.procedural.includes(m.name)&&AL[g];
      return withDyn(new THREE.MeshBasicMaterial({color:proc?0xffffff:m.color,map:proc?AL[g]:m.map,lightMap:LM[g]||null}),DU); };
    o.material=Array.isArray(o.material)?o.material.map(conv):conv(o.material); });
  scene.add(env.scene);
  ENV[key]={group:env.scene,sky,envMap:pm.fromEquirectangular(probe).texture,DU,emis,tex:[...Object.values(LM),...Object.values(AL),probe,sky]};
}
const blobTex=(()=>{ const cv=document.createElement('canvas'); cv.width=cv.height=128; const cx=cv.getContext('2d'), gr=cx.createRadialGradient(64,64,0,64,64,64);
  gr.addColorStop(0,'rgba(0,0,0,0.55)'); gr.addColorStop(0.5,'rgba(0,0,0,0.3)'); gr.addColorStop(1,'rgba(0,0,0,0)'); cx.fillStyle=gr; cx.fillRect(0,0,128,128); return new THREE.CanvasTexture(cv); })();
const hash=s=>{let h=0;for(const c of s)h=(h*31+c.charCodeAt(0))>>>0;return (h%1000)/1000*6.283;};
async function buildSeg(sg){
  await load(`data/seg_${sg.id}.js`); const S=window['SEG_'+sg.id], M=S.meta, E=ENV[sg.env]; delete window['SEG_'+sg.id];
  const dyn=await gltf.loadAsync(S.dyn); const grp=new THREE.Group(); grp.add(dyn.scene); scene.add(grp);
  const FACE={};
  for(const rig in M.faces){ const ey=await tl.loadAsync(S.eyes[rig]), mo=await tl.loadAsync(S.mouth[rig]); ey.colorSpace=mo.colorSpace=THREE.SRGBColorSpace;
    FACE[rig]={ey,mo,u:{eyeOff:{value:tile(0)},mouthOff:{value:tile(0)}},blush:(K.blush||{})[rig]||0}; }
  const faceOf={}; for(const rig in M.face_names) faceOf[M.face_names[rig]]=rig;
  dyn.scene.traverse(o=>{ if(!o.isMesh) return; o.castShadow=o.receiveShadow=true;
    const fix=m=>{ if(m.name==='hp_layar_nayla'||m.name==='hp_layar_dimas') return new THREE.MeshBasicMaterial({map:PH[m.name.slice(9)].t,color:new THREE.Color(1.6,1.6,1.6)});
      m=m.clone(); m.envMap=E.envMap; m.envMapIntensity=L.env; const rig=faceOf[m.name];
      if(rig){ const F=FACE[rig]; m.color.setRGB(...M.skin[rig]); m.map=null; const msk=M.mask[rig];
        m.onBeforeCompile=sh=>{ Object.assign(sh.uniforms,{eyeTex:{value:F.ey},mouthTex:{value:F.mo}},F.u);
          sh.vertexShader='varying vec3 vLoc;\n'+sh.vertexShader.replace('#include <begin_vertex>','#include <begin_vertex>\nvLoc=position;');
          sh.fragmentShader='varying vec3 vLoc; uniform sampler2D eyeTex,mouthTex; uniform vec2 eyeOff,mouthOff;\n'+sh.fragmentShader.replace('#include <map_fragment>',`
            vec2 fuv=vec2(vLoc.x+0.5,vLoc.y+0.5); vec2 inb=step(vec2(0.0),fuv)*step(fuv,vec2(1.0)); float ib=inb.x*inb.y*((-vLoc.z<${msk.toFixed(4)})?1.0:0.0);
            vec4 ec=texture2D(eyeTex,fuv*0.25+eyeOff); diffuseColor.rgb=mix(diffuseColor.rgb,ec.rgb,ec.a*ib);
            vec4 mc=texture2D(mouthTex,fuv*0.25+mouthOff); diffuseColor.rgb=mix(diffuseColor.rgb,mc.rgb,mc.a*ib);
            float bd=pow((abs(vLoc.x)-0.23)/0.085,2.0)+pow((vLoc.y+0.09)/0.05,2.0); float bl=pow(max(0.0,1.0-bd),1.5)*${F.blush.toFixed(3)}*((-vLoc.z<${msk.toFixed(4)})?1.0:0.0);
            diffuseColor.rgb=mix(diffuseColor.rgb,vec3(1.0,0.0844,0.1195),bl);`); };
        m.customProgramCacheKey=()=>'face_'+sg.id+rig; }
      return m; };
    o.material=Array.isArray(o.material)?o.material.map(fix):fix(o.material); });
  // lampu real-time (karakter) + lampu dinamis untuk lingkungan
  const LT=[];
  for(const [n,l] of Object.entries(M.lights)){ let o;
    if(l.type==='SUN'){ o=new THREE.DirectionalLight(); o.castShadow=true; o.shadow.mapSize.set(2048,2048); Object.assign(o.shadow.camera,{left:-12,right:12,top:12,bottom:-12,near:1,far:80}); o.shadow.bias=-0.0004; o.shadow.normalBias=0.02; o.shadow.radius=3; grp.add(o.target); }
    else if(l.type==='SPOT'){ o=new THREE.SpotLight(); o.angle=l.size/2; o.penumbra=l.blend; o.decay=2; grp.add(o.target); }
    else { o=new THREE.PointLight(); o.decay=2; }
    grp.add(o); LT.push({n,o,l}); }
  const mixer=new THREE.AnimationMixer(dyn.scene), ACTS=dyn.animations.map(c=>{const a=mixer.clipAction(c); a.play(); return {c,a};});
  ACTS.forEach(A=>A.c.tracks.forEach(t=>t.setInterpolation(THREE.InterpolateLinear)));
  const tracked=new Set(); for(const A of ACTS) for(const t of A.c.tracks) tracked.add(t.name.split('.')[0]);
  const IDLE=[], BLOB=[];
  for(const rig of K.rigs){ const root=dyn.scene.getObjectByName(rig); if(!root) continue; const B={};
    root.traverse(o=>{ if(o.type!=='Object3D'&&o.type!=='Bone') return; const base=o.name.replace(/_\d+$/,''); for(const k of ['hips','spine','head','armL','armR','braidL','braidR']) if(base===k&&!B[k]) B[k]=o; });
    for(const k in B) B[k].userData.base=B[k].quaternion.clone(); IDLE.push({root,B,ph:hash(rig)});
    const b=new THREE.Mesh(new THREE.PlaneGeometry(1.5,1.1),new THREE.MeshBasicMaterial({map:blobTex,transparent:true,depthWrite:false,toneMapped:false})); b.rotation.x=-Math.PI/2; b.renderOrder=2; grp.add(b); BLOB.push({b,node:root}); }
  const center=new THREE.Vector3(...M.cam[0].slice(3,6));
  return {...sg,M,E,grp,LT,mixer,ACTS,tracked,IDLE,BLOB,FACE,center,dyn:dyn.scene};
}
const _q=new THREE.Quaternion(), _pq=new THREE.Quaternion(), _ax=new THREE.Vector3();
function rot(bone,axis,ang){ if(!bone||!ang) return; bone.parent.getWorldQuaternion(_pq); _ax.copy(axis).applyQuaternion(_pq.invert()).normalize(); bone.quaternion.premultiply(_q.setFromAxisAngle(_ax,ang)); bone.updateMatrixWorld(true); }
function idle(S,t){
  for(const I of S.IDLE){ const {B,root,ph}=I; for(const k in B) if(!S.tracked.has(B[k].name)) B[k].quaternion.copy(B[k].userData.base);
    root.updateMatrixWorld(true); const rq=new THREE.Quaternion(); root.getWorldQuaternion(rq);
    const up=new THREE.Vector3(0,1,0), fwd=new THREE.Vector3(0,0,1).applyQuaternion(rq), side=new THREE.Vector3(1,0,0).applyQuaternion(rq), br=Math.sin(2*Math.PI*t/3.6+ph);
    rot(B.spine,side,0.35*D*Math.sin(2*Math.PI*t/4.2+ph)); rot(B.braidL,side,1.2*D*Math.sin(2*Math.PI*t/3.4+ph)); rot(B.braidR,side,1.2*D*Math.sin(2*Math.PI*t/3.6+ph+1));} }
const CUT=new Set(K.cuts); let active=null;
function dispose(obj){ obj.traverse(o=>{ if(o.geometry) o.geometry.dispose(); const ms=o.material?(Array.isArray(o.material)?o.material:[o.material]):[];
  for(const m of ms){ for(const k of ['map','lightMap','envMap']) if(m[k]&&m[k]!==tvTex&&!Object.values(PH).some(p=>p.t===m[k])&&m[k]!==blobTex) m[k].dispose(); m.dispose(); } }); obj.parent&&obj.parent.remove(obj); }
async function activate(sg){ if(active&&active.id===sg.id) return; const tl0=performance.now();
  if(active){ dispose(active.grp); if(active.env!==sg.env){ const E=ENV[active.env]; dispose(E.group); E.tex.forEach(t=>t.dispose()); E.envMap.dispose(); delete ENV[active.env]; } }
  say(`Memuat segmen ${sg.id}…`);
  if(!ENV[sg.env]) await buildEnv(sg.env);
  const S=await buildSeg(sg); S.grp.visible=true; ENV[sg.env].group.visible=true; active=S;
  document.querySelectorAll('script[src^="data/env_"],script[src^="data/seg_"]').forEach(e=>e.remove());
  for(const k in LOADS) if(k.includes(`seg_${sg.id}.`)||k.includes(`env_${sg.env}.`)) delete LOADS[k];
  r.compile(scene,cam); tLoad+=performance.now()-tl0;
  const i=K.segments.findIndex(x=>x.id===sg.id), nx=K.segments[i+1];          // muat data segmen berikutnya di latar belakang
  if(nx){ load(`data/seg_${nx.id}.js`); if(nx.env!==sg.env) load(`data/env_${nx.env}.js`); } scene.background=ENV[sg.env].sky; scene.backgroundIntensity=1; r.toneMappingExposure=K.exposure[sg.env]??1.3; }
const v3=new THREE.Vector3();
async function pose(t){ // t = detik global
  const g=Math.min(K.nf-1,Math.floor(t*12+1e-6)); const sg=K.segments.find(s=>g>=s.F0-1&&g<=s.F1-1)||K.segments[K.segments.length-1]; await activate(sg); const S=active;
  const NF=S.M.cam.length, k=Math.max(0,Math.min(NF-1,g-(S.F0-1))); let u=t*12-g; if(k+1>=NF||CUT.has(g+1)) u=0;
  for(const A of S.ACTS) A.a.time=Math.min((k+u)/12,A.c.duration); S.mixer.update(0);
  for(const n in (S.M.objscale||{})){ const v=S.M.objscale[n], sc=v[Math.min(v.length-1,k)], o=S.dyn.getObjectByName(n.replace(/\./g,''))||S.dyn.getObjectByName(n);
    if(o){ const p=o.parent; let ps=1; if(p){ p.updateMatrixWorld(true); ps=new THREE.Vector3().setFromMatrixScale(p.matrixWorld).x||1; } const s=sc/ps; o.scale.setScalar(s); } }
  for(const rig in (S.M.rigpos||{})){ const P=S.M.rigpos[rig], a=P[k], b=P[Math.min(P.length-1,k+1)], n=S.dyn.getObjectByName(rig+'_pos')||S.dyn.getObjectByName(rig); if(!n) continue;
    n.position.set(lerp(a[0],b[0],u),lerp(a[1],b[1],u),lerp(a[2],b[2],u)); n.quaternion.set(a[3],a[4],a[5],a[6]).slerp(new THREE.Quaternion(b[3],b[4],b[5],b[6]),u); }
  const a=S.M.cam[k], b=S.M.cam[Math.min(NF-1,k+1)], c=a.map((x,i)=>lerp(x,b[i],u));
  cam.position.set(c[0],c[1],c[2]); cam.up.set(c[6],c[7],c[8]).normalize(); cam.lookAt(c[3],c[4],c[5]); cam.fov=c[9]; cam.updateProjectionMatrix();
  focusDist=Math.hypot(c[3]-c[0],c[4]-c[1],c[5]-c[2]);
  idle(S,t);
  const DU=ENV[S.env].DU; let di=0;
  for(const {o,l} of S.LT){ const f=l.frames[l.static?0:Math.min(k,l.frames.length-1)], E=f[0], col=new THREE.Color(f[1],f[2],f[3]); const p=new THREE.Vector3(f[4],f[5],f[6]), d=new THREE.Vector3(f[7],f[8],f[9]);
    if(l.type==='SUN'){ o.color.copy(col); o.intensity=E; o.target.position.copy(S.center); o.position.copy(S.center).addScaledVector(d,-30); continue; }
    const I=E/(4*Math.PI); o.color.copy(col); o.intensity=I; o.position.copy(p); if(o.target) o.target.position.copy(p).add(d);
    if(!l.static&&di<4){ DU.dPos.value[di].copy(p); DU.dCol.value[di].set(col.r*I,col.g*I,col.b*I); DU.dDir.value[di].copy(d).normalize(); DU.dCone.value[di].set(l.type==='SPOT'?Math.cos(l.size/2):-2,l.type==='SPOT'?Math.cos(l.size/2*(1-l.blend)):-1); di++; } }
  for(;di<4;di++) DU.dCol.value[di].set(0,0,0);
  for(const [n,ms] of Object.entries(ENV[S.env].emis)){ const e=S.M.emissive[n]; if(!e) continue; const v=e.frames[Math.min(k,e.frames.length-1)]; for(const mm of ms) mm.color.setRGB(v[0]*v[3],v[1]*v[3],v[2]*v[3]); }
  for(const rig in S.FACE){ const fc=S.M.faces[rig][k]; S.FACE[rig].u.eyeOff.value.copy(tile(fc[0])); S.FACE[rig].u.mouthOff.value.copy(tile(fc[1])); }
  S.grp.updateMatrixWorld(true);
  for(const B of S.BLOB){ B.node.getWorldPosition(v3); B.b.position.set(v3.x,v3.y+0.035,v3.z-0.02); B.b.visible=v3.z>-150; }
  await drawTV(t); drawPhone(t);
}
function wrap(ctx,txt,maxW){ const w=txt.split(' '), lines=[]; let cur=''; for(const x of w){ const tt=cur?cur+' '+x:x; if(ctx.measureText(tt).width>maxW&&cur){lines.push(cur);cur=x;} else cur=tt; } if(cur) lines.push(cur); return lines; }
function text(ctx,W,H,txt,yb,size){ const s=W/1080; ctx.font=`700 ${size*s}px DejaVuSub`; ctx.textAlign='center'; ctx.textBaseline='middle';
  const lines=wrap(ctx,txt,W*0.86), lh=size*s*1.2, y0=H*(1-yb)-(lines.length-1)*lh/2; ctx.lineJoin='round'; ctx.lineWidth=size*s*0.2; ctx.strokeStyle='#000'; ctx.fillStyle='#fff';
  lines.forEach((ln,i)=>{ctx.strokeText(ln,W/2,y0+i*lh);ctx.fillText(ln,W/2,y0+i*lh);}); }
const SMALL=document.createElement('canvas');
const SPK={nayla:['NAYLA','#ff6fa3'],dimas:['DIMAS','#3d8bff']};
function caption(ctx,W,H,s){ const k=W/1080, y=H*0.70; ctx.textAlign='center'; ctx.textBaseline='middle';
  if(SPK[s.spk]&&!s.narasi){ const [nm,col]=SPK[s.spk]; ctx.font=`600 ${26*k}px OswaldSub`; const tw=ctx.measureText(nm).width+28*k;
    ctx.fillStyle=col; ctx.beginPath(); ctx.roundRect(W/2-tw/2,y-74*k,tw,36*k,10*k); ctx.fill(); ctx.fillStyle='#fff'; ctx.fillText(nm,W/2,y-55*k); }
  ctx.font=`700 ${70*k}px OswaldSub`; ctx.lineJoin='round'; ctx.lineWidth=12*k; ctx.strokeStyle='rgba(0,0,0,.85)';
  ctx.shadowColor='rgba(0,0,0,.35)'; ctx.shadowBlur=10*k; ctx.strokeText(s.text,W/2,y); ctx.shadowBlur=0; ctx.fillStyle=s.narasi?'#ffe066':'#fff'; ctx.fillText(s.text,W/2,y); }
function composite(t){ const W=out.width,H=out.height; const ins=K.inserts.find(([a,b])=>t>=a&&t<b);
  if(ins){ const sm=SMALL; sm.width=Math.round(W/12); sm.height=Math.round(H/12); sm.getContext('2d').drawImage(r.domElement,0,0,sm.width,sm.height); octx.imageSmoothingQuality='high'; octx.drawImage(sm,0,0,W,H); octx.fillStyle='rgba(0,0,0,.45)'; octx.fillRect(0,0,W,H);
    const P=PH[ins[2]], pw=W*0.62, ph=pw*16/9, x0=(W-pw)/2, y0=(H-ph)/2-H*0.02, rr=pw*0.11, tilt=(ins[2]==='nayla'?-1:1)*0.035;
    octx.save(); octx.translate(W/2,H/2); octx.rotate(tilt); octx.translate(-W/2,-H/2);
    octx.fillStyle=ins[2]==='nayla'?'#E8B4C8':'#2C3E66'; octx.beginPath(); octx.roundRect(x0-pw*0.04,y0-pw*0.04,pw*1.08,ph+pw*0.08,rr*1.2); octx.fill();
    octx.fillStyle='#000'; octx.beginPath(); octx.roundRect(x0,y0,pw,ph,rr); octx.fill(); octx.save(); octx.beginPath(); octx.roundRect(x0,y0,pw,ph,rr); octx.clip();
    octx.drawImage(P.c,x0,y0,pw,ph); octx.restore(); octx.fillStyle='#000'; octx.beginPath(); octx.roundRect(W/2-pw*0.16,y0+pw*0.03,pw*0.32,pw*0.07,pw*0.035); octx.fill(); octx.restore(); }
  else octx.drawImage(r.domElement,0,0,W,H);
  for(const s of K.subs) if(t>=s.t0&&t<s.t1) caption(octx,W,H,s);
  if(t>=K.end.t0){ octx.fillStyle='#000'; octx.fillRect(0,0,W,H); text(octx,W,H,K.end.text,0.5,96); } }
function setRes(w){ const h=Math.round(w*16/9/2)*2; r.setSize(w,h,false); comp.setSize(w,h); out.width=w; out.height=h; cam.aspect=w/h; cam.updateProjectionMatrix(); return [w,h]; }
setRes(540); await pose(K.preview); draw3d(); composite(K.preview);
const ab=await (await fetch(MED.audio)).arrayBuffer(); const audioBuf=await new OfflineAudioContext(2,48000,48000).decodeAudioData(ab);
$('go').disabled=false; $('go').textContent='Mulai render'; say('Aset siap. Biarkan tab ini tetap terbuka dan terlihat selama render.');
async function pickVideo(w,h,fps){ const bitrate=Math.round(w*h*fps*0.25);
  for(const hw of ['prefer-hardware','no-preference']) for(const [codec,kind] of [['avc1.640028','avc'],['avc1.4d0028','avc'],['avc1.640033','avc'],['vp09.00.40.08','vp9']]){
    const cfg={codec,width:w,height:h,bitrate,framerate:fps,hardwareAcceleration:hw,latencyMode:'quality'}; if(kind==='avc') cfg.avc={format:'avc'};
    try{ if((await VideoEncoder.isConfigSupported(cfg)).supported) return {cfg,kind,hw}; }catch(e){} }
  throw new Error('Tidak ada codec video yang didukung.'); }
async function pickAudio(sr,ch){ for(const [codec,kind] of [['mp4a.40.2','aac'],['opus','opus']]){ const cfg={codec,sampleRate:sr,numberOfChannels:ch,bitrate:192000};
    try{ if((await AudioEncoder.isConfigSupported(cfg)).supported) return {cfg,kind}; }catch(e){} } return null; }
const fmt=s=>s<60?`${s.toFixed(1)} dtk`:s<3600?`${Math.floor(s/60)} mnt ${Math.round(s%60)} dtk`:`${Math.floor(s/3600)} jam ${Math.round(s%3600/60)} mnt`;
$('go').onclick=async()=>{
  $('go').disabled=true; $('dl').style.display='none'; const old=$('frame').querySelector('video'); if(old){old.remove(); out.style.display='';}
  try{
    const {fps,res}=opt, [w,h]=setRes(res), DUR=K.total, N=Math.round(DUR*fps);
    const V=await pickVideo(w,h,fps), A=await pickAudio(audioBuf.sampleRate,audioBuf.numberOfChannels);
    $('enc').textContent=`${V.cfg.codec} · ${V.hw==='prefer-hardware'?'hardware':'otomatis'} · ${(V.cfg.bitrate/1e6).toFixed(1)} Mbps`; $('aenc').textContent=A?`${A.cfg.codec} · 192 kbps`:'tidak ada';
    const muxer=new Muxer({target:new ArrayBufferTarget(),video:{codec:V.kind,width:w,height:h,frameRate:fps},audio:A?{codec:A.kind,numberOfChannels:audioBuf.numberOfChannels,sampleRate:audioBuf.sampleRate}:undefined,fastStart:'in-memory',firstTimestampBehavior:'offset'});
    let err=null; const enc=new VideoEncoder({output:(c,m)=>muxer.addVideoChunk(c,m),error:e=>err=e}); enc.configure(V.cfg);
    const t0=performance.now(); let tR=0; tLoad=0;
    for(let i=0;i<N;i++){ if(err) throw err; const t=i/fps, a=performance.now(); await pose(t); draw3d(); composite(t); tR+=performance.now()-a;
      const vf=new VideoFrame(out,{timestamp:Math.round(i*1e6/fps),duration:Math.round(1e6/fps)}); enc.encode(vf,{keyFrame:i%(fps*2)===0}); vf.close();
      while(enc.encodeQueueSize>4) await new Promise(q=>setTimeout(q,1));
      if(i%4===0||i===N-1){ $('prog').style.width=`${(i+1)/N*100}%`; $('st_f').textContent=`${i+1} / ${N}`; await new Promise(q=>setTimeout(q,0)); } }
    await enc.flush(); enc.close();
    if(A){ let aerr=null; const ae=new AudioEncoder({output:(c,m)=>muxer.addAudioChunk(c,m),error:e=>aerr=e}); ae.configure(A.cfg);
      const sr=audioBuf.sampleRate, ch=audioBuf.numberOfChannels, len=Math.min(audioBuf.length,Math.round(DUR*sr)), B=1024;
      for(let s=0;s<len;s+=B){ const n=Math.min(B,len-s), d=new Float32Array(n*ch); for(let c=0;c<ch;c++) d.set(audioBuf.getChannelData(c).subarray(s,s+n),c*n);
        const ad=new AudioData({format:'f32-planar',sampleRate:sr,numberOfFrames:n,numberOfChannels:ch,timestamp:Math.round(s/sr*1e6),data:d}); ae.encode(ad); ad.close(); if(aerr) throw aerr; if(ae.encodeQueueSize>16) await new Promise(q=>setTimeout(q,0)); }
      await ae.flush(); ae.close(); }
    muxer.finalize(); const total=(performance.now()-t0)/1000, per=total/N;
    $('st_ms').textContent=`${(per*1000).toFixed(0)} ms/frame (gambar ${((tR-tLoad)/N).toFixed(0)} ms, memuat segmen ${(tLoad/1000).toFixed(1)} dtk total)`; $('st_t').textContent=`${fmt(total)} untuk ${N} frame`; $('st_ep').textContent=`${fmt(per*190*fps)} (${190*fps} frame)`;
    const blob=new Blob([muxer.target.buffer],{type:'video/mp4'}), url=URL.createObjectURL(blob), name=`${K.slug}_${fps}fps_${h}p.mp4`;
    const v=document.createElement('video'); v.src=url; v.controls=true; v.playsInline=true; out.style.display='none'; $('frame').appendChild(v);
    const stats=`GPU: ${$('gpu').textContent}\nVideo: ${$('enc').textContent}\nAudio: ${$('aenc').textContent}\nResolusi: ${w}x${h}, ${fps} fps\nFrame: ${N}\nRata-rata: ${$('st_ms').textContent}\nTotal: ${$('st_t').textContent}\nUkuran MP4: ${(blob.size/1e6).toFixed(2)} MB\n`;
    $('dl').innerHTML=`<a href="${url}" download="${name}">Unduh MP4 (${(blob.size/1e6).toFixed(1)} MB)</a><a href="${URL.createObjectURL(new Blob([stats],{type:'text/plain'}))}" download="${name.replace('.mp4','_statistik.txt')}">Unduh statistik</a>`;
    $('dl').style.display='flex'; say('Selesai. Putar videonya di samping, lalu unduh MP4 dan statistiknya.'); window.__result={size:blob.size,total,per,codec:V.cfg.codec,audio:A&&A.cfg.codec};
  }catch(e){ console.error(e); say('Gagal: '+(e.message||e),true); window.__result={error:String(e)}; }
  $('go').disabled=false; $('go').textContent='Render lagi';
};
window.__poseOnly=async t=>{ await pose(t); };
window.__snap=async(t,w)=>{ setRes(w||540); await pose(t); draw3d(); composite(t); return out.toDataURL('image/png'); };
window.__ready=true;
