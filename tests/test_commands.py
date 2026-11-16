"""命令拼装与终端对齐的单元测试。"""

from __future__ import annotations

import unittest

from fa import catalog, installer, ui


class CommandTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = catalog.load()

    def test_npm_install_and_upgrade(self):
        tool = self.catalog.get("gemini")
        self.assertEqual(
            installer.command_for(tool, "linux"),
            ["npm", "install", "-g", "--no-audit", "--no-fund", "@google/gemini-cli"],
        )
        self.assertIn("@google/gemini-cli@latest", installer.command_for(tool, "windows", upgrade=True))

    def test_uv(self):
        tool = self.catalog.get("aider")
        self.assertEqual(installer.command_for(tool, "linux"), ["uv", "tool", "install", "aider-chat"])
        self.assertEqual(installer.command_for(tool, "linux", upgrade=True),
                         ["uv", "tool", "upgrade", "aider-chat"])

    def test_script(self):
        tool = self.catalog.get("opencode")
        self.assertEqual(installer.command_for(tool, "wsl"),
                         ["bash", "-lc", "curl -fsSL https://opencode.ai/install | bash"])

    def test_winget(self):
        tool = self.catalog.get("cursor")
        command = installer.command_for(tool, "windows")
        self.assertEqual(command[:5], ["winget", "install", "--id", "Anysphere.Cursor", "-e"])

    def test_manual(self):
        tool = self.catalog.get("doubao")
        self.assertIsNone(installer.command_for(tool, "linux"))

    def test_vscode_extension(self):
        tool = self.catalog.get("ext-cline")
        self.assertEqual(installer.command_for(tool, "linux"),
                         ["code", "--install-extension", "saoudrizwan.claude-dev", "--force"])

    def test_describe(self):
        tool = self.catalog.get("claude")
        self.assertIn("npm -g", installer.describe(tool.method("linux")))


class UiTest(unittest.TestCase):
    def test_wide_char_width(self):
        self.assertEqual(ui.visible_width("代理"), 4)
        self.assertEqual(ui.visible_width("abc"), 3)
        self.assertEqual(ui.visible_width(ui.green("代理")), 4)

    def test_truncate(self):
        self.assertLessEqual(ui.visible_width(ui.truncate("中文测试内容", 6)), 6)


if __name__ == "__main__":
    unittest.main()
