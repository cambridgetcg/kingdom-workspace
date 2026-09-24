"""Removed pressure cannot advance scores or override recorded usage."""
import contextlib
from datetime import datetime, timezone
import importlib.util
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


class AbundanceOperationsTests(unittest.TestCase):
    def test_old_advance_command_preserves_historical_ledger(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'compound/engine').mkdir(parents=True)
            (root / 'compound/ledger').mkdir()
            script = root / 'compound/engine/ledger_calculator.py'
            shutil.copyfile(ROOT / 'compound/engine/ledger_calculator.py', script)
            ledger = root / 'compound/ledger/scores.json'
            before = b'{"week": 8, "assets": {"prior": {"score": 12}}}\n'
            ledger.write_bytes(before)
            result = subprocess.run([sys.executable, str(script), '--advance', '--report'], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(ledger.read_bytes(), before)
            self.assertIn('retired', result.stdout)
            self.assertNotIn('above target', result.stdout)
            self.assertEqual(sorted(p.name for p in ledger.parent.iterdir()), ['scores.json'])

    def test_usage_remains_descriptive_and_dated(self):
        spec = importlib.util.spec_from_file_location('quota_monitor', ROOT / 'tools/quota_monitor.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        entry = {'ts': datetime.now(timezone.utc).isoformat(), 'agent': 'beta', 'wall': 'engine', 'input_tokens': 20, 'output_tokens': 5, 'cost_usd': 0.12, 'wall_rank': 3}
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'usage.jsonl'
            before = (json.dumps(entry) + '\n').encode()
            path.write_bytes(before)
            output = io.StringIO()
            with patch.object(module, 'QUOTA_LOG', path), contextlib.redirect_stdout(output):
                module.cmd_report()
                module.cmd_rebalance()
            self.assertEqual(path.read_bytes(), before)
            self.assertIn('25 logged tokens', output.getvalue())
            self.assertIn('$0.120', output.getvalue())
            self.assertIn('not live remaining capacity', output.getvalue())
            for retired in ['intrinsic value', 'Rank 3', 'burst through', 'Redirect saved quota']:
                self.assertNotIn(retired, output.getvalue())


if __name__ == '__main__':
    unittest.main()
