// Original procedural architecture: equilateral Gothic arches, towers and
// frames, authored as Three.js shapes. No external meshes or franchise assets.

import * as THREE from 'three';

/** An equilateral pointed arch outline: width w, springing height s (apex at s + 0.866w). */
export function archPath(path: THREE.Path, w: number, s: number, x0 = 0): THREE.Path {
  const hw = w / 2;
  path.moveTo(x0 - hw, 0);
  path.lineTo(x0 - hw, s);
  path.absarc(x0 + hw, s, w, Math.PI, (2 * Math.PI) / 3, true);
  path.absarc(x0 - hw, s, w, Math.PI / 3, 0, true);
  path.lineTo(x0 + hw, 0);
  path.lineTo(x0 - hw, 0);
  return path;
}

export function archShape(w: number, s: number): THREE.Shape {
  return archPath(new THREE.Shape(), w, s) as THREE.Shape;
}

/** A frame: a single U-shaped polygon (outer arch up, inner arch back down), extruded. Open at the base. */
export function archFrameGeometry(w: number, s: number, thickness: number, depth: number): THREE.ExtrudeGeometry {
  const hw = w / 2;
  const W = w + 2 * thickness;
  const HW = W / 2;
  const sh = new THREE.Shape();
  sh.moveTo(-HW, 0);
  sh.lineTo(-HW, s);
  sh.absarc(HW, s, W, Math.PI, (2 * Math.PI) / 3, true);
  sh.absarc(-HW, s, W, Math.PI / 3, 0, true);
  sh.lineTo(HW, 0);
  sh.lineTo(hw, 0);
  sh.lineTo(hw, s);
  sh.absarc(-hw, s, w, 0, Math.PI / 3, false);
  sh.absarc(hw, s, w, (2 * Math.PI) / 3, Math.PI, false);
  sh.lineTo(-hw, 0);
  sh.lineTo(-HW, 0);
  const g = new THREE.ExtrudeGeometry(sh, { depth, bevelEnabled: true, bevelThickness: 0.05, bevelSize: 0.04, bevelSegments: 2, curveSegments: 24 });
  g.translate(0, 0, -depth / 2);
  return g;
}

export function archLeafGeometry(w: number, s: number, depth: number): THREE.ExtrudeGeometry {
  const g = new THREE.ExtrudeGeometry(archShape(w, s), { depth, bevelEnabled: false, curveSegments: 24 });
  g.translate(0, 0, -depth / 2);
  return g;
}

/** A wall pierced by n arched openings. */
export function arcadeWallGeometry(length: number, height: number, n: number, archW: number, archS: number, depth: number): THREE.ExtrudeGeometry {
  const shape = new THREE.Shape();
  shape.moveTo(-length / 2, -0.6);
  shape.lineTo(length / 2, -0.6);
  shape.lineTo(length / 2, height);
  shape.lineTo(-length / 2, height);
  shape.lineTo(-length / 2, -0.6);
  const step = length / n;
  for (let i = 0; i < n; i++) {
    const hole = new THREE.Path();
    archPath(hole, archW, archS, -length / 2 + step * (i + 0.5));
    shape.holes.push(hole);
  }
  const g = new THREE.ExtrudeGeometry(shape, { depth, bevelEnabled: false, curveSegments: 16 });
  g.translate(0, 0, -depth / 2);
  return g;
}

/** A tapered tower body with a four-sided spire. */
export function spireGeometry(radius: number, height: number): THREE.ConeGeometry {
  const g = new THREE.ConeGeometry(radius, height, 4, 1);
  g.rotateY(Math.PI / 4);
  g.translate(0, height / 2, 0);
  return g;
}

export function bridgeCurve(a: THREE.Vector3, b: THREE.Vector3, lift: number): THREE.QuadraticBezierCurve3 {
  const mid = a.clone().add(b).multiplyScalar(0.5);
  mid.y += lift;
  // bow the bridge outward from the atrium centre
  const out = new THREE.Vector3(mid.x, 0, mid.z).normalize().multiplyScalar(lift * 0.6);
  mid.add(out);
  return new THREE.QuadraticBezierCurve3(a, mid, b);
}
