/* Optional GPU point pass. Uses WebGL2 for catalog samples; CPU celestial graticule
   remains source of truth for semantic hit tests and line annotations. */
(function(global){'use strict';
const vs=`#version 300 es
precision highp float;
in vec3 pos; in vec3 col; in float bright; uniform float yaw,pitch,dist,aspect,scale;
out vec3 c;out float glow;
void main(){float cy=cos(yaw),sy=sin(yaw),cp=cos(pitch),sp=sin(pitch);
vec3 p=vec3(pos.x*cy-pos.z*sy,pos.y,pos.x*sy+pos.z*cy);
p=vec3(p.x,p.y*cp-p.z*sp,p.y*sp+p.z*cp);
float zz=max(.4,dist-p.z);float f=scale/zz;gl_Position=vec4(p.x*f/aspect,p.y*f,0.,1.);
gl_PointSize=clamp((3.3+bright*2.)*f,1.5,10.);c=col;glow=bright;}`;
const fs=`#version 300 es
precision highp float;in vec3 c;in float glow;out vec4 outColor;
void main(){vec2 p=gl_PointCoord*2.-1.;float r=length(p);float a=smoothstep(1.,.1,r);float core=exp(-r*r*9.);outColor=vec4(c*(.45+core*1.3),a*(.27+core*.67));}`;
function compile(gl,type,src){let s=gl.createShader(type);gl.shaderSource(s,src);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS))throw Error(gl.getShaderInfoLog(s));return s}
class StarGPU{constructor(canvas){this.canvas=canvas;this.gl=null;this.error=null;this.n=0;try{let gl=canvas.getContext('webgl2',{alpha:true,antialias:false,depth:false,preserveDrawingBuffer:false});if(!gl)throw Error('WebGL2 unavailable');let p=gl.createProgram();gl.attachShader(p,compile(gl,gl.VERTEX_SHADER,vs));gl.attachShader(p,compile(gl,gl.FRAGMENT_SHADER,fs));gl.linkProgram(p);if(!gl.getProgramParameter(p,gl.LINK_STATUS))throw Error(gl.getProgramInfoLog(p));this.program=p;this.gl=gl;this.buffer=gl.createBuffer();this.position=gl.getAttribLocation(p,'pos');this.color=gl.getAttribLocation(p,'col');this.brightness=gl.getAttribLocation(p,'bright');this.locations=Object.fromEntries(['yaw','pitch','dist','aspect','scale'].map(n=>[n,gl.getUniformLocation(p,n)]));gl.enable(gl.BLEND);gl.blendFunc(gl.SRC_ALPHA,gl.ONE);this.seed=null;}catch(e){this.error=e.message;}}
 populate(sky){if(!this.gl)return;const arr=[];for(const s of sky.stars){const v=s.v,b=Math.max(.15,Math.min(2.5,2.5-s.mag*.27));arr.push(...v,.63,.85,.95,b)}
 // Visually synthetic distant stars, segregated in a shader attribute range.
 for(let i=0;i<450;i++){let ra=(i*137.507764+31.8)%360,dec=(Math.asin((i*73.17%1000)/500-1))*180/Math.PI;
 const v=global.CelestialShells.vec(ra,dec,2.05);arr.push(...v,.44,.62,.83,.12)}
 this.n=arr.length/7;this.gl.bindBuffer(this.gl.ARRAY_BUFFER,this.buffer);this.gl.bufferData(this.gl.ARRAY_BUFFER,new Float32Array(arr),this.gl.STATIC_DRAW)}
 draw(sky,w,h){const gl=this.gl;if(!gl||!sky)return;if(!this.seed){this.populate(sky);this.seed=true}let pr=Math.min(global.devicePixelRatio||1,1.7),cw=Math.round(w*pr),ch=Math.round(h*pr);if(this.canvas.width!==cw||this.canvas.height!==ch){this.canvas.width=cw;this.canvas.height=ch}gl.viewport(0,0,cw,ch);gl.clearColor(0,0,0,0);gl.clear(gl.COLOR_BUFFER_BIT);gl.useProgram(this.program);gl.uniform1f(this.locations.yaw,sky.yaw);gl.uniform1f(this.locations.pitch,sky.pitch);gl.uniform1f(this.locations.dist,sky.cameraDistance);gl.uniform1f(this.locations.aspect,w/h);gl.uniform1f(this.locations.scale,1.43*2*Math.min(w,h)/h);gl.bindBuffer(gl.ARRAY_BUFFER,this.buffer);let stride=7*4;for(const [loc,sz,offset] of [[this.position,3,0],[this.color,3,3*4],[this.brightness,1,6*4]]){gl.enableVertexAttribArray(loc);gl.vertexAttribPointer(loc,sz,gl.FLOAT,false,stride,offset)}gl.drawArrays(gl.POINTS,0,this.n)}
 clear(){if(this.gl){this.gl.clearColor(0,0,0,0);this.gl.clear(this.gl.COLOR_BUFFER_BIT)}}
 diagnostic(){return {enabled:!!this.gl,error:this.error,points:this.n,backend:this.gl?'WebGL2 POINTS':'CPU fallback'}}}
const api={StarGPU};if(typeof module!=='undefined'&&module.exports)module.exports=api;global.CelestialGPU=api;
})(typeof window!=='undefined'?window:globalThis);
