import { useMemo, useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { RESIDENTS, residentLocation } from '../world/residents';
import { materials } from './materials';
import { useStore } from '../state/store';
import { openResident } from '../ui/residentBus';

/** Lightweight robed silhouettes walking scheduled loops; selecting one opens its dialogue. */
export function Residents3D({ count }: { count: number }) {
  const reduced = useStore((s) => s.settings.reducedMotion);
  const hour = new Date().getHours();
  const list = useMemo(() => {
    const atrium = RESIDENTS.filter((r) => residentLocation(r, hour) === 'atrium');
    const extra = RESIDENTS.filter((r) => !atrium.includes(r));
    return [...atrium, ...extra].slice(0, count).map((r, i) => ({
      r,
      radius: i < atrium.length ? 6 + (i % 3) * 1.4 : 17.5 + (i % 2) * 2,
      speed: (0.06 + (i % 4) * 0.015) * (i % 2 ? 1 : -1),
      phase: (i * 2.399) % (Math.PI * 2),
    }));
  }, [count, hour]);
  return (
    <group>
      {list.map((x) => (
        <Figure key={x.r.id} id={x.r.id} color={x.r.color} radius={x.radius} speed={reduced ? 0 : x.speed} phase={x.phase} />
      ))}
    </group>
  );
}

function Figure({ id, color, radius, speed, phase }: { id: string; color: string; radius: number; speed: number; phase: number }) {
  const g = useRef<THREE.Group>(null);
  const t = useRef(phase);
  const m = materials();
  const halo = useMemo(() => new THREE.MeshStandardMaterial({ color, emissive: color, emissiveIntensity: 1.2, toneMapped: false }), [color]);
  useFrame((_, dt) => {
    if (!g.current) return;
    t.current += dt * speed;
    const a = t.current;
    g.current.position.set(radius * Math.sin(a), 0, radius * Math.cos(a) - (radius < 12 ? 1 : 0));
    g.current.rotation.y = a + (speed >= 0 ? Math.PI / 2 : -Math.PI / 2);
    g.current.children[0]!.position.y = 0.95 + Math.abs(Math.sin(a * 40)) * 0.03;
  });
  return (
    <group
      ref={g}
      onClick={(e) => {
        e.stopPropagation();
        openResident(id);
      }}
      onPointerOver={() => (document.body.style.cursor = 'pointer')}
      onPointerOut={() => (document.body.style.cursor = '')}
    >
      <group>
        <mesh material={m.robe}>
          <coneGeometry args={[0.42, 1.9, 10]} />
        </mesh>
        <mesh material={m.robe} position={[0, 1.05, 0]}>
          <sphereGeometry args={[0.2, 12, 8]} />
        </mesh>
        <mesh material={halo} position={[0, 1.05, 0]} rotation={[Math.PI / 2, 0, 0]}>
          <torusGeometry args={[0.3, 0.025, 6, 24]} />
        </mesh>
        <mesh material={halo} position={[0.35, 0.3, 0.1]}>
          <octahedronGeometry args={[0.08]} />
        </mesh>
      </group>
    </group>
  );
}
