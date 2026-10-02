const cast = {
      mara:{name:'MARA', side:'left', skin:'#f0c0a2', hair:'#271517', outfit:'#c8a04d', accent:'#f2d18c'},
      adrian:{name:'ADRIAN', side:'right', skin:'#e7b28e', hair:'#5f2b24', outfit:'#10151d', accent:'#d9dfe9'},
      celeste:{name:'CELESTE', side:'right', skin:'#f0bea4', hair:'#341821', outfit:'#8e2138', accent:'#f2b7c5'},
      victor:{name:'VICTOR', side:'center', skin:'#dfb08d', hair:'#4a4546', outfit:'#1a1d24', accent:'#dbc7a3'}
    };
    const scenes = [
      {id:1,d:4,shot:'Extreme Close-Up',action:"Champagne trembles on Mara's tray as the ballroom lights flare.",speaker:'mara',line:'That ring was supposed to be mine.',mood:'dread • ballroom reveal',bg:'hall',chars:['mara']},
      {id:2,d:5,shot:'Wide Reveal',action:'Adrian steps onto the gold-lit stage beside Celeste. He sees Mara in the crowd.',speaker:'host',line:'Tonight, the Vale family welcomes a new bride.',mood:'public humiliation',bg:'hall',chars:['mara','adrian']},
      {id:3,d:5,shot:'Two-Shot',action:'Mara corners Adrian in a mirrored service hall as red light cuts between them.',speaker:'mara',line:'Did our vow expire when you got rich?',mood:'confrontation',bg:'glass',chars:['mara','adrian']},
      {id:4,d:5,shot:'Handheld Close-Up',action:'Adrian reveals the matching ring on a chain beneath his shirt.',speaker:'adrian',line:'I disappeared to keep you alive.',mood:'intimate reveal',bg:'glass',chars:['mara','adrian']},
      {id:5,d:4,shot:'Dutch Angle',action:'Behind frosted glass, Celeste has heard every word.',speaker:'celeste',line:'So the rumors were true.',mood:'suspicion',bg:'glass',chars:['mara','celeste']},
      {id:6,d:5,shot:'Crash Zoom',action:"The elevator doors open. Victor Vale lifts a sealed marriage certificate.",speaker:'victor',line:'Tell your wife why her name is on my death list.',mood:'cliffhanger',bg:'elevator',chars:['victor']}
    ];

    const q=s=>document.querySelector(s);
    const sceneList=q('#sceneList');
    const total = scenes.reduce((a,s)=>a+s.d,0);
    q('#timeTotal').textContent = fmt(total);
    q('#storyMeta').textContent = scenes.length+' scenes • ~'+total+' sec';

    function fmt(sec){sec=Math.max(0,Math.floor(sec)); return Math.floor(sec/60)+':'+String(sec%60).padStart(2,'0');}
    function sceneAt(t){let a=0; for(let i=0;i<scenes.length;i++){if(t < a + scenes[i].d) return {scene: scenes[i], index:i, start:a}; a += scenes[i].d;} return {scene:scenes[scenes.length-1], index:scenes.length-1, start: total-scenes[scenes.length-1].d};}
    sceneList.innerHTML = scenes.map(s=>'<div class="scene-item" data-id="'+s.id+'"><div class="scene-no">'+String(s.id).padStart(2,'0')+'</div><div class="scene-copy"><b>'+s.shot+'</b><p>'+s.action+'</p><span>'+speakerName(s.speaker)+': '+s.line+'</span></div><div class="scene-dur">'+s.d+'s</div></div>').join('');
    sceneList.addEventListener('click', e=>{const row=e.target.closest('.scene-item'); if(!row) return; const s=scenes.find(x=>x.id==row.dataset.id); restartTo(sceneStart(s.id));});
    function sceneStart(id){let t=0; for(const s of scenes){ if(s.id===id) return t; t+=s.d;} return 0;}
    function speakerName(k){return k==='host'?'HOST':cast[k]?.name||k.toUpperCase();}

    function renderChar(c){
      if(!c) return '';
      const isMale = c.name==='ADRIAN' || c.name==='VICTOR';
      const hairSide = isMale ? '<path d="M80 207 Q110 236 140 207" fill="#11151d"/>' : '<path d="M68 106 C44 155,57 214,73 236 C88 224,96 215,97 198 C73 179,63 137,68 106" fill="'+c.hair+'"/><path d="M152 110 C177 153,164 214,148 240 C131 226,124 214,123 198 C148 179,158 140,152 110" fill="'+c.hair+'"/>';
      return '<svg viewBox="0 0 220 420" aria-hidden="true"><defs><linearGradient id="coat-'+c.name+'" x1="0" x2="1"><stop offset="0" stop-color="'+c.outfit+'"/><stop offset="1" stop-color="#05070b"/></linearGradient></defs><ellipse cx="110" cy="390" rx="78" ry="18" fill="rgba(0,0,0,.28)"/><path d="M42 385 C55 275,70 220,110 220 C150 220,165 275,178 385" fill="url(#coat-'+c.name+')"/><path d="M87 220 L133 220 L146 272 L74 272 Z" fill="'+(c.outfit==='#10151d'?'#f8f8f6':'#171d26')+'" opacity=".92"/><circle cx="110" cy="132" r="56" fill="'+c.skin+'"/><path d="M57 134 C60 74,89 40,138 50 C166 56,169 92,162 131 C146 108,121 96,85 98 C73 99,65 115,57 134" fill="'+c.hair+'"/>'+hairSide+'<ellipse class="eye" cx="90" cy="138" rx="7" ry="4" fill="#1d1615"/><ellipse class="eye" cx="128" cy="138" rx="7" ry="4" fill="#1d1615"/><path d="M100 160 Q110 167 120 160" stroke="#a86863" stroke-width="2.6" fill="none" stroke-linecap="round"/><g transform="translate(95,177)"><ellipse class="mouth" cx="15" cy="5" rx="14" ry="5" fill="#7d3644"/><ellipse cx="15" cy="3" rx="12" ry="2" fill="#d77b89" opacity=".52"/></g><path d="M77 121 Q90 114 101 121" stroke="#3d1d1e" stroke-width="3" fill="none" stroke-linecap="round"/><path d="M119 121 Q130 114 143 121" stroke="#3d1d1e" stroke-width="3" fill="none" stroke-linecap="round"/><path d="M68 284 Q108 260 151 286 L164 385 L56 385 Z" fill="'+c.outfit+'" opacity=".96"/><path d="M99 216 Q110 227 122 216" stroke="'+c.accent+'" stroke-width="2.4" fill="none"/></svg>';
    }

    const nodes = {
      sceneTag:q('#sceneTag'), shot:q('#sceneShot'), action:q('#sceneAction'), speaker:q('#speaker'), line:q('#line'), mood:q('#mood'),
      left:q('#charLeft'), right:q('#charRight'), center:q('#charCenter'), seek:q('#seek'), now:q('#timeNow'), play:q('#playBtn'), playTop:q('#playTop')
    };
    nodes.seek.max = total;
    let elapsed = 0, playing = false, startMs = 0, raf=0, lastIdx=-1;
    let voices = [];
    function loadVoices(){voices = speechSynthesis.getVoices ? speechSynthesis.getVoices() : [];}
    if('speechSynthesis' in window){loadVoices(); speechSynthesis.onvoiceschanged = loadVoices;}
    function pickVoice(type){ if(!voices.length) return null; const female = voices.find(v=>/female|zira|samantha|ava|victoria|karen|moira|ting-ting/i.test(v.name)); const male = voices.find(v=>/male|daniel|alex|fred|jorge|thomas|tom|lekha/i.test(v.name)); return type==='female' ? (female||voices[0]) : (male||voices[0]); }
    function speak(scene){ if(!q('#voiceToggle').checked || !('speechSynthesis' in window)) return; speechSynthesis.cancel(); const u = new SpeechSynthesisUtterance(scene.line); const voice = scene.speaker==='mara'||scene.speaker==='celeste' ? pickVoice('female') : pickVoice('male'); if(voice) u.voice = voice; u.rate=.96; u.pitch= scene.speaker==='victor' ? .82 : scene.speaker==='mara' ? 1.05 : .92; speechSynthesis.speak(u); }
    function sfx(freq=85){ if(!q('#sfxToggle').checked) return; const AC = window.AudioContext || window.webkitAudioContext; if(!AC) return; const ac = new AC(); const osc = ac.createOscillator(); const gain = ac.createGain(); osc.type='triangle'; osc.frequency.setValueAtTime(freq, ac.currentTime); osc.frequency.exponentialRampToValueAtTime(freq*.55, ac.currentTime+.33); gain.gain.setValueAtTime(.0001, ac.currentTime); gain.gain.exponentialRampToValueAtTime(.07, ac.currentTime+.03); gain.gain.exponentialRampToValueAtTime(.0001, ac.currentTime+.33); osc.connect(gain); gain.connect(ac.destination); osc.start(); osc.stop(ac.currentTime+.35); setTimeout(()=>ac.close(),420); }

    function updateVisual(){
      const {scene,index} = sceneAt(elapsed);
      nodes.sceneTag.textContent = 'Scene '+(index+1)+' / '+scenes.length;
      nodes.shot.textContent = scene.shot;
      nodes.action.textContent = scene.action;
      nodes.speaker.textContent = speakerName(scene.speaker);
      nodes.line.textContent = scene.line;
      nodes.mood.textContent = scene.mood;
      q('#bg').style.transform = 'scale('+(1 + ((elapsed - sceneStart(scene.id))/scene.d)*0.05)+')';
      document.querySelectorAll('.scene-item').forEach((el,i)=>el.classList.toggle('active', i===index));
      const slots = {left:null,right:null,center:null};
      scene.chars.forEach(k=>{ const c = cast[k]; if(!c) return; const pos = c.side === 'center' || scene.chars.length===1 && k==='victor' ? 'center' : c.side; slots[pos]=c; });
      if(scene.id===5){ slots.left = cast.mara; slots.right = cast.celeste; slots.center = null; }
      if(scene.id===6){ slots.left=null; slots.right=null; slots.center=cast.victor; }
      ['left','right','center'].forEach(pos=>{
        const el = nodes[pos], c = slots[pos];
        if(c){ el.style.display='block'; el.innerHTML = renderChar(c); el.className = 'char '+pos; }
        else { el.style.display='none'; el.innerHTML=''; }
      });
      const activePos = scene.speaker==='mara' ? 'left' : scene.speaker==='adrian' ? 'right' : scene.speaker==='celeste' ? 'right' : scene.speaker==='victor' ? 'center' : null;
      ['left','right','center'].forEach(pos=>{
        const el=nodes[pos]; if(el.style.display==='none') return;
        el.classList.toggle('active', pos===activePos);
        el.classList.toggle('speaking', pos===activePos);
        if(pos!==activePos) el.classList.remove('speaking');
        if(scene.id===5 && pos==='left') el.classList.add('fade');
        if(scene.id===5 && pos==='right') el.classList.add('active');
      });
    }

    function tick(ts){ if(!playing) return; elapsed = (ts - startMs)/1000; if(elapsed>=total){ elapsed=total; updateTime(); updateVisual(); stop(false); return; } const {index,scene} = sceneAt(elapsed); if(index !== lastIdx){ lastIdx=index; updateVisual(); speak(scene); sfx(index===scenes.length-1?58:88+index*8); } updateTime(); raf=requestAnimationFrame(tick); }
    function updateTime(){ nodes.seek.value = elapsed; nodes.now.textContent = fmt(elapsed); }
    function play(){ if(elapsed>=total) elapsed=0; playing=true; startMs = performance.now()-elapsed*1000; lastIdx=-1; nodes.play.textContent='❚❚'; nodes.playTop.textContent='Pause'; raf=requestAnimationFrame(tick); }
    function stop(cancelSpeech=true){ playing=false; cancelAnimationFrame(raf); nodes.play.textContent='▶'; nodes.playTop.textContent='Play'; if(cancelSpeech && 'speechSynthesis' in window) speechSynthesis.cancel(); }
    function togglePlay(){ if(playing) stop(); else play(); }
    function restartTo(t=0){ stop(); elapsed=t; updateTime(); updateVisual(); }
    q('#playBtn').onclick = togglePlay;
    q('#playTop').onclick = togglePlay;
    q('#restartBtn').onclick = ()=>restartTo(0);
    q('#replayTop').onclick=()=>restartTo(0);
    q('#nextSceneTop').onclick=()=>{ const cur = sceneAt(elapsed); const next = Math.min(scenes.length-1, cur.index+1); restartTo(sceneStart(scenes[next].id)); };
    nodes.seek.oninput = e=>{ elapsed = Number(e.target.value); updateTime(); updateVisual(); if(playing){ stop(false); play(); } };
    updateVisual(); updateTime();