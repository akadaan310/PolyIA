"""Capability registry: typed interfaces + metadata, not implementation imports."""
from dataclasses import dataclass

@dataclass(frozen=True)
class Atom:
    id: str
    inputs: tuple[str,...]
    outputs: tuple[str,...]
    provides: tuple[str,...]
    effects: tuple[str,...]=()
    cost: int=1
    evidence: str='fixture'
    version: str='0.1.0'

# Registered fixture models are sample operators, not language knowledge or genuine attestations.
ATOMS = (
    Atom('text.surface@0.1', ('TaskText',), ('Surface',), ('surface',)),
    Atom('lang.identity@0.1', ('Surface',), ('LanguageScope',), ('language-identity',)),
    Atom('pronunciation.fixture@0.1',('LanguageScope',),('Pronunciations',),('pronunciation',),cost=2),
    Atom('ipa.feature.fixture@0.1',('Pronunciations',),('PhoneFeatures',),('phone-features',)),
    Atom('prefix.match.fixture@0.1',('PhoneFeatures',),('PhoneticMatches',),('phonetic-prefix',),cost=2),
    Atom('morphology.fixture@0.1',('LanguageScope',),('MorphCandidates',),('morphology',)),
    Atom('evidence.graph.fixture@0.1',('PhoneticMatches','MorphCandidates'),('Wordset',),('wordset','typed-relations'),cost=2),
    Atom('automaton.package@0.1',('Wordset',),('StateArtifact',),('composed-automaton',)),
)
REGISTRY={a.id:a for a in ATOMS}
CAPABILITY_OUTPUT={'phonetic-prefix':'PhoneticMatches','composed-automaton':'StateArtifact','morphology':'MorphCandidates','typed-relations':'Wordset','wordset':'Wordset','surface':'Surface','pronunciation':'Pronunciations','phone-features':'PhoneFeatures','language-identity':'LanguageScope'}
