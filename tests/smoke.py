#!/usr/bin/env python3
"""Small full core-workflow test; no Trinity assembly or database downloads."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import yaml
from Bio import SeqIO
from make_fixture import generate


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--workdir", required=True, help="New output directory")
    p.add_argument("--threads", type=int, default=2)
    p.add_argument("--trinity-env", default="")
    p.add_argument("--transcripts", type=int, default=600)
    p.add_argument("--preprocess", action="store_true", help="Also test fastp and FastQC")
    p.add_argument("--single-end", action="store_true", help="Exercise single-end quantification")
    args = p.parse_args()
    root = Path(args.workdir).resolve()
    started = time.monotonic()
    manifest = generate(root, args.transcripts)
    repo = Path(__file__).resolve().parents[1]
    config = {"reads": ["_R1", "_R2"], "swiss_prot": str(root / "test.proteins.fasta"),
              "pfam_hmm": str(root / "test.pfam.hmm"), "trinity_env": args.trinity_env,
              "busco_lineage": "", "omark_database": "", "emapper_database": ""}
    (root / "config.yml").write_text(yaml.safe_dump(config))
    cmd = [sys.executable, "-B", str(repo / "optDNTRA.py"), "-c", str(root / "config.yml"),
           "-t", str(root / "assembly.test.fasta"), "-o", str(root / "out"), "-p", str(args.threads)]
    if args.single_end:
        cmd += ["-se", "-f", str(root / "sample.test_R1.fastq.gz")]
    else:
        cmd += ["-1", str(root / "sample.test_R1.fastq.gz"), "-2", str(root / "sample.test_R2.fastq.gz")]
    if args.preprocess:
        cmd += ["--trim", "--qc"]
    for stage, extra in [("dryrun", ["--snakemakeOptions=--dry-run"]), ("run", [])]:
        with (root / f"{stage}.log").open("w") as log:
            subprocess.run(cmd + extra, cwd=root, stdout=log, stderr=subprocess.STDOUT, check=True)
    final = root / "out/results/02-optimization/03-transEvidence"
    tx = list(SeqIO.parse(final / "transcript.flt.final.fa", "fasta"))
    pep = list(SeqIO.parse(final / "transcript.flt.final.pep", "fasta"))
    assert tx and len(tx) == len(pep), "Missing or inconsistent final FASTA records"
    assert len({r.id for r in tx}) == len(tx), "Duplicate final transcript IDs"
    assert {r.id for r in tx} == {r.id for r in pep}, "Transcript/protein IDs differ"
    assert {r.id for r in tx} <= {r.id for r in SeqIO.parse(root / "assembly.test.fasta", "fasta")}
    assert not (root / "test.proteins.fasta.dmnd").exists(), "Index written beside source database"
    manifest.update(passed=True, final_transcripts=len(tx), seconds=round(time.monotonic() - started, 2))
    (root / "validation.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
