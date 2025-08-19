import fs from 'node:fs'; 
import path from 'node:path';

function fkGrade(text){
  const s = Math.max(1,(text.match(/[.!?]+/g)||[]).length);
  const w = Math.max(1,(text.match(/\b[\w''-]+\b/g)||[]).length);
  const y = (text.toLowerCase().match(/[aeiouy]{1,2}/g)||[]).length;
  return 0.39*(w/s) + 11.8*(y/w) - 15.59;
}

let fail = false;
function checkFile(p){
  const t = fs.readFileSync(p,'utf8');
  
  // Poetic blocks  look for data-tone="poetic"
  const poeticBlocks = t.match(/data-tone=["']poetic["'][^>]*>([\s\S]*?)<\/(section|div)>/gi) || [];
  for(const b of poeticBlocks){
    const text = b.replace(/<[^>]+>/g,' ').trim();
    const words = text.split(/\s+/).filter(Boolean).length;
    if(words>40){ 
      console.error(`L Poetic >40 words: ${p} (${words} words)`); 
      fail = true; 
    }
    if(/\b(guarantee[sd]?|perfect|flawless|zero-?risk|endorsed|certified|revolutionary)\b/i.test(b)){ 
      console.error(`L Poetic contains banned claims: ${p}`); 
      fail = true; 
    }
  }
  
  // Plain blocks  data-tone="plain"
  const plainBlocks = t.match(/data-tone=["']plain["'][^>]*>([\s\S]*?)<\/(section|div)>/gi) || [];
  for(const b of plainBlocks){
    const text = b.replace(/<[^>]+>/g,' ').trim();
    const grade = fkGrade(text);
    if(grade>8){ 
      console.error(`L Plain grade ${grade.toFixed(1)} (>8): ${p}`); 
      fail = true; 
    }
  }
  
  // Technical blocks  require 'Limits' and 'Dependencies' mentions
  const techBlocks = t.match(/data-tone=["']technical["'][^>]*>([\s\S]*?)<\/(section|div)>/gi) || [];
  for(const b of techBlocks){
    if(!/limit/i.test(b) || !/dependenc/i.test(b)){ 
      console.error(`L Technical lacks limits/dependencies: ${p}`); 
      fail = true; 
    }
  }
}

console.log('Scanning tone compliance...');
['branding','lukhas_website','docs'].filter(fs.existsSync).forEach(root=>{
  (function walk(dir){ 
    for(const f of fs.readdirSync(dir)){ 
      const p = path.join(dir,f); 
      const st = fs.statSync(p);
      if(st.isDirectory()) {
        walk(p); 
      } else if(/\.(mdx?|tsx?|jsx?|html)$/i.test(p)) {
        checkFile(p);
      }
    }
  })(root);
});

if(fail) {
  console.error('\n=¡ Fix suggestions:');
  console.error('   - Poetic: d40 words, no claims/guarantees');
  console.error('   - Plain: Keep under Grade 8 reading level');
  console.error('   - Technical: Include limitations and dependencies');
  process.exit(1);
} else {
  console.log(' Tone lint OK');
}