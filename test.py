import unittest, os, json
from unittest.mock import patch
from main import *

# unit testing derived from https://www.geeksforgeeks.org/python/unit-testing-python-unittest/

class TestConfigClass(unittest.TestCase):

    def setUp(self):
        if os.path.exists("test_config.json"):
            os.remove("test_config.json")
        if os.path.exists("test_config2.json"):
            os.remove("test_config2.json")

    def tearDown(self):
        if os.path.exists("test_config.json"):
            os.remove("test_config.json")
        if os.path.exists("test_config2.json"):
            os.remove("test_config2.json")



    # sample rate

    def test_valid_sr(self):
        c = Config(path="test_config.json")
        c.set_sr(44100)
        self.assertEqual(c.sr, 44100)

    def test_valid_sr_lower_bound(self):
        c = Config(path="test_config.json")
        c.set_sr(8000)
        self.assertEqual(c.sr, 8000)

    def test_valid_sr_upper_bound(self):
        c = Config(path="test_config.json")
        c.set_sr(192000)
        self.assertEqual(c.sr, 192000)

    def test_invalid_sr(self):
        c = Config(path="test_config.json")
        with self.assertRaises(ValueError):
            c.set_sr(12345)

    def test_invalid_sr_format(self):
        c = Config(path="test_config.json")
        with self.assertRaises((TypeError, ValueError)):
            c.set_sr("according to all known laws of aviation, there is no way that the bee should be able to fly.")



    # buffer

    def test_valid_buf(self):
        c = Config(path="test_config.json")
        c.set_buf(500)
        self.assertEqual(c.buf, 500)

    def test_valid_buf_lower_bound(self):
        c = Config(path="test_config.json")
        c.set_buf(0)
        self.assertEqual(c.buf, 0)

    def test_invalid_buf_lower_bound(self):
        c = Config(path="test_config.json")
        with self.assertRaises(ValueError):
            c.set_buf(-100)

    def test_invalid_buf_format(self):
        c = Config(path="test_config.json")
        with self.assertRaises((TypeError, ValueError)):
            c.set_buf("according to all known laws of aviation, there is no way that the bee should be able to fly.")



    # gain

    def test_valid_gain(self):
        c = Config(path="test_config.json")
        c.set_gain(1.5)
        self.assertEqual(c.gain, 1.5)

    def test_valid_gain_upper_bound(self):
        c = Config(path="test_config.json")
        c.set_gain(8.0)
        self.assertEqual(c.gain, 8.0)

    def test_invalid_gain_lower_bound(self):
        c = Config(path="test_config.json")
        with self.assertRaises(ValueError):
            c.set_gain(0.0)

    def test_invalid_gain_upper_bound(self):
        c = Config(path="test_config.json")
        with self.assertRaises(ValueError):
            c.set_gain(9.0)

    def test_invalid_gain_format(self):
        c = Config(path="test_config.json")
        with self.assertRaises((TypeError, ValueError)):
            c.set_gain("according to all known laws of aviation, there is no way that the bee should be able to fly.")



    # port

    def test_valid_port(self):
        c = Config(path="test_config.json")
        c.set_port(5006)
        self.assertEqual(c.port, 5006)

    def test_valid_port_lower_bound(self):
        c = Config(path="test_config.json")
        c.set_port(1024)
        self.assertEqual(c.port, 1024)

    def test_valid_port_upper_bound(self):
        c = Config(path="test_config.json")
        c.set_port(65535)
        self.assertEqual(c.port, 65535)

    def test_invalid_port_lower_bound(self):
        c = Config(path="test_config.json")
        with self.assertRaises(ValueError):
            c.set_port(80)

    def test_invalid_port_upper_bound(self):
        c = Config(path="test_config.json")
        with self.assertRaises(ValueError):
            c.set_port(1189998819991197253)

    def test_invalid_port_format(self):
        c = Config(path="test_config.json")
        with self.assertRaises((TypeError, ValueError)):
            c.set_port("according to all known laws of aviation, there is no way that the bee should be able to fly.")



    # save/load

    def test_save_and_load(self):

        # TODO put in in/out dev tests once implemented in script

        c = Config(path="test_config.json")
        c.set_sr(44100)
        c.set_buf(300)
        c.set_gain(2.0)
        c.set_port(5006)
        # c.set_in_dev(some_value)
        # c.set_out_dev(some_value)
        c.save()

        c2 = Config(path="test_config.json")
        self.assertEqual(c2.sr, 44100)
        self.assertEqual(c2.buf, 300)
        self.assertEqual(c2.gain, 2.0)
        self.assertEqual(c2.port, 5006)
        # self.assertEqual(c2.in_dev, some_value)
        # self.assertEqual(c2.out_dev, some_value)

    def test_no_file_creates_one(self):
        self.assertFalse(os.path.exists("test_config.json"))
        c = Config(path="test_config.json")
        self.assertTrue(os.path.exists("test_config.json"))

    def test_save_contains_correct_keys(self):
        c = Config(path="test_config.json")
        c.save()
        with open("test_config.json", "r") as f:
            data = json.load(f)
        for key in ["sr", "buf", "gain", "port", "in_dev", "out_dev"]:
            self.assertIn(key, data)

    def test_load_bad_json(self):
        with open("test_config.json", "w") as f:
            f.write("according to all known laws of aviation {{{ there is no way that the bee should be able to fly")
        with patch("builtins.input", side_effect=EOFError):
            with self.assertRaises((Exception, RuntimeError)):
                c = Config(path="test_config.json")

    def test_load_partial_file_uses_defaults(self):
        with open("test_config.json", "w") as f:
            json.dump({"sr": 44100}, f)
        c = Config(path="test_config.json")
        self.assertEqual(c.sr, 44100)
        self.assertEqual(c.buf, 500)
        self.assertEqual(c.gain, 1.0)
        self.assertEqual(c.port, 5005)

    def test_file_overrides_default(self):
        c = Config(path="test_config.json", sr=44100)
        c.save()
        c2 = Config(path="test_config.json")
        self.assertEqual(c2.sr, 44100)

    def test_valid_path_wrong_keys(self):
        with open("test_config.json", "w") as f:
            json.dump({"according": 1, "to": 2}, f)
        with patch("builtins.input", side_effect=EOFError):
            with self.assertRaises((Exception, RuntimeError)):
                c = Config(path="test_config.json")

    def test_load_file_with_extra_keys(self):
        with open("test_config.json", "w") as f:
            json.dump({"sr": 44100, "buf": 300, "foo": "bar"}, f)
        with patch("builtins.input", side_effect=EOFError):
            with self.assertRaises((Exception, RuntimeError)):
                c = Config(path="test_config.json")

    def test_path_set_correctly(self):
        c = Config(path="test_config.json")
        self.assertEqual(c.path, "test_config.json")



    # path input prompt — corrected by user

    def test_invalid_path_corrected_by_user(self):
        with patch("builtins.input", return_value="test_config.json"):
            c = Config(path="test_config.txt")
            self.assertEqual(c.path, "test_config.json")

    def test_invalid_path_rejected_then_corrected(self):
        with patch("builtins.input", side_effect=["according.txt", "test_config.json"]):
            c = Config(path="test_config.txt")
            self.assertEqual(c.path, "test_config.json")

    def test_invalid_path_many_bad_then_corrected(self):
        with patch("builtins.input", side_effect=["according.txt", "to.csv", "all.dmg", "known.docz", "laws.pptx", "test_config.json"]):
            c = Config(path="test_config.txt")
            self.assertEqual(c.path, "test_config.json")

    def test_invalid_path_no_input_available(self):
        with patch("builtins.input", side_effect=EOFError):
            with self.assertRaises((EOFError, RuntimeError)):
                c = Config(path="test_config.txt")



    # defaults

    def test_default_sr(self):
        c = Config(path="test_config.json")
        self.assertEqual(c.sr, 48000)

    def test_default_buf(self):
        c = Config(path="test_config.json")
        self.assertEqual(c.buf, 500)

    def test_default_gain(self):
        c = Config(path="test_config.json")
        self.assertEqual(c.gain, 1.0)

    def test_default_port(self):
        c = Config(path="test_config.json")
        self.assertEqual(c.port, 5005)

    def test_default_in_dev(self):
        c = Config(path="test_config.json")
        self.assertIsNone(c.in_dev)

    def test_default_out_dev(self):
        c = Config(path="test_config.json")
        self.assertIsNone(c.out_dev)



    # manually specified arguments override defaults

    def test_init_sr_override(self):
        c = Config(path="test_config.json", sr=44100)
        self.assertEqual(c.sr, 44100)

    def test_init_buf_override(self):
        c = Config(path="test_config.json", buf=300)
        self.assertEqual(c.buf, 300)

    def test_init_gain_override(self):
        c = Config(path="test_config.json", gain=2.0)
        self.assertEqual(c.gain, 2.0)

    def test_init_port_override(self):
        c = Config(path="test_config.json", port=5006)
        self.assertEqual(c.port, 5006)



    # fallback to defaults when invalid override specified

    def test_init_invalid_sr_falls_back_to_default(self):
        c = Config(path="test_config.json", sr=12345)
        self.assertEqual(c.sr, 48000)

    def test_init_invalid_buf_falls_back_to_default(self):
        c = Config(path="test_config.json", buf=-1)
        self.assertEqual(c.buf, 500)

    def test_init_invalid_gain_falls_back_to_default(self):
        c = Config(path="test_config.json", gain=0.0)
        self.assertEqual(c.gain, 1.0)

    def test_init_invalid_port_falls_back_to_default(self):
        c = Config(path="test_config.json", port=80)
        self.assertEqual(c.port, 5005)
    


    # fallback to current when invalid value found in file

    def test_load_invalid_sr_in_file_uses_default(self):
        with open("test_config.json", "w") as f:
            json.dump({"sr": 99999, "buf": 300, "gain": 1.0, "port": 5006}, f)
        c = Config(path="test_config.json")
        self.assertEqual(c.sr, 48000)
        self.assertEqual(c.buf, 300)

    def test_load_invalid_gain_in_file_uses_default(self):
        with open("test_config.json", "w") as f:
            json.dump({"sr": 44100, "buf": 300, "gain": 99.0, "port": 5006}, f)
        c = Config(path="test_config.json")
        self.assertEqual(c.gain, 1.0)
        self.assertEqual(c.sr, 44100)



    # manual arguments override values loaded from file

    def test_init_arg_overrides_file(self):
        c = Config(path="test_config.json", sr=44100)
        c.save()
        c2 = Config(path="test_config.json", sr=96000)
        self.assertEqual(c2.sr, 96000)



if __name__ == "__main__":
    unittest.main()