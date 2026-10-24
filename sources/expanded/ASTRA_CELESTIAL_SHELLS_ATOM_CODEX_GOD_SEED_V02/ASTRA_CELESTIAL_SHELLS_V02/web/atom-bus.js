/* ASTRA intent micro-automata. No tokens, eval, arbitrary tool calls or
   implicit durable authority. Visual intents are bounded; persistent writes
   remain owned by ATOM server's ADMIT/VERIFY/CHECKPOINT cycle. */
(function(global){'use strict';
const CONTRACTS={
 'shell.expand':{args:[],effect:'render-scale',readOnly:true},
 'shell.contract':{args:[],effect:'render-scale',readOnly:true},
 'shell.orbit':{args:[],effect:'camera-toggle',readOnly:true},
 'shell.grid':{args:[],effect:'render-toggle',readOnly:true},
 'journey.shift':{args:['destination'],effect:'visual-journey',readOnly:true},
 'sound.enable':{args:[],effect:'local-audio',readOnly:true},
 'sound.mute':{args:[],effect:'local-audio',readOnly:true},
 'celestial.focus':{args:['name'],effect:'inspector',readOnly:true}
};
class IntentBus{
 constructor(){this.handlers=new Map();this.events=[];this.sequence=0}
 register(name,fn){if(!Object.prototype.hasOwnProperty.call(CONTRACTS,name)||typeof fn!=='function')throw Error('No contract for '+name);this.handlers.set(name,fn)}
 async dispatch(name,input={}){const contract=CONTRACTS[name];if(!contract)throw Error('Unregistered intent '+name);
 if(!input||typeof input!=='object'||Array.isArray(input))throw Error('Object input required');
 const ks=Object.keys(input);if(ks.some(k=>!contract.args.includes(k)))throw Error('Undeclared arguments');
 for(const k of contract.args)if(typeof input[k]!=='string'||!input[k].length||input[k].length>90)throw Error('Bad parameter '+k);
 const fn=this.handlers.get(name);if(!fn)throw Error('No handler');
 const result=await fn(Object.freeze({...input}));const event={id:++this.sequence,name,input,category:contract.effect,verdict:'PASS',durable:false,output:result??null};
 this.events.push(event);if(this.events.length>128)this.events.shift();return event;}
 inspect(){return {protocol:'ASTRA-UI-AUTOMATA/0.2',definitions:CONTRACTS,events:this.events.slice(-12),count:this.sequence,durableWrites:false}}
}
const api={IntentBus,CONTRACTS};if(typeof module!=='undefined'&&module.exports)module.exports=api;global.AstraIntent=api;
})(typeof window!=='undefined'?window:globalThis);
