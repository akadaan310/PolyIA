import { useLayoutEffect, useMemo, useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { DIVISIONS } from '../content/registry';
import { materials } from './materials';
import { Sign } from './Sign';
import { useStore } from '../state/store';
import { doorAngle, REALM_RADIUS, onCircle } from '../world/locations';
import { plateFor, type Plate } from '../books/plates';
import { bridgeRecord, foldRecord, addressRecord } from '../exhibits/records';
import { analyseInterval } from '../math/music';
import { weave } from '../math/world';
import { analyse, mat } from '../math/matrix';

const INK: Record<string, string> = { gold: '#F1D79C', ink: '#F4EBDC', crimson: '#c0394a', faint: '#6b6358' };

/** Draw a computed plate as glowing vector lines on a vertical panel (unit square → size × size). */
function PlatePanel({ plate, size = 7 }: { plate: Plate; size?: number }) {
  const { lines, colors } = useMemo(() => {
    const pts: number[] = [];
    const cols: number[] = [];
    const c = new THREE.Color();
    const P = (x: number, y: number) => [(x - 0.5) * size, (0.5 - y) * size + size / 2, 0];
    const push = (a: number[], b: number[], ink: string) => {
      pts.push(...a, ...b);
      c.set(INK[ink] ?? '#fff');
      cols.push(c.r, c.g, c.b, c.r, c.g, c.b);
    };
    for (const p of plate.prims) {
      if (p.t === 'line') push(P(p.x1, p.y1), P(p.x2, p.y2), p.ink);
      else if (p.t === 'poly') for (let i = 0; i + 1 < p.pts.length + (p.closed ? 1 : 0); i++) push(P(...p.pts[i % p.pts.length]!), P(...p.pts[(i + 1) % p.pts.length]!), p.ink);
      else if (p.t === 'circle') {
        const n = 12;
        for (let i = 0; i < n; i++) {
          const a1 = (i / n) * Math.PI * 2;
          const a2 = ((i + 1) / n) * Math.PI * 2;
          push(P(p.cx + p.r * Math.cos(a1), p.cy + p.r * Math.sin(a1)), P(p.cx + p.r * Math.cos(a2), p.cy + p.r * Math.sin(a2)), p.ink);
        }
      } else if (p.t === 'rect') {
        const q: [number, number][] = [[p.x, p.y], [p.x + p.w, p.y], [p.x + p.w, p.y + p.h], [p.x, p.y + p.h]];
        for (let i = 0; i < 4; i++) push(P(...q[i]!), P(...q[(i + 1) % 4]!), p.ink);
      }
    }
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.Float32BufferAttribute(pts, 3));
    g.setAttribute('color', new THREE.Float32BufferAttribute(cols, 3));
    return { lines: g, colors: cols.length };
  }, [plate, size]);
  const texts = plate.prims.filter((p) => p.t === 'text').slice(0, 24) as Extract<Plate['prims'][number], { t: 'text' }>[];
  return (
    <group>
      <mesh position={[0, size / 2, -0.05]}>
        <planeGeometry args={[size + 0.6, size + 0.6]} />
        <meshStandardMaterial color="#0d0c0b" roughness={0.6} metalness={0.2} />
      </mesh>
      {colors > 0 ? (
        <lineSegments geometry={lines}>
          <lineBasicMaterial vertexColors toneMapped={false} />
        </lineSegments>
      ) : null}
      {texts.map((t, i) => (
        <Sign key={i} mood="math" text={t.text} fontSize={0.32} position={[(t.x - 0.5) * size, (0.5 - t.y) * size + size / 2, 0.05]} color={INK[t.ink]} />
      ))}
    </group>
  );
}

function FoundationsExhibit() {
  const bridges = useStore((s) => s.world.bridges);
  const rec = useStore((s) => s.world.exercises['bridge-grammar']);
  const plate = useMemo(() => plateFor('bridge-grammar', { ...bridgeRecord(String(rec?.input.word ?? 'FRPG'), bridges), at: '' }), [bridges, rec]);
  return <PlatePanel plate={plate} />;
}

function RelationalExhibit() {
  const word = useStore((s) => s.world.foldWord);
  const depth = useStore((s) => s.world.foldDepth);
  const plate = useMemo(() => plateFor('fold', { ...foldRecord(word, depth), at: '' }), [word, depth]);
  return <PlatePanel plate={plate} />;
}

function LanguagesExhibit() {
  const address = useStore((s) => s.world.compiledAddress) ?? 'loom://plate/START/ROTATE:90/SCALE:2/SHIFT:1,0/COMMIT';
  const plate = useMemo(() => plateFor('address-compiler', { ...addressRecord(address), at: '' }), [address]);
  const m = materials();
  const nOps = address.split('/').length - 3;
  return (
    <group>
      <PlatePanel plate={plate} />
      {/* the loom: one warp thread per admitted operation */}
      {Array.from({ length: Math.max(0, Math.min(8, nOps)) }, (_, i) => (
        <mesh key={i} material={i % 2 ? m.goldGlow : m.gold} position={[-3 + i * 0.85, 8.6, 0.3]}>
          <cylinderGeometry args={[0.04, 0.04, 2.4, 6]} />
        </mesh>
      ))}
    </group>
  );
}

function GeometryExhibit() {
  const sculpture = useStore((s) => s.world.sculpture) ?? [[1, 0, 0], [0, 1, 0], [0, 0, 0]];
  const ref = useRef<THREE.InstancedMesh>(null);
  const m = materials();
  const { pts, kernel } = useMemo(() => {
    const n = sculpture[0]!.length;
    const R = [-1, -0.5, 0, 0.5, 1];
    const out: THREE.Vector3[] = [];
    for (const x of R) for (const y of R) for (const z of n === 3 ? R : [0]) {
      const v = n === 3 ? [x, y, z] : [x, y];
      const o = sculpture.map((row) => row.reduce((s, c, j) => s + c * v[j]!, 0));
      out.push(new THREE.Vector3(o[0] ?? 0, o[1] ?? 0, o[2] ?? 0));
    }
    const a = analyse(mat(sculpture));
    const k = a.kernel.map((v) => new THREE.Vector3(...v.map((q) => q.toNumber()), ...(n === 2 ? [0] : [])).normalize());
    return { pts: out, kernel: k };
  }, [sculpture]);
  useLayoutEffect(() => {
    if (!ref.current) return;
    const d = new THREE.Object3D();
    pts.forEach((p, i) => {
      d.position.copy(p).multiplyScalar(1.4);
      d.scale.setScalar(0.1);
      d.updateMatrix();
      ref.current!.setMatrixAt(i, d.matrix);
    });
    ref.current.instanceMatrix.needsUpdate = true;
  }, [pts]);
  const spin = useRef<THREE.Group>(null);
  const reduced = useStore((s) => s.settings.reducedMotion);
  useFrame((_, dt) => {
    if (spin.current && !reduced) spin.current.rotation.y += dt * 0.25;
  });
  return (
    <group position={[0, 4, 0]}>
      <group ref={spin}>
        <instancedMesh ref={ref} args={[undefined, undefined, pts.length]} material={m.goldGlow}>
          <icosahedronGeometry args={[1, 0]} />
        </instancedMesh>
        {kernel.map((k, i) => (
          <mesh key={i} material={m.crimson} position={[0, 0, 0]} quaternion={new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 1, 0), k)}>
            <cylinderGeometry args={[0.04, 0.04, 7, 6]} />
          </mesh>
        ))}
      </group>
      <Sign mood="luminous" text="gold: im A · crimson: ker A (input space)" fontSize={0.3} position={[0, -3.4, 0]} />
    </group>
  );
}

function AcousticExhibit() {
  const k = useStore((s) => s.world.interval);
  const a = useMemo(() => analyseInterval(k), [k]);
  const color = useMemo(() => new THREE.Color().setHSL(a.hue / 360, 0.65, 0.62), [a.hue]);
  const lit = useMemo(() => new THREE.MeshStandardMaterial({ color, emissive: color, emissiveIntensity: 1.3, toneMapped: false }), [color]);
  const m = materials();
  const pos = (i: number): [number, number, number] => [3.4 * Math.sin((i * Math.PI) / 6), 0, 3.4 * Math.cos((i * Math.PI) / 6)];
  const star = useMemo(() => {
    const g = new THREE.BufferGeometry();
    const p: number[] = [];
    a.orbit.forEach((x, i) => {
      const y = a.orbit[(i + 1) % a.orbit.length]!;
      const A = pos(x);
      const B = pos(y);
      p.push(A[0], 3.2, A[2], B[0], 3.2, B[2]);
    });
    g.setAttribute('position', new THREE.Float32BufferAttribute(p, 3));
    return g;
  }, [a]);
  return (
    <group>
      {Array.from({ length: 12 }, (_, i) => (
        <mesh key={i} position={[pos(i)[0], 1.6, pos(i)[2]]} material={a.orbit.includes(i) ? lit : m.darkStone}>
          <cylinderGeometry args={[0.22, 0.28, 3.2, 8]} />
        </mesh>
      ))}
      <lineSegments geometry={star}>
        <lineBasicMaterial color={color} toneMapped={false} />
      </lineSegments>
      <Sign mood="math" text={`|⟨${a.k}⟩| = 12 / gcd(12, ${a.k}) = ${a.orbitLength}`} fontSize={0.42} position={[0, 4.6, 0]} />
    </group>
  );
}

function WorldsExhibit() {
  const rule = useStore((s) => s.world.loomRule);
  const ref = useRef<THREE.InstancedMesh>(null);
  const grid = useMemo(() => weave(rule, 31, 16), [rule]);
  const count = 31 * 16;
  useLayoutEffect(() => {
    if (!ref.current) return;
    const d = new THREE.Object3D();
    const c = new THREE.Color();
    let i = 0;
    grid.forEach((row, y) =>
      row.forEach((v, x) => {
        const h = v ? 0.9 + ((x * 7 + y * 3) % 5) * 0.12 : 0.08;
        d.position.set((x - 15) * 0.26, h / 2, (y - 8) * 0.26);
        d.scale.set(0.24, h, 0.24);
        d.updateMatrix();
        ref.current!.setMatrixAt(i, d.matrix);
        ref.current!.setColorAt(i, c.set(v ? '#9fc58a' : '#1c1b18'));
        i++;
      }),
    );
    ref.current.instanceMatrix.needsUpdate = true;
    if (ref.current.instanceColor) ref.current.instanceColor.needsUpdate = true;
  }, [grid]);
  return (
    <group>
      <instancedMesh ref={ref} args={[undefined, undefined, count]}>
        <boxGeometry args={[1, 1, 1]} />
        <meshStandardMaterial roughness={0.7} emissive="#14200f" />
      </instancedMesh>
      <Sign mood="math" text={`rule ${rule} = ${rule.toString(2).padStart(8, '0')}₂`} fontSize={0.42} position={[0, 3.2, -2.4]} />
    </group>
  );
}

const EXHIBITS = [FoundationsExhibit, RelationalExhibit, LanguagesExhibit, GeometryExhibit, AcousticExhibit, WorldsExhibit];

export function Realms() {
  const m = materials();
  return (
    <group>
      {DIVISIONS.map((d, i) => {
        const [x, , z] = onCircle(i, REALM_RADIUS);
        const Ex = EXHIBITS[i]!;
        return (
          <group key={d.id} position={[x, 0, z]} rotation={[0, doorAngle(i) + Math.PI, 0]}>
            <mesh material={m.darkStone} position={[0, 0.12, 0]}>
              <cylinderGeometry args={[6.2, 6.6, 0.24, 6]} />
            </mesh>
            <mesh material={m.gold} position={[0, 0.25, 0]} rotation={[-Math.PI / 2, 0, 0]}>
              <ringGeometry args={[6, 6.08, 6]} />
            </mesh>
            <group position={[0, 0.25, -1.5]}>
              <Ex />
            </group>
            <Sign text={`${d.numeral} · ${d.exhibitTitle.toUpperCase()}`} fontSize={0.36} position={[0, 0.5, 3.6]} rotation={[-Math.PI / 2.6, 0, 0]} />
            <pointLight color={d.accent} intensity={9} distance={14} position={[0, 6, 2]} />
          </group>
        );
      })}
    </group>
  );
}
