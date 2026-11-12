"""Rebuild and verify all Module 6a experiments; capture authentic local results.

From repository root:
    uv run --with duckdb python Module06a/run_all.py
"""
from pathlib import Path
import importlib.util
import subprocess
import sys

HERE = Path(__file__).resolve().parent
if not importlib.util.find_spec("duckdb"):
    raise SystemExit("DuckDB not installed in this Python. Run: "
                     "uv run --with duckdb python Module06a/run_all.py")


def run(script, output, *args):
    cmd = [sys.executable, str(HERE / script), *args]
    print(f"Running: {script} {' '.join(args)}", flush=True)
    proc = subprocess.run(cmd, capture_output=True, text=True)
    captured = (proc.stdout or "") + (proc.stderr or "")
    (HERE / output).write_text(captured, encoding="utf-8")
    print(captured[-1600:], end="" if captured.endswith("\n") else "\n", flush=True)
    if proc.returncode:
        raise SystemExit(f"{script} failed (exit {proc.returncode}); see Module06a/{output}")


def main():
    run("prepare.py", "prepare_results.txt")
    run("to_parquet.py", "conversion_results.txt")
    run("race.py", "race_results.txt")
    run("plan.py", "plan_results.txt")
    run("boundary.py", "boundary_results.txt")
    run("optional.py", "optional_results.txt")
    run("refresh.py", "refresh_results.txt")
    run("refresh.py", "refresh_check_results.txt", "--check")
    # Rebuild again to test idempotency; check the second copy too.
    run("refresh.py", "refresh_repeat_results.txt")
    run("refresh.py", "refresh_second_check_results.txt", "--check")
    run("generate_memo.py", "memo_results.txt")
    must_have = ["prepare_results.txt", "conversion_results.txt", "race_results.txt",
                 "plan_results.txt", "boundary_results.txt", "refresh_results.txt",
                 "refresh_check_results.txt", "refresh_repeat_results.txt",
                 "refresh_second_check_results.txt", "decision-memo.md"]
    assert all((HERE / f).stat().st_size > 0 for f in must_have)
    print("\nMODULE 6A COMPLETE: all scripts passed; results recorded in Module06a/.")
    print("Generated .db, .csv, .parquet and .json files are ignored by Git.")


if __name__ == "__main__":
    main()
