import json
import socket
import sounddevice
import struct
import threading
import queue
import numpy as np
import time


BLOCKSIZE = 1024

# message type defenitions
MSG_AUDIO = 0x01
MSG_CONTROL = 0x02

# framing functions
def send_frame(sock, msg_type: int, payload: bytes):
    header = struct.pack(">BI", msg_type, len(payload))
    sock.sendall(header + payload)

def recv_exactly(sock, n: int) -> bytes:
    buf = b""
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise ConnectionError("Connection closed before all bytes received")
        buf += chunk
    return buf

def recv_frame(sock) -> tuple:
    header = recv_exactly(sock, 5)
    msg_type, length = struct.unpack(">BI", header)
    payload = recv_exactly(sock, length) if length > 0 else b""
    return msg_type, payload


# check if port is free
# code adapted from https://www.geeksforgeeks.org/python/python-simple-port-scanner-with-sockets/ 
def port_in_use(port:int):
    with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:
        try: 
            s.bind(("",port))
            return False
        except OSError:
            return True



# audio device shit
def find_device_by_name(name:str, kind:str):
    for i, device in enumerate(sounddevice.query_devices()):
        if kind == "input" and device["max_input_channels"] == 0: continue
        if kind == "output" and device["max_output_channels"] == 0: continue
        if name.lower() == device["name"].lower(): return i

    raise ValueError(f"No {kind} device found matching '{name}'")

def list_input_devices() -> list:
    return [
        device["name"]
        for device in sounddevice.query_devices()
        if device["max_input_channels"] > 0
    ]

def list_output_devices() -> list:
    return [
        device["name"]
        for device in sounddevice.query_devices()
        if device["max_output_channels"] > 0
    ]



class Config:
    def __init__(self, path="config.json", mode=None, ch=None, sr=None, buf=None, gain=None, port=None, in_dev=None, out_dev=None, nic_ip=None, target_ip=None):
        self.path   = path
        self.mode   = "transmitter"
        self.ch     = 2
        self.sr     = 48000
        self.buf    = 500
        self.gain   = 1.0
        self.port   = 5005
        self.in_dev = None  # none will use system defaults
        self.out_dev = None
        self.nic_ip = "0.0.0.0" # will use system default
        self.target_ip = None

        valid_path = False
        while not valid_path:
            try: 
                self.set_path(path)
                valid_path = True
            except Exception as e:
                try:
                    path = input(f"Unable to use config path \"{path}\" due to the following exception: {e}\nPlease enter a new filename to use, ending in .json: ")
                except EOFError:
                    raise RuntimeError(f"Unable to use config path, and no interactive input available to fix. Re-run the program with either a different path specified, or fix the issue loading the current path.")

        try:
            self.load()
        except FileNotFoundError:
            pass

        if mode is not None:
            try: self.set_mode(mode)
            except Exception: pass

        if ch is not None:
            try: self.set_ch(ch)
            except Exception: pass

        if sr is not None:
            try: self.set_sr(sr)
            except Exception: pass
            
        if buf is not None:
            try: self.set_buf(buf)
            except Exception: pass

        if gain is not None:
            try: self.set_gain(gain)
            except Exception: pass

        if port is not None:
            try: self.set_port(port)
            except Exception: pass
        
        if in_dev is not None:
            try: self.set_in_dev(in_dev)
            except Exception: pass

        if out_dev is not None:
            try: self.set_out_dev(out_dev)
            except Exception: pass
        
        if nic_ip is not None:
            try: self.set_nic_ip(nic_ip)
            except Exception: pass

        if target_ip is not None:
            try: self.set_target_ip(target_ip)
            except Exception: pass
        
        self.save()
    
    # to GET use config.var_name as a direct reference

    # SET methods w/ validation

    def set_path(self, path:str):
        if path.split(".")[-1] != "json": raise ValueError(f"Invalid path: {path} - filename must end in .json")
        else: 
            try:
                with open(path, 'r') as f:
                    data = json.load(f)
                for key in data.keys():
                    if not key in ["mode", "ch", "sr", "buf", "gain", "port", "nic_ip", "target_ip", "in_dev", "out_dev"]:
                        raise ValueError(f"Invalid path: {path} - file exists but contains keys this program can't generate, possibly config file for another program?")
            except FileNotFoundError:
                pass
            self.path = path

    def set_mode(self, mode:str):
        # kill me why do I always spell receiver with an ie that's going to break so much stuff i can already feel it
        if not mode in ["transmitter", "receiver"]: raise ValueError(f"Invalid mode: {mode} - must be \"transmitter\" or \"receiver\"")
        else: self.mode = mode

    def set_sr(self, sr:int):
        if not sr in [8000, 11025, 22050, 32000, 44100, 48000, 88200, 96000, 176400, 192000]: raise ValueError(f"Invalid Sample rate: {str(sr)} - must be one of 8000, 11025, 22050, 32000, 44100, 48000, 88200, 96000, 176400, or 192000")
        else: self.sr = sr

    def set_ch(self, ch:int):
        if ch < 1: raise ValueError(f"Invalid channel count: {str(ch)} - must transmit/recieve at least one channel")
        else: self.ch = ch

    def set_buf(self, buf:int):
        if buf < 0: raise ValueError(f"Invalid buffer size: {str(buf)} - must be greater than or equal to zero")
        else: self.buf = buf

    def set_gain(self, gain:float):
        if gain <= 0.0 or gain > 8.0: raise ValueError(f"Invalid gain: {str(gain)} - must be greater than 0.0 and less than (or equal to) 8.0")
        else: self.gain = gain

    def set_port(self, port:int):
        if port < 1024 or port > 65535: raise ValueError(f"Invalid port: {str(port)} - must be greater than or equal to 1024 and less than or equal to 65535")
        elif port_in_use(port): raise ValueError(f"Invalid port: {str(port)} - port in use by another program on this host")
        else: self.port = port

    def set_in_dev(self, in_dev: str):
        if in_dev is not None and not isinstance(in_dev, str): # allow missing devices to keep config, check should be done on transmit/recieve start
            raise ValueError(f"Invalid input device: {in_dev} — must be a string name or None for defautl")
        self.in_dev = in_dev

    def set_out_dev(self, out_dev: str):
        if out_dev is not None and not isinstance(out_dev, str): # same again
            raise ValueError(f"Invalid output device: {out_dev} — must be a string name or None for default")
        self.out_dev = out_dev
    
    def set_nic_ip(self, nic_ip: str):
        if not isinstance(nic_ip, str):
            raise ValueError(f"Invalid NIC IP: {nic_ip} — must be a string")
        parts = nic_ip.split(".")
        if nic_ip != "0.0.0.0":
            if len(parts) != 4 or not all(p.isdigit() and 0 <= int(p) <= 255 for p in parts):
                raise ValueError(f"Invalid NIC IP: {nic_ip} — must be a valid IPv4 address or 0.0.0.0")
        self.nic_ip = nic_ip

    def set_target_ip(self, target_ip: str):
        if target_ip is None:
            self.target_ip = None
            return
        if not isinstance(target_ip, str):
            raise ValueError(f"Invalid target IP: {target_ip} — must be a string")
        parts = target_ip.split(".")
        if len(parts) != 4 or not all(p.isdigit() and 0 <= int(p) <= 255 for p in parts):
            raise ValueError(f"Invalid target IP: {target_ip} — must be a valid IPv4 address")
        self.target_ip = target_ip
    

    # save/load to/from json

    def save(self):
        to_save = {
            "mode": self.mode,
            "ch": self.ch,
            "sr": self.sr,
            "buf": self.buf,
            "gain": self.gain,
            "port": self.port,
            "in_dev": self.in_dev,
            "out_dev": self.out_dev,
            "nic_ip": self.nic_ip,
            "target_ip": self.target_ip,
        }

        with open(self.path, 'w') as f:
            json.dump(to_save, f)

    def load(self):
        with open(self.path, 'r') as f:
            data = json.load(f)
        
        try: self.set_mode(data.get("mode", self.mode))
        except Exception: pass
        
        try: self.set_ch(data.get("ch", self.ch))
        except Exception: pass
        
        try: self.set_sr(data.get("sr", self.sr))
        except Exception: pass

        try: self.set_buf(data.get("buf", self.buf))
        except Exception: pass

        try: self.set_gain(data.get("gain", self.gain))
        except Exception: pass

        try: self.set_port(data.get("port", self.port))
        except Exception: pass

        try: self.set_in_dev(data.get("in_dev", self.in_dev))
        except Exception: pass

        try: self.set_out_dev(data.get("out_dev", self.out_dev))
        except Exception: pass

        try: self.set_nic_ip(data.get("nic_ip", self.nic_ip))
        except Exception: pass

        try: self.set_target_ip(data.get("target_ip", self.target_ip))
        except Exception: pass

        self.save()



# AudioInput and AudioOutput classes cobbled together with examples from
# https://python-sounddevice.readthedocs.io/en/latest/examples.html and
# examples on stackoverflow

class AudioInput:
    def __init__(self, config):
        self.config = config
        self._stream = None

    def start(self, callback):
        kwargs = dict(
            samplerate=self.config.sr,
            channels=self.config.ch,
            dtype="float32",
            blocksize=BLOCKSIZE,
            callback=callback,
        )

        if self.config.in_dev is not None: kwargs["device"] = find_device_by_name(self.config.in_dev, "input")
        # for testing override the device 
        # kwargs["device"] = find_device_by_name("Coursework Loopback", "input")

        self._stream = sounddevice.InputStream(**kwargs)
        self._stream.start()

    def stop(self):
        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None


class AudioOutput:
    def __init__(self, config):
        self.config = config
        self._stream = None

    def start(self, callback):
        kwargs = dict(
            samplerate=self.config.sr,
            channels=self.config.ch,
            dtype="float32",
            blocksize=BLOCKSIZE,
            callback=callback,
        )

        if self.config.out_dev is not None: kwargs["device"] = find_device_by_name(self.config.out_dev, "output")
        # again for testing override the device 
        # kwargs["device"] = find_device_by_name("UMC404HD 192k", "output")

        self._stream = sounddevice.OutputStream(**kwargs)
        self._stream.start()

    def stop(self):
        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None



class PlaybackBuffer:
    def __init__(self, config):
        self.config  = config
        self.queue = queue.Queue()
        self.lock = threading.Lock()
        self.pfilled = False

    def push(self, frames):
        self.queue.put(frames)

    def pop(self):
        silence = np.zeros((BLOCKSIZE, self.config.ch), dtype="float32")
        
        with self.lock:
            if not self.pfilled:
                queued_ms = (self.queue.qsize() * BLOCKSIZE / self.config.sr) * 1000
                if queued_ms < self.config.buf:
                    return silence
                self.pfilled = True

        try:
            frames = self.queue.get_nowait()
            return (frames * self.config.gain).astype(np.float32)
        except queue.Empty:
            with self.lock:
                self.pfilled = False
            return silence

    def update_buf(self):
        target  = self.config.buf
        current = (self.queue.qsize() * BLOCKSIZE / self.config.sr) * 1000

        if current > target:
            ms_to_drop     = current - target
            frames_to_drop = int((ms_to_drop / 1000) * self.config.sr / BLOCKSIZE)
            for _ in range(frames_to_drop):
                try: self.queue.get_nowait()
                except queue.Empty: break

        elif current < target:
            ms_to_add     = target - current
            frames_to_add = int((ms_to_add / 1000) * self.config.sr / BLOCKSIZE)
            silence       = np.zeros((BLOCKSIZE, self.config.ch), dtype="float32")
            for _ in range(frames_to_add):
                self.queue.put(silence)

        with self.lock:
            self.pfilled = True

    def reset(self):
        with self.lock:
            self.queue = queue.Queue()
            self.pfilled = False



class Connection:
    def __init__(self, config):
        self.config = config
        self.sock = None
        self.server = None
        self.running = False
        self.send_lock = threading.Lock()
        self.on_message = None

    def connect(self, host: str, on_message):
        self.on_message = on_message
        self.running = True

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        nic_ip = self.config.nic_ip if hasattr(self.config, "nic_ip") else "0.0.0.0"
        if nic_ip and nic_ip != "0.0.0.0":
            s.bind((nic_ip, 0))

        s.connect((host, self.config.port))
        self.sock = s
        print(f"[Connection] Connected to {host}:{self.config.port}")

        threading.Thread(target=self.reader, daemon=True).start()

    def listen(self, on_message):
        self.on_message = on_message
        self.running = True

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        nic_ip = self.config.nic_ip if hasattr(self.config, "nic_ip") else "0.0.0.0"
        bind_ip = nic_ip if nic_ip and nic_ip != "0.0.0.0" else ""
        self.server.bind((bind_ip, self.config.port))
        self.server.listen(1)
        self.server.settimeout(1.0)

        print(f"[Connection] Listening on port {self.config.port}")
        threading.Thread(target=self.accept_loop, daemon=True).start()

    def accept_loop(self):
        while self.running:
            try:
                conn, addr = self.server.accept()
                conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                self.sock = conn
                print(f"[Connection] Transmitter connected from {addr[0]}")
                self.reader()
                self.sock = None
                print("[Connection] Transmitter disconnected — waiting for reconnect")
            except socket.timeout:
                continue
            except OSError:
                break

    def reader(self):
        while self.running:
            try:
                msg_type, payload = recv_frame(self.sock)
                if self.on_message:
                    self.on_message(msg_type, payload)
            except (ConnectionError, OSError):
                break

    def send(self, msg_type: int, payload: bytes):
        if not self.sock:
            return
        with self.send_lock:
            try:
                send_frame(self.sock, msg_type, payload)
            except OSError:
                pass

    def disconnect(self):
        self.running = False
        if self.sock:
            try: self.sock.close()
            except OSError: pass
            self.sock = None
        if self.server:
            try: self.server.close()
            except OSError: pass
            self.server = None
        print("[Connection] Disconnected")


class SettingsSync:
    def __init__(self, config, connection):
        self.config = config
        self.connection = connection

        self.remote_input_devices  = []
        self.remote_output_devices = []

    def send_setting(self, key:str, value):
        data = {"type": "setting", "key": key, "value": value}
        self.connection.send(MSG_CONTROL, json.dumps(data).encode())
    
    def send_device_list(self, kind:str):
        if kind == "input": devices = list_input_devices()
        elif kind == "output": devices = list_output_devices()
        else: raise ValueError(f"Invalid device type passed to send_device_list: {kind} is neither \"input\" nor \"output\"")

        data = {"type": "device_list", "kind": kind, "devices": devices}
        self.connection.send(MSG_CONTROL, json.dumps(data).encode())

    def send_all_settings(self):
        self.send_setting("sr", self.config.sr)
        self.send_setting("ch", self.config.ch)
        self.send_setting("buf", self.config.buf)
        self.send_setting("gain", self.config.gain)
        # self.send_setting("in_dev", self.config.in_dev)
        # self.send_setting("out_dev", self.config.out_dev)

    def handle_message(self, msg_type, payload):
        if msg_type == MSG_CONTROL: # we only care about control messages, audio goes to other palces
            data = json.loads(payload.decode())

            setters = {
                "sr":      self.config.set_sr,
                "ch":      self.config.set_ch,
                "buf":     self.config.set_buf,
                "gain":    self.config.set_gain,
                "in_dev":  self.config.set_in_dev,
                "out_dev": self.config.set_out_dev,
            }

            if data["type"] == "setting":
                if data["key"] in setters:
                    try:
                        setters[data["key"]](data["value"])
                    except Exception:
                        pass

            elif data["type"] == "device_list":
                if data["kind"] == "input":
                    self.remote_input_devices = data["devices"]
                elif data["kind"] == "output":
                    self.remote_output_devices = data["devices"]



class DeviceMonitor:
    def __init__(self, sync, mode: str):
        if mode not in ["input", "output"]:
            raise ValueError(f"Invalid mode: {mode} — must be 'input' or 'output'")
        self.sync = sync
        self.mode = mode
        self.running = False
        self.last_devices = []

    def start(self):
        self.running = True
        self.last_devices = list_input_devices() if self.mode == "input" else list_output_devices()
        threading.Thread(target=self.poll_loop, daemon=True).start()

    def stop(self):
        self.running = False

    def poll_loop(self):
        while self.running:
            time.sleep(1.5)
            current = list_input_devices() if self.mode == "input" else list_output_devices()
            if current != self.last_devices:
                self.last_devices = current
                self.sync.send_device_list(self.mode)



class TransmitStream:
    def __init__(self, config, connection, sync, monitor):
        self.config = config
        self.connection = connection
        self.sync = sync
        self.monitor = monitor

        self.audio_in = None
        self.running = False

    def connect(self, host):
        self.connection.connect(host, self.sync.handle_message)
        self.sync.send_all_settings()
        self.sync.send_device_list("input")
        self.monitor.start()
    
    def start_stream(self):
        self.running = True
        self.audio_in = AudioInput(self.config)
        self.audio_in.start(self.on_audio)

    def on_audio(self, indata, frames, time, status):
        if self.running:
            self.connection.send(MSG_AUDIO, indata.tobytes())

    def stop_stream(self):
        if self.audio_in is not None:
            self.audio_in.stop()
            self.audio_in = None
        self.running = False

    def disconnect(self):
        
        if self.audio_in is not None: self.stop_stream()

        self.monitor.stop()
        self.connection.disconnect()
