/// <reference lib="webworker" />
// Compares one path signature against many candidates off the main thread.
import { bestCorrespondence, compare, type Normalization, type PathSignature } from '../math/paths';

export interface PathJob {
  source: PathSignature;
  candidates: { id: string; sig: PathSignature }[];
  normalization: Normalization | 'best';
}

self.onmessage = (e: MessageEvent<PathJob>) => {
  const { source, candidates, normalization } = e.data;
  const results = candidates.map((c) => ({ id: c.id, ...(normalization === 'best' ? bestCorrespondence(source, c.sig) : compare(source, c.sig, normalization)) }));
  results.sort((a, b) => b.similarity - a.similarity);
  (self as unknown as Worker).postMessage(results);
};
