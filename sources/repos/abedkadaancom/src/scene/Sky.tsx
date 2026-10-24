import { useMemo } from 'react';
import * as THREE from 'three';
import { computeSky, bvToRgb, type SkyObject } from '../math/sky';
import { Sign } from './Sign';

/** Horizon frame → world: north = −z, east = +x, zenith = +y. */
export function altAzToVec(alt: number, az: number, r: number): THREE.Vector3 {
  const a = THREE.MathUtils.degToRad(alt);
  const z = THREE.MathUtils.degToRad(az);
  return new THREE.Vector3(Math.sin(z) * Math.cos(a) * r, Math.sin(a) * r, -Math.cos(z) * Math.cos(a) * r);
}

const vert = /* glsl */ `
  attribute float size;
  attribute vec3 tint;
  varying vec3 vTint;
  varying float vSize;
  uniform float uScale;
  void main() {
    vTint = tint;
    vec4 mv = modelViewMatrix * vec4(position, 1.0);
    gl_PointSize = size * uScale;
    vSize = gl_PointSize;
    gl_Position = projectionMatrix * mv;
  }
`;
const frag = /* glsl */ `
  varying vec3 vTint;
  varying float vSize;
  uniform float uDim;
  void main() {
    vec2 p = gl_PointCoord - 0.5;
    float d = length(p);
    float core = smoothstep(0.5, 0.0, d);
    float a = pow(core, 1.6) * uDim;
    if (a < 0.01) discard;
    gl_FragColor = vec4(vTint * (0.7 + core), a);
  }
`;

export function Stars({ objects, radius = 320, scale = 1, dim = 1, minAlt = -4 }: { objects: SkyObject[]; radius?: number; scale?: number; dim?: number; minAlt?: number }) {
  const geom = useMemo(() => {
    const stars = objects.filter((o) => o.kind === 'star' && o.alt > minAlt);
    const pos = new Float32Array(stars.length * 3);
    const size = new Float32Array(stars.length);
    const tint = new Float32Array(stars.length * 3);
    stars.forEach((s, i) => {
      const v = altAzToVec(s.alt, s.az, radius);
      pos.set([v.x, v.y, v.z], i * 3);
      size[i] = Math.max(1.6, 7.5 - 1.25 * (s.mag + 1.5));
      tint.set(bvToRgb(s.bv), i * 3);
    });
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    g.setAttribute('size', new THREE.BufferAttribute(size, 1));
    g.setAttribute('tint', new THREE.BufferAttribute(tint, 3));
    return g;
  }, [objects, radius, minAlt]);
  const mat = useMemo(
    () =>
      new THREE.ShaderMaterial({
        vertexShader: vert,
        fragmentShader: frag,
        uniforms: { uScale: { value: scale * Math.min(2, typeof window !== 'undefined' ? window.devicePixelRatio : 1) }, uDim: { value: dim } },
        transparent: true,
        depthWrite: false,
        blending: THREE.AdditiveBlending,
        fog: false,
      }),
    [scale, dim],
  );
  return <points geometry={geom} material={mat} frustumCulled={false} renderOrder={-1} />;
}

/** The campus sky: real star positions for the shared observer, rendered as night (a declared choice). */
export function CampusSky({ lat, lon, magLimit, time, labels = false }: { lat: number; lon: number; magLimit: number; time: string | null; labels?: boolean }) {
  // Recompute at most once per 10 minutes of wall time (stars move ~2.5° in that time).
  const slot = time ? new Date(time).getTime() : Math.floor(Date.now() / 600_000) * 600_000;
  const objects = useMemo(() => computeSky({ lat, lon, date: new Date(slot) }, magLimit), [lat, lon, slot, magLimit]);
  const moon = objects.find((o) => o.kind === 'moon');
  return (
    <group>
      <Stars objects={objects} scale={labels ? 1.9 : 1} />
      {moon && moon.alt > 2 ? (
        <mesh position={altAzToVec(moon.alt, moon.az, 280)}>
          <sphereGeometry args={[7, 32, 16]} />
          <meshBasicMaterial color="#e9e4d8" fog={false} toneMapped={false} />
        </mesh>
      ) : null}
      {labels
        ? objects
            .filter((o) => o.alt > 3 && ((o.kind === 'star' && o.name && o.mag < 1.6) || o.kind === 'planet' || o.kind === 'moon'))
            .map((o) => {
              const v = altAzToVec(o.alt, o.az, 250);
              return <Sign key={o.id} mood="luminous" text={o.name!} fontSize={7} position={[v.x, v.y + 5, v.z]} color={o.kind === 'star' ? '#b6ab9a' : '#F1D79C'} />;
            })
        : null}
      {/* a faint horizon glow: sky gradient as a large inverted sphere */}
      <mesh renderOrder={-2}>
        <sphereGeometry args={[360, 32, 16]} />
        <shaderMaterial
          side={THREE.BackSide}
          depthWrite={false}
          fog={false}
          uniforms={{}}
          vertexShader={'varying vec3 vP; void main(){ vP = normalize(position); gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0);}'}
          fragmentShader={'varying vec3 vP; void main(){ float h = clamp(vP.y, -0.2, 1.0); vec3 top = vec3(0.012,0.012,0.022); vec3 hor = vec3(0.09,0.07,0.06); vec3 c = mix(hor, top, smoothstep(-0.02, 0.45, h)); gl_FragColor = vec4(c,1.0);}'}
        />
      </mesh>
    </group>
  );
}
