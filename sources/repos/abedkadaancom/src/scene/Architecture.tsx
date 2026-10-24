import { useLayoutEffect, useMemo, useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { useNavigate } from 'react-router-dom';
import { archFrameGeometry, arcadeWallGeometry, spireGeometry } from './geometry';
import { materials } from './materials';
import { Sign } from './Sign';
import { useStore } from '../state/store';
import { specimens, SPECIMEN_LABEL } from '../world/specimens';
import { WING_ANGLES, WING_RADIUS, wingPos } from '../world/locations';

/** Rotation that turns a building's front (+z) toward the atrium centre. */
const face = (id: keyof typeof WING_ANGLES): [number, number, number] => [0, WING_ANGLES[id] + Math.PI, 0];

function hoverCursor(on: boolean) {
  document.body.style.cursor = on ? 'pointer' : '';
}

/** Click target helper: invisible box that navigates. */
function Hotspot({ to, position, size }: { to: string; position: [number, number, number]; size: [number, number, number] }) {
  const navigate = useNavigate();
  return (
    <mesh
      position={position}
      onClick={(e) => {
        e.stopPropagation();
        navigate(to);
      }}
      onPointerOver={() => hoverCursor(true)}
      onPointerOut={() => hoverCursor(false)}
    >
      <boxGeometry args={size} />
      <meshBasicMaterial transparent opacity={0} depthWrite={false} />
    </mesh>
  );
}

function Tower({ x, z, h = 20, w = 4 }: { x: number; z: number; h?: number; w?: number }) {
  const m = materials();
  const spire = useMemo(() => spireGeometry(w * 0.78, 8), [w]);
  return (
    <group position={[x, 0, z]}>
      <mesh material={m.stone} position={[0, h / 2, 0]}>
        <boxGeometry args={[w, h, w]} />
      </mesh>
      {[0.25, 0.55, 0.85].map((f) => (
        <mesh key={f} material={m.darkStone} position={[0, h * f, 0]}>
          <boxGeometry args={[w + 0.5, 0.35, w + 0.5]} />
        </mesh>
      ))}
      {/* gold inlay lines */}
      {[-1, 1].map((s) => (
        <mesh key={s} material={m.gold} position={[s * (w / 2 - 0.35), h / 2, w / 2 + 0.02]}>
          <boxGeometry args={[0.06, h * 0.9, 0.04]} />
        </mesh>
      ))}
      {/* lancet windows */}
      {[0.4, 0.7].map((f) => (
        <mesh key={f} material={m.window} position={[0, h * f, w / 2 + 0.03]}>
          <planeGeometry args={[0.5, 2.4]} />
        </mesh>
      ))}
      <mesh geometry={spire} material={m.darkStone} position={[0, h, 0]} />
      <mesh material={m.goldGlow} position={[0, h + 8.3, 0]}>
        <octahedronGeometry args={[0.35]} />
      </mesh>
    </group>
  );
}

function Gate() {
  const m = materials();
  const gate = useStore((s) => s.world.gate);
  const shift = useStore((s) => s.world.inscriptionShift);
  const frame = useMemo(() => archFrameGeometry(9, 7.5, 1.6, 2.6), []);
  const inner = useMemo(() => archFrameGeometry(8.2, 7.2, 0.25, 2.8), []);
  const wall = useMemo(() => arcadeWallGeometry(12, 8, 3, 2.4, 3.5, 1.4), []);
  const plaque = useRef<THREE.Group>(null);
  useFrame((_, dt) => {
    if (!plaque.current) return;
    const target = shift * 0.9;
    plaque.current.position.x += (target - plaque.current.position.x) * Math.min(1, dt * 2);
  });
  return (
    <group position={[0, 0, 30]}>
      <Tower x={-8.6} z={0} h={21} w={4.4} />
      <Tower x={8.6} z={0} h={21} w={4.4} />
      <mesh geometry={frame} material={m.stone} />
      <mesh geometry={inner} material={m.gold} />
      <mesh geometry={wall} material={m.stone} position={[-17, 0, 0]} />
      <mesh geometry={wall} material={m.stone} position={[17, 0, 0]} />
      <mesh material={m.darkStone} position={[0, 17.2, 1.45]}>
        <boxGeometry args={[12.6, 2.6, 0.5]} />
      </mesh>
      <Sign text="SUBSTRATE UNIVERSITY" fontSize={0.62} position={[0, 17.6, 1.75]} />
      <Sign text="HAQ ROOTS" fontSize={0.36} position={[0, 16.7, 1.75]} color="#F1D79C" />
      <Sign text="THE GATE · HALL OF FIRST PRINCIPLES" fontSize={0.32} position={[0, 0.9, 1.6]} />
      <group ref={plaque} position={[0, 0, 0]}>
        <Sign
          mood="math"
          text={gate.stage === 0 ? '1 + 1 = ?' : gate.stage === 1 ? `1 + 1 in ${gate.system === 'F2' ? 'F₂ = 0' : gate.system === 'Z' ? 'ℤ = 2' : 'ℕ = 2'}` : gate.stage === 2 ? '0 / 1 = 0   1 / 0 ∉ im   0 / 0 ∈ ker' : 'im A ⊕ ker A'}
          fontSize={0.62}
          position={[0, 14.9, 1.4]}
          color="#F1D79C"
        />
      </group>
      <Hotspot to="/gate" position={[0, 5, 0]} size={[9, 10, 3]} />
    </group>
  );
}

/** Image-space sculpture: an accepted matrix applied to a lattice of points. */
function Sculpture({ matrix, position }: { matrix: number[][]; position: [number, number, number] }) {
  const ref = useRef<THREE.InstancedMesh>(null);
  const m = materials();
  const pts = useMemo(() => {
    const out: THREE.Vector3[] = [];
    const n = matrix[0]!.length;
    const R = [-1, -0.5, 0, 0.5, 1];
    for (const x of R) for (const y of R) for (const z of n === 3 ? R : [0]) {
      const v = n === 3 ? [x, y, z] : [x, y];
      const o = matrix.map((row) => row.reduce((s, c, j) => s + c * v[j]!, 0));
      out.push(new THREE.Vector3(o[0] ?? 0, o[1] ?? 0, o[2] ?? 0));
    }
    return out;
  }, [matrix]);
  const t = useRef(0);
  useFrame((_, dt) => {
    if (!ref.current) return;
    t.current = Math.min(1, t.current + dt * 0.6);
    const d = new THREE.Object3D();
    pts.forEach((p, i) => {
      d.position.copy(p).multiplyScalar(1.1 * t.current);
      d.scale.setScalar(0.12);
      d.updateMatrix();
      ref.current!.setMatrixAt(i, d.matrix);
    });
    ref.current.instanceMatrix.needsUpdate = true;
  });
  return (
    <group position={position}>
      <instancedMesh ref={ref} args={[undefined, undefined, pts.length]} material={m.goldGlow}>
        <icosahedronGeometry args={[1, 0]} />
      </instancedMesh>
      <mesh material={m.darkStone} position={[0, -2.6, 0]}>
        <cylinderGeometry args={[1.4, 1.7, 0.6, 6]} />
      </mesh>
    </group>
  );
}

function HallOfFirstPrinciples() {
  const m = materials();
  const sculpture = useStore((s) => s.world.sculpture);
  const colZ = useMemo(() => Array.from({ length: 6 }, (_, i) => 27 - i * 2.4), []);
  const colRef = useRef<THREE.InstancedMesh>(null);
  const rib = useMemo(() => archFrameGeometry(9.4, 6, 0.45, 0.5), []);
  useLayoutEffect(() => {
    if (!colRef.current) return;
    const d = new THREE.Object3D();
    let i = 0;
    for (const z of colZ)
      for (const x of [-5, 5]) {
        d.position.set(x, 3.2, z);
        d.updateMatrix();
        colRef.current.setMatrixAt(i++, d.matrix);
      }
    colRef.current.instanceMatrix.needsUpdate = true;
  }, [colZ]);
  return (
    <group>
      <instancedMesh ref={colRef} args={[undefined, undefined, colZ.length * 2]} material={m.stone}>
        <cylinderGeometry args={[0.42, 0.5, 6.4, 10]} />
      </instancedMesh>
      {[26, 21.2, 16.4].map((z) => (
        <mesh key={z} geometry={rib} material={m.stone} position={[0, 0.2, z]} />
      ))}
      {/* gold runner */}
      <mesh material={m.goldGlow} position={[0, 0.03, 21]} rotation={[-Math.PI / 2, 0, 0]}>
        <planeGeometry args={[0.12, 12]} />
      </mesh>
      {sculpture ? <Sculpture matrix={sculpture} position={[0, 4.2, 21.2]} /> : null}
      {sculpture ? <Sign mood="luminous" text="Image-space sculpture · the image of your matrix" fontSize={0.34} position={[0, 1.2, 22.6]} /> : null}
    </group>
  );
}

function Library() {
  const m = materials();
  const navigate = useNavigate();
  const specs = useMemo(() => specimens(), []);
  const ref = useRef<THREE.InstancedMesh>(null);
  const wall = useMemo(() => arcadeWallGeometry(22, 12, 5, 3, 5.2, 1), []);
  useLayoutEffect(() => {
    {
      const mesh = ref.current;
      if (!mesh) return;
      const d = new THREE.Object3D();
      const c = new THREE.Color();
      specs.forEach((s, i) => {
        const bay = Math.floor(s.slot / 12);
        const x = -9 + bay * 4.6 + (s.slot % 12) * 0.32;
        d.position.set(x, 1.2 + s.shelf * 1.7 + s.height / 2, -4.2);
        d.scale.set(s.width * 1.6, s.height, 0.9);
        d.updateMatrix();
        mesh.setMatrixAt(i, d.matrix);
        mesh.setColorAt(i, c.set(s.color).multiplyScalar(0.55));
      });
      mesh.instanceMatrix.needsUpdate = true;
      if (mesh.instanceColor) mesh.instanceColor.needsUpdate = true;
    }
  }, [specs]);
  return (
    <group position={wingPos('library')} rotation={face('library')}>
      <mesh material={m.stone} position={[0, 6, -5.5]}>
        <boxGeometry args={[22, 12, 1]} />
      </mesh>
      {[-11, 11].map((x) => (
        <mesh key={x} material={m.stone} position={[x, 6, 0]}>
          <boxGeometry args={[1, 12, 12]} />
        </mesh>
      ))}
      <mesh material={m.darkStone} position={[0, 12.3, 0]}>
        <boxGeometry args={[23, 0.6, 12.5]} />
      </mesh>
      <mesh geometry={wall} material={m.stone} position={[0, 0, 5.5]} />
      {/* shelves */}
      {Array.from({ length: 6 }, (_, k) => (
        <mesh key={k} material={m.darkStone} position={[0, 1.15 + k * 1.7, -4.2]}>
          <boxGeometry args={[20, 0.08, 1.1]} />
        </mesh>
      ))}
      <instancedMesh
        ref={ref}
        args={[undefined, undefined, specs.length]}
        onClick={(e) => {
          e.stopPropagation();
          const s = e.instanceId !== undefined ? specs[e.instanceId] : undefined;
          if (s) navigate(`/library/specimens/${s.id}`);
        }}
        onPointerOver={() => hoverCursor(true)}
        onPointerOut={() => hoverCursor(false)}
      >
        <boxGeometry args={[1, 1, 1]} />
        <meshStandardMaterial roughness={0.6} metalness={0.1} emissive="#2a1a08" />
      </instancedMesh>
      {/* the founding shelf: the real CGT book, distinct and unlabelled as specimen */}
      <mesh material={m.gold} position={[9.6, 9.7, -3.8]} onClick={(e) => { e.stopPropagation(); navigate('/library/computational-grammar-theory'); }} onPointerOver={() => hoverCursor(true)} onPointerOut={() => hoverCursor(false)}>
        <boxGeometry args={[0.6, 1.4, 1]} />
      </mesh>
      <Sign text="FOUNDING SHELF" fontSize={0.22} position={[9.6, 10.8, -3.6]} />
      <pointLight color="#f1c27a" intensity={18} distance={20} position={[0, 7, 0]} />
      <Sign text="THE LIBRARY OF FORMS" fontSize={0.7} position={[0, 10.6, 6.3]} />
      <Sign mood="luminous" text={`${specs.length} specimen volumes (${SPECIMEN_LABEL.split(' / ')[1]!.toLowerCase()}s) · one real founding book`} fontSize={0.34} position={[0, 9.7, 6.3]} />
      <Hotspot to="/library" position={[0, 4, 6]} size={[22, 8, 1.5]} />
    </group>
  );
}

function Observatory() {
  const m = materials();
  const dome = useRef<THREE.Group>(null);
  const reduced = useStore((s) => s.settings.reducedMotion);
  useFrame((_, dt) => {
    if (dome.current && !reduced) dome.current.rotation.y += dt * 0.03;
  });
  return (
    <group position={wingPos('observatory')} rotation={face('observatory')}>
      <mesh material={m.stone} position={[0, 8, 0]}>
        <cylinderGeometry args={[5.2, 5.8, 16, 24]} />
      </mesh>
      {[4, 8, 12].map((y) => (
        <mesh key={y} material={m.gold} position={[0, y, 0]}>
          <torusGeometry args={[5.5, 0.06, 6, 48]} />
        </mesh>
      ))}
      <group ref={dome} position={[0, 16, 0]}>
        <mesh material={m.polished}>
          <sphereGeometry args={[5.4, 32, 16, 0, Math.PI * 2, 0, Math.PI / 2]} />
        </mesh>
        <mesh material={m.goldGlow} position={[0, 2.8, 2.6]} rotation={[0.9, 0, 0]}>
          <boxGeometry args={[0.9, 0.06, 4.2]} />
        </mesh>
        <mesh material={m.gold} position={[0, 3.4, 2.4]} rotation={[-0.75, 0, 0]}>
          <cylinderGeometry args={[0.35, 0.45, 5, 12]} />
        </mesh>
      </group>
      <mesh material={m.window} position={[0, 9, 5.65]}>
        <planeGeometry args={[0.8, 3]} />
      </mesh>
      <mesh material={m.gold} position={[0, 0, 5.4]}>
        <boxGeometry args={[3.2, 0.12, 0.6]} />
      </mesh>
      <Sign text="THE OBSERVATORY" fontSize={0.7} position={[0, 3, 6.05]} />
      <Sign mood="luminous" text="Earth · addresses · the real sky · images" fontSize={0.32} position={[0, 2.2, 6.05]} />
      <Hotspot to="/observatory" position={[0, 9, 0]} size={[11, 18, 11]} />
    </group>
  );
}

function Nave({ position, rotationY = 0, length, width, height, title, subtitle, to, banners }: { position: [number, number, number]; rotationY?: number; length: number; width: number; height: number; title: string; subtitle?: string; to: string; banners?: string[] }) {
  const m = materials();
  const door = useMemo(() => archFrameGeometry(3.4, 4, 0.6, 1.2), []);
  const roof = useMemo(() => {
    const s = new THREE.Shape();
    s.moveTo(-width / 2 - 0.6, 0);
    s.lineTo(0, width * 0.55);
    s.lineTo(width / 2 + 0.6, 0);
    s.lineTo(-width / 2 - 0.6, 0);
    const g = new THREE.ExtrudeGeometry(s, { depth: length + 1, bevelEnabled: false });
    g.translate(0, 0, -(length + 1) / 2);
    return g;
  }, [length, width]);
  return (
    <group position={position} rotation={[0, rotationY, 0]}>
      <mesh material={m.stone} position={[0, height / 2, 0]}>
        <boxGeometry args={[width, height, length]} />
      </mesh>
      <mesh geometry={roof} material={m.darkStone} position={[0, height, 0]} />
      <mesh geometry={door} material={m.gold} position={[0, 0, length / 2 + 0.2]} />
      <mesh material={m.window} position={[0, 2.6, length / 2 + 0.05]}>
        <planeGeometry args={[3.2, 5.2]} />
      </mesh>
      {/* rose window */}
      <mesh material={m.window} position={[0, height - 1.2, length / 2 + 0.05]}>
        <circleGeometry args={[1.5, 24]} />
      </mesh>
      <mesh material={m.gold} position={[0, height - 1.2, length / 2 + 0.1]}>
        <torusGeometry args={[1.55, 0.09, 6, 32]} />
      </mesh>
      {Array.from({ length: 6 }, (_, i) => (
        <mesh key={i} material={m.gold} position={[0, height - 1.2, length / 2 + 0.1]} rotation={[0, 0, (i * Math.PI) / 6]}>
          <boxGeometry args={[3, 0.06, 0.04]} />
        </mesh>
      ))}
      {(banners ?? []).map((c, i) => (
        <mesh key={i} position={[-width / 2 - 0.05, height * 0.55, -length / 2 + 2 + i * ((length - 4) / Math.max(1, (banners ?? []).length - 1))]} rotation={[0, -Math.PI / 2, 0]}>
          <planeGeometry args={[1.1, 4]} />
          <meshStandardMaterial color={c} emissive={c} emissiveIntensity={0.35} side={THREE.DoubleSide} />
        </mesh>
      ))}
      <Sign text={title} fontSize={0.55} position={[0, height + 0.6 + width * 0.2, length / 2 + 0.6]} />
      {subtitle ? <Sign mood="luminous" text={subtitle} fontSize={0.3} position={[0, 0.5, length / 2 + 1.2]} /> : null}
      <Hotspot to={to} position={[0, height / 2, length / 2]} size={[width, height, 2]} />
    </group>
  );
}

const WINGS = Object.keys(WING_ANGLES) as (keyof typeof WING_ANGLES)[];

function Walkways() {
  const m = materials();
  return (
    <group>
      <mesh material={m.polished} position={[0, 0.02, 23]} rotation={[-Math.PI / 2, 0, 0]}>
        <planeGeometry args={[6, 18]} />
      </mesh>
      {WINGS.map((w) => (
        <group key={w} rotation={[0, WING_ANGLES[w], 0]}>
          <mesh material={m.polished} position={[0, 0.02, (16 + WING_RADIUS - 6) / 2]} rotation={[-Math.PI / 2, 0, 0]}>
            <planeGeometry args={[4, WING_RADIUS - 6 - 16]} />
          </mesh>
          <mesh material={m.gold} position={[0, 0.035, (16 + WING_RADIUS - 6) / 2]} rotation={[-Math.PI / 2, 0, 0]}>
            <planeGeometry args={[0.08, WING_RADIUS - 6 - 16]} />
          </mesh>
        </group>
      ))}
    </group>
  );
}

function Lanterns({ count }: { count: number }) {
  const m = materials();
  const posts = useMemo(() => {
    const ps: [number, number, number][] = [];
    for (let z = 42; z > 16; z -= 6.5) ps.push([-3.6, 0, z], [3.6, 0, z]);
    for (const w of WINGS) {
      const a = WING_ANGLES[w];
      for (const r of [22, 31]) for (const side of [-2.6, 2.6]) ps.push([r * Math.sin(a) + side * Math.cos(a), 0, r * Math.cos(a) - side * Math.sin(a)]);
    }
    return ps.slice(0, count);
  }, [count]);
  return (
    <group>
      {posts.map((p, i) => (
        <group key={i} position={p}>
          <mesh material={m.darkStone} position={[0, 1.4, 0]}>
            <cylinderGeometry args={[0.07, 0.1, 2.8, 6]} />
          </mesh>
          <mesh material={m.goldGlow} position={[0, 2.95, 0]}>
            <octahedronGeometry args={[0.18]} />
          </mesh>
        </group>
      ))}
    </group>
  );
}

export function Architecture({ lanterns }: { lanterns: number }) {
  return (
    <group>
      <Gate />
      <HallOfFirstPrinciples />
      <Library />
      <Observatory />
      <Nave position={wingPos('harness-masters', WING_RADIUS + 3)} rotationY={face('harness-masters')[1]} length={22} width={13} height={11} title="HALL OF HARNESS MASTERS" subtitle="Co-founders · Harness Masters · the one-day path" to="/harness-masters" banners={['#d6ac62', '#c9a3d8', '#7fc1c4', '#f1d79c', '#e08a7a', '#9fc58a']} />
      <Nave position={wingPos('scriptorium')} rotationY={face('scriptorium')[1]} length={14} width={10} height={8} title="THE SCRIPTORIUM" subtitle="Where a day becomes six books" to="/scriptorium" />
      <Nave position={wingPos('common-room')} rotationY={face('common-room')[1]} length={14} width={10} height={8} title="FOUNDER OFFICE · COMMON ROOM" subtitle="Questions, notes and invitations" to="/common-room" />
      <Walkways />
      <Lanterns count={lanterns} />
    </group>
  );
}
