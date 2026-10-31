import unittest

from config.settings import env_bool, env_int


class TestConfigurationHelpers(unittest.TestCase):

    def test_boolean_true_values(self):
        for value in ("true", "TRUE", "yes", "1", "on"):
            with self.subTest(value=value):
                import os
                from unittest.mock import patch

                with patch.dict(os.environ, {"TEST_BOOL": value}):
                    self.assertTrue(
                        env_bool("TEST_BOOL", False)
                    )

    def test_boolean_false_values(self):
        for value in ("false", "FALSE", "no", "0", "off"):
            with self.subTest(value=value):
                import os
                from unittest.mock import patch

                with patch.dict(os.environ, {"TEST_BOOL": value}):
                    self.assertFalse(
                        env_bool("TEST_BOOL", True)
                    )

    def test_invalid_boolean_raises(self):
        import os
        from unittest.mock import patch

        with patch.dict(os.environ, {"TEST_BOOL": "maybe"}):
            with self.assertRaises(ValueError):
                env_bool("TEST_BOOL", True)

    def test_integer_within_range(self):
        import os
        from unittest.mock import patch

        with patch.dict(os.environ, {"TEST_INT": "10"}):
            self.assertEqual(
                env_int("TEST_INT", 5, 1, 20),
                10,
            )

    def test_integer_out_of_range_raises(self):
        import os
        from unittest.mock import patch

        with patch.dict(os.environ, {"TEST_INT": "50"}):
            with self.assertRaises(ValueError):
                env_int("TEST_INT", 5, 1, 20)


if __name__ == "__main__":
    unittest.main()