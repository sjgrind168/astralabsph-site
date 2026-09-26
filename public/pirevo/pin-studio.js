const pins=window.PIREVO_PINS||[],grid=document.querySelector("#pinGrid");
function esc(s){return String(s).replace(/[&<>"']/g,m=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[m]))}
function wrap(ctx,text,x,y,max,lineH,maxLines=6){const words=text.split(/\s+/),lines=[];let line="";for(const w of words){const test=line?line+" "+w:w;if(ctx.measureText(test).width>max&&line){lines.push(line);line=w}else line=test}if(line)lines.push(line);lines.slice(0,maxLines).forEach((l,i)=>ctx.fillText(l,x,y+i*lineH));return y+Math.min(lines.length,maxLines)*lineH}
async function downloadPin(p){
 const img=new Image();img.crossOrigin="anonymous";img.src=p.image;
 await img.decode();
 const c=document.createElement("canvas"),ctx=c.getContext("2d");c.width=1000;c.height=1500;
 const scale=Math.max(c.width/img.width,c.height/img.height),w=img.width*scale,h=img.height*scale;
 ctx.drawImage(img,(c.width-w)/2,(c.height-h)/2,w,h);
 const g=ctx.createLinearGradient(0,0,0,980);g.addColorStop(0,"rgba(249,246,238,.96)");g.addColorStop(.42,"rgba(249,246,238,.78)");g.addColorStop(1,"rgba(249,246,238,0)");ctx.fillStyle=g;ctx.fillRect(0,0,1000,1000);
 ctx.fillStyle="#111";ctx.font="900 44px Arial";ctx.fillText("PIREVO",74,92);
 ctx.font="600 20px Arial";ctx.letterSpacing="4px";ctx.fillText("SMART FINDS WORTH DISCOVERING",76,128);
 ctx.letterSpacing="0px";ctx.fillStyle="#c9ff64";ctx.beginPath();ctx.roundRect(72,165,Math.min(430,140+p.category.length*12),58,29);ctx.fill();
 ctx.fillStyle="#111";ctx.font="800 23px Arial";ctx.fillText(p.category,98,202);
 ctx.font="900 68px Arial";wrap(ctx,p.title,72,320,840,76,6);
 ctx.fillStyle="rgba(245,255,224,.96)";ctx.beginPath();ctx.roundRect(72,1368,856,78,39);ctx.fill();
 ctx.fillStyle="#111";ctx.font="800 26px Arial";ctx.fillText("Read the full guide →",112,1418);ctx.font="500 23px Arial";ctx.fillText("astralabsph.com/pirevo",500,1418);
 c.toBlob(blob=>{const a=document.createElement("a");a.href=URL.createObjectURL(blob);a.download=p.id+"-"+p.slug+".png";a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1500)},"image/png");
}
pins.forEach(p=>{
 const card=document.createElement("article");card.className="photo-pin-card";
 card.innerHTML=`<div class="photo-pin"><img src="${esc(p.image)}" alt="${esc(p.title)}" loading="lazy" crossorigin="anonymous"><div class="photo-pin-shade"></div><div class="photo-pin-copy"><div class="pin-brand">PIREVO<span>SMART FINDS WORTH DISCOVERING</span></div><div class="pin-category">${esc(p.category)}</div><h2>${esc(p.title)}</h2><div class="pin-cta">Read the full guide → <span>astralabsph.com/pirevo</span></div></div></div><div class="pin-meta"><strong>${esc(p.board)}</strong><span>Photo-forward editorial pin</span><button>Download ${esc(p.id)} PNG</button></div>`;
 card.querySelector("button").onclick=()=>downloadPin(p);
 grid.append(card);
});