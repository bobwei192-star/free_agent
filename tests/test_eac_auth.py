"""EAC 授权模块的离线单元测试（不联网、不写系统目录）。"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from fa import cli, eac_auth


class TokenDiscoveryTest(unittest.TestCase):
    def test_token_re_extracts_launch_token(self):
        line = "dsh web: http://127.0.0.1:3080/?token=EXAMPLEtkn_000000000000000000000000000000000000"
        self.assertEqual(eac_auth.TOKEN_RE.findall(line),
                         ["EXAMPLEtkn_000000000000000000000000000000000000"])

    def test_token_re_ignores_short_values(self):
        self.assertEqual(eac_auth.TOKEN_RE.findall("http://127.0.0.1:3080/?token=abc"), [])

    def test_read_recent_logs_falls_back_to_dsh_home(self):
        token = "AbCdEfGhIjKlMnOpQrStUvWxYz0123456789abcd"
        import os
        import tempfile

        with tempfile.TemporaryDirectory() as home:
            root = Path(home)
            (root / "logs").mkdir()
            (root / "logs" / "startup-2026-11-16T08-00-03.071Z-ca512db3.log").write_text(
                f"dsh web: http://127.0.0.1:3080/?token={token}\n", encoding="utf-8"
            )
            previous = os.environ.get("DSH_HOME")
            os.environ["DSH_HOME"] = root.as_posix()
            try:
                self.assertIn(token, eac_auth.read_recent_logs(3080))
            finally:
                if previous is None:
                    os.environ.pop("DSH_HOME", None)
                else:
                    os.environ["DSH_HOME"] = previous


class StatusRenderingTest(unittest.TestCase):
    def test_describe_maps_the_status_document(self):
        rows = dict(eac_auth.describe({
            "available": True, "required": True, "authorized": False, "starred": False,
            "login": "", "local": False, "repo": "Ebony-Vinyl/dsh-our-free-model",
        }))
        self.assertEqual(rows["车道可用"], "是")
        self.assertEqual(rows["已授权"], "否")
        self.assertEqual(rows["GitHub 账号"], "—")
        self.assertEqual(rows["目标仓库"], "Ebony-Vinyl/dsh-our-free-model")

    def test_describe_keeps_unknown_verdicts_explicit(self):
        rows = dict(eac_auth.describe({"available": True}))
        self.assertEqual(rows["需要授权"], "未知")
        self.assertEqual(rows["策略确认"], "已确认")

    def test_describe_reports_an_unverified_gateway(self):
        rows = dict(eac_auth.describe({"authorized": True, "unverified": True}))
        self.assertEqual(rows["策略确认"], "网关未确认")


class RequestShapeTest(unittest.TestCase):
    """只验证请求路径与参数，不发出任何网络请求。"""

    def setUp(self):
        self.calls = []
        self.client = eac_auth.Session(3080)
        self.client._send = lambda method, path, body=None: self.calls.append((method, path, body)) or (200, {})

    def test_login_start_posts_an_empty_json_body(self):
        eac_auth.start_login(self.client)
        self.assertEqual(self.calls[-1][:2], ("POST", "/api/our-free-model/eac/login/start"))
        self.assertEqual(json.loads(self.calls[-1][2]), {})

    def test_poll_url_encodes_the_link(self):
        eac_auth.poll(self.client, "abc-_def")
        self.assertEqual(self.calls[-1][1], "/api/our-free-model/eac/login/poll?link=abc-_def")
        eac_auth.poll(self.client, "a+b/c")
        self.assertEqual(self.calls[-1][1], "/api/our-free-model/eac/login/poll?link=a%2Bb%2Fc")

    def test_api_raises_a_readable_error(self):
        self.client._send = lambda *_, **__: (404, {"error": "no-lane"})
        with self.assertRaises(eac_auth.EacError):
            eac_auth.status(self.client)


class CliWiringTest(unittest.TestCase):
    def test_eac_subcommand_parses(self):
        args = cli.build_parser().parse_args(["eac", "--login", "--timeout", "30", "--no-open"])
        self.assertEqual(args.command, "eac")
        self.assertTrue(args.login)
        self.assertEqual(args.timeout, 30)
        self.assertTrue(args.no_open)

    def test_wait_stops_on_the_first_terminal_verdict(self):
        client = eac_auth.Session(3080)
        seen = []

        def fake_send(method, path, body=None):
            seen.append(path)
            return 200, {"status": "ok", "login": "octocat"}

        client._send = fake_send
        self.assertEqual(eac_auth.wait(client, "link", timeout=1), {"status": "ok", "login": "octocat"})
        self.assertEqual(len(seen), 1)


if __name__ == "__main__":
    unittest.main()
