import fs from 'node:fs';
import Ajv from 'ajv';
import addFormats from 'ajv-formats';

const ajv = new Ajv({ allErrors: true }); 
addFormats(ajv);

function load(p){ 
  return JSON.parse(fs.readFileSync(p,'utf8')); 
}

function validate(schemaPath, dataPath){
  const schema = load(schemaPath); 
  const data = load(dataPath);
  const validate = ajv.compile(schema); 
  const ok = validate(data);
  if(!ok){ 
    console.error(`❌ ${dataPath}`); 
    console.error(validate.errors); 
    process.exit(1); 
  }
  console.log(`✅ ${dataPath}`);
  return data;
}

const mods = validate('branding/schemas/modules.registry.schema.json','branding/modules.registry.json');
const sections = validate('branding/schemas/site.sections.schema.json','branding/site.sections.json');

// cross-field: dependency keys must exist
const keys = new Set(mods.modules.map(m=>m.key));
for(const m of mods.modules){
  for(const d of (m.dependencies||[])){
    if(!keys.has(d)){ 
      console.error(`❌ dependency "${d}" not found (module ${m.key})`); 
      process.exit(1); 
    }
  }
}
console.log('✅ dependencies resolved');

// check for duplicate slugs
const slugs = new Set();
for(const m of mods.modules){
  if(m.slug){
    if(slugs.has(m.slug)){
      console.error(`❌ duplicate slug "${m.slug}"`);
      process.exit(1);
    }
    slugs.add(m.slug);
  }
}
for(const s of sections.sections){
  if(slugs.has(s.slug)){
    console.error(`❌ duplicate slug "${s.slug}"`);
    process.exit(1);
  }
  slugs.add(s.slug);
}
console.log('✅ no duplicate slugs');

// check Lambda usage policy
for(const m of mods.modules){
  if(m.allowLambdaInDisplay === true){
    const allowedModules = ['matriz', 'identity'];
    if(!allowedModules.includes(m.key)){
      console.error(`❌ allowLambdaInDisplay=true only allowed for MΛTRIZ/ΛiD, not ${m.key}`);
      process.exit(1);
    }
  }
}
console.log('✅ Lambda usage policy compliant');

console.log('🎉 All validations passed');