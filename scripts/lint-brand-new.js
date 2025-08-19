import fs from 'node:fs'; 
import path from 'node:path';

const roots = ['branding','lukhas_website','docs'].filter(fs.existsSync);
const ignorePatterns = /(node_modules|\.git|\.venv|__pycache__|\.next|build|dist)/;
const bannedWords = /\b(revolutionary|guaranteed|flawless|perfect|zero-?risk|unbreakable|unlimited|unparalleled|breakthrough|cutting-?edge|world-?class|industry-?leading|state-?of-?the-?art)\b/i;
const lambda = /Λ/;
const okDisplayContexts = /(wordmark|logo|hero|lockup|brand|matriz|identity|display)/i; // filenames/dirs that are allowed to include Λ
let fail = false;

function scan(p){
  if(ignorePatterns.test(p)) return;
  
  const st = fs.statSync(p);
  if(st.isDirectory()){
    for(const f of fs.readdirSync(p)) scan(path.join(p,f));
  }else if(/\.(mdx?|tsx?|jsx?|html)$/i.test(p)){
    const t = fs.readFileSync(p,'utf8');
    if(bannedWords.test(t)){ 
      console.error('❌ Banned superlative:', p); 
      const matches = t.match(bannedWords);
      console.error(`   Found: ${matches[0]}`);
      fail = true; 
    }
    if(lambda.test(t) && !okDisplayContexts.test(p)){ 
      console.error('❌ Λ outside display contexts:', p); 
      fail = true; 
    }
  }
}

console.log('Scanning brand compliance...');
roots.forEach(r=>scan(r));
if(fail) {
  console.error('\n💡 Fix suggestions:');
  console.error('   - Replace banned words with factual descriptions');
  console.error('   - Use Λ only in display contexts (wordmarks, heroes, logos)');
  console.error('   - Use plain names (Lukhas, Matriz) in body text');
  process.exit(1); 
} else {
  console.log(' Brand lint OK');
}