import unittest, os, json
from unittest.mock import patch, MagicMock
import numpy as np
from main import *
import time

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

    def test_default_sr(self):
        c = Config(path="test_config.json")
        self.assertEqual(c.sr, 48000)



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

    def test_default_buf(self):
        c = Config(path="test_config.json")
        self.assertEqual(c.buf, 500)



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

    def test_default_gain(self):
        c = Config(path="test_config.json")
        self.assertEqual(c.gain, 1.0)



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

    def test_default_port(self):
        c = Config(path="test_config.json")
        self.assertEqual(c.port, 5005)
    
    
    
    # mode

    def test_valid_mode_transmitter(self):
        c = Config(path="test_config.json")
        c.set_mode("transmitter")
        self.assertEqual(c.mode, "transmitter")

    def test_valid_mode_receiver(self):
        c = Config(path="test_config.json")
        c.set_mode("receiver")
        self.assertEqual(c.mode, "receiver")

    def test_invalid_mode(self):
        c = Config(path="test_config.json")
        with self.assertRaises(ValueError):
            c.set_mode("according to all known laws of aviation, there is no way that the bee should be able to fly.")

    def test_invalid_mode_format(self):
        c = Config(path="test_config.json")
        with self.assertRaises((TypeError, ValueError)):
            c.set_mode(1853)

    def test_default_mode(self):
        c = Config(path="test_config.json")
        self.assertEqual(c.mode, "transmitter")

    def test_init_mode_override(self):
        c = Config(path="test_config.json", mode="receiver")
        self.assertEqual(c.mode, "receiver")

    def test_init_invalid_mode_falls_back_to_default(self):
        c = Config(path="test_config.json", mode="banana")
        self.assertEqual(c.mode, "transmitter")



    # channels

    def test_valid_ch(self):
        c = Config(path="test_config.json")
        c.set_ch(2)
        self.assertEqual(c.ch, 2)

    def test_valid_ch_lower_bound(self):
        c = Config(path="test_config.json")
        c.set_ch(1)
        self.assertEqual(c.ch, 1)

    def test_invalid_ch_lower_bound(self):
        c = Config(path="test_config.json")
        with self.assertRaises(ValueError):
            c.set_ch(0)

    def test_invalid_ch_negative(self):
        c = Config(path="test_config.json")
        with self.assertRaises(ValueError):
            c.set_ch(-1)

    def test_invalid_ch_format(self):
        c = Config(path="test_config.json")
        with self.assertRaises((TypeError, ValueError)):
            c.set_ch("according to all known laws of aviation, there is no way that the bee should be able to fly.")

    def test_default_ch(self):
        c = Config(path="test_config.json")
        self.assertEqual(c.ch, 2)

    def test_init_ch_override(self):
        c = Config(path="test_config.json", ch=1)
        self.assertEqual(c.ch, 1)

    def test_init_invalid_ch_falls_back_to_default(self):
        c = Config(path="test_config.json", ch=0)
        self.assertEqual(c.ch, 2)



    # input device

    def test_valid_in_dev_string(self):
        c = Config(path="test_config.json")
        c.set_in_dev("MacBook Pro Microphone")
        self.assertEqual(c.in_dev, "MacBook Pro Microphone")

    def test_valid_in_dev_none(self):
        c = Config(path="test_config.json")
        c.set_in_dev(None)
        self.assertIsNone(c.in_dev)

    def test_invalid_in_dev_int(self):
        c = Config(path="test_config.json")
        with self.assertRaises(ValueError):
            c.set_in_dev(2)

    def test_invalid_in_dev_bool(self):
        c = Config(path="test_config.json")
        with self.assertRaises(ValueError):
            c.set_in_dev(True)

    def test_default_in_dev(self):
        c = Config(path="test_config.json")
        self.assertIsNone(c.in_dev)

    def test_in_dev_saves_and_loads(self):
        c = Config(path="test_config.json")
        c.set_in_dev("MacBook Pro Microphone")
        c.save()
        c2 = Config(path="test_config.json")
        self.assertEqual(c2.in_dev, "MacBook Pro Microphone")

    def test_in_dev_none_saves_and_loads(self):
        c = Config(path="test_config.json")
        c.set_in_dev(None)
        c.save()
        c2 = Config(path="test_config.json")
        self.assertIsNone(c2.in_dev)



    # output device

    def test_valid_out_dev_string(self):
        c = Config(path="test_config.json")
        c.set_out_dev("MacBook Pro Speakers")
        self.assertEqual(c.out_dev, "MacBook Pro Speakers")

    def test_valid_out_dev_none(self):
        c = Config(path="test_config.json")
        c.set_out_dev(None)
        self.assertIsNone(c.out_dev)

    def test_invalid_out_dev_int(self):
        c = Config(path="test_config.json")
        with self.assertRaises(ValueError):
            c.set_out_dev(2)

    def test_invalid_out_dev_bool(self):
        c = Config(path="test_config.json")
        with self.assertRaises(ValueError):
            c.set_out_dev(True)

    def test_default_out_dev(self):
        c = Config(path="test_config.json")
        self.assertIsNone(c.out_dev)

    def test_out_dev_saves_and_loads(self):
        c = Config(path="test_config.json")
        c.set_out_dev("MacBook Pro Speakers")
        c.save()
        c2 = Config(path="test_config.json")
        self.assertEqual(c2.out_dev, "MacBook Pro Speakers")

    def test_out_dev_none_saves_and_loads(self):
        c = Config(path="test_config.json")
        c.set_out_dev(None)
        c.save()
        c2 = Config(path="test_config.json")
        self.assertIsNone(c2.out_dev)



    # save/load

    # def test_save_and_load(self):

    #     c = Config(path="test_config.json")
    #     c.set_mode("receiver")
    #     c.set_ch(2)
    #     c.set_sr(44100)
    #     c.set_buf(300)
    #     c.set_gain(2.0)
    #     c.set_port(5006)
    #     c.set_in_dev("some_value1")
    #     c.set_out_dev("some_value2")
    #     c.save()

    #     c2 = Config(path="test_config.json")
    #     self.assertEqual(c2.mode, "receiver")
    #     self.assertEqual(c2.ch, 2)
    #     self.assertEqual(c2.sr, 44100)
    #     self.assertEqual(c2.buf, 300)
    #     self.assertEqual(c2.gain, 2.0)
    #     self.assertEqual(c2.port, 5006)
    #     self.assertEqual(c2.in_dev, "some_value1")
    #     self.assertEqual(c2.out_dev, "some_value2")

    def test_no_file_creates_one(self):
        self.assertFalse(os.path.exists("test_config.json"))
        c = Config(path="test_config.json")
        self.assertTrue(os.path.exists("test_config.json"))

    def test_save_contains_correct_keys(self):
        c = Config(path="test_config.json")
        c.save()
        with open("test_config.json", "r") as f:
            data = json.load(f)
        self.assertIn("mode", data)
        self.assertIn("transmitter-config", data)
        self.assertIn("receiver-config", data)
        for key in ["nic_ip", "target_ip", "target_port", "in_dev"]:
            self.assertIn(key, data["transmitter-config"])
        for key in ["nic_ip", "port", "ch", "sr", "buf", "tolerance", "gain", "out_dev"]:
            self.assertIn(key, data["receiver-config"])

    def test_load_bad_json(self):
        with open("test_config.json", "w") as f:
            f.write("according to all known laws of aviation {{{ there is no way that the bee should be able to fly")
        with patch("builtins.input", side_effect=EOFError):
            with self.assertRaises((Exception, RuntimeError)):
                c = Config(path="test_config.json")

    def test_load_partial_file_uses_defaults(self):
        with open("test_config.json", "w") as f:
            json.dump({"receiver-config": {"sr": 44100}}, f)
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
            json.dump({"receiver-config": {"sr": 99999, "buf": 300, "gain": 1.0, "port": 5006}}, f)
        c = Config(path="test_config.json")
        self.assertEqual(c.sr, 48000)
        self.assertEqual(c.buf, 300)

    def test_load_invalid_gain_in_file_uses_default(self):
        with open("test_config.json", "w") as f:
            json.dump({"receiver-config": {"sr": 44100, "buf": 300, "gain": 99.0, "port": 5006}}, f)
        c = Config(path="test_config.json")
        self.assertEqual(c.gain, 1.0)
        self.assertEqual(c.sr, 44100)



    # manual arguments override values loaded from file

    def test_init_arg_overrides_file(self):
        c = Config(path="test_config.json", sr=44100)
        c.save()
        c2 = Config(path="test_config.json", sr=96000)
        self.assertEqual(c2.sr, 96000)



    # target_port

    def test_valid_target_port(self):
        c = Config(path="test_config.json")
        c.set_target_port(5006)
        self.assertEqual(c.target_port, 5006)

    def test_valid_target_port_lower_bound(self):
        c = Config(path="test_config.json")
        c.set_target_port(1024)
        self.assertEqual(c.target_port, 1024)

    def test_valid_target_port_upper_bound(self):
        c = Config(path="test_config.json")
        c.set_target_port(65535)
        self.assertEqual(c.target_port, 65535)

    def test_invalid_target_port_lower_bound(self):
        c = Config(path="test_config.json")
        with self.assertRaises(ValueError):
            c.set_target_port(80)

    def test_invalid_target_port_upper_bound(self):
        c = Config(path="test_config.json")
        with self.assertRaises(ValueError):
            c.set_target_port(1189998819991197253)

    def test_default_target_port(self):
        c = Config(path="test_config.json")
        self.assertEqual(c.target_port, 5005)

    def test_init_target_port_override(self):
        c = Config(path="test_config.json", target_port=6000)
        self.assertEqual(c.target_port, 6000)

    def test_init_invalid_target_port_falls_back_to_default(self):
        c = Config(path="test_config.json", target_port=80)
        self.assertEqual(c.target_port, 5005)

    def test_target_port_saves_and_loads(self):
        c = Config(path="test_config.json")
        c.set_target_port(6000)
        c.save()
        c2 = Config(path="test_config.json")
        self.assertEqual(c2.target_port, 6000)

    def test_target_port_independent_of_receiver_port(self):
        c = Config(path="test_config.json")
        c.set_target_port(6000)
        self.assertEqual(c.port, 5005)   # receiver port unchanged



    # t_nic_ip (transmitter NIC)

    def test_valid_t_nic_ip(self):
        c = Config(path="test_config.json")
        c.set_t_nic_ip("192.168.1.10")
        self.assertEqual(c.t_nic_ip, "192.168.1.10")

    def test_valid_t_nic_ip_wildcard(self):
        c = Config(path="test_config.json")
        c.set_t_nic_ip("0.0.0.0")
        self.assertEqual(c.t_nic_ip, "0.0.0.0")

    def test_invalid_t_nic_ip(self):
        c = Config(path="test_config.json")
        with self.assertRaises(ValueError):
            c.set_t_nic_ip("not.an.ip")

    def test_invalid_t_nic_ip_format(self):
        c = Config(path="test_config.json")
        with self.assertRaises(ValueError):
            c.set_t_nic_ip(12345)

    def test_default_t_nic_ip(self):
        c = Config(path="test_config.json")
        self.assertEqual(c.t_nic_ip, "0.0.0.0")

    def test_t_nic_ip_saves_and_loads(self):
        c = Config(path="test_config.json")
        c.set_t_nic_ip("10.0.0.1")
        c.save()
        c2 = Config(path="test_config.json")
        self.assertEqual(c2.t_nic_ip, "10.0.0.1")

    def test_init_t_nic_ip_override(self):
        c = Config(path="test_config.json", t_nic_ip="10.0.0.1")
        self.assertEqual(c.t_nic_ip, "10.0.0.1")



    # r_nic_ip (receiver NIC)

    def test_valid_r_nic_ip(self):
        c = Config(path="test_config.json")
        c.set_r_nic_ip("192.168.1.20")
        self.assertEqual(c.r_nic_ip, "192.168.1.20")

    def test_valid_r_nic_ip_wildcard(self):
        c = Config(path="test_config.json")
        c.set_r_nic_ip("0.0.0.0")
        self.assertEqual(c.r_nic_ip, "0.0.0.0")

    def test_invalid_r_nic_ip(self):
        c = Config(path="test_config.json")
        with self.assertRaises(ValueError):
            c.set_r_nic_ip("not.an.ip")

    def test_invalid_r_nic_ip_format(self):
        c = Config(path="test_config.json")
        with self.assertRaises(ValueError):
            c.set_r_nic_ip(12345)

    def test_default_r_nic_ip(self):
        c = Config(path="test_config.json")
        self.assertEqual(c.r_nic_ip, "0.0.0.0")

    def test_r_nic_ip_saves_and_loads(self):
        c = Config(path="test_config.json")
        c.set_r_nic_ip("10.0.0.2")
        c.save()
        c2 = Config(path="test_config.json")
        self.assertEqual(c2.r_nic_ip, "10.0.0.2")

    def test_init_r_nic_ip_override(self):
        c = Config(path="test_config.json", r_nic_ip="10.0.0.2")
        self.assertEqual(c.r_nic_ip, "10.0.0.2")

    def test_t_nic_ip_and_r_nic_ip_are_independent(self):
        c = Config(path="test_config.json")
        c.set_t_nic_ip("10.0.0.1")
        c.set_r_nic_ip("10.0.0.2")
        self.assertEqual(c.t_nic_ip, "10.0.0.1")
        self.assertEqual(c.r_nic_ip, "10.0.0.2")



    # nested file structure

    def test_save_produces_nested_structure(self):
        c = Config(path="test_config.json")
        c.save()
        with open("test_config.json", "r") as f:
            data = json.load(f)
        self.assertIn("transmitter-config", data)
        self.assertIn("receiver-config", data)

    def test_transmitter_config_section_contains_expected_keys(self):
        c = Config(path="test_config.json")
        c.save()
        with open("test_config.json", "r") as f:
            data = json.load(f)
        for key in ["nic_ip", "target_ip", "target_port", "in_dev"]:
            self.assertIn(key, data["transmitter-config"])

    def test_receiver_config_section_contains_expected_keys(self):
        c = Config(path="test_config.json")
        c.save()
        with open("test_config.json", "r") as f:
            data = json.load(f)
        for key in ["nic_ip", "port", "ch", "sr", "buf", "tolerance", "gain", "out_dev"]:
            self.assertIn(key, data["receiver-config"])

    def test_transmitter_and_receiver_sections_are_independent(self):
        # changing a receiver value should not affect the transmitter section and vice versa
        c = Config(path="test_config.json")
        c.set_r_nic_ip("10.0.0.2")
        c.set_t_nic_ip("10.0.0.1")
        c.save()
        with open("test_config.json", "r") as f:
            data = json.load(f)
        self.assertEqual(data["transmitter-config"]["nic_ip"], "10.0.0.1")
        self.assertEqual(data["receiver-config"]["nic_ip"], "10.0.0.2")

    def test_load_file_with_unknown_top_level_key_raises(self):
        with open("test_config.json", "w") as f:
            json.dump({"mode": "receiver", "transmitter-config": {}, "receiver-config": {}, "banana": 1}, f)
        with patch("builtins.input", side_effect=EOFError):
            with self.assertRaises((Exception, RuntimeError)):
                Config(path="test_config.json")

    def test_load_file_with_unknown_tx_key_raises(self):
        with open("test_config.json", "w") as f:
            json.dump({"transmitter-config": {"banana": 1}, "receiver-config": {}}, f)
        with patch("builtins.input", side_effect=EOFError):
            with self.assertRaises((Exception, RuntimeError)):
                Config(path="test_config.json")

    def test_load_file_with_unknown_rx_key_raises(self):
        with open("test_config.json", "w") as f:
            json.dump({"transmitter-config": {}, "receiver-config": {"banana": 1}}, f)
        with patch("builtins.input", side_effect=EOFError):
            with self.assertRaises((Exception, RuntimeError)):
                Config(path="test_config.json")



class TestAudioInOutClasses(unittest.TestCase):

    def setUp(self):
        if os.path.exists("test_config.json"):
            os.remove("test_config.json")
        self.config = Config(path="test_config.json") # don't need to manually set up each time since some config tests required variation in config files and/or when it was loaded
        # also don't need a test 2 config file

    def tearDown(self):
        if os.path.exists("test_config.json"):
            os.remove("test_config.json")



    # audioinput

    @patch("main.sounddevice.InputStream")
    def test_audio_input_start_opens_stream(self, mock_stream_class):
        mock_stream = MagicMock()
        mock_stream_class.return_value = mock_stream
        ai = AudioInput(self.config)
        ai.start(lambda indata, f, t, s: None)
        mock_stream_class.assert_called_once()
        mock_stream.start.assert_called_once()

    @patch("main.sounddevice.InputStream")
    def test_audio_input_stop_closes_stream(self, mock_stream_class):
        mock_stream = MagicMock()
        mock_stream_class.return_value = mock_stream
        ai = AudioInput(self.config)
        ai.start(lambda indata, f, t, s: None)
        ai.stop()
        mock_stream.stop.assert_called_once()
        mock_stream.close.assert_called_once()

    @patch("main.sounddevice.InputStream")
    def test_audio_input_stop_clears_stream_reference(self, mock_stream_class):
        mock_stream_class.return_value = MagicMock()
        ai = AudioInput(self.config)
        ai.start(lambda indata, f, t, s: None)
        ai.stop()
        self.assertIsNone(ai._stream)

    @patch("main.sounddevice.InputStream")
    def test_audio_input_stop_before_start_does_not_crash(self, mock_stream_class):
        ai = AudioInput(self.config)
        ai.stop()



    # audioinput config values

    @patch("main.sounddevice.InputStream")
    def test_audio_input_uses_config_samplerate(self, mock_stream_class):
        mock_stream_class.return_value = MagicMock()
        ai = AudioInput(self.config)
        ai.start(lambda indata, f, t, s: None)
        kwargs = mock_stream_class.call_args.kwargs
        self.assertEqual(kwargs["samplerate"], self.config.sr)

    @patch("main.sounddevice.InputStream")
    def test_audio_input_uses_config_channels(self, mock_stream_class):
        mock_stream_class.return_value = MagicMock()
        self.config.set_ch(17) # something other than default of 2 since if it's hardcoded for some reason it's likely to be 2
        ai = AudioInput(self.config)                  # if anyone uses 17 channels for something they're a fucking psychopath
        ai.start(lambda indata, f, t, s: None)
        kwargs = mock_stream_class.call_args.kwargs
        self.assertEqual(kwargs["channels"], 17)

    @patch("main.sounddevice.InputStream")
    def test_audio_input_uses_float32(self, mock_stream_class):
        mock_stream_class.return_value = MagicMock()
        ai = AudioInput(self.config)
        ai.start(lambda indata, f, t, s: None)
        kwargs = mock_stream_class.call_args.kwargs
        self.assertEqual(kwargs["dtype"], "float32")

    @patch("main.sounddevice.InputStream")
    def test_audio_input_uses_blocksize_1024(self, mock_stream_class):
        mock_stream_class.return_value = MagicMock()
        ai = AudioInput(self.config)
        ai.start(lambda indata, f, t, s: None)
        kwargs = mock_stream_class.call_args.kwargs
        self.assertEqual(kwargs["blocksize"], 1024)

    @patch("main.sounddevice.InputStream")
    def test_audio_input_no_device_kwarg_when_in_dev_none(self, mock_stream_class):
        mock_stream_class.return_value = MagicMock()
        self.config.in_dev = None
        ai = AudioInput(self.config)
        ai.start(lambda indata, f, t, s: None)
        kwargs = mock_stream_class.call_args.kwargs
        self.assertNotIn("device", kwargs)

    @patch("main.find_device_by_name", return_value=3)
    @patch("main.sounddevice.InputStream")
    def test_audio_input_passes_device_index_when_in_dev_set(self, mock_stream_class, mock_find):
        mock_stream_class.return_value = MagicMock()
        self.config.in_dev = "MacBook Pro Microphone"
        ai = AudioInput(self.config)
        ai.start(lambda indata, f, t, s: None)
        kwargs = mock_stream_class.call_args.kwargs
        self.assertEqual(kwargs["device"], 3)

    @patch("main.find_device_by_name", return_value=3)
    @patch("main.sounddevice.InputStream")
    def test_audio_input_calls_find_device_with_correct_args(self, mock_stream_class, mock_find):
        mock_stream_class.return_value = MagicMock()
        self.config.in_dev = "MacBook Pro Microphone"
        ai = AudioInput(self.config)
        ai.start(lambda indata, f, t, s: None)
        mock_find.assert_called_once_with("MacBook Pro Microphone", "input")



    # audioinput callbacks

    @patch("main.sounddevice.InputStream")
    def test_audio_input_callback_receives_data(self, mock_stream_class):
        mock_stream_class.return_value = MagicMock()
        received = []
        def tmp_callback(indata, frames, time, status):
            received.append(indata.copy())
        ai = AudioInput(self.config)
        ai.start(tmp_callback)
        callback = mock_stream_class.call_args.kwargs["callback"]
        fake_audio = np.ones((1024, 2), dtype="float32") * 0.5
        callback(fake_audio, 1024, None, None)
        self.assertEqual(len(received), 1)
        np.testing.assert_array_equal(received[0], fake_audio)

    @patch("main.sounddevice.InputStream")
    def test_audio_input_callback_called_multiple_times(self, mock_stream_class):
        mock_stream_class.return_value = MagicMock()
        call_count = [0]
        def tmp_callback(indata, frames, time, status):
            call_count[0] += 1
        ai = AudioInput(self.config)
        ai.start(tmp_callback)
        callback = mock_stream_class.call_args.kwargs["callback"]
        fake_audio = np.zeros((1024, 2), dtype="float32")
        for _ in range(5):
            callback(fake_audio, 1024, None, None)
        self.assertEqual(call_count[0], 5)

    @patch("main.sounddevice.InputStream")
    def test_audio_input_callback_receives_correct_frame_count(self, mock_stream_class):
        mock_stream_class.return_value = MagicMock()
        received_frames = []
        def tmp_callback(indata, frames, time, status):
            received_frames.append(frames)
        ai = AudioInput(self.config)
        ai.start(tmp_callback)
        callback = mock_stream_class.call_args.kwargs["callback"]
        callback(np.zeros((1024, 2), dtype="float32"), 1024, None, None)
        self.assertEqual(received_frames[0], 1024)

    @patch("main.sounddevice.InputStream")
    def test_audio_input_config_reference_not_copy(self, mock_stream_class):
        mock_stream_class.return_value = MagicMock()
        ai = AudioInput(self.config)
        self.assertIs(ai.config, self.config)



    # audiooutput

    @patch("main.sounddevice.OutputStream")
    def test_audio_output_start_opens_stream(self, mock_stream_class):
        mock_stream = MagicMock()
        mock_stream_class.return_value = mock_stream
        ao = AudioOutput(self.config)
        ao.start(lambda outdata, f, t, s: outdata.__setitem__(slice(None), 0))
        mock_stream_class.assert_called_once()
        mock_stream.start.assert_called_once()

    @patch("main.sounddevice.OutputStream")
    def test_audio_output_stop_closes_stream(self, mock_stream_class):
        mock_stream = MagicMock()
        mock_stream_class.return_value = mock_stream
        ao = AudioOutput(self.config)
        ao.start(lambda outdata, f, t, s: outdata.__setitem__(slice(None), 0))
        ao.stop()
        mock_stream.stop.assert_called_once()
        mock_stream.close.assert_called_once()

    @patch("main.sounddevice.OutputStream")
    def test_audio_output_stop_clears_stream_reference(self, mock_stream_class):
        mock_stream_class.return_value = MagicMock()
        ao = AudioOutput(self.config)
        ao.start(lambda outdata, f, t, s: outdata.__setitem__(slice(None), 0))
        ao.stop()
        self.assertIsNone(ao._stream)

    @patch("main.sounddevice.OutputStream")
    def test_audio_output_stop_before_start_does_not_crash(self, mock_stream_class):
        ao = AudioOutput(self.config)
        ao.stop()



    # autiooutput config values

    @patch("main.sounddevice.OutputStream")
    def test_audio_output_uses_config_samplerate(self, mock_stream_class):
        mock_stream_class.return_value = MagicMock()
        ao = AudioOutput(self.config)
        ao.start(lambda outdata, f, t, s: outdata.__setitem__(slice(None), 0))
        kwargs = mock_stream_class.call_args.kwargs
        self.assertEqual(kwargs["samplerate"], self.config.sr)

    @patch("main.sounddevice.OutputStream")
    def test_audio_output_uses_config_channels(self, mock_stream_class):
        mock_stream_class.return_value = MagicMock()
        self.config.set_ch(17) # again something other than default of 2, check notes from above section
        ao = AudioOutput(self.config)
        ao.start(lambda outdata, f, t, s: outdata.__setitem__(slice(None), 0))
        kwargs = mock_stream_class.call_args.kwargs
        self.assertEqual(kwargs["channels"], 17)

    @patch("main.sounddevice.OutputStream")
    def test_audio_output_uses_float32(self, mock_stream_class):
        mock_stream_class.return_value = MagicMock()
        ao = AudioOutput(self.config)
        ao.start(lambda outdata, f, t, s: outdata.__setitem__(slice(None), 0))
        kwargs = mock_stream_class.call_args.kwargs
        self.assertEqual(kwargs["dtype"], "float32")

    @patch("main.sounddevice.OutputStream")
    def test_audio_output_uses_blocksize_1024(self, mock_stream_class):
        mock_stream_class.return_value = MagicMock()
        ao = AudioOutput(self.config)
        ao.start(lambda outdata, f, t, s: outdata.__setitem__(slice(None), 0))
        kwargs = mock_stream_class.call_args.kwargs
        self.assertEqual(kwargs["blocksize"], 1024)

    @patch("main.sounddevice.OutputStream")
    def test_audio_output_no_device_kwarg_when_out_dev_none(self, mock_stream_class):
        mock_stream_class.return_value = MagicMock()
        self.config.out_dev = None
        ao = AudioOutput(self.config)
        ao.start(lambda outdata, f, t, s: outdata.__setitem__(slice(None), 0))
        kwargs = mock_stream_class.call_args.kwargs
        self.assertNotIn("device", kwargs)

    @patch("main.find_device_by_name", return_value=1)
    @patch("main.sounddevice.OutputStream")
    def test_audio_output_passes_device_index_when_out_dev_set(self, mock_stream_class, mock_find):
        mock_stream_class.return_value = MagicMock()
        self.config.out_dev = "MacBook Pro Speakers"
        ao = AudioOutput(self.config)
        ao.start(lambda outdata, f, t, s: outdata.__setitem__(slice(None), 0))
        kwargs = mock_stream_class.call_args.kwargs
        self.assertEqual(kwargs["device"], 1)

    @patch("main.find_device_by_name", return_value=1)
    @patch("main.sounddevice.OutputStream")
    def test_audio_output_calls_find_device_with_correct_args(self, mock_stream_class, mock_find):
        mock_stream_class.return_value = MagicMock()
        self.config.out_dev = "MacBook Pro Speakers"
        ao = AudioOutput(self.config)
        ao.start(lambda outdata, f, t, s: outdata.__setitem__(slice(None), 0))
        mock_find.assert_called_once_with("MacBook Pro Speakers", "output")



    # audiooutput callbacks

    @patch("main.sounddevice.OutputStream")
    def test_audio_output_callback_fills_outdata(self, mock_stream_class):
        mock_stream_class.return_value = MagicMock()
        def tmp_callback(outdata, frames, time, status):
            outdata[:] = np.ones((frames, 2), dtype="float32") * 0.5
        ao = AudioOutput(self.config)
        ao.start(tmp_callback)
        callback = mock_stream_class.call_args.kwargs["callback"]
        outdata = np.zeros((1024, 2), dtype="float32")
        callback(outdata, 1024, None, None)
        self.assertTrue(np.all(outdata == 0.5))

    @patch("main.sounddevice.OutputStream")
    def test_audio_output_callback_called_multiple_times(self, mock_stream_class):
        mock_stream_class.return_value = MagicMock()
        call_count = [0]
        def tmp_callback(outdata, frames, time, status):
            call_count[0] += 1
            outdata[:] = 0
        ao = AudioOutput(self.config)
        ao.start(tmp_callback)
        callback = mock_stream_class.call_args.kwargs["callback"]
        for _ in range(5):
            outdata = np.zeros((1024, 2), dtype="float32")
            callback(outdata, 1024, None, None)
        self.assertEqual(call_count[0], 5)

    @patch("main.sounddevice.OutputStream")
    def test_audio_output_config_is_reference(self, mock_stream_class):
        mock_stream_class.return_value = MagicMock()
        ao = AudioOutput(self.config)
        self.assertIs(ao.config, self.config)



    # updates config mid-runtime

    @patch("main.sounddevice.InputStream")
    def test_audio_input_gain_change_reflected_in_callback(self, mock_stream_class):
        mock_stream_class.return_value = MagicMock()
        results = []
        def tmp_callback(indata, frames, time, status):
            results.append(indata[0, 0] * self.config.gain)
        ai = AudioInput(self.config)
        ai.start(tmp_callback)
        callback = mock_stream_class.call_args.kwargs["callback"]
        fake = np.ones((1024, 2), dtype="float32")
        self.config.set_gain(2.0)
        callback(fake, 1024, None, None)
        self.assertAlmostEqual(results[0], 2.0)

    @patch("main.sounddevice.InputStream")
    def test_audio_input_gain_update_does_not_require_restart(self, mock_stream_class):
        mock_stream_class.return_value = MagicMock()
        ai = AudioInput(self.config)
        ai.start(lambda indata, f, t, s: None)
        self.config.set_gain(3.0)
        self.assertEqual(self.config.gain, 3.0)
        self.assertIsNotNone(ai._stream)



class TestFramingFunctions(unittest.TestCase):
    def test_audio_frame_roundtrip(self):
        a, b = socket.socketpair()
        try:
            send_frame(a, MSG_AUDIO, b"according to all known laws of aviation")
            msg_type, payload = recv_frame(b)
            self.assertEqual(msg_type, MSG_AUDIO)
            self.assertEqual(payload, b"according to all known laws of aviation")
        finally:
            a.close()
            b.close()

    def test_control_frame_roundtrip(self):
        a, b = socket.socketpair()
        try:
            send_frame(a, MSG_CONTROL, b"according to all known laws of aviation")
            msg_type, payload = recv_frame(b)
            self.assertEqual(msg_type, MSG_CONTROL)
            self.assertEqual(payload, b"according to all known laws of aviation")
        finally:
            a.close()
            b.close()
            
    def test_empty_payload_roundtrip(self):
        a, b = socket.socketpair()
        try:
            send_frame(a, MSG_AUDIO, b"")
            msg_type, payload = recv_frame(b)
            self.assertEqual(msg_type, MSG_AUDIO)
            self.assertEqual(payload, b"")
        finally:
            a.close()
            b.close()
            
    def test_massive_payload_roundtrip(self):
        a, b = socket.socketpair()
        try:
            send_frame(a, MSG_AUDIO, b"x"*4096)
            msg_type, payload = recv_frame(b)
            self.assertEqual(msg_type, MSG_AUDIO)
            self.assertEqual(payload, b"x"*4096)
        finally:
            a.close()
            b.close()

    def test_frame_order_consistency(self):
        a, b = socket.socketpair()
        try:
            send_frame(a, MSG_AUDIO, b"according to all known laws of aviation")
            send_frame(a, MSG_CONTROL, b"there is no way that the bee should be able to fly")
            send_frame(a, MSG_CONTROL, b"the bee of course flies anyway")
            send_frame(a, MSG_AUDIO, b"because bees don't care what humans think is impossible")
            msg_type, payload = recv_frame(b)
            self.assertEqual(msg_type, MSG_AUDIO)
            self.assertEqual(payload, b"according to all known laws of aviation")
            msg_type, payload = recv_frame(b)
            self.assertEqual(msg_type, MSG_CONTROL)
            self.assertEqual(payload, b"there is no way that the bee should be able to fly")
            msg_type, payload = recv_frame(b)
            self.assertEqual(msg_type, MSG_CONTROL)
            self.assertEqual(payload, b"the bee of course flies anyway")
            msg_type, payload = recv_frame(b)
            self.assertEqual(msg_type, MSG_AUDIO)
            self.assertEqual(payload, b"because bees don't care what humans think is impossible")
        finally:
            a.close()
            b.close()
            
    def test_recv_exactly_connection_error(self):
        a, b = socket.socketpair()
        a.close()
        with self.assertRaises(ConnectionError):
            msg_type, payload = recv_frame(b)
        b.close()



class TestPlaybackBuffer(unittest.TestCase):

    def setUp(self):
        if os.path.exists("test_config.json"):
            os.remove("test_config.json")
        self.config = Config(path="test_config.json")

    def tearDown(self):
        if os.path.exists("test_config.json"):
            os.remove("test_config.json")

    def _prefill(self, buf):
        frames_needed = int((self.config.buf / 1000) * self.config.sr / BLOCKSIZE) + 1
        for _ in range(frames_needed):
            buf.push(np.ones((BLOCKSIZE, self.config.ch), dtype="float32"))
        # trigger the prefill flag by calling pop once
        buf.pop()
        # drain remaining frames
        while True:
            try:
                buf.queue.get_nowait()
            except queue.Empty:
                break



    # pre-fill behaviour

    def test_pop_returns_silence_before_prefill(self):
        buf = PlaybackBuffer(self.config)
        result = buf.pop()
        np.testing.assert_array_equal(result, np.zeros((BLOCKSIZE, self.config.ch), dtype="float32"))

    def test_pop_returns_silence_shape_matches_channels(self):
        buf = PlaybackBuffer(self.config)
        result = buf.pop()
        self.assertEqual(result.shape, (BLOCKSIZE, self.config.ch))

    def test_pop_silence_shape_updates_with_channel_count(self):
        self.config.set_ch(1)
        buf = PlaybackBuffer(self.config)
        result = buf.pop()
        self.assertEqual(result.shape, (BLOCKSIZE, 1))

    def test_pop_stops_returning_silence_after_prefill(self):
        buf = PlaybackBuffer(self.config)
        self._prefill(buf)
        buf.push(np.ones((BLOCKSIZE, self.config.ch), dtype="float32") * 0.5)
        result = buf.pop()
        self.assertFalse(np.all(result == 0))



    # update_buf

    def test_update_buf_increase_keeps_playing(self):
        buf = PlaybackBuffer(self.config)
        self._prefill(buf)
        self.config.set_buf(self.config.buf + 200)
        buf.update_buf()
        self.assertTrue(buf.pfilled)

    def test_update_buf_decrease_keeps_playing(self):
        buf = PlaybackBuffer(self.config)
        self._prefill(buf)
        self.config.set_buf(self.config.buf - 200)
        buf.update_buf()
        self.assertTrue(buf.pfilled)

    def test_update_buf_increase_adds_silence_frames(self):
        buf = PlaybackBuffer(self.config)
        self._prefill(buf)
        size_before = buf.queue.qsize()
        self.config.set_buf(self.config.buf + 200)
        buf.update_buf()
        self.assertGreater(buf.queue.qsize(), size_before)

    def test_update_buf_decrease_drops_frames(self):
        buf = PlaybackBuffer(self.config)
        self._prefill(buf)
        # push some frames so there's something to drop
        for _ in range(50):
            buf.push(np.ones((BLOCKSIZE, self.config.ch), dtype="float32"))
        size_before = buf.queue.qsize()
        self.config.set_buf(self.config.buf - 200)
        buf.update_buf()
        self.assertLess(buf.queue.qsize(), size_before)

    def test_update_buf_increase_preserves_existing_audio(self):
        # audio already in queue should still be there after increasing buffer
        buf = PlaybackBuffer(self.config)
        self._prefill(buf)
        frames = np.ones((BLOCKSIZE, self.config.ch), dtype="float32") * 0.5
        buf.push(frames)
        size_before = buf.queue.qsize()
        self.config.set_buf(self.config.buf + 200)
        buf.update_buf()
        # queue should be larger, not smaller
        self.assertGreater(buf.queue.qsize(), size_before)

    def test_update_buf_no_change_keeps_playing(self):
        buf = PlaybackBuffer(self.config)
        self._prefill(buf)
        buf.update_buf() # same buffer value, nothing should change
        self.assertTrue(buf.pfilled)



    # push and pop

    def test_pushed_frames_come_back_out(self):
        buf = PlaybackBuffer(self.config)
        self._prefill(buf)
        frames = np.ones((BLOCKSIZE, self.config.ch), dtype="float32") * 0.5
        buf.push(frames)
        result = buf.pop()
        np.testing.assert_array_almost_equal(result, frames)

    def test_gain_applied_on_pop(self):
        self.config.set_gain(2.0)
        buf = PlaybackBuffer(self.config)
        self._prefill(buf)
        frames = np.ones((BLOCKSIZE, self.config.ch), dtype="float32") * 0.5
        buf.push(frames)
        result = buf.pop()
        expected = frames * 2.0
        np.testing.assert_array_almost_equal(result, expected)

    def test_gain_change_reflected_without_restart(self):
        buf = PlaybackBuffer(self.config)
        self._prefill(buf)
        frames = np.ones((BLOCKSIZE, self.config.ch), dtype="float32")
        buf.push(frames)
        self.config.set_gain(3.0)
        result = buf.pop()
        np.testing.assert_array_almost_equal(result, frames * 3.0)

    def test_pop_returns_silence_when_queue_runs_dry(self):
        buf = PlaybackBuffer(self.config)
        self._prefill(buf)
        while True:
            try:
                buf.queue.get_nowait()
            except queue.Empty:
                break
        result = buf.pop()
        np.testing.assert_array_equal(result, np.zeros((BLOCKSIZE, self.config.ch), dtype="float32"))

    def test_pop_resets_prefill_when_queue_runs_dry(self):
        buf = PlaybackBuffer(self.config)
        self._prefill(buf)
        while True:
            try:
                buf.queue.get_nowait()
            except queue.Empty:
                break
        buf.pop()   # triggers dry buffer, resets pfilled
        self.assertFalse(buf.pfilled)

    def test_frames_come_out_in_order(self):
        buf = PlaybackBuffer(self.config)
        self._prefill(buf)
        a = np.ones((BLOCKSIZE, self.config.ch), dtype="float32") * 0.1
        b = np.ones((BLOCKSIZE, self.config.ch), dtype="float32") * 0.2
        c = np.ones((BLOCKSIZE, self.config.ch), dtype="float32") * 0.3
        buf.push(a)
        buf.push(b)
        buf.push(c)
        np.testing.assert_array_almost_equal(buf.pop(), a)
        np.testing.assert_array_almost_equal(buf.pop(), b)
        np.testing.assert_array_almost_equal(buf.pop(), c)



    # reset

    def test_reset_clears_queue(self):
        buf = PlaybackBuffer(self.config)
        self._prefill(buf)
        buf.reset()
        self.assertEqual(buf.queue.qsize(), 0)

    def test_reset_resets_prefill(self):
        buf = PlaybackBuffer(self.config)
        self._prefill(buf)
        buf.reset()
        self.assertFalse(buf.pfilled)

    def test_pop_returns_silence_after_reset(self):
        buf = PlaybackBuffer(self.config)
        self._prefill(buf)
        buf.reset()
        result = buf.pop()
        np.testing.assert_array_equal(result, np.zeros((BLOCKSIZE, self.config.ch), dtype="float32"))



class TestConnectionClass(unittest.TestCase):

    def setUp(self):
        if os.path.exists("test_config.json"):
            os.remove("test_config.json")
        self.config = Config(path="test_config.json")
        # find a free port dynamically (5010 broke when tests failed and didn't release it properly)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("", 0))
            free_port = s.getsockname()[1]
        self.config.set_port(free_port)
        self.config.target_port = free_port  # connect() uses target_port; align with the receiver's port

    def tearDown(self):
        if os.path.exists("test_config.json"):
            os.remove("test_config.json")

    def make_connected_pair(self):
        received = []
        receiver = Connection(self.config)
        transmitter = Connection(self.config)

        receiver.listen(lambda msg_type, payload: received.append((msg_type, payload)))
        time.sleep(0.1)  # give the server socket time to start listening
        transmitter.connect("127.0.0.1", lambda msg_type, payload: received.append((msg_type, payload)))
        time.sleep(0.1)  # give the connection time to connect

        return receiver, transmitter, received

    def test_transmitter_connects_successfully(self):
        receiver = Connection(self.config)
        transmitter = Connection(self.config)
        receiver.listen(lambda t, p: None)
        time.sleep(0.1)
        transmitter.connect("127.0.0.1", lambda t, p: None)
        time.sleep(0.1)
        self.assertIsNotNone(transmitter.sock)
        receiver.disconnect()
        transmitter.disconnect()

    def test_receiver_accepts_connection(self):
        receiver = Connection(self.config)
        transmitter = Connection(self.config)
        receiver.listen(lambda t, p: None)
        time.sleep(0.1)
        transmitter.connect("127.0.0.1", lambda t, p: None)
        time.sleep(0.1)
        self.assertIsNotNone(receiver.sock)
        receiver.disconnect()
        transmitter.disconnect()

    def test_receiver_running_after_listen(self):
        receiver = Connection(self.config)
        receiver.listen(lambda t, p: None)
        time.sleep(0.1)
        self.assertTrue(receiver.running)
        receiver.disconnect()

    def test_transmitter_running_after_connect(self):
        receiver = Connection(self.config)
        transmitter = Connection(self.config)
        receiver.listen(lambda t, p: None)
        time.sleep(0.1)
        transmitter.connect("127.0.0.1", lambda t, p: None)
        time.sleep(0.1)
        self.assertTrue(transmitter.running)
        receiver.disconnect()
        transmitter.disconnect()

    def test_transmitter_sends_audio_frame(self):
        receiver, transmitter, received = self.make_connected_pair()
        transmitter.send(MSG_AUDIO, b"hello")
        time.sleep(0.1)
        self.assertEqual(len(received), 1)
        self.assertEqual(received[0][0], MSG_AUDIO)
        self.assertEqual(received[0][1], b"hello")
        receiver.disconnect()
        transmitter.disconnect()

    def test_transmitter_sends_control_frame(self):
        receiver, transmitter, received = self.make_connected_pair()
        transmitter.send(MSG_CONTROL, b'{"key": "gain", "value": 2.0}')
        time.sleep(0.1)
        self.assertEqual(len(received), 1)
        self.assertEqual(received[0][0], MSG_CONTROL)
        receiver.disconnect()
        transmitter.disconnect()

    def test_receiver_sends_back_to_transmitter(self):
        received_by_transmitter = []
        receiver    = Connection(self.config)
        transmitter = Connection(self.config)
        receiver.listen(lambda t, p: None)
        time.sleep(0.1)
        transmitter.connect("127.0.0.1", lambda t, p: received_by_transmitter.append((t, p)))
        time.sleep(0.1)
        receiver.send(MSG_CONTROL, b'{"key": "buf", "value": 300}')
        time.sleep(0.1)
        self.assertEqual(len(received_by_transmitter), 1)
        self.assertEqual(received_by_transmitter[0][0], MSG_CONTROL)
        receiver.disconnect()
        transmitter.disconnect()

    def test_multiple_frames_received_in_order(self):
        receiver, transmitter, received = self.make_connected_pair()
        transmitter.send(MSG_AUDIO,   b"according to all known las of abiation")
        transmitter.send(MSG_CONTROL, b"there is now ay that the bee should be able to fly")
        transmitter.send(MSG_AUDIO,   b"its wings are too small to get its fat little b ody off the ground")
        transmitter.send(MSG_AUDIO,   b"the bee of course flies anyway")
        transmitter.send(MSG_AUDIO,   b"because bees dont care what humans think is impossible")
        time.sleep(0.1)
        self.assertEqual(len(received), 5)
        self.assertEqual(received[0][1], b"according to all known las of abiation")
        self.assertEqual(received[1][1], b"there is now ay that the bee should be able to fly")
        self.assertEqual(received[2][1], b"its wings are too small to get its fat little b ody off the ground")
        self.assertEqual(received[3][1], b"the bee of course flies anyway")
        self.assertEqual(received[4][1], b"because bees dont care what humans think is impossible")
        receiver.disconnect()
        transmitter.disconnect()

    def test_empty_payload_sent_and_received(self):
        receiver, transmitter, received = self.make_connected_pair()
        transmitter.send(MSG_CONTROL, b"")
        time.sleep(0.1)
        self.assertEqual(received[0][1], b"")
        receiver.disconnect()
        transmitter.disconnect()

    def test_large_payload_sent_and_received(self):
        receiver, transmitter, received = self.make_connected_pair()
        big = b"x" * 65536
        transmitter.send(MSG_AUDIO, big)
        time.sleep(0.2)  # larger payload needs more time
        self.assertEqual(received[0][1], big)
        receiver.disconnect()
        transmitter.disconnect()

    def test_send_does_not_crash_when_not_connected(self):
        transmitter = Connection(self.config)
        transmitter.send(MSG_AUDIO, b"according to all known laws of aviation") # should do nothing, not throw

    def test_disconnect_sets_running_false(self):
        receiver, transmitter, _ = self.make_connected_pair()
        transmitter.disconnect()
        self.assertFalse(transmitter.running)
        receiver.disconnect()

    def test_disconnect_clearssock(self):
        receiver, transmitter, _ = self.make_connected_pair()
        transmitter.disconnect()
        self.assertIsNone(transmitter.sock)
        receiver.disconnect()

    def test_receiver_disconnect_clears_server(self):
        receiver, transmitter, _ = self.make_connected_pair()
        receiver.disconnect()
        self.assertIsNone(receiver.server)
        transmitter.disconnect()

    def test_disconnect_before_connect_does_not_crash(self):
        conn = Connection(self.config)
        conn.disconnect()   # should do nothing

    # def test_receiver_waits_for_reconnect_after_transmitter_drops(self):
    #     received = []
    #     receiver = Connection(self.config)
    #     transmitter = Connection(self.config)
    #     receiver.listen(lambda t, p: received.append((t, p)))
    #     time.sleep(0.2)
    #     transmitter.connect("127.0.0.1", lambda t, p: None)
    #     time.sleep(0.2)
    #     transmitter.disconnect()

    #     # poll until sock is None or timeout after 5 seconds
    #     deadline = time.time() + 5.0
    #     while time.time() < deadline:
    #         if receiver.sock is None:
    #             break
    #         time.sleep(0.05)

    #     self.assertTrue(receiver.running)
    #     self.assertIsNone(receiver.sock)
    #     receiver.disconnect()

    # ── config values used correctly ──────────────────────────────────────────

    def test_uses_config_port(self):
        receiver    = Connection(self.config)
        transmitter = Connection(self.config)
        receiver.listen(lambda t, p: None)
        time.sleep(0.1)
        transmitter.connect("127.0.0.1", lambda t, p: None)
        time.sleep(0.1)
        self.assertIsNotNone(transmitter.sock)
        receiver.disconnect()
        transmitter.disconnect()



class TestSettingsSync(unittest.TestCase):

    class FakeConnection:
        def __init__(self):
            self.sent = []
        def send(self, msg_type, payload):
            self.sent.append((msg_type, payload))

    def setUp(self):
        if os.path.exists("test_config.json"):
            os.remove("test_config.json")
        self.config = Config(path="test_config.json")
        self.sync = SettingsSync(self.config, self.FakeConnection(), role="receiver")

    def tearDown(self):
        if os.path.exists("test_config.json"):
            os.remove("test_config.json")


    # send_setting

    def test_send_setting_sends_msg_control(self):
        self.sync.send_setting("sr", 48000)
        self.assertEqual(self.sync.connection.sent[0][0], MSG_CONTROL)

    def test_send_setting_deserialises_correctly(self):
        self.sync.send_setting("buf", 500)
        data = json.loads(self.sync.connection.sent[0][1].decode())
        self.assertEqual(data, {"type": "setting", "key": "buf", "value": 500})

    def test_send_setting_key_correct(self):
        self.sync.send_setting("gain", 2.0)
        data = json.loads(self.sync.connection.sent[0][1].decode())
        self.assertEqual(data["key"], "gain")

    def test_send_setting_value_correct(self):
        self.sync.send_setting("gain", 2.0)
        data = json.loads(self.sync.connection.sent[0][1].decode())
        self.assertEqual(data["value"], 2.0)

    def test_send_setting_type_field_correct(self):
        self.sync.send_setting("sr", 44100)
        data = json.loads(self.sync.connection.sent[0][1].decode())
        self.assertEqual(data["type"], "setting")



    # send_device_list

    @patch("main.list_input_devices", return_value=["MacBook Pro Microphone", "UMC404HD 192k"])
    def test_send_device_list_input_sends_msg_control(self, _):
        self.sync.send_device_list("input")
        self.assertEqual(self.sync.connection.sent[0][0], MSG_CONTROL)

    @patch("main.list_input_devices", return_value=["MacBook Pro Microphone", "UMC404HD 192k"])
    def test_send_device_list_input_contains_devices(self, _):
        self.sync.send_device_list("input")
        data = json.loads(self.sync.connection.sent[0][1].decode())
        self.assertEqual(data["devices"], ["MacBook Pro Microphone", "UMC404HD 192k"])

    @patch("main.list_input_devices", return_value=["MacBook Pro Microphone", "UMC404HD 192k"])
    def test_send_device_list_input_kind_correct(self, _):
        self.sync.send_device_list("input")
        data = json.loads(self.sync.connection.sent[0][1].decode())
        self.assertEqual(data["kind"], "input")

    @patch("main.list_output_devices", return_value=["MacBook Pro Speakers", "Headphones"])
    def test_send_device_list_output_contains_devices(self, _):
        self.sync.send_device_list("output")
        data = json.loads(self.sync.connection.sent[0][1].decode())
        self.assertEqual(data["devices"], ["MacBook Pro Speakers", "Headphones"])

    @patch("main.list_output_devices", return_value=["MacBook Pro Speakers", "Headphones"])
    def test_send_device_list_output_kind_correct(self, _):
        self.sync.send_device_list("output")
        data = json.loads(self.sync.connection.sent[0][1].decode())
        self.assertEqual(data["kind"], "output")

    def test_send_device_list_invalid_kind_raises(self):
        with self.assertRaises(ValueError):
            self.sync.send_device_list("banana")



    # send_all_settings

    def test_send_all_settings_sends_sr(self):
        self.sync.send_all_settings()
        keys = [json.loads(p.decode())["key"] for _, p in self.sync.connection.sent]
        self.assertIn("sr", keys)

    def test_send_all_settings_sends_ch(self):
        self.sync.send_all_settings()
        keys = [json.loads(p.decode())["key"] for _, p in self.sync.connection.sent]
        self.assertIn("ch", keys)

    def test_send_all_settings_sends_buf(self):
        self.sync.send_all_settings()
        keys = [json.loads(p.decode())["key"] for _, p in self.sync.connection.sent]
        self.assertIn("buf", keys)

    def test_send_all_settings_sends_gain(self):
        self.sync.send_all_settings()
        keys = [json.loads(p.decode())["key"] for _, p in self.sync.connection.sent]
        self.assertIn("gain", keys)

    def test_send_all_settings_sends_tolerance(self):
        self.sync.send_all_settings()
        keys = [json.loads(p.decode())["key"] for _, p in self.sync.connection.sent]
        self.assertIn("tolerance", keys)

    def test_send_all_settings_does_not_send_in_dev(self):
        self.sync.send_all_settings()
        keys = [json.loads(p.decode())["key"] for _, p in self.sync.connection.sent]
        self.assertNotIn("in_dev", keys)

    def test_send_all_settings_does_not_send_out_dev(self):
        self.sync.send_all_settings()
        keys = [json.loads(p.decode())["key"] for _, p in self.sync.connection.sent]
        self.assertNotIn("out_dev", keys)



    # handle_message — settings

    def test_handle_message_ignores_audio(self):
        self.sync.handle_message(MSG_AUDIO, b"some audio data")
        # config should be unchanged — no exception, no side effects
        self.assertEqual(self.config.sr, 48000)

    def test_handle_message_applies_sr(self):
        msg = json.dumps({"type": "setting", "key": "sr", "value": 44100}).encode()
        self.sync.handle_message(MSG_CONTROL, msg)
        self.assertEqual(self.config.sr, 44100)

    def test_handle_message_applies_ch(self):
        msg = json.dumps({"type": "setting", "key": "ch", "value": 1}).encode()
        self.sync.handle_message(MSG_CONTROL, msg)
        self.assertEqual(self.config.ch, 1)

    def test_handle_message_applies_buf(self):
        msg = json.dumps({"type": "setting", "key": "buf", "value": 300}).encode()
        self.sync.handle_message(MSG_CONTROL, msg)
        self.assertEqual(self.config.buf, 300)

    def test_handle_message_applies_gain(self):
        msg = json.dumps({"type": "setting", "key": "gain", "value": 2.0}).encode()
        self.sync.handle_message(MSG_CONTROL, msg)
        self.assertEqual(self.config.gain, 2.0)

    def test_handle_message_applies_in_dev(self):
        msg = json.dumps({"type": "setting", "key": "in_dev", "value": "MacBook Pro Microphone"}).encode()
        self.sync.handle_message(MSG_CONTROL, msg)
        self.assertEqual(self.config.in_dev, "MacBook Pro Microphone")

    def test_handle_message_applies_out_dev(self):
        msg = json.dumps({"type": "setting", "key": "out_dev", "value": "MacBook Pro Speakers"}).encode()
        self.sync.handle_message(MSG_CONTROL, msg)
        self.assertEqual(self.config.out_dev, "MacBook Pro Speakers")

    def test_handle_message_invalid_key_does_not_crash(self):
        msg = json.dumps({"type": "setting", "key": "according to all known laws", "value": 999}).encode()
        self.sync.handle_message(MSG_CONTROL, msg)   # should do nothing

    def test_handle_message_invalid_value_does_not_crash(self):
        msg = json.dumps({"type": "setting", "key": "sr", "value": 99999}).encode()
        self.sync.handle_message(MSG_CONTROL, msg)
        self.assertEqual(self.config.sr, 48000)   # unchanged



    # handle_message — device lists

    def test_handle_message_stores_input_device_list(self):
        msg = json.dumps({"type": "device_list", "kind": "input", "devices": ["MacBook Pro Microphone", "UMC404HD 192k"]}).encode()
        self.sync.handle_message(MSG_CONTROL, msg)
        self.assertEqual(self.sync.remote_input_devices, ["MacBook Pro Microphone", "UMC404HD 192k"])

    def test_handle_message_stores_output_device_list(self):
        msg = json.dumps({"type": "device_list", "kind": "output", "devices": ["MacBook Pro Speakers", "External Headphones"]}).encode()
        self.sync.handle_message(MSG_CONTROL, msg)
        self.assertEqual(self.sync.remote_output_devices, ["MacBook Pro Speakers", "External Headphones"])

    def test_handle_message_updates_device_list_on_change(self):
        msg1 = json.dumps({"type": "device_list", "kind": "output", "devices": ["MacBook Pro Speakers"]}).encode()
        msg2 = json.dumps({"type": "device_list", "kind": "output", "devices": ["MacBook Pro Speakers", "External Headphones"]}).encode()
        self.sync.handle_message(MSG_CONTROL, msg1)
        self.sync.handle_message(MSG_CONTROL, msg2)
        self.assertEqual(self.sync.remote_output_devices, ["MacBook Pro Speakers", "External Headphones"])

    def test_remote_input_devices_starts_empty(self):
        self.assertEqual(self.sync.remote_input_devices, [])

    def test_remote_output_devices_starts_empty(self):
        self.assertEqual(self.sync.remote_output_devices, [])



    def test_handle_message_applies_tolerance(self):
        msg = json.dumps({"type": "setting", "key": "tolerance", "value": 50}).encode()
        self.sync.handle_message(MSG_CONTROL, msg)
        self.assertEqual(self.config.tolerance, 50)

    def test_handle_message_receiver_saves_receiver_owned_key(self):
        sync = SettingsSync(self.config, self.FakeConnection(), role="receiver")
        msg = json.dumps({"type": "setting", "key": "gain", "value": 3.0}).encode()
        sync.handle_message(MSG_CONTROL, msg)
        c2 = Config(path="test_config.json")
        self.assertEqual(c2.gain, 3.0)

    def test_handle_message_transmitter_does_not_save_receiver_owned_key(self):
        sync = SettingsSync(self.config, self.FakeConnection(), role="transmitter")
        msg = json.dumps({"type": "setting", "key": "gain", "value": 3.0}).encode()
        sync.handle_message(MSG_CONTROL, msg)
        # gain applied in memory but not persisted — reload should give default
        c2 = Config(path="test_config.json")
        self.assertEqual(c2.gain, 1.0)

    def test_handle_message_transmitter_applies_setting_in_memory(self):
        sync = SettingsSync(self.config, self.FakeConnection(), role="transmitter")
        msg = json.dumps({"type": "setting", "key": "buf", "value": 300}).encode()
        sync.handle_message(MSG_CONTROL, msg)
        self.assertEqual(self.config.buf, 300)   # applied in memory even though not saved



class TestDeviceMonitor(unittest.TestCase):

    class FakeSync:
        def __init__(self):
            self.sent_device_lists = []
        def send_device_list(self, kind):
            self.sent_device_lists.append(kind)

    def setUp(self):
        if os.path.exists("test_config.json"):
            os.remove("test_config.json")
        self.config = Config(path="test_config.json")
        self.sync = self.FakeSync()

    def tearDown(self):
        if os.path.exists("test_config.json"):
            os.remove("test_config.json")



    # init

    def test_invalid_mode_raises(self):
        with self.assertRaises(ValueError):
            DeviceMonitor(self.sync, "according to all known laws of aviation, there is no way the tthe bee should be able to fly")

    def test_valid_input_mode(self):
        monitor = DeviceMonitor(self.sync, "input")
        self.assertEqual(monitor.mode, "input")

    def test_valid_output_mode(self):
        monitor = DeviceMonitor(self.sync, "output")
        self.assertEqual(monitor.mode, "output")

    def test_starts_not_running(self):
        monitor = DeviceMonitor(self.sync, "input")
        self.assertFalse(monitor.running)

    def test_remote_device_list_starts_empty(self):
        monitor = DeviceMonitor(self.sync, "input")
        self.assertEqual(monitor.last_devices, [])



    # start / stop

    @patch("main.list_input_devices", return_value=["MacBook Pro Microphone"])
    def test_start_sets_running(self, _):
        monitor = DeviceMonitor(self.sync, "input")
        monitor.start()
        self.assertTrue(monitor.running)
        monitor.stop()

    @patch("main.list_input_devices", return_value=["MacBook Pro Microphone"])
    def test_start_populates_last_devices(self, _):
        monitor = DeviceMonitor(self.sync, "input")
        monitor.start()
        self.assertEqual(monitor.last_devices, ["MacBook Pro Microphone"])
        monitor.stop()

    @patch("main.list_output_devices", return_value=["MacBook Pro Speakers"])
    def test_start_populates_last_devices_output(self, _):
        monitor = DeviceMonitor(self.sync, "output")
        monitor.start()
        self.assertEqual(monitor.last_devices, ["MacBook Pro Speakers"])
        monitor.stop()

    @patch("main.list_input_devices", return_value=["MacBook Pro Microphone"])
    def test_stop_sets_running_false(self, _):
        monitor = DeviceMonitor(self.sync, "input")
        monitor.start()
        monitor.stop()
        self.assertFalse(monitor.running)



    # poll loop — device change detection

    def one_shot_sleep(self, monitor):
        call_count = [0]
        def fake_sleep(_):
            call_count[0] += 1
            if call_count[0] >= 2:   # stop after second sleep
                monitor.running = False
        return fake_sleep

    @patch("main.list_input_devices", side_effect=[["MacBook Pro Microphone"], ["MacBook Pro Microphone", "UMC404HD 192k"]])
    def test_poll_loop_detects_input_device_added(self, _):
        monitor = DeviceMonitor(self.sync, "input")
        monitor.last_devices = ["MacBook Pro Microphone"]
        monitor.running = True
        with patch("time.sleep", side_effect=self.one_shot_sleep(monitor)):
            monitor.poll_loop()
        self.assertIn("input", self.sync.sent_device_lists)

    @patch("main.list_input_devices", side_effect=[["MacBook Pro Microphone", "UMC404HD 192k"], ["MacBook Pro Microphone"]])
    def test_poll_loop_detects_input_device_removed(self, _):
        monitor = DeviceMonitor(self.sync, "input")
        monitor.last_devices = ["MacBook Pro Microphone", "UMC404HD 192k"]
        monitor.running = True
        with patch("time.sleep", side_effect=self.one_shot_sleep(monitor)):
            monitor.poll_loop()
        self.assertIn("input", self.sync.sent_device_lists)

    @patch("main.list_output_devices", side_effect=[["MacBook Pro Speakers"], ["MacBook Pro Speakers", "External Headphones"]])
    def test_poll_loop_detects_output_device_added(self, _):
        monitor = DeviceMonitor(self.sync, "output")
        monitor.last_devices = ["MacBook Pro Speakers"]
        monitor.running = True
        with patch("time.sleep", side_effect=self.one_shot_sleep(monitor)):
            monitor.poll_loop()
        self.assertIn("output", self.sync.sent_device_lists)

    @patch("main.list_input_devices", return_value=["MacBook Pro Microphone"])
    def test_poll_loop_does_not_send_when_no_change(self, _):
        monitor = DeviceMonitor(self.sync, "input")
        monitor.last_devices = ["MacBook Pro Microphone"]
        monitor.running = True
        with patch("time.sleep", side_effect=self.one_shot_sleep(monitor)):
            monitor.poll_loop()
        self.assertEqual(self.sync.sent_device_lists, [])

    @patch("main.list_input_devices", side_effect=[["MacBook Pro Microphone"], ["MacBook Pro Microphone", "UMC404HD 192k"]])
    def test_poll_loop_updates_last_devices_on_change(self, _):
        monitor = DeviceMonitor(self.sync, "input")
        monitor.last_devices = ["MacBook Pro Microphone"]
        monitor.running = True
        with patch("time.sleep", side_effect=self.one_shot_sleep(monitor)):
            monitor.poll_loop()
        self.assertEqual(monitor.last_devices, ["MacBook Pro Microphone", "UMC404HD 192k"])


if __name__ == "__main__":
    unittest.main()