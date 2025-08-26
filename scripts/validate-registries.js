import fs from 'node:fs';
import path from 'node:path';

function load(p){ return JSON.parse(fs.readFileSync(p,'utf8')); }
const modsPath = 'branding/modules.registry.json';
const sitePath = 'branding/site.sections.json';

const mods = fs.existsSync(modsPath) ? load(modsPath) : { modules: [] };
const sections = fs.existsSync(sitePath) ? load(sitePath) : { sections: [] };

// Basic shape checks
const errors = [];
function req(obj, field, where){ if(!(field in obj)) errors.push(`${where} missing ${field}`); }
mods.modules.forEach(m=>{
  req(m,'key',`module:${m.key}`); req(m,'plain',`module:${m.key}`); req(m,'owner',`module:${m.key}`);
  req(m,'sources',`module:${m.key}`);
  if(m.isUserFacing){ if(!m.slug) errors.push(`module:${m.key} isUserFacing=true but missing slug`); }
});
sections.sections.forEach(s=>{
  req(s,'key',`section:${s.key}`); req(s,'slug',`section:${s.key}`); req(s,'owner',`section:${s.key}`); req(s,'sources',`section:${s.key}`);
});

// Uniqueness & collisions
const slugs = new Map();
function seen(map, slug, who){ if(map.has(slug)) errors.push(`duplicate slug ${slug} (${map.get(slug)} vs ${who})`); else map.set(slug, who); }
mods.modules.filter(m=>m.slug).forEach(m=>seen(slugs,m.slug,`module:${m.key}`));
sections.sections.forEach(s=>seen(slugs,s.slug,`section:${s.key}`));

// Dependencies resolve
const keys = new Set(mods.modules.map(m=>m.key));
mods.modules.forEach(m=>{
  (m.dependencies||[]).forEach(d=>{ if(!keys.has(d)) errors.push(`module:${m.key} dependency missing: ${d}`); });
});

// Lambda usage policy
mods.modules.forEach(m=>{
  if(m.allowLambdaInDisplay === true){
    const allowedModules = ['matriz', 'identity'];
    if(!allowedModules.includes(m.key)){
      errors.push(`allowLambdaInDisplay=true only allowed for MΛTRIZ/ΛiD, not ${m.key}`);
    }
  }
});

// Output
if(errors.length){ console.error('Policy registry errors:\n - ' + errors.join('\n - ')); process.exit(1); }
console.log('✅ Registries OK');
