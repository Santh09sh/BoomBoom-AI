html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>BoomBoom AI — Pitch Deck</title>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;900&family=Lato:wght@300;400;700&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box}
:root{--black:#0a0a0a;--green:#11CAA0;--coral:#FF823A;--white:#f0f0f0;--grey:#888}
body{background:#000;font-family:'Lato',sans-serif;overflow:hidden}
.deck{width:100vw;height:100vh;position:relative}
.slide{position:absolute;inset:0;background:var(--black);display:none;padding:60px 80px;flex-direction:column;justify-content:center}
.slide.active{display:flex}
h1{font-family:'Poppins',sans-serif;font-size:2.8rem;font-weight:900;color:var(--white);line-height:1.2}
h2{font-family:'Poppins',sans-serif;font-size:2rem;font-weight:700;color:var(--white)}
h3{font-family:'Poppins',sans-serif;font-size:1.3rem;font-weight:600}
p,li{font-family:'Lato',sans-serif;font-size:1rem;color:#ccc;line-height:1.7}
.green{color:var(--green)}
.coral{color:var(--coral)}
.tag{display:inline-block;padding:4px 14px;border-radius:20px;font-size:.75rem;font-weight:700;letter-spacing:1px;margin-bottom:18px}
.tag-green{background:rgba(17,202,160,.15);color:var(--green);border:1px solid var(--green)}
.tag-coral{background:rgba(255,130,58,.15);color:var(--coral);border:1px solid var(--coral)}

/* NAV */
.nav{position:fixed;bottom:32px;left:50%;transform:translateX(-50%);display:flex;gap:12px;align-items:center;z-index:99}
.nav button{background:none;border:1px solid #333;color:#888;padding:8px 20px;border-radius:30px;cursor:pointer;font-family:'Lato',sans-serif;font-size:.85rem;transition:all .2s}
.nav button:hover,.nav button.active-btn{border-color:var(--green);color:var(--green)}
.nav .dots{display:flex;gap:8px}
.dot{width:8px;height:8px;border-radius:50%;background:#333;cursor:pointer;transition:all .2s}
.dot.on{background:var(--green);width:24px;border-radius:4px}
.slide-num{position:fixed;top:24px;right:40px;font-size:.75rem;color:#444;font-family:'Poppins',sans-serif}

/* GRID CARDS */
.cards{display:grid;gap:24px}
.cards.two{grid-template-columns:1fr 1fr}
.cards.three{grid-template-columns:1fr 1fr 1fr}
.card{background:#111;border:1px solid #1e1e1e;border-radius:16px;padding:28px;transition:border-color .2s}
.card:hover{border-color:#2a2a2a}
.card-icon{width:48px;height:48px;border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:1.4rem;margin-bottom:16px}
.card-icon.g{background:rgba(17,202,160,.12)}
.card-icon.c{background:rgba(255,130,58,.12)}

/* SECTION SLIDE */
.section-slide{background:linear-gradient(135deg,#0a0a0a 0%,#0d1a16 100%)}
.section-slide .big{font-size:3.5rem;font-weight:900;font-family:'Poppins',sans-serif;line-height:1.1}
.section-slide .sub{color:#666;font-size:1.05rem;max-width:560px;margin-top:16px}

/* CHART */
.bar-wrap{display:flex;flex-direction:column;gap:18px;margin-top:24px}
.bar-row{display:flex;align-items:center;gap:16px}
.bar-label{width:180px;font-size:.9rem;color:#aaa;text-align:right}
.bar-track{flex:1;background:#151515;border-radius:8px;height:42px;overflow:hidden}
.bar-fill{height:100%;border-radius:8px;display:flex;align-items:center;padding-left:14px;font-weight:700;font-family:'Poppins',sans-serif;font-size:.95rem;transition:width 1s ease}
.bar-val{width:70px;font-size:.9rem;color:#888}

/* TABLE */
table{width:100%;border-collapse:collapse;margin-top:24px}
th{background:#111;padding:14px 20px;text-align:left;font-family:'Poppins',sans-serif;font-size:.9rem;color:#888;font-weight:600;border-bottom:1px solid #222}
td{padding:14px 20px;font-size:.9rem;border-bottom:1px solid #161616}
tr:last-child td{border:none}
.yes{color:var(--green);font-weight:700}
.no{color:#555}
.bold-col{font-weight:600;color:var(--white)}

/* NUMBERS */
.stat-box{background:#111;border:1px solid #1e1e1e;border-radius:20px;padding:40px;text-align:center}
.stat-num{font-family:'Poppins',sans-serif;font-size:5rem;font-weight:900;background:linear-gradient(135deg,var(--green),var(--coral));-webkit-background-clip:text;-webkit-text-fill-color:transparent;line-height:1}
.stat-label{font-size:1rem;color:#888;margin-top:8px;font-weight:600;letter-spacing:1px}

/* TIMELINE */
.timeline{display:flex;gap:0;margin-top:32px}
.phase{flex:1;position:relative;padding:0 16px}
.phase:not(:last-child)::after{content:'';position:absolute;top:20px;right:-1px;width:2px;height:calc(100% - 20px);background:#1e1e1e}
.phase-num{width:40px;height:40px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-family:'Poppins',sans-serif;font-weight:700;font-size:.9rem;margin-bottom:14px}
.phase h3{font-size:1rem;margin-bottom:6px}
.phase p{font-size:.82rem;color:#666}
.phase.current .phase-num{background:var(--green);color:#000}
.phase.p2 .phase-num{background:rgba(17,202,160,.2);color:var(--green);border:1px solid var(--green)}
.phase.p3 .phase-num,.phase.p4 .phase-num{background:#151515;color:#555;border:1px solid #222}

/* TITLE SLIDE */
.title-slide{background:radial-gradient(ellipse at 30% 50%,#0d1a16 0%,#0a0a0a 70%)}
.title-slide .eyebrow{font-family:'Poppins',sans-serif;font-size:.8rem;letter-spacing:3px;color:var(--green);text-transform:uppercase;margin-bottom:20px}
.title-slide h1{font-size:3.8rem}
.title-slide .subtitle{font-size:1.1rem;color:#888;max-width:520px;margin-top:16px;line-height:1.8}
.pills{display:flex;gap:12px;margin-top:28px}
.pill{padding:8px 20px;border-radius:30px;font-size:.82rem;font-weight:700;font-family:'Poppins',sans-serif}
.pill-g{border:1px solid var(--green);color:var(--green)}
.pill-c{border:1px solid var(--coral);color:var(--coral)}
.pill-w{border:1px solid #333;color:#666}
.img-right{position:absolute;right:60px;top:50%;transform:translateY(-50%);width:340px;height:340px;object-fit:contain;opacity:.9}
.img-right2{position:absolute;right:60px;top:50%;transform:translateY(-50%);width:380px;height:280px;object-fit:contain;opacity:.85}

/* QA SLIDE */
.qa-slide{background:radial-gradient(ellipse at 70% 50%,#0d1a16 0%,#0a0a0a 70%);text-align:center;align-items:center}
.qa-slide .big-q{font-size:5rem;color:var(--green);font-family:'Poppins',sans-serif;font-weight:900;line-height:1;margin-bottom:8px}
.qa-slide h2{font-size:2.2rem}
.qa-slide p{max-width:500px;margin-top:16px;color:#666}
.logo-text{font-family:'Poppins',sans-serif;font-weight:900;font-size:1.4rem;margin-top:32px}
</style>
</head>
<body>
<div class="deck">

<!-- SLIDE 1: TITLE -->
<div class="slide title-slide active" id="s1">
  <div class="eyebrow">Product Overview · 2026</div>
  <h1><span class="green">BoomBoom</span> AI<br>The Local Multimodal<br>OS Layer</h1>
  <p class="subtitle">Redefining Human-Computer Interaction through Edge-Native Intelligence.</p>
  <div class="pills">
    <div class="pill pill-g">⚡ Zero Latency</div>
    <div class="pill pill-c">🔒 Total Privacy</div>
    <div class="pill pill-w">📡 100% Offline</div>
  </div>
  <img src="boomboom_hero.png" alt="BoomBoom AI" class="img-right">
</div>

<!-- SLIDE 2: SECTION TITLE -->
<div class="slide section-slide" id="s2">
  <div class="tag tag-coral">THE PROBLEM</div>
  <div class="big">The Crisis of<br><span class="coral">Cloud Dependency</span></div>
  <p class="sub">Why current AI interaction models are fundamentally broken for enterprise and professional use.</p>
</div>

<!-- SLIDE 3: TWO COLUMN -->
<div class="slide" id="s3">
  <div class="tag tag-coral">THE BOTTLENECK</div>
  <h2>The Latency &amp; Privacy <span class="coral">Problem</span></h2>
  <div class="cards two" style="margin-top:32px">
    <div class="card">
      <div class="card-icon c">🔒</div>
      <h3 class="coral" style="margin-bottom:10px">The Privacy Gap</h3>
      <p>Sending screen data and clipboard context to 3rd-party servers is a massive compliance risk for legal, finance, and healthcare enterprises.</p>
      <div style="margin-top:18px;padding:12px;background:#1a0e0a;border-radius:10px;border-left:3px solid var(--coral)">
        <p style="font-size:.85rem;color:#FF823A">⚠ GDPR · HIPAA · SOC 2 all violated by default cloud AI pipelines</p>
      </div>
    </div>
    <div class="card">
      <div class="card-icon g">⏱</div>
      <h3 class="green" style="margin-bottom:10px">The Latency Penalty</h3>
      <p>Cloud AI round-trips take 1.5s+. Real-time hardware control requires sub-100ms response times to feel native and responsive.</p>
      <div style="margin-top:18px;padding:12px;background:#0d1a16;border-radius:10px;border-left:3px solid var(--green)">
        <p style="font-size:.85rem;color:var(--green)">✓ BoomBoom achieves 85ms deterministic triggers — 14× faster</p>
      </div>
    </div>
  </div>
</div>

<!-- SLIDE 4: SECTION TITLE -->
<div class="slide section-slide" id="s4" style="background:radial-gradient(ellipse at 30% 50%,#0d1a16 0%,#0a0a0a 70%)">
  <div class="tag tag-green">THE SOLUTION</div>
  <div class="big"><span class="green">BoomBoom AI</span><br><span style="color:var(--white)">Strips the Cloud.</span><br><span style="color:var(--white)">Runs on Silicon.</span></div>
  <p class="sub" style="color:#aaa">An independent OS layer that strips away the cloud and runs entirely on local silicon — no internet required.</p>
</div>

<!-- SLIDE 5: IMAGE RIGHT TEXT LEFT -->
<div class="slide" id="s5" style="flex-direction:row;align-items:center;gap:60px">
  <div style="flex:1">
    <div class="tag tag-green">ARCHITECTURE</div>
    <h2>Multimodal <span class="green">Perception</span> Pillars</h2>
    <div style="display:flex;flex-direction:column;gap:20px;margin-top:28px">
      <div style="display:flex;gap:16px;align-items:flex-start">
        <div class="card-icon g" style="flex-shrink:0">👁</div>
        <div><h3 class="green">Vision</h3><p style="color:#aaa">MediaPipe spatial tracking for depth-independent gesture recognition across all screen zones.</p></div>
      </div>
      <div style="display:flex;gap:16px;align-items:flex-start">
        <div class="card-icon c" style="flex-shrink:0">🎙</div>
        <div><h3 class="coral">Voice</h3><p style="color:#aaa">Zero-latency short-circuit router for instant OS hardware triggers — bypasses the LLM entirely.</p></div>
      </div>
      <div style="display:flex;gap:16px;align-items:flex-start">
        <div style="width:48px;height:48px;border-radius:12px;background:rgba(255,255,255,.06);display:flex;align-items:center;justify-content:center;font-size:1.4rem;flex-shrink:0">🧠</div>
        <div><h3 style="color:#ddd">Brain</h3><p style="color:#aaa">Optimized Gemma 2B model with 4-bit quantization for complex cognitive reasoning under 2 GB RAM.</p></div>
      </div>
    </div>
  </div>
  <img src="boomboom_schematic.png" alt="Architecture" style="width:340px;height:280px;object-fit:contain;flex-shrink:0">
</div>

<!-- SLIDE 6: TILED WITH ICONS -->
<div class="slide" id="s6">
  <div class="tag tag-green">FEATURES</div>
  <h2>Core Features: <span class="green">The Jedi Desktop</span></h2>
  <div class="cards three" style="margin-top:32px">
    <div class="card">
      <div class="card-icon g">🖐</div>
      <h3 class="green" style="margin-bottom:8px">Spatial Control</h3>
      <p>Navigate the OS, switch tabs, and adjust volume using only hand gestures — no mouse required.</p>
    </div>
    <div class="card">
      <div class="card-icon c">🛡</div>
      <h3 class="coral" style="margin-bottom:8px">Ghost Reader</h3>
      <p>Securely extract and summarize highlighted text locally via clipboard context. Zero data leakage.</p>
    </div>
    <div class="card">
      <div style="width:48px;height:48px;border-radius:12px;background:rgba(255,255,255,.1);display:flex;align-items:center;justify-content:center;font-size:1.4rem;margin-bottom:16px">⚡</div>
      <h3 style="margin-bottom:8px;color:#ddd">Hardware Hooks</h3>
      <p style="color:#aaa">Instant voice-control for brightness, zoom, screenshots, and system commands via intent routing.</p>
    </div>
  </div>
</div>

<!-- SLIDE 7: BAR CHART -->
<div class="slide" id="s7">
  <div class="tag tag-green">PERFORMANCE</div>
  <h2>Speed: The <span class="green">14× Latency</span> Advantage</h2>
  <div class="bar-wrap">
    <div class="bar-row">
      <div class="bar-label">Cloud API</div>
      <div class="bar-track"><div class="bar-fill" style="width:100%;background:linear-gradient(90deg,#3a1818,#8B2222);color:#ff6b6b">1,200 ms</div></div>
    </div>
    <div class="bar-row">
      <div class="bar-label">Optimized Edge</div>
      <div class="bar-track"><div class="bar-fill" style="width:37.5%;background:linear-gradient(90deg,#1a2a1a,#2d6b4a);color:#6bd4a0">450 ms</div></div>
    </div>
    <div class="bar-row">
      <div class="bar-label">BoomBoom Local</div>
      <div class="bar-track"><div class="bar-fill" style="width:7%;background:linear-gradient(90deg,var(--green),#0aaa80);color:#000;min-width:90px">85 ms ⚡</div></div>
    </div>
  </div>
  <div style="margin-top:28px;padding:18px 24px;background:#0d1a16;border-radius:12px;border-left:3px solid var(--green)">
    <p><strong style="color:var(--green)">Key Insight:</strong> By bypassing the LLM entirely for hardware tasks via intent routing, BoomBoom achieves deterministic, real-time performance unmatched by any cloud model.</p>
  </div>
</div>

<!-- SLIDE 8: TABLE -->
<div class="slide" id="s8">
  <div class="tag tag-coral">COMPETITIVE ANALYSIS</div>
  <h2>Local vs. <span class="coral">Cloud</span> — No Contest</h2>
  <table>
    <thead>
      <tr><th>Feature</th><th>Cloud AI (Copilot / GPT)</th><th class="green">BoomBoom AI</th></tr>
    </thead>
    <tbody>
      <tr><td class="bold-col">Data Sovereignty</td>      <td style="color:#cc5555">✗ No</td><td class="yes">✓ YES — 100% Local</td></tr>
      <tr><td class="bold-col">Offline Functionality</td>      <td style="color:#cc5555">✗ No</td><td class="yes">✓ YES — Full Feature</td></tr>
      <tr><td class="bold-col">Hardware Execution</td>      <td style="color:#cc5555">Delayed (1.2s+)</td><td class="yes">Instant (85ms)</td></tr>
      <tr><td class="bold-col">RAM Footprint</td><td style="color:#cc5555">Heavy (4 GB+)</td><td class="yes">&lt; 2 GB Total</td></tr>
      <tr><td class="bold-col">Gesture Control</td><td style="color:#cc5555">✗ None</td><td class="yes">✓ Full Spatial OS</td></tr>
    </tbody>
  </table>
</div>

<!-- SLIDE 9: HIGHLIGHTED NUMBER -->
<div class="slide" id="s9" style="flex-direction:row;gap:60px;align-items:center">
  <div style="flex:1">
    <div class="tag tag-green">EFFICIENCY</div>
    <h2>High Performance,<br><span class="green">Low Overhead</span></h2>
    <p style="margin-top:20px;max-width:440px">Through 4-bit quantization and efficient routing, our entire AI Operating System uses less memory than a few open Google Chrome tabs — while running a full vision, voice, and reasoning pipeline simultaneously.</p>
    <div style="margin-top:24px;display:flex;gap:16px">
      <div style="padding:14px 20px;background:#111;border-radius:12px;border:1px solid #1e1e1e;text-align:center">
        <div style="font-family:'Poppins',sans-serif;font-size:1.6rem;font-weight:900;color:var(--green)">4-bit</div>
        <div style="font-size:.75rem;color:#555;margin-top:4px">Quantization</div>
      </div>
      <div style="padding:14px 20px;background:#111;border-radius:12px;border:1px solid #1e1e1e;text-align:center">
        <div style="font-family:'Poppins',sans-serif;font-size:1.6rem;font-weight:900;color:var(--coral)">85ms</div>
        <div style="font-size:.75rem;color:#555;margin-top:4px">Trigger Latency</div>
      </div>
    </div>
  </div>
  <div class="stat-box" style="flex-shrink:0;width:300px">
    <div class="stat-num">1.8 GB</div>
    <div class="stat-label">TOTAL RAM USAGE</div>
    <p style="font-size:.8rem;color:#444;margin-top:16px">Full AI OS Stack<br>Vision · Voice · Reasoning</p>
  </div>
</div>

<!-- SLIDE 10: TIMELINE -->
<div class="slide" id="s10">
  <div class="tag tag-green">ROADMAP</div>
  <h2>Strategic <span class="green">Roadmap</span></h2>
  <div class="timeline">
    <div class="phase current">
      <div class="phase-num">01</div>
      <h3 class="green">Local Multimodal MVP</h3>
      <p>Gesture + Voice + Ghost Reader. Fully operational on-device AI layer.</p>
      <div style="margin-top:12px;font-size:.75rem;color:var(--green);font-weight:700">● CURRENT</div>
    </div>
    <div class="phase p2">
      <div class="phase-num">02</div>
      <h3 class="green">Biometric Lock</h3>
      <p>Voice print &amp; face-lock authentication. Zero-trust local security layer.</p>
      <div style="margin-top:12px;font-size:.75rem;color:#555">Q3 2026</div>
    </div>
    <div class="phase p3">
      <div class="phase-num">03</div>
      <h3 style="color:#aaa">Enterprise Deploy</h3>
      <p style="color:#777">Cross-platform packaging. Air-gapped enterprise fleet support.</p>
      <div style="margin-top:12px;font-size:.75rem;color:#666">Q1 2027</div>
    </div>
    <div class="phase p4">
      <div class="phase-num">04</div>
      <h3 style="color:#aaa">Autonomous Agent</h3>
      <p style="color:#777">Full OS Agent Framework — self-directed task execution pipeline.</p>
      <div style="margin-top:12px;font-size:.75rem;color:#666">Q3 2027</div>
    </div>
  </div>
</div>

<!-- SLIDE 11: SECTION TITLE -->
<div class="slide section-slide" id="s11">
  <div class="tag tag-coral">GO TO MARKET</div>
  <div class="big"><span style="color:var(--white)">Business Model</span><br>&amp; <span class="coral">Scalability</span></div>
  <p class="sub" style="color:#aaa">Target Markets: Quant Trading floors, Air-Gapped Legal Workspaces, and Privacy-Focused Pro-Developers who cannot afford cloud exposure.</p>
  <div style="display:flex;gap:16px;margin-top:32px">
    <div class="pill pill-c">📈 Quant Trading</div>
    <div class="pill pill-c">⚖ Legal &amp; Compliance</div>
    <div class="pill pill-c">💻 Pro Developers</div>
  </div>
</div>

<!-- SLIDE 12: Q&A -->
<div class="slide qa-slide" id="s12">
  <div class="big-q">Q&amp;A</div>
  <h2>The Future of the Desktop<br>is <span class="green">Local</span></h2>
  <p>Thank you. Let's build a private, faster future together.</p>
  <div class="logo-text"><span class="green">Boom</span><span class="coral">Boom</span> <span style="color:#444">AI</span></div>
  <div class="pills" style="margin-top:16px">
    <div class="pill pill-g">⚡ Zero Latency</div>
    <div class="pill pill-c">🔒 Total Privacy</div>
  </div>
</div>

</div><!-- end deck -->

<!-- SLIDE NUMBER -->
<div class="slide-num" id="slideNum">1 / 12</div>

<!-- NAV -->
<nav class="nav">
  <button id="prevBtn" onclick="go(-1)">← Prev</button>
  <div class="dots" id="dots"></div>
  <button id="nextBtn" onclick="go(1)">Next →</button>
</nav>

<script>
const slides=document.querySelectorAll('.slide');
const dotsEl=document.getElementById('dots');
const numEl=document.getElementById('slideNum');
let cur=0;
slides.forEach((_,i)=>{
  const d=document.createElement('div');
  d.className='dot'+(i===0?' on':'');
  d.onclick=()=>show(i);
  dotsEl.appendChild(d);
});
function show(n){
  slides[cur].classList.remove('active');
  dotsEl.children[cur].classList.remove('on');
  cur=(n+slides.length)%slides.length;
  slides[cur].classList.add('active');
  dotsEl.children[cur].classList.add('on');
  numEl.textContent=(cur+1)+' / '+slides.length;
}
function go(d){show(cur+d);}
document.addEventListener('keydown',e=>{
  if(e.key==='ArrowRight'||e.key==='ArrowDown')go(1);
  if(e.key==='ArrowLeft'||e.key==='ArrowUp')go(-1);
});
</script>
</body>
</html>"""

with open('boomboom_deck.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Done! boomboom_deck.html written.")
