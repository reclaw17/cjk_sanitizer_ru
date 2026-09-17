"""Unit tests for sanitize.py and hook callbacks. No Hermes runtime."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / filename)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


sanitize = _load("sanitize", "sanitize.py")
plugin = _load("cjk_sanitizer_ru", "__init__.py")


class SanitizeTests(unittest.TestCase):
    def setUp(self):
        plugin.reset_skip_flags()

    def tearDown(self):
        plugin.reset_skip_flags()

    def test_russian_and_latin_unchanged(self):
        text = "Привет, Hermes. Check config.yaml and run pytest."
        self.assertIsNone(sanitize.sanitize(text))

    def test_empty_and_clean_text_are_noop(self):
        self.assertIsNone(sanitize.sanitize(""))
        self.assertIsNone(sanitize.sanitize("Чистый ответ без чужих письменностей."))

    def test_chinese_hangul_arabic_stripped(self):
        text = "Ответ: 你好 안녕하세요 مرحبا конец"
        cleaned = sanitize.sanitize(text)
        self.assertIsNotNone(cleaned)
        self.assertNotIn("你好", cleaned)
        self.assertNotIn("안녕", cleaned)
        self.assertNotIn("مرحبا", cleaned)
        self.assertIn("Ответ:", cleaned)
        self.assertIn("конец", cleaned)

    def test_cjk_punctuation_stripped(self):
        text = "Да。Нет、ок"
        cleaned = sanitize.sanitize(text)
        self.assertIsNotNone(cleaned)
        self.assertNotIn("。", cleaned)
        self.assertNotIn("、", cleaned)
        self.assertIn("Да", cleaned)
        self.assertIn("Нет", cleaned)

    def test_pi_and_emoji_kept(self):
        text = "Угол π ≈ 3.14 👍 и ℝ"
        self.assertIsNone(sanitize.sanitize(text))

    def test_fenced_code_with_cjk_kept(self):
        text = "Смотри:\n```python\nlabel = '你好'\n```\nготово"
        self.assertIsNone(sanitize.sanitize(text))

    def test_inline_code_with_cjk_kept(self):
        text = "Фикстура `你好` в тесте"
        self.assertIsNone(sanitize.sanitize(text))

    def test_prose_cjk_stripped_around_code(self):
        text = "Утечка 汉字 и код `keep 汉字` рядом"
        cleaned = sanitize.sanitize(text)
        self.assertIsNotNone(cleaned)
        self.assertEqual(cleaned.count("汉字"), 1)
        self.assertIn("`keep 汉字`", cleaned)
        self.assertIn("Утечка", cleaned)

    def test_fullwidth_ascii_unwrapped(self):
        text = "run ｐｙｔｅｓｔ"
        self.assertEqual(sanitize.sanitize(text), "run pytest")

    def test_prompt_with_cjk_skips_output(self):
        leaked = "Модель ответила 你好 и ещё текст"
        self.assertIsNotNone(sanitize.sanitize(leaked))

        result = plugin.on_pre_llm_call(
            user_message="Как сказать 你好 по-русски?",
            session_id="s1",
        )
        self.assertIsNone(result)
        self.assertIsNone(plugin.on_transform_llm_output(leaked, session_id="s1"))

    def test_pre_llm_call_always_returns_none(self):
        self.assertIsNone(
            plugin.on_pre_llm_call(user_message="только русский", session_id="s2")
        )
        self.assertIsNone(plugin.on_pre_llm_call(user_message="漢字", session_id="s3"))

    def test_clean_russian_prompt_still_strips_model_leak(self):
        plugin.on_pre_llm_call(user_message="Объясни pytest", session_id="s4")
        cleaned = plugin.on_transform_llm_output("Шаг 1 你好 готов", session_id="s4")
        self.assertIsNotNone(cleaned)
        self.assertNotIn("你好", cleaned)
        self.assertIn("Шаг 1", cleaned)
        self.assertIn("готов", cleaned)

    def test_register_wires_both_hooks(self):
        seen: list[tuple[str, object]] = []

        class Ctx:
            def register_hook(self, name, callback):
                seen.append((name, callback))

        plugin.register(Ctx())
        names = [name for name, _ in seen]
        self.assertEqual(names, ["pre_llm_call", "transform_llm_output"])
        self.assertIs(seen[0][1], plugin.on_pre_llm_call)
        self.assertIs(seen[1][1], plugin.on_transform_llm_output)


if __name__ == "__main__":
    unittest.main()
