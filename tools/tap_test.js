window.addEventListener('error',e=>{document.title='ERR '+e.message+' @'+e.lineno;});
// Tap test: real screen coordinates through the same path as a finger tap (clientX - canvas left).
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
setTimeout(()=>{try{const m=GG.debug.main,g=GG.debug.geo; const out=[];
  const t0=m.t; out.push(run(m,g,'start'));
  const zoomIn=f=>{const t=d3.zoomIdentity.translate(m.w/2-(m.w/2-m.t.x)*f, m.h/2-(m.h/2-m.t.y)*f).scale(m.t.k*f); m.sel.call(m.zoom.transform,t);};
  zoomIn(2.5); out.push(run(m,g,'zoom x2.5'));
  zoomIn(3); out.push(run(m,g,'zoom x7.5'));
  document.title=out.join(' || ');}catch(e){document.title='dbg '+e.message+' '+e.stack;}},6000);
