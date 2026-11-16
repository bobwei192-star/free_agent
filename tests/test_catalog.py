"""清单结构与平台解析的单元测试（不访问网络）。"""

from __future__ import annotations

import json
import unittest

from fa import catalog, installer
from fa.catalog import CatalogError, validate

PLATFORMS = ("linux", "wsl", "windows", "macos")


class CatalogTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = catalog.load()

    def test_schema(self):
        self.assertEqual(self.catalog.data["schema"], 1)
        self.assertTrue(self.catalog.updated)

    def test_ids_unique(self):
        ids = [tool.id for tool in self.catalog.tools]
        self.assertEqual(len(ids), len(set(ids)))

    def test_every_tool_has_method(self):
        for tool in self.catalog.tools:
            for plat in PLATFORMS:
                method = tool.method(plat)
                self.assertIn(method["type"], catalog.VALID_TYPES, f"{tool.id}/{plat}")
                if method["type"] != "manual":
                    self.assertIsNotNone(installer.command_for(tool, plat), f"{tool.id}/{plat}")

    def test_wsl_falls_back_to_linux(self):
        for tool in self.catalog.tools:
            if "linux" not in tool.install and "wsl" not in tool.install:
                continue
            self.assertEqual(tool.method("wsl"), tool.method("linux"), tool.id)

    def test_windows_never_falls_back_to_script(self):
        for tool in self.catalog.tools:
            method = tool.method("windows")
            if "windows" not in tool.install:
                continue
            self.assertNotEqual(method["type"], "script", tool.id)

    def test_groups_cover_all_kinds(self):
        for tool in self.catalog.tools:
            self.assertIn(tool.kind, self.catalog.groups, tool.id)

    def test_select(self):
        self.assertEqual(len(self.catalog.select(["cli"])), len(self.catalog.by_kind("cli")))
        self.assertEqual(len(self.catalog.select(["all"])), len(self.catalog.tools))
        self.assertEqual([tool.id for tool in self.catalog.select(["gemini"])], ["gemini"])
        with self.assertRaises(CatalogError):
            self.catalog.select(["nope"])

    def test_extension_ids(self):
        for tool in self.catalog.by_kind("ext"):
            method = tool.method("windows")
            self.assertEqual(method["type"], "vscode-ext")
            self.assertIn(".", method["id"])

    def test_validate_rejects_bad_type(self):
        data = json.loads(self.catalog.path.read_text(encoding="utf-8"))
        data["tools"][0]["install"] = {"default": {"type": "brew", "pkg": "x"}}
        with self.assertRaises(CatalogError):
            validate(data)

    def test_validate_rejects_duplicate_ids(self):
        data = json.loads(self.catalog.path.read_text(encoding="utf-8"))
        data["tools"].append(dict(data["tools"][0]))
        with self.assertRaises(CatalogError):
            validate(data)


if __name__ == "__main__":
    unittest.main()
