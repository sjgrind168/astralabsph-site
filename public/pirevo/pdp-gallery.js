(()=>{
const main=document.querySelector("[data-pdp-main-image]");
const wrap=document.querySelector(".pdp-image-wrap");
const thumbs=[...document.querySelectorAll(".pdp-thumb")];
if(!main||!thumbs.length)return;
function select(btn){
  const src=btn.dataset.full;
  if(!src||btn.classList.contains("active"))return;
  thumbs.forEach(x=>{x.classList.remove("active");x.setAttribute("aria-pressed","false")});
  btn.classList.add("active");btn.setAttribute("aria-pressed","true");
  wrap?.classList.add("is-switching");
  const probe=new Image();
  probe.onload=()=>{main.src=src;main.alt=btn.dataset.alt||main.alt;wrap?.classList.remove("is-switching")};
  probe.onerror=()=>{const fallback=btn.querySelector("img")?.src;if(fallback)main.src=fallback;wrap?.classList.remove("is-switching")};
  probe.src=src;
}
thumbs.forEach(b=>b.addEventListener("click",()=>select(b)));
})();