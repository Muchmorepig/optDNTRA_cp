#!/usr/bin/env python3
"""Optional tiny assembly test. Requires core plus optDNTRA-trinity environments."""
import argparse
import json
from pathlib import Path
import subprocess
import time
from Bio import SeqIO
from make_fixture import generate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workdir", required=True)
    parser.add_argument("--trinity-env", default="optDNTRA-trinity")
    args = parser.parse_args()
    root = Path(args.workdir).resolve()
    started = time.monotonic()
    manifest = generate(root, count=3)
    wrapper = Path(__file__).resolve().parents[1] / "scripts/run_trinity.py"
    selector = "-p" if Path(args.trinity_env).is_absolute() else "-n"
    with (root / "trinity.log").open("w") as log:
        subprocess.run(["mamba", "run", selector, args.trinity_env, "python", str(wrapper),
                        "--seqType", "fq", "--left", str(root / "sample.test_R1.fastq.gz"),
                        "--right", str(root / "sample.test_R2.fastq.gz"), "--CPU", "2", "--max_memory", "2G",
                        "--output", str(root / "trinity")], stdout=log, stderr=subprocess.STDOUT, check=True)
    records = list(SeqIO.parse(root / "trinity.Trinity.fasta", "fasta"))
    assert records, "Trinity produced no final sequences"
    manifest.update(passed=True, assembled_transcripts=len(records), seconds=round(time.monotonic() - started, 2))
    (root / "validation.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
