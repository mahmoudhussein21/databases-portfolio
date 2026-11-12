"""Recreate all local Module 5 evidence and run independent checks."""
from pathlib import Path
import subprocess
import sys

BASE = Path(__file__).resolve().parent
for filename in ('anomalies.py', 'benchmark.py'):
    subprocess.run([sys.executable, str(BASE / filename)], check=True)
required = (
    'README.md', 'normalization-notes.md', 'er-sketches.md',
    'flat_model.png', 'normalized_model.png', 'anomalies.sql',
    'anomaly_results.txt', 'setup.sql', 'report_queries.sql',
    'benchmark_results.txt', 'query_plans.txt', 'benchmark.md',
    'round5-storage.md', 'recommendation-memo.md', 'harvest.md',
)
for name in required:
    assert (BASE / name).exists(), f'Missing file: {name}'
print('All Module 5 checks passed; normalize.db is local and ignored by Git.')
