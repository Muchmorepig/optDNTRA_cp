# Small generated tests

The default test no longer requires a Trinity assembly or large checked-in FASTQs.
From the repository root, after creating the unified environment:

```bash
mamba activate optDNTRA-stable
python -B -m unittest discover -s tests -p 'test_*.py' -v
python -B tests/smoke.py --workdir .test-runs/core --threads 2
```

The deterministic fixture contains 600 synthetic coding transcripts and 15,600
paired reads. It generates a small synthetic protein database and one synthetic
HMM locally; no external database download is required. It tests execution, not
transcriptome completeness or biological accuracy. `PF00000.1` in the test HMM
is a synthetic identifier, not a real Pfam annotation.

To include preprocessing or test single-end reads:

```bash
python -B tests/smoke.py --workdir .test-runs/preprocess --threads 2 --preprocess
python -B tests/smoke.py --workdir .test-runs/single --threads 2 --single-end
```

The separate, optional assembly test has only three synthetic transcripts and
78 read pairs, and uses two threads / a 2G Trinity memory parameter:

```bash
python -B tests/trinity_smoke.py --workdir .test-runs/trinity
```

Always choose a new work directory; tests refuse to overwrite an existing one.
Each successful integration test writes `validation.json` with measured runtime
and record counts. Tests run locally in roughly a minute for the core; runtime
depends on hardware and environment startup overhead. Environment installation
time is separate.

The original ~66 MB test inputs remain available in the earlier commit
`fa7e389d0991fa4615892f7d2269cdf4d5c4ca06` if needed. They are no longer part of
the current tree. Use `git clone --depth 1` to avoid downloading their history.
