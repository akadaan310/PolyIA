const assert=require('node:assert/strict');const {IntentBus,CONTRACTS}=require('../web/atom-bus.js');
(async()=>{let b=new IntentBus();b.register('shell.expand',()=>42);let x=await b.dispatch('shell.expand');assert.equal(x.output,42);assert.equal(x.durable,false);
let refused=false;try{await b.dispatch('shell.expand',{shell:'/../../'})}catch(e){refused=true}assert(refused);
try{await b.dispatch('exec',{code:'rm -rf'})}catch(e){refused=true}assert(refused);
assert.equal(Object.keys(CONTRACTS).length,8);assert.equal(b.inspect().count,1);console.log('Intent bus: 5 assertions OK')})().catch(e=>{console.error(e);process.exit(1)});
