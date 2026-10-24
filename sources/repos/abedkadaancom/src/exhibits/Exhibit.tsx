import type { ExhibitId } from '../content/types';
import type { ExerciseRecord } from '../state/store';
import { BridgeGrammarExhibit } from './BridgeGrammar';
import { FoldExhibit } from './Fold';
import { AddressCompilerExhibit } from './AddressCompiler';
import { ImageSculptureExhibit } from './ImageSculpture';
import { IntervalRingExhibit } from './IntervalRing';
import { WorldLoomExhibit } from './WorldLoom';

export function Exhibit({ id, onRecord }: { id: ExhibitId; onRecord?: (r: ExerciseRecord) => void }) {
  switch (id) {
    case 'bridge-grammar': return <BridgeGrammarExhibit onRecord={onRecord} />;
    case 'fold': return <FoldExhibit onRecord={onRecord} />;
    case 'address-compiler': return <AddressCompilerExhibit onRecord={onRecord} />;
    case 'image-sculpture': return <ImageSculptureExhibit onRecord={onRecord} />;
    case 'interval-ring': return <IntervalRingExhibit onRecord={onRecord} />;
    case 'world-loom': return <WorldLoomExhibit onRecord={onRecord} />;
  }
}
