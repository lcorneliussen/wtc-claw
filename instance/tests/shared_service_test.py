"""Exercise the committed service command with a disposable Compose stub."""
import os
from pathlib import Path
import re
import signal
import subprocess
import tempfile
import textwrap
import time
import unittest


REPO = Path(__file__).resolve().parents[2]


class SharedServiceTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.log = self.root / "calls"
        self.running = self.root / "running"
        (self.root / "bin").mkdir()
        claw = self.root / "bin/claw"
        claw.write_text('''#!/bin/sh
printf '%s\\n' "$*" >> "$TASK_LOG"
case "$*" in
  deploy)
    test "$CLAW_BUILD" = auto || exit 99
    # A failed rollout can restart the rollback container detached.
    if test "$DEPLOY_EXIT" != 0; then touch "$TASK_RUNNING"; fi
    exit "$DEPLOY_EXIT" ;;
  'compose stop claw') rm -f "$TASK_RUNNING" ;;
  'compose up claw')
    touch "$TASK_RUNNING"
    if test "$UP_EXIT" != wait; then exit "$UP_EXIT"; fi
    while :; do sleep 0.05; done ;;
  *) exit 98 ;;
esac
''')
        claw.chmod(0o755)
        task = (REPO / ".harness/dekit.tasks.yaml").read_text()
        block = re.search(r"(?m)^      - \|\n((?:        [^\n]*\n|\n)+)", task)
        self.assertIsNotNone(block, "service command must be exercised by this test")
        self.script = textwrap.dedent(block.group(1))

    def start(self, deploy="0", up="0"):
        env = {**os.environ, "TASK_LOG": str(self.log),
               "TASK_RUNNING": str(self.running), "DEPLOY_EXIT": deploy, "UP_EXIT": up}
        proc = subprocess.Popen(["sh", "-c", self.script], cwd=self.root, env=env,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                start_new_session=True)
        def cleanup():
            if proc.poll() is None:
                os.killpg(proc.pid, signal.SIGKILL)
                proc.wait()
        self.addCleanup(cleanup)
        return proc

    def finish(self, proc, code):
        output, _ = proc.communicate(timeout=5)
        self.assertEqual(proc.returncode, code, output.decode())
        self.assertFalse(self.running.exists(), "detached gateway escaped supervision")
        return self.log.read_text().splitlines()

    def test_normal_exit_stops_gateway_in_order(self):
        self.assertEqual(self.finish(self.start(), 0),
                         ["compose stop claw", "deploy", "compose up claw", "compose stop claw"])

    def test_deploy_failure_stops_rollback_and_preserves_failure(self):
        self.assertEqual(self.finish(self.start(deploy="23"), 23),
                         ["compose stop claw", "deploy", "compose stop claw"])

    def test_compose_failure_stops_gateway_and_preserves_failure(self):
        self.assertEqual(self.finish(self.start(up="17"), 17),
                         ["compose stop claw", "deploy", "compose up claw", "compose stop claw"])

    def test_termination_stops_gateway(self):
        proc = self.start(up="wait")
        deadline = time.monotonic() + 5
        while not self.running.exists() and time.monotonic() < deadline:
            time.sleep(0.01)
        self.assertTrue(self.running.exists(), "foreground Compose did not start")
        os.killpg(proc.pid, signal.SIGTERM)
        self.assertEqual(self.finish(proc, 0)[-1], "compose stop claw")


if __name__ == "__main__":
    unittest.main()
