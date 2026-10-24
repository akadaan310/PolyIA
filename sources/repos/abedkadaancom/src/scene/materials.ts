import * as THREE from 'three';
import { MATERIAL } from '../style/bible';

// Shared materials, created once. Procedural textures only (no image downloads).

function noiseTexture(size: number, seed: number, scale: number): THREE.DataTexture {
  const data = new Uint8Array(size * size * 4);
  let s = seed >>> 0;
  const rnd = () => ((s = (Math.imul(s ^ (s >>> 15), 2246822507) + 0x9e3779b9) >>> 0) / 4294967296);
  // value noise, two octaves
  const grid = 8;
  const g = Array.from({ length: (grid + 1) * (grid + 1) }, rnd);
  const at = (x: number, y: number) => g[(y % (grid + 1)) * (grid + 1) + (x % (grid + 1))]!;
  for (let y = 0; y < size; y++)
    for (let x = 0; x < size; x++) {
      const fx = (x / size) * grid;
      const fy = (y / size) * grid;
      const ix = Math.floor(fx);
      const iy = Math.floor(fy);
      const tx = fx - ix;
      const ty = fy - iy;
      const v = at(ix, iy) * (1 - tx) * (1 - ty) + at(ix + 1, iy) * tx * (1 - ty) + at(ix, iy + 1) * (1 - tx) * ty + at(ix + 1, iy + 1) * tx * ty;
      const fine = rnd();
      const val = Math.round(255 * (0.55 + scale * (v - 0.5) + 0.12 * (fine - 0.5)));
      const i = 4 * (y * size + x);
      data[i] = data[i + 1] = data[i + 2] = Math.max(0, Math.min(255, val));
      data[i + 3] = 255;
    }
  const t = new THREE.DataTexture(data, size, size, THREE.RGBAFormat);
  t.wrapS = t.wrapT = THREE.RepeatWrapping;
  t.needsUpdate = true;
  return t;
}

/** Flagstone pattern for the courtyards: square slabs with dark joints. */
function flagstoneTexture(size: number): THREE.DataTexture {
  const data = new Uint8Array(size * size * 4);
  const n = 8;
  for (let y = 0; y < size; y++)
    for (let x = 0; x < size; x++) {
      const cx = (x / size) * n;
      const cy = (y / size) * n;
      const jx = Math.min(cx % 1, 1 - (cx % 1));
      const jy = Math.min(cy % 1, 1 - (cy % 1));
      const joint = Math.min(jx, jy) < 0.025;
      const slab = ((Math.floor(cx) * 7 + Math.floor(cy) * 13) % 5) / 5;
      const v = joint ? 40 : 150 + slab * 50 + ((x * 31 + y * 17) % 13);
      const i = 4 * (y * size + x);
      data[i] = data[i + 1] = data[i + 2] = v;
      data[i + 3] = 255;
    }
  const t = new THREE.DataTexture(data, size, size, THREE.RGBAFormat);
  t.wrapS = t.wrapT = THREE.RepeatWrapping;
  t.needsUpdate = true;
  return t;
}

let cache: ReturnType<typeof build> | null = null;

function build() {
  const stoneRough = noiseTexture(128, 7, 0.28);
  stoneRough.repeat.set(2, 2);
  const flag = flagstoneTexture(256);
  flag.repeat.set(14, 14);
  return {
    stone: new THREE.MeshStandardMaterial({ ...MATERIAL.blackStone, roughnessMap: stoneRough, bumpMap: stoneRough, bumpScale: 0.012 }),
    darkStone: new THREE.MeshStandardMaterial({ color: '#272421', roughness: 0.88, metalness: 0.04, roughnessMap: stoneRough }),
    polished: new THREE.MeshStandardMaterial({ ...MATERIAL.polishedStone }),
    floor: new THREE.MeshStandardMaterial({ color: '#46413b', roughness: 0.32, metalness: 0.25, roughnessMap: flag, map: flag }),
    floorTexture: flag,
    gold: new THREE.MeshStandardMaterial({ ...MATERIAL.gold }),
    goldGlow: new THREE.MeshStandardMaterial({ color: MATERIAL.goldGlow.color, emissive: MATERIAL.goldGlow.emissive, emissiveIntensity: MATERIAL.goldGlow.emissiveIntensity, toneMapped: false }),
    crimson: new THREE.MeshStandardMaterial({ ...MATERIAL.crimsonGlass }),
    ivory: new THREE.MeshStandardMaterial({ ...MATERIAL.ivory }),
    window: new THREE.MeshStandardMaterial({ color: '#2b1d0c', emissive: '#e7b866', emissiveIntensity: 0.9, toneMapped: false }),
    doorLeaf: new THREE.MeshStandardMaterial({ color: '#221c16', roughness: 0.5, metalness: 0.35 }),
    robe: new THREE.MeshStandardMaterial({ color: '#16130f', roughness: 0.9 }),
  };
}

export function materials() {
  if (!cache) cache = build();
  return cache;
}
