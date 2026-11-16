"""开机自启动（systemd --user）与 run_args 的单元测试（不联网、不写系统目录）。"""

from __future__ import annotations

import unittest

from fa import autostart, catalog


class AutostartTest(unittest.TestCase):
    def test_resolve_aliases(self):
        self.assertEqual(autostart.resolve("dsh"), "dsh")
        self.assertEqual(autostart.resolve("dsh-web"), "dsh")
        self.assertEqual(autostart.resolve("harness"), "dsh")
        self.assertIsNone(autostart.resolve("nope"))

    def test_unit_file_path(self):
        path = autostart.unit_file("dsh")
        self.assertTrue(path.name.endswith(".service"))
        self.assertIn("systemd", str(path))

    def test_render_unit_contains_expected_parts(self):
        text = autostart.render_unit("dsh", port=3080, proxy_port=7897)
        self.assertIn("[Unit]", text)
        self.assertIn("[Service]", text)
        self.assertIn("[Install]", text)
        self.assertIn("WantedBy=default.target", text)
        self.assertIn("--port 3080", text)
        self.assertIn("--no-open", text)
        self.assertIn("Restart=always", text)
        self.assertIn("Environment=HTTPS_PROXY=http://127.0.0.1:7897", text)
        self.assertIn("Environment=NO_PROXY=", text)
        self.assertNotIn("ALL_PROXY=http", text)

    def test_render_unit_without_proxy(self):
        text = autostart.render_unit("dsh", port=3080, proxy_port=None)
        self.assertNotIn("HTTPS_PROXY", text)
        self.assertIn("--port 3080", text)

    def test_detect_proxy_port_from_env(self):
        import os

        old = os.environ.get("HTTPS_PROXY")
        os.environ["HTTPS_PROXY"] = "http://127.0.0.1:10809"
        try:
            self.assertEqual(autostart.detect_proxy_port(), 10809)
        finally:
            if old is None:
                os.environ.pop("HTTPS_PROXY", None)
            else:
                os.environ["HTTPS_PROXY"] = old


class RunArgsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = catalog.load()

    def test_dsh_runs_web_profile(self):
        tool = self.catalog.get("dsh-free-model")
        self.assertEqual(tool.run_args("linux"), ["web"])

    def test_other_tools_have_no_run_args(self):
        for tool in self.catalog.tools:
            if tool.id == "dsh-free-model":
                continue
            self.assertEqual(tool.run_args("linux"), [], tool.id)


if __name__ == "__main__":
    unittest.main()
