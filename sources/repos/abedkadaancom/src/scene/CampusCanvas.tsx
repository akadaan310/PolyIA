import { Suspense, useEffect, useMemo, useRef, useState } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { Environment, Lightformer, MeshReflectorMaterial, OrbitControls, PerformanceMonitor } from '@react-three/drei';
import * as THREE from 'three';
import type { OrbitControls as OrbitControlsImpl } from 'three-stdlib';
import { Architecture } from './Architecture';
import { Atrium } from './Atrium';
import { Realms } from './Realms';
import { Residents3D } from './Residents3D';
import { CampusSky } from './Sky';
import { materials } from './materials';
import { CHOREOGRAPHY, COLOR, LIGHTING, TIERS, detectTier, type Tier } from '../style/bible';
import { useStore } from '../state/store';
import type { Location, Vec3 } from '../world/locations';

export const APPROACH_START: Vec3 = [0, 22, 135];

function CameraRig({ location, intro, onIntroDone, panelOpen }: { location: Location; intro: boolean; onIntroDone: () => void; panelOpen: boolean }) {
  const controls = useRef<OrbitControlsImpl>(null);
  const { camera, size } = useThree();

  // On wide screens the page panel covers the right side: shift the projection so the
  // subject of each location is centred in the visible part of the world.
  useEffect(() => {
    const cam = camera as THREE.PerspectiveCamera;
    if (panelOpen && size.width > 760) cam.setViewOffset(size.width, size.height, Math.min(250, size.width * 0.17), 0, size.width, size.height);
    else cam.clearViewOffset();
    cam.updateProjectionMatrix();
  }, [camera, size, panelOpen]);
  const reduced = useStore((s) => s.settings.reducedMotion);
  const goal = useRef({ pos: new THREE.Vector3(...location.camera), tgt: new THREE.Vector3(...location.target), active: true });
  const introT = useRef<number | null>(intro && !reduced ? 0 : null);
  const introFrom = useRef(new THREE.Vector3(...APPROACH_START));

  // initial placement
  useEffect(() => {
    if (introT.current !== null) camera.position.set(...APPROACH_START);
    else camera.position.set(...location.camera);
    controls.current?.target.set(...location.target);
    controls.current?.update();
    if (introT.current === null) onIntroDone();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // on location change, start a damped travel (or snap under reduced motion)
  useEffect(() => {
    goal.current.pos.set(...location.camera);
    goal.current.tgt.set(...location.target);
    goal.current.active = true;
    if (introT.current !== null && location.path !== '/') introT.current = null;
    if (reduced) {
      camera.position.copy(goal.current.pos);
      controls.current?.target.copy(goal.current.tgt);
      controls.current?.update();
    }
  }, [location, reduced, camera]);

  // skipping the intro (event from the DOM)
  useEffect(() => {
    const skip = () => {
      if (introT.current === null) return;
      introT.current = null;
      camera.position.copy(goal.current.pos);
      controls.current?.target.copy(goal.current.tgt);
      onIntroDone();
    };
    window.addEventListener('su:skip-intro', skip);
    return () => window.removeEventListener('su:skip-intro', skip);
  }, [camera, onIntroDone]);

  useFrame((_, dt) => {
    const c = controls.current;
    if (!c) return;
    if (introT.current !== null) {
      introT.current = Math.min(1, introT.current + dt / CHOREOGRAPHY.approachSeconds);
      const e = CHOREOGRAPHY.ease(introT.current);
      camera.position.lerpVectors(introFrom.current, goal.current.pos, e);
      c.target.lerp(goal.current.tgt, Math.min(1, dt * 2));
      c.update();
      if (introT.current >= 1) {
        introT.current = null;
        onIntroDone();
      }
      return;
    }
    if (goal.current.active && !reduced) {
      const k = 1 - Math.exp(-CHOREOGRAPHY.travelDamping * dt);
      camera.position.lerp(goal.current.pos, k);
      c.target.lerp(goal.current.tgt, k);
      c.update();
      if (camera.position.distanceTo(goal.current.pos) < 0.05 && c.target.distanceTo(goal.current.tgt) < 0.05) goal.current.active = false;
    }
  });

  return (
    <OrbitControls
      ref={controls}
      makeDefault
      enableDamping
      dampingFactor={0.08}
      enablePan={false}
      minDistance={4}
      maxDistance={90}
      maxPolarAngle={Math.PI * 0.49}
      rotateSpeed={0.5}
      zoomSpeed={0.6}
      onStart={() => {
        goal.current.active = false;
        if (introT.current !== null) {
          introT.current = null;
          onIntroDone();
        }
      }}
    />
  );
}

function Ground({ tier }: { tier: Tier }) {
  const m = materials();
  if (tier.reflections) {
    return (
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0, 0]}>
        <planeGeometry args={[260, 260]} />
        <MeshReflectorMaterial
          blur={[280, 80]}
          resolution={512}
          mixBlur={1}
          mixStrength={0.9}
          roughness={0.75}
          depthScale={1.1}
          minDepthThreshold={0.4}
          maxDepthThreshold={1.3}
          color="#151413"
          metalness={0.55}
          mirror={0.55}
          roughnessMap={m.floorTexture}
        />
      </mesh>
    );
  }
  return (
    <mesh rotation={[-Math.PI / 2, 0, 0]} material={m.floor}>
      <planeGeometry args={[260, 260]} />
    </mesh>
  );
}

function Scene({ tier, skyLabels }: { tier: Tier; skyLabels: boolean }) {
  const observer = useStore((s) => s.world.observer);
  const skyTime = useStore((s) => s.world.skyTime);
  return (
    <>
      <color attach="background" args={[COLOR.obsidian]} />
      <fogExp2 attach="fog" args={[COLOR.fog, LIGHTING.fogDensity]} />
      <ambientLight intensity={LIGHTING.ambient} />
      <hemisphereLight args={['#5a5f7a', '#1a130c', 0.9]} />
      <directionalLight color={LIGHTING.moon.color} intensity={LIGHTING.moon.intensity} position={[-40, 60, 30]} />
      <directionalLight color={LIGHTING.key.color} intensity={LIGHTING.key.intensity} position={[25, 22, 90]} />
      {tier.environment ? (
        <Environment resolution={64} frames={1}>
          <Lightformer form="rect" intensity={2} color="#F1D79C" position={[0, 6, 10]} scale={[10, 2, 1]} />
          <Lightformer form="rect" intensity={1} color="#8D232C" position={[-10, 4, -6]} scale={[6, 6, 1]} />
          <Lightformer form="ring" intensity={1.5} color="#b9c4d6" position={[8, 10, -8]} scale={4} />
        </Environment>
      ) : null}
      <CampusSky lat={observer.lat} lon={observer.lon} magLimit={tier.stars} time={skyTime} labels={skyLabels} />
      <Ground tier={tier} />
      <Architecture lanterns={tier.id === 'low' ? 10 : 24} />
      <Atrium />
      <Realms />
      <Residents3D count={tier.residents} />
    </>
  );
}

export function webglAvailable(): boolean {
  try {
    const c = document.createElement('canvas');
    return !!(c.getContext('webgl2') || c.getContext('webgl'));
  } catch {
    return false;
  }
}

export interface CampusCanvasProps {
  location: Location;
  intro: boolean;
  onIntroDone: () => void;
  onContextLost: () => void;
  panelOpen: boolean;
}

export default function CampusCanvas({ location, intro, onIntroDone, onContextLost, panelOpen }: CampusCanvasProps) {
  const quality = useStore((s) => s.settings.quality);
  const tierId = quality === 'auto' ? detectTier() : quality;
  const tier = TIERS[tierId];
  const [dpr, setDpr] = useState<number>(Math.min(tier.dpr[1], typeof window !== 'undefined' ? window.devicePixelRatio : 1));
  useEffect(() => setDpr(Math.min(tier.dpr[1], window.devicePixelRatio)), [tier]);
  const gl = useMemo(() => ({ antialias: tier.antialias, powerPreference: 'high-performance' as const, alpha: false }), [tier.antialias]);
  return (
    <Canvas
      key={tierId}
      dpr={dpr}
      gl={gl}
      camera={{ fov: 50, near: 0.1, far: 800, position: APPROACH_START }}
      onCreated={({ gl: renderer }) => {
        renderer.domElement.addEventListener('webglcontextlost', (e) => {
          e.preventDefault();
          onContextLost();
        });
        renderer.toneMappingExposure = 1.15;
        renderer.domElement.setAttribute('aria-hidden', 'true');
        renderer.domElement.setAttribute('data-testid', 'campus-canvas');
      }}
    >
      <PerformanceMonitor onDecline={() => setDpr((d) => Math.max(tier.dpr[0], d * 0.75))} onIncline={() => setDpr((d) => Math.min(tier.dpr[1], d * 1.15))}>
        <Suspense fallback={null}>
          <Scene tier={tier} skyLabels={location.id === 'sky'} />
        </Suspense>
        <CameraRig location={location} intro={intro} onIntroDone={onIntroDone} panelOpen={panelOpen} />
      </PerformanceMonitor>
    </Canvas>
  );
}
