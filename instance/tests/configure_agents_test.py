"""Exercise the agent step through its real helpers and an isolated JSON setter."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


REPO = Path(__file__).resolve().parents[2]
STUB = r'''
import json
import os
from pathlib import Path
import re
import sys

args = sys.argv[1:]
if len(args) not in (4, 5) or args[:2] != ["config", "set"]:
    raise SystemExit("only config set is permitted in this fixture")
log = Path(os.environ["CONFIG_TEST_LOG"])
calls = json.loads(log.read_text()) if log.exists() else []
calls.append(args)
log.write_text(json.dumps(calls))
if str(len(calls)) == os.environ.get("CONFIG_TEST_FAIL_AT"):
    raise SystemExit(23)
state = Path(os.environ["CONFIG_TEST_STATE"])
config = json.loads(state.read_text())
path = args[2]
segments = []
position = 0
for match in re.finditer(r'(?:^|\.)([\w-]+)|\["([^"\\]+)"\]', path):
    if match.start() != position:
        raise SystemExit("invalid fixture path")
    segments.append(match.group(1) or match.group(2))
    position = match.end()
if position != len(path) or not segments:
    raise SystemExit("invalid fixture path")
value = json.loads(args[3]) if args[4:] == ["--strict-json"] else args[3]
target = config
for segment in segments[:-1]:
    if not isinstance(target, dict):
        raise SystemExit("non-object fixture container")
    target = target.setdefault(segment, {})
if not isinstance(target, dict):
    raise SystemExit("non-object fixture container")
target[segments[-1]] = value
state.write_text(json.dumps(config, ensure_ascii=False))
'''


class ConfigureAgentsTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.state = self.root / "candidate.json"
        self.log = self.root / "calls.json"
        self.stub = self.root / "openclaw_stub.py"
        self.stub.write_text(STUB)
        (self.root / "bin").mkdir()
        (self.root / "home").mkdir()

    def configure(self, config, fail_at=None):
        if isinstance(config, str):
            self.state.write_text(config)
        else:
            self.state.write_text(json.dumps(config, ensure_ascii=False))
        self.state.chmod(0o600)
        self.log.unlink(missing_ok=True)
        env = {
            "PATH": str(self.root / "bin"),
            "HOME": str(self.root / "home"),
            "PYTHONUTF8": "1",
            "CONFIG_TEST_PYTHON": sys.executable,
            "CONFIG_TEST_STUB": str(self.stub),
            "CONFIG_TEST_STATE": str(self.state),
            "CONFIG_TEST_LOG": str(self.log),
        }
        if fail_at is not None:
            env["CONFIG_TEST_FAIL_AT"] = str(fail_at)
        return subprocess.run(
            ["/bin/sh", "-eu", "-c", '''
. "$1"
openclaw() { "$CONFIG_TEST_PYTHON" "$CONFIG_TEST_STUB" "$@"; }
. "$2"
''', "configure-agents-test", str(REPO / "core/configure/lib.sh"),
             str(REPO / "instance/configure.d/50-agents.sh")],
            env=env, text=True, capture_output=True, timeout=10,
        )

    def assert_owned_fields(self, config):
        main = config["agents"]["entries"]["main"]
        self.assertEqual(main["name"], "Team Claw")
        self.assertEqual(main["workspace"], "/home/node/.openclaw/workspaces/main")
        self.assertEqual(main["identity"]["name"], "Team Claw")
        self.assertEqual(main["identity"]["emoji"], "🦞")

    def test_fresh_configuration_and_repeat_are_equivalent(self):
        result = self.configure({})
        self.assertEqual(result.returncode, 0, result.stderr)
        first = json.loads(self.state.read_text())
        self.assert_owned_fields(first)
        self.assertIs(first["agents"]["defaults"]["skipBootstrap"], True)
        self.assertIs(first["skills"]["entries"]["github"]["enabled"], True)
        self.assertIs(first["skills"]["entries"]["gh-issues"]["enabled"], True)
        result = self.configure(first)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(self.state.read_text()), first)

    def test_preserves_models_and_unowned_agent_fields(self):
        for model in ("example/selected", {"primary": "example/selected",
                                         "fallbacks": ["example/backup"]}):
            with self.subTest(model=model):
                main = {
                    "name": "Earlier name", "workspace": "/old/workspace",
                    "model": model, "skills": ["custom-skill"],
                    "tools": {"exec": {"security": "allowlist"}},
                    "identity": {"name": "Earlier identity", "emoji": "X",
                                 "avatar": "avatars/custom.svg", "theme": "quiet"},
                }
                config = {
                    "agents": {"entries": {"other": {"model": "example/other"},
                                           "main": main},
                               "defaults": {"model": "example/default"}},
                    "skills": {"entries": {"custom": {"enabled": False}}},
                    "unrelated": {"preserve": [1, {"nested": "value"}]},
                }
                expected = copy.deepcopy(config)
                expected_main = expected["agents"]["entries"]["main"]
                expected_main.update(name="Team Claw", workspace="/home/node/.openclaw/workspaces/main")
                expected_main["identity"].update(name="Team Claw", emoji="🦞")
                expected["agents"]["defaults"]["skipBootstrap"] = True
                expected["skills"]["entries"].update(github={"enabled": True}, **{"gh-issues": {"enabled": True}})
                result = self.configure(config)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(json.loads(self.state.read_text()), expected)

    def test_invalid_configuration_is_not_replaced(self):
        for invalid in ('{"unfinished":', '["not an object"]', '{"agents": []}'):
            with self.subTest(invalid=invalid):
                result = self.configure(invalid)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(self.state.read_text(), invalid)
                self.assertEqual(len(json.loads(self.log.read_text())), 1)

    def test_failed_command_stops_step_without_dropping_user_settings(self):
        config = {"agents": {"entries": {"main": {"model": "example/selected"},
                                         "other": {"model": "example/other"}}}}
        result = self.configure(config, fail_at=2)
        self.assertEqual(result.returncode, 23, result.stderr)
        self.assertEqual(json.loads(self.state.read_text())["agents"]["entries"],
                         config["agents"]["entries"])
        self.assertEqual(len(json.loads(self.log.read_text())), 2)


if __name__ == "__main__":
    unittest.main()
