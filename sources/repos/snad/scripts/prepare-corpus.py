#!/usr/bin/env python3
"""Rebuild independently licensed corpus data from unchanged local snapshots.

No network, text normalization, semantic attribution, or missing-feature filling.
Alignment-only folding is explicit and never changes source text or raw QAC rows.
"""
import hashlib
import json
import re
import unicodedata
from collections import defaultdict, Counter
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "data"
UPSTREAM = DATA / "upstream"
QAC_NAME = "quranic-corpus-morphology-0.4.txt"
QAC_SHA256 = "a1d12923815341face765083805d2148ed2d9f5cc3f7d6665219d887675d8c46"
RISAN_SHA256 = "d8a8adff387f60ce3ff7dbe3238dd9b27120bfe29d8fcb07ad2e89cad37cefd4"
QAC_SOURCE = "qac-v0.4:a1d12923815341fa"
BW = dict(zip("'>&<}AbptvjHxd*rzs$SDTZEg_fqklmnhwYyFNKaui~o^#`{:@\"[;,.!-+%]",
              "ءأؤإئا بةتثجحخدذرزسشصضطظعغـفقكلمنهوىيًٌٍَُِّْٰٓٔٱۣۜ۟۠ۢۥۦ۪ۭۨ۫۬".replace(" ", "")))


def decode(value):
    return "".join(BW.get(c, c) for c in value)


def alignment_key(value):
    # Preserve all actual base letters except the documented alef-wasla fold.
    return "".join(c for c in value.replace("ٱ", "ا")
                   if unicodedata.category(c) not in {"Mn", "Me"} and c != "ـ")


def write_json(path, value):
    payload = (json.dumps(value, ensure_ascii=False, separators=(",", ":")) + "\n").encode()
    path.write_bytes(payload)
    return {"path": str(path.relative_to(BASE)), "sha256": hashlib.sha256(payload).hexdigest(), "bytes": len(payload)}


def segment_features(raw):
    out = {}
    for flag in raw.split("|"):
        match = re.fullmatch(r"([123])([MF])?([SDP])", flag)
        number = re.fullmatch(r"[MF]?([SDP])", flag)
        if match:
            out["person"] = match[1]
            out["number"] = {"S": "singular", "D": "dual", "P": "plural"}[match[3]]
        elif number:
            out["number"] = {"S": "singular", "D": "dual", "P": "plural"}[number[1]]
        elif flag in {"PERF", "IMPF"}:
            out["aspect"] = flag
        elif flag == "IMPV":
            out["mood"] = flag
        elif flag.startswith("ROOT:"):
            out["root"] = decode(flag[5:])
        elif flag.startswith("LEM:"):
            out["lemma"] = decode(flag[4:])
    return out


def main():
    raw = (UPSTREAM / "risan-quran-v3.1.2.json").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == RISAN_SHA256, "Risan snapshot differs from pinned bytes"
    source = "https://github.com/risan/quran-json/blob/64c0d713a91923c6ee1216b7c0206bad9a7846b8/dist/quran.json"
    records = [dict(id=f"quran:{s['id']}:{v['id']}", surah=s["id"], ayah=v["id"], text=v["text"], source=source)
               for s in json.loads(raw) for v in s["verses"]]
    assert len(records) == 6236 and len({r["id"] for r in records}) == 6236
    assert {r["surah"] for r in records} == set(range(1, 115))
    corpus_artifact = write_json(DATA / "quran.json", records)

    qac_raw = (UPSTREAM / QAC_NAME).read_bytes()
    assert hashlib.sha256(qac_raw).hexdigest() == QAC_SHA256, "QAC snapshot differs from pinned bytes"
    words = defaultdict(lambda: defaultdict(list))
    segments = 0
    for line in qac_raw.decode().splitlines():
        if not line or line.startswith("#") or line.startswith("LOCATION"):
            continue
        location, form, tag, features = line.split("\t")
        match = re.fullmatch(r"\((\d+):(\d+):(\d+):(\d+)\)", location)
        assert match, f"Malformed QAC location: {location}"
        s, a, w, seg = map(int, match.groups())
        words[f"quran:{s}:{a}"][w].append((seg, form, tag, features))
        segments += 1
    assert segments == 128219 and sum(map(len, words.values())) == 77429
    assert set(words) == {r["id"] for r in records}

    output, totals = {}, Counter()
    for record in records:
        locus = record["id"]
        source_words = words[locus]
        tokens = record["text"].split()
        count_match = len(source_words) == len(tokens)
        morphology, unaligned = [], []
        for word_index, rows in sorted(source_words.items()):
            rows = sorted(rows)
            source_surface = "".join(decode(row[1]) for row in rows)
            aligned = (count_match and alignment_key(source_surface) == alignment_key(tokens[word_index - 1]))
            location = f"({record['surah']}:{record['ayah']}:{word_index})"
            if not aligned:
                unaligned.append({"qacWordIndex": word_index,
                                  "reason": "word-count-mismatch" if not count_match else "surface-key-mismatch"})
                totals["unalignedWords"] += 1
                continue
            totals["alignedWords"] += 1
            candidates = defaultdict(set)
            segment_annotations = []
            for segment, form, tag, raw_features in rows:
                f = segment_features(raw_features)
                segment_annotations.append({"segment": segment, "features": f})
                for field, value in f.items():
                    candidates[field].add(value)
            unique = {field: next(iter(values)) for field, values in candidates.items() if len(values) == 1}
            ambiguous = {field: sorted(values) for field, values in candidates.items() if len(values) > 1}
            if ambiguous:
                totals["ambiguousWords"] += 1
            if unique:
                totals["featureWords"] += 1
                totals["personWords"] += "person" in unique
                morphology.append({"tokenIndex": word_index - 1, "qacWordIndex": word_index,
                                   "features": unique, "segmentFeatures": segment_annotations,
                                   "ambiguousFields": ambiguous,
                                   "evidence": [{"id": f"qac:{record['surah']}:{record['ayah']}:{word_index}",
                                                 "status": "derived", "method": "QAC v0.4 tag projection; gated alignment v1",
                                                 "sourceId": QAC_SOURCE,
                                                 "note": f"Original source word {location}; source features are grammatical annotations, not speaker identities. Unanimous segment fields only; disagreements retained."}]})
        status = "aligned" if not unaligned else "unaligned" if not morphology else "partial"
        totals[status + "Ayahs"] += 1
        totals["featureAyahs"] += bool(morphology)
        output[locus] = {"sourceId": QAC_SOURCE, "status": status,
                         "qacWordCount": len(source_words), "textTokenCount": len(tokens),
                         "morphology": morphology, "unalignedWords": unaligned}
    morphology_artifact = write_json(DATA / "quran.morphology.json", output)
    compact = {locus: {"sourceId": entry["sourceId"], "status": entry["status"],
                       "features": [[m["tokenIndex"], m["features"]] for m in entry["morphology"]],
                       "unalignedWords": len(entry["unalignedWords"]),
                       "ambiguousWords": sum(bool(m["ambiguousFields"]) for m in entry["morphology"])}
               for locus, entry in output.items()}
    compact_artifact = write_json(DATA / "quran.features.json", compact)
    notice = qac_raw.decode().split("LOCATION\tFORM\tTAG\tFEATURES")[0]
    (UPSTREAM / "QAC-NOTICES.txt").write_text(notice)
    report = {"schemaVersion": "snad.qac-projection.v1", "sourceId": QAC_SOURCE,
              "sourceRepository": "https://github.com/taziksh/quran-frequencies",
              "sourceCommit": "079cdc74cd494ec1b35011363288d80cae047c51",
              "sourcePath": "data/quranic-corpus-morphology-0.4.txt",
              "sourceUrl": "https://raw.githubusercontent.com/taziksh/quran-frequencies/079cdc74cd494ec1b35011363288d80cae047c51/data/quranic-corpus-morphology-0.4.txt",
              "sourceSha256": QAC_SHA256, "sourceBytes": len(qac_raw),
              "officialOrigin": "https://corpus.quran.com/download/", "retrievedAt": "2026-10-18",
              "officialDigestVerified": False,
              "crossMirror": {"repository": "https://github.com/AhmedSaadi0/quran-words", "commit": "a6d4217a9e1422978c367eadc833ff4883db77fb", "path": "data/quranic-corpus-morphology-0.4.txt", "sha256": "910b721a8f04f4334ac5d4c62b19e858f5d720c525bb975f2e750ea2c6bb532d", "comparison": "Identical content after CRLF/LF folding; bundled snapshot unchanged CRLF."},
              "license": {"annotations": "GNU General Public License (version unspecified in dataset header), plus verbatim/no-changing notice", "underlyingText": "Tanzil Uthmani v1.0.2; CC BY-ND 3.0 Unported, plus verbatim/no-changing notice", "noticePath": "data/upstream/QAC-NOTICES.txt", "rawUnmodified": True, "scope": "Separate third-party data; no relicensing of generic SDK code."},
              "alignment": {"version": 1, "method": "Equal per-ayah word count AND each mapped word surface matches after alignment-key folding", "folds": ["remove Unicode Mn and Me combining characters", "remove U+0640 tatweel", "replace U+0671 alef wasla with U+0627 alef"], "foldAppliedToStoredText": False, "failedWords": "No features assigned; source word coordinates and reason retained.", "limitation": "Surface equality is an alignment check, not an independent validation of QAC annotation accuracy."},
              "projection": {"person": "Exact QAC flags 1/2/3 with number, only if segment values agree", "number": "QAC S/D/P flags; only if segment values agree", "aspect": "Original PERF/IMPF tags retained; no past/future semantic inference", "mood": "Original imperative tag IMPV retained separately from aspect", "rootLemma": "Buckwalter strings decoded to Arabic, no linguistic changes", "tense": "Absent: no inferred tense", "conflicts": "Omit conflicting aggregate field and retain every segmentFeatures value plus ambiguousFields", "unknown": "Absence remains absence"},
              "coverage": {"totalAyahs": 6236, "sourceMorphologyAyahs": len(words), "sourceWords": 77429, "sourceSegments": segments, **totals},
              "compactSchema": {"version": "snad.qac-features.v1", "path": "data/quran.features.json", "shape": "Object keyed quran:<surah>:<ayah>; value {sourceId,status,features:[[zeroBasedWhitespaceTokenIndex,features]],unalignedWords,ambiguousWords}", "evidenceReconstruction": "Each tuple is a derived QAC tag projection, method qac-tag-projection-v1, sourceId from its enclosing record. Full segment conflict/evidence details live in quran.morphology.json; raw source and all notices are unchanged in data/upstream."},
              "sourceNotices": notice,
              "artifacts": [corpus_artifact, morphology_artifact, compact_artifact]}
    (DATA / "quran.morphology.provenance.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    provenance = json.loads((DATA / "quran.provenance.json").read_text())
    provenance["morphology"] = {"status": "separate-licensed-original-QAC-projection", "path": "data/quran.morphology.json", "provenancePath": "data/quran.morphology.provenance.json", "sourceAyahs": 6236, "featureAyahs": totals["featureAyahs"]}
    (DATA / "quran.provenance.json").write_text(json.dumps(provenance, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(report["coverage"], indent=2))


if __name__ == "__main__":
    main()
