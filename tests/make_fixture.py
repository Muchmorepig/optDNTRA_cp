#!/usr/bin/env python3
"""Generate deterministic synthetic coding transcripts and matched paired reads.

This fixture is for execution/regression tests, not biological benchmarking.
No research data or downloaded databases are included.
"""
import argparse
import gzip
import json
from pathlib import Path
import random
import subprocess
from Bio.Seq import Seq
from Bio.Data import CodonTable


def generate(out, count=600, seed=20261029):
    out = Path(out).resolve()
    out.mkdir(parents=True, exist_ok=False)
    rng = random.Random(seed)
    codons = sorted(CodonTable.unambiguous_dna_by_id[1].forward_table)
    proteins = []
    pairs = 0
    with (out / "assembly.test.fasta").open("w") as fa, \
         gzip.open(out / "sample.test_R1.fastq.gz", "wt") as r1, \
         gzip.open(out / "sample.test_R2.fastq.gz", "wt") as r2:
        for i in range(count):
            coding = "ATG" + "".join(rng.choices(codons, k=399))
            dna = "TAATAGTGA" + coding + "TAA"
            name = f"TRINITY_DN{i}_c0_g1_i1"
            fa.write(f">{name}\n{dna}\n")
            proteins.append(str(Seq(coding).translate()))
            for start in range(0, len(dna) - 330 + 1, 35):
                fragment = dna[start:start + 330]
                left = fragment[:150]
                right = str(Seq(fragment[-150:]).reverse_complement())
                pairs += 1
                r1.write(f"@fixture_{i}_{start}/1\n{left}\n+\n{'I' * 150}\n")
                r2.write(f"@fixture_{i}_{start}/2\n{right}\n+\n{'I' * 150}\n")
    # Known protein evidence for only a subset: remaining transcripts exercise RSEM.
    with (out / "test.proteins.fasta").open("w") as f:
        for i, seq in enumerate(proteins[:max(1, count // 10)]):
            f.write(f">synthetic_protein_{i}\n{seq}\n")
    (out / "model.fasta").write_text(f">synthetic_model\n{proteins[0]}\n")
    with (out / "hmmbuild.log").open("w") as log:
        subprocess.run(["hmmbuild", "--amino", str(out / "test.pfam.hmm"), str(out / "model.fasta")], stdout=log, stderr=subprocess.STDOUT, check=True)
    # TransDecoder identifies domtblout orientation from the PF accession.
    # PF00000 is a synthetic test identifier, not an actual Pfam annotation.
    hmm = out / "test.pfam.hmm"
    lines = hmm.read_text().splitlines(keepends=True)
    i = next(i for i, line in enumerate(lines) if line.startswith("NAME"))
    lines.insert(i + 1, "ACC   PF00000.1\n")
    hmm.write_text("".join(lines))
    manifest = {"synthetic": True, "seed": seed, "transcripts": count, "read_pairs": pairs}
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("output")
    p.add_argument("--transcripts", type=int, default=600)
    args = p.parse_args()
    print(json.dumps(generate(args.output, args.transcripts), indent=2))
