// A tiny bus so the 3D scene can open a resident's dialogue in the DOM.
import { useSyncExternalStore } from 'react';

let current: string | null = null;
const ls = new Set<() => void>();

export function openResident(id: string | null) {
  current = id;
  ls.forEach((l) => l());
}

export function useActiveResident(): string | null {
  return useSyncExternalStore(
    (l) => {
      ls.add(l);
      return () => ls.delete(l);
    },
    () => current,
    () => current,
  );
}
