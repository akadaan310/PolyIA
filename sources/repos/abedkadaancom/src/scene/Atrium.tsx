import { useMemo, useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import { Text } from '@react-three/drei';
import * as THREE from 'three';
import { useNavigate } from 'react-router-dom';
import { DIVISIONS } from '../content/registry';
import { archFrameGeometry, archLeafGeometry, bridgeCurve } from './geometry';
import { materials } from './materials';
import { Sign } from './Sign';
import { useStore } from '../state/store';
import { ATRIUM_RADIUS, doorAngle, onCircle } from '../world/locations';
import { DOORS, type DoorId } from '../math/bridgeGrammar';
import { analyseInterval } from '../math/music';
import { expand, foldOnce, startFold } from '../math/fold';

const DOOR_W = 3.6;
const DOOR_S = 4.4;

function Door({ index }: { index: number }) {
  const d = DIVISIONS[index]!;
  const m = materials();
  const navigate = useNavigate();
  const visited = useStore((s) => s.world.visited.includes(`division:${d.id}`));
  const gateOpened = useStore((s) => s.world.gate.doorOpened);
  const reduced = useStore((s) => s.settings.reducedMotion);
  const open = visited || (index === 0 && gateOpened);
  const frame = useMemo(() => archFrameGeometry(DOOR_W, DOOR_S, 0.55, 1.3), []);
  const outer = useMemo(() => archFrameGeometry(DOOR_W + 1.1, DOOR_S, 0.16, 1.5), []);
  const leaf = useMemo(() => archLeafGeometry(DOOR_W / 2, DOOR_S, 0.22), []);
  const glow = useMemo(() => new THREE.MeshStandardMaterial({ color: d.accent, emissive: d.accent, emissiveIntensity: 0.9, toneMapped: false }), [d.accent]);
  const left = useRef<THREE.Group>(null);
  const right = useRef<THREE.Group>(null);
  useFrame((_, dt) => {
    const target = open ? 1.25 : 0;
    for (const [g, sgn] of [[left.current, 1], [right.current, -1]] as const) {
      if (!g) continue;
      const cur = g.rotation.y;
      const goal = sgn * target;
      g.rotation.y = reduced ? goal : cur + (goal - cur) * Math.min(1, dt * 1.8);
    }
  });
  const [x, , z] = onCircle(index, ATRIUM_RADIUS);
  const a = doorAngle(index);
  return (
    <group position={[x, 0, z]} rotation={[0, a + Math.PI, 0]}>
      <mesh geometry={frame} material={m.stone} />
      <mesh geometry={outer} material={m.gold} />
      {/* closed doors are backed by a dark panel; open doors show the realm beyond */}
      {open ? null : (
        <mesh position={[0, 0, -0.4]} material={m.doorLeaf}>
          <shapeGeometry args={[archShapeCached()]} />
        </mesh>
      )}
      <group ref={left} position={[-DOOR_W / 2, 0, 0.1]}>
        <mesh geometry={leaf} material={m.doorLeaf} position={[DOOR_W / 4, 0, 0]} />
        <mesh material={glow} position={[DOOR_W / 4, DOOR_S * 0.55, 0.13]}>
          <boxGeometry args={[0.04, DOOR_S * 0.8, 0.02]} />
        </mesh>
      </group>
      <group ref={right} position={[DOOR_W / 2, 0, 0.1]}>
        <mesh geometry={leaf} material={m.doorLeaf} position={[-DOOR_W / 4, 0, 0]} />
        <Sign mood="math" text={d.glyph} fontSize={0.9} position={[-DOOR_W / 4 - 0.9, DOOR_S * 0.62, 0.14]} color={d.accent} />
      </group>
      <Sign text={d.numeral} fontSize={0.6} position={[0, DOOR_S + 3.6, 0.7]} />
      <Sign text={d.door.toUpperCase()} fontSize={0.26} position={[0, DOOR_S + 2.9, 0.7]} />
      <Sign mood="luminous" text={d.name} fontSize={0.3} position={[0, 0.45, 1.1]} color={d.accent} />
      <mesh
        position={[0, 3.6, 0.2]}
        onClick={(e) => {
          e.stopPropagation();
          navigate(`/divisions/${d.id}`);
        }}
        onPointerOver={() => (document.body.style.cursor = 'pointer')}
        onPointerOut={() => (document.body.style.cursor = '')}
      >
        <boxGeometry args={[DOOR_W + 1, 7.4, 1.6]} />
        <meshBasicMaterial transparent opacity={0} depthWrite={false} />
      </mesh>
    </group>
  );
}

let _arch: THREE.Shape | null = null;
function archShapeCached() {
  if (!_arch) {
    const s = new THREE.Shape();
    const hw = DOOR_W / 2;
    s.moveTo(-hw, 0);
    s.lineTo(-hw, DOOR_S);
    s.absarc(hw, DOOR_S, DOOR_W, Math.PI, (2 * Math.PI) / 3, true);
    s.absarc(-hw, DOOR_S, DOOR_W, Math.PI / 3, 0, true);
    s.lineTo(hw, 0);
    _arch = s;
  }
  return _arch;
}

function RingWall() {
  const m = materials();
  const segs = useMemo(() => {
    const out: { pos: [number, number, number]; rot: number; len: number }[] = [];
    for (let i = 0; i < 5; i++) {
      const a1 = doorAngle(i) + 0.17;
      const a2 = doorAngle(i + 1) - 0.17;
      const steps = 3;
      for (let k = 0; k < steps; k++) {
        const b1 = a1 + ((a2 - a1) * k) / steps;
        const b2 = a1 + ((a2 - a1) * (k + 1)) / steps;
        const p1 = new THREE.Vector3(ATRIUM_RADIUS * Math.sin(b1), 0, ATRIUM_RADIUS * Math.cos(b1));
        const p2 = new THREE.Vector3(ATRIUM_RADIUS * Math.sin(b2), 0, ATRIUM_RADIUS * Math.cos(b2));
        const mid = p1.clone().add(p2).multiplyScalar(0.5);
        out.push({ pos: [mid.x, 0, mid.z], rot: Math.atan2(p2.x - p1.x, p2.z - p1.z) + Math.PI / 2, len: p1.distanceTo(p2) + 0.1 });
      }
    }
    return out;
  }, []);
  return (
    <group>
      {segs.map((s, i) => (
        <group key={i} position={s.pos} rotation={[0, s.rot, 0]}>
          <mesh material={m.stone} position={[0, 4.6, 0]}>
            <boxGeometry args={[s.len, 9.2, 1.2]} />
          </mesh>
          <mesh material={m.gold} position={[0, 9.25, 0]}>
            <boxGeometry args={[s.len, 0.14, 1.3]} />
          </mesh>
          <mesh material={m.window} position={[0, 6, 0.62]}>
            <planeGeometry args={[0.35, 2]} />
          </mesh>
        </group>
      ))}
      {/* entrance pylons flanking the open front */}
      {[-1, 1].map((sgn) => (
        <group key={sgn} position={[sgn * 6.2, 0, 13.6]}>
          <mesh material={m.stone} position={[0, 6, 0]}>
            <boxGeometry args={[1.6, 12, 1.6]} />
          </mesh>
          <mesh material={m.goldGlow} position={[0, 12.3, 0]}>
            <octahedronGeometry args={[0.4]} />
          </mesh>
        </group>
      ))}
    </group>
  );
}

function Bridges() {
  const bridges = useStore((s) => s.world.bridges);
  const m = materials();
  const geoms = useMemo(() => {
    const pos = new Map<DoorId, THREE.Vector3>(DOORS.map((d, i) => [d, new THREE.Vector3(...onCircle(i, ATRIUM_RADIUS - 2.6, 0.25))]));
    return bridges.map((b) => ({ b, g: new THREE.TubeGeometry(bridgeCurve(pos.get(b.a)!, pos.get(b.b)!, 1.6), 32, b.type === 'gold' ? 0.16 : 0.22, 6, false) }));
  }, [bridges]);
  return (
    <group>
      {geoms.map(({ b, g }) => (
        <mesh key={`${b.a}${b.b}`} geometry={g} material={b.type === 'gold' ? m.goldGlow : m.polished} />
      ))}
    </group>
  );
}

function IntervalArches() {
  const k = useStore((s) => s.world.interval);
  const a = useMemo(() => analyseInterval(k), [k]);
  const m = materials();
  const geom = useMemo(() => archFrameGeometry(1.3, 1.8, 0.16, 0.25), []);
  const lit = useMemo(() => {
    // The pitch-class hue is mixed into the campus gold so the palette stays restrained.
    const c = new THREE.Color().setHSL(a.hue / 360, 0.45, 0.6).lerp(new THREE.Color('#D6AC62'), 0.55);
    return new THREE.MeshStandardMaterial({ color: c, emissive: c, emissiveIntensity: 0.75 });
  }, [a.hue]);
  return (
    <group>
      {Array.from({ length: 12 }, (_, i) => {
        const ang = (i * Math.PI) / 6;
        const on = a.orbit.includes(i);
        return (
          <group key={i} position={[8.4 * Math.sin(ang), 0, 8.4 * Math.cos(ang) - 1]} rotation={[0, ang + Math.PI, 0]}>
            <mesh geometry={geom} material={on ? lit : m.darkStone} />
          </group>
        );
      })}
      <pointLight color={new THREE.Color().setHSL(a.hue / 360, 0.5, 0.6).lerp(new THREE.Color('#F1D79C'), 0.5)} intensity={8 + a.orbitLength * 1.2} distance={20} position={[0, 4, -1]} />
    </group>
  );
}

function FoldWalkway() {
  const word = useStore((s) => s.world.foldWord);
  const depth = useStore((s) => s.world.foldDepth);
  const m = materials();
  const tiles = useMemo(() => {
    let st = startFold(word);
    for (let i = 0; i < depth && st.current.length > 1; i++) st = foldOnce(st);
    const lens = st.current.map((g) => expand(g, st.rules).length);
    const total = lens.reduce((x, y) => x + y, 0);
    const L = 9.5;
    let z = 13.2;
    return st.current.map((g, i) => {
      const len = (lens[i]! / total) * L;
      const center = z - len / 2;
      z -= len;
      return { g, len, center, folded: st.rules.some((r) => r.glyph === g) };
    });
  }, [word, depth]);
  return (
    <group>
      {tiles.map((t, i) => (
        <group key={`${i}-${t.g}`} position={[0, 0.06, t.center]}>
          <mesh material={t.folded ? m.goldGlow : m.polished}>
            <boxGeometry args={[t.folded ? 1.5 : 1.2, 0.08, Math.max(0.2, t.len - 0.08)]} />
          </mesh>
          <Sign mood="math" text={t.g} fontSize={Math.min(0.9, 0.3 + t.len * 0.25)} position={[0, 0.12, 0]} rotation={[-Math.PI / 2, 0, 0]} color={t.folded ? '#0A0A0A' : '#F1D79C'} />
        </group>
      ))}
    </group>
  );
}

const FRIEZE = '1 + 1 = 2 in ℕ · 1 + 1 = 0 in F₂ · 0 / 1 = 0 · 1 / 0 ∉ im · 0 / 0 ∈ ker · rank A + dim ker A = n · |⟨k⟩| = 12 / gcd(12, k) · unfold(fold(w)) = w · ⟦uv⟧ = ⟦u⟧ ; ⟦v⟧ · ';

function Frieze() {
  const ref = useRef<THREE.Group>(null);
  const reduced = useStore((s) => s.settings.reducedMotion);
  useFrame((_, dt) => {
    if (ref.current && !reduced) ref.current.rotation.y += dt * 0.02;
  });
  const R = ATRIUM_RADIUS - 0.75;
  return (
    <group ref={ref} position={[0, 10.6, 0]}>
      {[0, Math.PI].map((r) => (
        <group key={r} rotation={[0, r, 0]}>
          <Text font="/fonts/pdf/DejaVuSansMono.ttf" fontSize={0.62} {...({ curveRadius: -R } as object)} position={[0, 0, -R]} rotation={[0, 0, 0]} color="#F1D79C" anchorX="center" anchorY="middle" material-toneMapped={false} material-side={THREE.FrontSide}>
            {FRIEZE}
          </Text>
        </group>
      ))}
    </group>
  );
}

function Armillary() {
  const a = useRef<THREE.Group>(null);
  const b = useRef<THREE.Group>(null);
  const c = useRef<THREE.Group>(null);
  const reduced = useStore((s) => s.settings.reducedMotion);
  const m = materials();
  useFrame((_, dt) => {
    if (reduced) return;
    if (a.current) a.current.rotation.y += dt * 0.12;
    if (b.current) b.current.rotation.x += dt * 0.08;
    if (c.current) c.current.rotation.z += dt * 0.05;
  });
  return (
    <group position={[0, 13.5, -1]}>
      <group ref={a}>
        <mesh material={m.gold}>
          <torusGeometry args={[3.2, 0.05, 6, 64]} />
        </mesh>
      </group>
      <group ref={b} rotation={[0, 0, 0.4]}>
        <mesh material={m.gold}>
          <torusGeometry args={[2.6, 0.04, 6, 64]} />
        </mesh>
      </group>
      <group ref={c} rotation={[1.2, 0, 0]}>
        <mesh material={m.gold}>
          <torusGeometry args={[2, 0.04, 6, 64]} />
        </mesh>
      </group>
      <mesh material={m.goldGlow}>
        <sphereGeometry args={[0.45, 24, 12]} />
      </mesh>
      <pointLight color="#F1D79C" intensity={12} distance={26} />
    </group>
  );
}

function Portal() {
  const portal = useStore((s) => s.world.portal);
  const reduced = useStore((s) => s.settings.reducedMotion);
  const ring = useRef<THREE.Mesh>(null);
  const m = materials();
  useFrame((_, dt) => {
    if (ring.current && !reduced) ring.current.rotation.z += dt * (portal?.mode === 'braid' ? 1.2 : 0.3);
  });
  if (!portal) return null;
  return (
    <group position={[-11, 0, 20]} rotation={[0, 0.5, 0]}>
      <mesh ref={ring} position={[0, 3.2, 0]} material={m.goldGlow}>
        <torusGeometry args={[2.4, 0.12, 8, 64, Math.PI * 2]} />
      </mesh>
      <mesh position={[0, 3.2, 0]} material={m.crimson}>
        <circleGeometry args={[2.3, 48]} />
      </mesh>
      <Sign text="FICTIONAL PORTAL" fontSize={0.32} position={[0, 6.2, 0]} />
      <Sign mood="luminous" text={`visualizes a computed path correspondence · similarity ${(portal.similarity * 100).toFixed(0)}% · ${portal.mode}`} fontSize={0.22} position={[0, 0.4, 0.2]} maxWidth={6} textAlign="center" />
    </group>
  );
}

function Floor() {
  const m = materials();
  return (
    <group>
      <mesh material={m.polished} position={[0, 0.015, 0]} rotation={[-Math.PI / 2, 0, 0]}>
        <circleGeometry args={[ATRIUM_RADIUS - 0.4, 72]} />
      </mesh>
      {[5, 11.6, ATRIUM_RADIUS - 0.6].map((r) => (
        <mesh key={r} material={m.gold} position={[0, 0.03, 0]} rotation={[-Math.PI / 2, 0, 0]}>
          <ringGeometry args={[r - 0.06, r, 96]} />
        </mesh>
      ))}
    </group>
  );
}

export function Atrium() {
  return (
    <group>
      <Floor />
      <RingWall />
      {DIVISIONS.map((_, i) => (
        <Door key={i} index={i} />
      ))}
      <Bridges />
      <IntervalArches />
      <FoldWalkway />
      <Frieze />
      <Armillary />
      <Portal />
      <Sign text="THE ATRIUM OF SIX DIVISIONS" fontSize={0.42} position={[0, 0.35, 14.2]} rotation={[-Math.PI / 2.4, 0, 0]} />
    </group>
  );
}
