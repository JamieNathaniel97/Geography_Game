window.addEventListener('error',e=>{document.title='ERR '+e.message+' @'+e.lineno;});
function rnd(seed){return()=>{seed=(seed*16807)%2147483647;return seed/2147483647;};}
function run(m,g,label){
  m.draw(); const rect=m.canvas.getBoundingClientRect(); const P=m.projection(); const R=rnd(42);
  const sizeOk=Math.abs(rect.width-m.w)<1&&Math.abs(rect.height-m.h)<1;
  let n=0,ok=0; const fails={};
  const tap=(cx,cy,want)=>{const x=cx-rect.left,y=cy-rect.top; const got=m.resolveTap(x,y); n++; if(got===want) ok++; else {const k=want.iso+'>'+(got?got.iso:'nothing'); fails[k]=(fails[k]||0)+1;}};
  const onScreen=p=>p&&p[0]>2&&p[0]<m.w-2&&p[1]>2&&p[1]<m.h-2;
  for(const c of g.countries){ if(!m.active(c)) continue;
    // 1. points on the country's land
    if(c.feature){const b=c.bounds; let got=0,tries=0;
      while(got<10&&tries<400){tries++; let lon=b[0][0]+(((b[1][0]-b[0][0])+360)%360||360)*R(); if(lon>180)lon-=360; const lat=b[0][1]+(b[1][1]-b[0][1])*R();
        if(!d3.geoContains(c.feature,[lon,lat])||!m.visible([lon,lat])) continue; const p=P([lon,lat]); if(!onScreen(p)) continue;
        // skip points under another country's circle centre zone (those belong to the small country by design)
        if(m.hits.rings.some(r=>r.c!==c&&Math.hypot(r.x-p[0],r.y-p[1])<=r.d*0.3)) continue;
        tap(rect.left+p[0],rect.top+p[1],c); got++;}}
    // 2. points inside its island oval, on open sea (not on another country's land)
    const s=m.hits.islands.find(h=>h.c===c);
    if(s){let got=0,tries=0; const xs=s.pts.map(p=>p[0]),ys=s.pts.map(p=>p[1]);
      while(got<10&&tries<400){tries++; const x=d3.min(xs)+(d3.max(xs)-d3.min(xs))*R(), y=d3.min(ys)+(d3.max(ys)-d3.min(ys))*R();
        if(!d3.polygonContains(s.pts,[x,y])||!onScreen([x,y])) continue; const land=m.landAt(x,y); if(land&&land!==c) continue;
        // where ovals overlap, the nearest centre should win: only expect c if it's the nearest of the ovals here
        const here=m.hits.islands.filter(h=>d3.polygonContains(h.pts,[x,y])).sort((a,b)=>Math.hypot(a.x-x,a.y-y)-Math.hypot(b.x-x,b.y-y));
        if(here[0].c!==c) continue; tap(rect.left+x,rect.top+y,c); got++;}}
    // 3. points inside the inner part of its circle
    const r=m.hits.rings.find(h=>h.c===c);
    if(r){for(let i=0;i<10;i++){const a=R()*2*Math.PI, d=R()*r.d*0.28; const x=r.x+Math.cos(a)*d,y=r.y+Math.sin(a)*d; if(onScreen([x,y])) tap(rect.left+x,rect.top+y,c);}}
  }
  const top=Object.entries(fails).sort((a,b)=>b[1]-a[1]).slice(0,12).map(([k,v])=>k+'x'+v).join(' ');
  return label+': size '+(sizeOk?'OK':'MISMATCH')+', '+ok+'/'+n+' right ('+(100*ok/Math.max(1,n)).toFixed(1)+'%) '+top;
}

const SPOTS = { balkans:[20,42.5], benelux:[5,50.5], caribbean:[-63,14], gulf:[51,25.5], centralAmerica:[-86,13], pacific:[175,-10] };
setTimeout(async()=>{try{const m=GG.debug.main,g=GG.debug.geo,$=id=>document.getElementById(id),out=[];
  GG.debug.startGame('find','world','flat');
  for (const [name,[lon,lat]] of Object.entries(SPOTS)) {
    m.lookAt(lon,lat,40,false); await new Promise(r=>setTimeout(r,200));
    const r=m.canvas.getBoundingClientRect(), p=m.projection()([lon,lat]);
    $('magBtn').click(); m.canvas.dispatchEvent(new MouseEvent('click',{clientX:r.left+p[0],clientY:r.top+p[1],bubbles:true}));
    await new Promise(r=>setTimeout(r,300));
    const v=GG.debug.inset(); out.push(name+' '+run(v,g,'magnifier'));
    $('insetClose').click();
  }
  // a real answer through the magnifier: make Belgium the question, magnify Benelux, tap Belgium once
  let guard=0; while($('target').textContent!=='Belgium' && guard<200){$('fwd').click(); guard++;}
  m.lookAt(5,50.5,40,false); await new Promise(r=>setTimeout(r,200));
  const r=m.canvas.getBoundingClientRect(), p=m.projection()([5,50.5]);
  $('magBtn').click(); m.canvas.dispatchEvent(new MouseEvent('click',{clientX:r.left+p[0],clientY:r.top+p[1],bubbles:true}));
  await new Promise(r=>setTimeout(r,300));
  const v=GG.debug.inset(), ir=v.canvas.getBoundingClientRect(), bp=v.projection()(g.byIso.BEL.anchor);
  v.canvas.dispatchEvent(new MouseEvent('click',{clientX:ir.left+bp[0],clientY:ir.top+bp[1],bubbles:true}));
  out.push('real answer: Belgium '+m.opts.getState(g.byIso.BEL)+', score '+$('score').textContent+', magnifier closed '+$('inset').hidden);
  document.title=out.join(' || ');
}catch(e){document.title='dbg '+e.message+' '+e.stack;}},4000);
