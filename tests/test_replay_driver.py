import os
from pathlib import Path
import subprocess
import tempfile
import unittest
import shutil

SCRIPT = Path(__file__).resolve().parent.parent / "scripts/lean/replay_verify.sh"


class ReplayDriverTests(unittest.TestCase):
    def run_case(self, *, driver, build_library, replay_exit=0):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            scripts = root / "scripts"
            scripts.mkdir()
            shutil.copy2(SCRIPT, scripts / "replay_verify.sh")
            if driver:
                (scripts / "cold_kernel_replay.lean").write_text("-- orchestration fixture\n")
            binary = root / "bin"
            binary.mkdir()
            (binary / "lake").write_text(
                '#!/bin/sh\necho "$*" >> calls.txt\n'
                + ('if [ "$1" = build ]; then mkdir -p .lake/build/lib/lean; fi\n' if build_library else '')
                + f'if [ "$1" = env ]; then exit {replay_exit}; fi\nexit 0\n')
            (binary / "python3").write_text("#!/bin/sh\nexit 0\n")
            for file in binary.iterdir():
                file.chmod(0o755)
            env = dict(os.environ, PATH=str(binary) + os.pathsep + os.environ["PATH"])
            result = subprocess.run(["bash", str(scripts / "replay_verify.sh")], cwd=root,
                                    env=env, capture_output=True, text=True)
            calls = (root / "calls.txt").read_text() if (root / "calls.txt").exists() else ""
            return result, calls

    def test_missing_required_driver_fails_before_clean(self):
        result, calls = self.run_case(driver=False, build_library=True)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertEqual(calls, "")

    def test_missing_compiled_library_fails(self):
        result, _ = self.run_case(driver=True, build_library=False)
        self.assertNotEqual(result.returncode, 0, result.stdout)

    def test_failed_kernel_replay_propagates(self):
        result, calls = self.run_case(driver=True, build_library=True, replay_exit=7)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("env lean", calls)

    def test_every_required_stage_runs_on_success(self):
        result, calls = self.run_case(driver=True, build_library=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("build", calls)
        self.assertIn("env lean", calls)


if __name__ == "__main__":
    unittest.main()
