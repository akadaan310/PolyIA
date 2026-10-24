"""QIA/0.1 reproducible domain-limited demonstrator.

No quantum hardware, general NLP, broad physical engine, or universal semantic inference.
This implementation is deliberately independent of the medical FNMS/RDKit package.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Iterable
import hashlib, math, json, unicodedata

STATUS = {'externally_supported','formal_derivation','source_lexicon',
          'user_stipulation','hypothesis','rejected'}

@dataclass(frozen=True)
class Form:
    id: str
    sort: str
    surface: str
    namespace: str
    language: str = 'und'
    sense: str = ''

@dataclass(frozen=True)
class RelationSignature:
    name: str
    inputs: tuple[str, ...]
    output: str
    reversible: bool = False
    symmetric: bool = False
    transitive: bool = False

@dataclass(frozen=True)
class Claim:
    id: str
    relation: str
    inputs: tuple[str, ...]
    output: str
    status: str
    evidence: str
    context: str
    cost: float = 1.0  # artificial routing cost, NOT scientific confidence

@dataclass(frozen=True)
class Witness:
    target: str
    cost: float
    claim_ids: tuple[str, ...]

class QIARefusal(ValueError): pass

class QIA:
    def __init__(self):
        self.forms: dict[str, Form] = {}
        self.signatures: dict[str, RelationSignature] = {}
        self.claims: dict[str, Claim] = {}

    def add_form(self, form: Form):
        if form.id in self.forms:
            raise QIARefusal(f'duplicate form {form.id}')
        self.forms[form.id] = form

    def register(self, rel: RelationSignature):
        if rel.name in self.signatures:
            raise QIARefusal('duplicate signature')
        self.signatures[rel.name] = rel

    def add_claim(self, claim: Claim):
        if claim.id in self.claims:
            raise QIARefusal('duplicate claim')
        if claim.status not in STATUS or not claim.evidence or not claim.context:
            raise QIARefusal('claim requires status, evidence and context')
        if not math.isfinite(claim.cost) or claim.cost < 0:
            raise QIARefusal('cost must be nonnegative and finite')
        if claim.relation not in self.signatures:
            raise QIARefusal('unknown relation')
        try:
            actual_inputs = tuple(self.forms[i].sort for i in claim.inputs)
            actual_output = self.forms[claim.output].sort
        except KeyError as err:
            raise QIARefusal(f'unknown form {err}') from err
        sig = self.signatures[claim.relation]
        if (actual_inputs, actual_output) != (sig.inputs, sig.output):
            raise QIARefusal(f'wrong sort or ordered port: {actual_inputs}->{actual_output}; expected {sig.inputs}->{sig.output}')
        self.claims[claim.id] = claim

    def derive(self, seeds: Iterable[str], *, allowed=frozenset({'externally_supported','formal_derivation','source_lexicon'})) -> dict[str, Witness]:
        """Minimum-cost *derivation tree* over registered AND hyperedges.

        All input ports needed; no LLM inferencing; nonnegative cost; finite registry.
        Shared ancestor cost may be double-counted: not minimum DAG/proof-sharing cost.
        """
        seedset = set(seeds)
        if seedset - self.forms.keys():
            raise QIARefusal('unknown seed')
        best = {x: Witness(x, 0.0, ()) for x in seedset}
        changed = True
        while changed:
            changed = False
            for e in self.claims.values():
                if e.status not in allowed or any(i not in best for i in e.inputs):
                    continue
                candidate = e.cost + sum(best[i].cost for i in e.inputs)
                if e.output not in best or candidate < best[e.output].cost - 1e-12:
                    trace = tuple(s for i in e.inputs for s in best[i].claim_ids) + (e.id,)
                    best[e.output] = Witness(e.output, candidate, trace)
                    changed = True
        return best

    def inverse_fiber(self, relation: str, target: str, allowed=frozenset({'externally_supported','formal_derivation','source_lexicon'})) -> tuple[tuple[str, ...], ...]:
        """Finite one-step, registered inverse; no global inverse oracle."""
        return tuple(e.inputs for e in self.claims.values() if e.relation == relation
                     and e.output == target and e.status in allowed)

    def certificate(self, target: str, seeds: Iterable[str], *, allowed=frozenset({'externally_supported','formal_derivation','source_lexicon'})):
        best = self.derive(seeds, allowed=allowed)
        if target not in best:
            return {'target':target,'verdict':'not-derivable','available_seeds':sorted(seeds)}
        w=best[target]
        return {'target':target,'verdict':'derivable-under-registered-claims',
                'tree_cost':w.cost,'claim_witness':[asdict(self.claims[i]) for i in w.claim_ids],
                'note':'derivability does not prove external scientific truth; cost not a probability'}


def exact_encoding(text: str) -> dict:
    raw=text.encode('utf-8')
    return {'surface':text,'codec':'UTF-8','codepoint_count':len(text),
            'raw_byte_count':len(raw),'utf8_hex':raw.hex(),'utf8_bits':''.join(f'{b:08b}' for b in raw),
            'sha256':hashlib.sha256(raw).hexdigest(),
            'nfc_surface':unicodedata.normalize('NFC',text),
            'nfc_changed':text!=unicodedata.normalize('NFC',text)}


def verify_encoding(record: dict) -> bool:
    b=bytes.fromhex(record['utf8_hex'])
    return b.decode(record['codec'])==record['surface'] and hashlib.sha256(b).hexdigest()==record['sha256']


def lexicon_demo() -> QIA:
    """Small curated evidence lattice: one ordinary name does not determine a drug.

    The *user_stipulation* identity is allowed only for a separately asserted
    hypothetical named product, not inferred from its description. Historical
    etymologies here are source labels from attached FNMS note, not automated NLP.
    """
    q=QIA()
    for id,sort,surface,namespace,language,sense in [
        ('phrase','Surface','Head Pain Reliever','household','en','contextual-name'),
        ('head','Lexeme','head','en','en','body-part'),
        ('pain','Lexeme','pain','en','en','nociceptive-experience'),
        ('reliever','Lexeme','reliever','en','en','intended-effect-agent'),
        ('caput','Lemma','caput/capitis','classical-latin','la','head'),
        ('dolor','Lemma','dolor/doloris','classical-latin','la','pain'),
        ('levare','Lemma','levare','classical-latin','la','ease'),
        ('intention','Intent','reduce pain at head','compositional','en','target'),
        ('headache','Effect','headache analgesia','clinical','en','use'),
        ('acetaminophen','Substance','acetaminophen','USAN','en','drug'),
        ('ibuprofen','Substance','ibuprofen','INN','en','drug'),
        ('naproxen','Substance','naproxen','INN','en','drug'),
        ('para','ChemicalAlias','paracetamol','INN','en','identity-alias'),
        ('named-product','Product','hypothetical product HPR','user-defined','en','identity'),
        ('triple','LexicalAnalysis','head:location|pain:condition|reliever:function','analysis','en','compound'),
    ]:
        q.add_form(Form(id,sort,surface,namespace,language,sense))
    for r,inp,out in [
        ('SEGMENT',('Surface',),'LexicalAnalysis'),
        ('LATIN_LEMMA_HEAD',('Lexeme',),'Lemma'),
        ('LATIN_LEMMA_PAIN',('Lexeme',),'Lemma'),
        ('LATIN_LEMMA_EASE',('Lexeme',),'Lemma'),
        ('INTERPRET_3',('Lexeme','Lexeme','Lexeme'),'Intent'),
        ('TARGET_EFFECT',('Intent',),'Effect'),
        ('SUPPORTS_INDICATION',('Substance',),'Effect'),
        ('NAMED_AS',('Substance',),'ChemicalAlias'),
        ('PRODUCT_IDENTITY',('Product',),'Substance'),
    ]:
        q.register(RelationSignature(r,inp,out))
    claims = [
        ('segment','SEGMENT',('phrase',),'triple','source_lexicon','FNMS note; English parse'),
        ('head-la','LATIN_LEMMA_HEAD',('head',),'caput','source_lexicon','FNMS note; classical Latin gloss'),
        ('pain-la','LATIN_LEMMA_PAIN',('pain',),'dolor','source_lexicon','FNMS note; classical Latin gloss'),
        ('ease-la','LATIN_LEMMA_EASE',('reliever',),'levare','source_lexicon','FNMS note; lexical approximant'),
        ('interpret','INTERPRET_3',('head','pain','reliever'),'intention','formal_derivation','typed compositional rule'),
        ('effect','TARGET_EFFECT',('intention',),'headache','formal_derivation','intent targets a use, not a molecule'),
        ('clinical-a','SUPPORTS_INDICATION',('acetaminophen',),'headache','externally_supported','FNMS source/FDA clinical use'),
        ('clinical-i','SUPPORTS_INDICATION',('ibuprofen',),'headache','externally_supported','FNMS finite demonstrator'),
        ('clinical-n','SUPPORTS_INDICATION',('naproxen',),'headache','externally_supported','FNMS finite demonstrator'),
        ('chem-alias','NAMED_AS',('acetaminophen',),'para','externally_supported','FNMS/PubChem naming'),
        ('stipulated','PRODUCT_IDENTITY',('named-product',),'acetaminophen','user_stipulation','user stipulates invented product active'),
    ]
    for cid,r,src,dest,status,evidence in claims:
        q.add_claim(Claim(cid,r,src,dest,status,evidence,'example; not individual medical advice'))
    return q


def lexical_candidates() -> dict:
    """Predeclared alternatives with *typed* relationships, not a general thesaurus."""
    return {
      'head': [{'form':'caput / capitis','kind':'translation-lemma','language':'Latin','note':'classical Latin'},
               {'form':'cephal-','kind':'learned-combining-form','language':'Greek','note':'NOT classical Latin'},
               {'form':'cranial','kind':'anatomic-related','language':'English','note':'not identical to head'}],
      'pain': [{'form':'dolor / doloris','kind':'translation-lemma','language':'Latin','note':'classical Latin'},
               {'form':'alg-','kind':'learned-combining-form','language':'Greek','note':'pain root; not Latin'},
               {'form':'discomfort','kind':'broader-or-weaker','language':'English','note':'not strict synonym'}],
      'reliever': [{'form':'levare','kind':'function-gloss','language':'Latin','note':'ease; not a lexical identity'},
                   {'form':'remedium','kind':'functional-noun','language':'Latin','note':'remedy, not drug ID'},
                   {'form':'aggravator','kind':'directionally-opposed-function','language':'English','note':'only under fixed outcome and time'}]
    }


def hadamard(state:tuple[complex,complex]) -> tuple[complex,complex]:
    a,b=state
    return ((a+b)/math.sqrt(2),(a-b)/math.sqrt(2))


def norm2(state:tuple[complex,complex]) -> float:
    return sum(abs(x)**2 for x in state)


def two_basis_interference() -> dict:
    """Actual 2-d Hilbert space quantum-MATH toy on a classical CPU."""
    initial=(complex(1),complex(0))
    once=hadamard(initial)
    twice=hadamard(once)
    return {'initial_probabilities':[abs(x)**2 for x in initial],
            'after_one_H':[abs(x)**2 for x in once],
            'after_two_H':[abs(x)**2 for x in twice],
            'norms':[norm2(initial),norm2(once),norm2(twice)],
            'interpretation':'classically simulated unitary interference; no quantum speedup'}


@dataclass(frozen=True)
class SpringMassIR:
    """One physical *representative* of a finite typed world-system."""
    mass_kg: float
    stiffness_newton_per_m: float
    damping_newton_second_per_m: float
    position_m: float
    velocity_m_per_s: float
    dt_s: float

    def __post_init__(self):
        vals=tuple(asdict(self).values())
        if any(not math.isfinite(v) for v in vals): raise QIARefusal('non-finite physical parameter')
        if self.mass_kg<=0 or self.stiffness_newton_per_m<0 or self.damping_newton_second_per_m<0 or self.dt_s<=0:
            raise QIARefusal('invalid physical units/parameter domain')

    def step(self) -> 'SpringMassIR':
        # Symplectic Euler for m x'' + c x' + k x = 0; discretization, not exact physics.
        accel=(-self.stiffness_newton_per_m*self.position_m-self.damping_newton_second_per_m*self.velocity_m_per_s)/self.mass_kg
        v=self.velocity_m_per_s+self.dt_s*accel
        x=self.position_m+self.dt_s*v
        return SpringMassIR(self.mass_kg,self.stiffness_newton_per_m,self.damping_newton_second_per_m,x,v,self.dt_s)

    def energy_joules(self) -> float:
        return 0.5*self.mass_kg*self.velocity_m_per_s**2+0.5*self.stiffness_newton_per_m*self.position_m**2

    def stability_ratio_undamped(self) -> float:
        return self.dt_s*math.sqrt(self.stiffness_newton_per_m/self.mass_kg)


def geometric_optics_sound_demo(distance_m: float, sound_speed_m_per_s:float=343.0) -> dict:
    if distance_m<=0 or sound_speed_m_per_s<=0: raise QIARefusal('invalid free-field geometry')
    return {'source_distance_m':distance_m,'sound_delay_s':distance_m/sound_speed_m_per_s,
            'ideal_free_field_pressure_ratio_to_1m':1/distance_m,
            'ideal_isotropic_intensity_ratio_to_1m':1/distance_m**2,
            'assumptions':['point emitter','far field','no reflections','homogeneous medium','distance >= 1 meter idealization']}


def toy_packet()->dict:
    q=lexicon_demo()
    general=q.certificate('headache',['head','pain','reliever'])
    no_identity=q.certificate('acetaminophen',['phrase','head','pain','reliever'])
    stipulated=q.certificate('acetaminophen',['named-product'],allowed=frozenset({'externally_supported','formal_derivation','source_lexicon','user_stipulation'}))
    fiber=q.inverse_fiber('SUPPORTS_INDICATION','headache')
    s=SpringMassIR(1.0,100.0,0.1,0.1,0,0.005)
    return {'schema':'QIA/0.1','phrase_encoding':exact_encoding('Head Pain Reliever'),
            'lexical_candidates':lexical_candidates(),'generic_intent_path':general,
            'cannot_infer_specific_drug_from_name':no_identity,
            'stipulated_product_identity':stipulated,
            'known_indication_sources_in_finite_demo':fiber,
            'two_basis_interference':two_basis_interference(),
            'physics_ir_initial':asdict(s),'physics_ir_next':asdict(s.step()),
            'physics_kinetic_plus_elastic_energy_j':s.energy_joules(),
            'acoustic_toy':geometric_optics_sound_demo(10.0)}

if __name__=='__main__':
    print(json.dumps(toy_packet(),indent=2,ensure_ascii=False))

@dataclass(frozen=True)
class DimQuantity:
    """Dimensioned scalar with L/M/T exponent tuple. Not a symbolic PDE checker."""
    value: float
    dims: tuple[int,int,int]  # powers of m, kg, s
    def __add__(self,other:'DimQuantity')->'DimQuantity':
        if self.dims!=other.dims: raise QIARefusal(f'incompatible dimensions {self.dims} vs {other.dims}')
        return DimQuantity(self.value+other.value,self.dims)
    def __mul__(self,other:'DimQuantity')->'DimQuantity':
        return DimQuantity(self.value*other.value,tuple(a+b for a,b in zip(self.dims,other.dims)))
    def __truediv__(self,other:'DimQuantity')->'DimQuantity':
        if other.value==0:raise QIARefusal('division by zero')
        return DimQuantity(self.value/other.value,tuple(a-b for a,b in zip(self.dims,other.dims)))


def formal_context_closure(incidence:dict[str,set[str]],attributes:Iterable[str])->dict:
    """FCA double-prime closure, not ontology truth discovery.

    A'=objects containing all A; A''=shared attributes of A'.
    Empty support has intent=all *declared* attributes (vacuous intersection).
    """
    objset={o for o,attrs in incidence.items() if set(attributes)<=attrs}
    universe=set().union(*incidence.values()) if incidence else set()
    closed=set.intersection(*(incidence[o] for o in objset)) if objset else universe
    return {'extent':sorted(objset),'closed_intent':sorted(closed)}
