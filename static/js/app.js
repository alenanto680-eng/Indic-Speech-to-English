const LANGS=[["hi","Hindi","हिन्दी"],["kn","Kannada","ಕನ್ನಡ"],["ta","Tamil","தமிழ்"],
["te","Telugu","తెలుగు"],["ml","Malayalam","മലയാളം"],["bn","Bengali","বাংলা"],
["mr","Marathi","मराठी"],["gu","Gujarati","ગુજરાતી"],["pa","Punjabi","ਪੰਜਾਬੀ"],
["or","Odia","ଓଡ଼ିଆ"],["ur","Urdu","اردو"]];
const $=id=>document.getElementById(id);
let lang="ml", speed="fast", running=false;
let ctx, proc, stream, buf=[], bufLen=0, speaking=false, silentSamples=0, queue=Promise.resolve();
const SR=16000, THRESH=0.012, SILENCE_END=0.7*SR, MAX_CHUNK=8*SR;

for(const id of ["bl","br"]){for(let i=0;i<6;i++){const s=document.createElement("span");
 s.style.animationDelay=(i*0.12)+"s";$(id).appendChild(s);}}

LANGS.forEach(([c,n,nat])=>{const d=document.createElement("div");d.className="it";
 d.innerHTML=`<div class="flag"></div><div class="nm"><b>${n}</b><small style="display:block;color:var(--muted)">${nat}</small></div>`;
 d.onclick=()=>{lang=c;$("lname").textContent=n;$("lnat").textContent=nat;$("menu").classList.remove("open");};
 $("menu").appendChild(d);});
$("sel").onclick=e=>{e.stopPropagation();$("menu").classList.toggle("open");};
document.onclick=()=>$("menu").classList.remove("open");

document.querySelectorAll("#seg button").forEach(b=>b.onclick=()=>{
 document.querySelectorAll("#seg button").forEach(x=>x.classList.remove("on"));
 b.classList.add("on");speed=b.dataset.v;});

$("theme").onclick=()=>{const h=document.documentElement;
 h.dataset.theme=h.dataset.theme==="dark"?"light":"dark";};

function flush(){
  if(!bufLen){return;}
  const all=new Float32Array(bufLen);let o=0;
  for(const b of buf){all.set(b,o);o+=b.length;}
  buf=[];bufLen=0;speaking=false;silentSamples=0;
  const l=lang, s=speed;
  queue=queue.then(async()=>{
    try{
      $("state").textContent="Listening... (processing)";
      const r=await(await fetch(`/chunk?lang=${l}&speed=${s}`,{method:"POST",body:all.buffer})).json();
      if(r.english){
        if($("en").querySelector(".ph")){$("en").textContent="";$("nat").textContent="";}
        $("en").textContent+=($("en").textContent?" ":"")+r.english;
        $("nat").textContent+=($("nat").textContent?" ":"")+r.native;
        $("en").scrollTop=$("en").scrollHeight;
        $("time").textContent=r.sec.toFixed(2)+" s";
      }
    }catch(e){console.error(e);}
    if(running)$("state").textContent="Listening... speak now";
  });
}

$("mic").onclick=async()=>{
  if(!running){
    try{
      stream=await navigator.mediaDevices.getUserMedia({audio:{echoCancellation:true,noiseSuppression:true}});
    }catch(e){$("state").textContent="Microphone blocked. Allow it in Chrome.";return;}
    ctx=new AudioContext({sampleRate:SR});
    const src=ctx.createMediaStreamSource(stream);
    proc=ctx.createScriptProcessor(4096,1,1);
    proc.onaudioprocess=e=>{
      const d=new Float32Array(e.inputBuffer.getChannelData(0));
      let sum=0;for(let i=0;i<d.length;i++)sum+=d[i]*d[i];
      const loud=Math.sqrt(sum/d.length)>THRESH;
      if(loud){speaking=true;silentSamples=0;}
      else if(speaking){silentSamples+=d.length;}
      if(speaking){buf.push(d);bufLen+=d.length;
        if(silentSamples>=SILENCE_END||bufLen>=MAX_CHUNK)flush();}
    };
    src.connect(proc);proc.connect(ctx.destination);
    running=true;$("mic").classList.add("rec");
    $("bl").classList.add("live");$("br").classList.add("live");
    $("state").textContent="Listening... speak now";
  }else{
    running=false;flush();
    proc.disconnect();stream.getTracks().forEach(t=>t.stop());ctx.close();
    $("mic").classList.remove("rec");$("bl").classList.remove("live");$("br").classList.remove("live");
    $("state").textContent="Tap to start speaking";
  }
};

const PH_EN='<span class="ph">Speak in your language. The English text appears here as you talk.</span>';
const PH_NAT='<span class="ph">What the speech model heard.</span>';
$("clear").onclick=()=>{$("en").innerHTML=PH_EN;$("nat").innerHTML=PH_NAT;$("time").textContent="0.00 s";};
$("copy").onclick=async()=>{
  if(!$("en").querySelector(".ph")){await navigator.clipboard.writeText($("en").textContent);
  $("copy").textContent="Copied!";setTimeout(()=>$("copy").textContent="Copy English",1200);}};
