import argparse
import importlib.machinery
import importlib.util
import logging
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "workflow"))
import optDNTRA_utils as utils

loader = importlib.machinery.SourceFileLoader("salmon_adapter", str(ROOT / "scripts/compat/salmon"))
spec = importlib.util.spec_from_loader(loader.name, loader)
adapter = importlib.util.module_from_spec(spec)
loader.exec_module(adapter)


class RegressionTests(unittest.TestCase):
    def test_dotted_filenames_and_compressed_fastq(self):
        with tempfile.TemporaryDirectory() as tmp:
            for name, allowed in [("trinity.Trinity.fasta", utils.fastaExt),
                                  ("sample.clean.R1.fastq.gz", utils.fastqExt)]:
                p = Path(tmp) / name
                p.touch()
                utils.check_extensions(str(p), allowed, logging.getLogger())
            invalid = Path(tmp) / "sample.fastq.backup"
            invalid.touch()
            with self.assertRaises(utils.OptDNTRAError):
                utils.check_extensions(str(invalid), utils.fastqExt, logging.getLogger())
        self.assertEqual(utils.fastq_extension("sample.clean.R1.fastq.gz"), ".fastq.gz")

    def test_command_preserves_arguments(self):
        args = argparse.Namespace(snakemakeOptions=["snakemake", "--snakefile", "/a b/Snakefile", "all"], threads=2)
        result = utils.update_snakemakeOptions(args, logging.getLogger())
        self.assertIn("/a b/Snakefile", result)
        self.assertEqual(result[-2:], ["--cores", "2"])

    def test_transdecoder6_layout(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "util").mkdir()
            (root / "util/TransDecoder.LongOrfs").touch()
            with mock.patch.object(utils.shutil, "which", side_effect=[None, str(root / "TransDecoder")]):
                self.assertIn("util/TransDecoder.LongOrfs", utils.transdecoder_command("LongOrfs"))

    def test_salmon_versions_and_threshold(self):
        original = ["quant", "-r", "both.fa", "--minAssignedFrags", "1"]
        self.assertEqual(adapter.adapt_args(original, 1), (original, None))
        self.assertEqual(adapter.adapt_args(original, 2), (["quant", "-r", "both.fa"], 1))
        with self.assertRaises(ValueError):
            adapter.adapt_args(["quant", "--minAssignedFrags", "10"], 2)

    def test_fasta_conversion_preserves_sequences(self):
        with tempfile.TemporaryDirectory() as tmp:
            src, dst = Path(tmp) / "reads.fa", Path(tmp) / "reads.fq"
            src.write_text(">a/1\nACGT\nAC\n>b/2\nNNGT\n")
            adapter.fasta_to_fastq(src, dst)
            self.assertEqual(dst.read_text(), "@a/1\nACGTAC\n+\nIIIIII\n@b/2\nNNGT\n+\nIIII\n")

    def test_isolated_tool_environment(self):
        self.assertEqual(utils.tool_command({"trinity_env": "optDNTRA-trinity"}, "trinity_env", "Trinity"),
                         "mamba run -n optDNTRA-trinity Trinity")


if __name__ == "__main__":
    unittest.main()
