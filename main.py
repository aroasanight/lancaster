import json
import socket
import sounddevice
import struct
import threading
import queue
import numpy as np
import time
import logging
log = logging.getLogger("main")

logging.basicConfig(
    level=logging.DEBUG,   # change to DEBUG when diagnosing issues
    format="%(asctime)s.%(msecs)03d [%(name)s] %(message)s",
    datefmt="%H:%M:%S"
)


BLOCKSIZE = 1024

# message type defenitions
MSG_AUDIO = 0x01
MSG_CONTROL = 0x02

# framing functions
def send_frame(sock, msg_type: int, payload: bytes):
    # log.debug(f"send_frame type={msg_type:#04x} len={len(payload)}")
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
    # log.debug(f"recv_frame type={msg_type:#04x} len={length}")
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
    TRANSMITTER_KEYS = {"t_nic_ip", "target_ip", "target_port", "in_dev"}
    RECEIVER_KEYS = {"r_nic_ip", "port", "ch", "sr", "buf", "tolerance", "gain", "out_dev"}

    def __init__(self, path="lancaster-config.json", mode=None,
                 # transmitter
                 t_nic_ip=None, target_ip=None, target_port=None, in_dev=None,
                 # receiver
                 r_nic_ip=None, port=None, ch=None, sr=None, buf=None,
                 tolerance=None, gain=None, out_dev=None):
        
        self.path   = path
        self.mode   = "transmitter"

        # transmitter
        self.t_nic_ip = "0.0.0.0"
        self.target_ip = None
        self.target_port = 5005
        self.in_dev = None  # none will use system defaults

        # receiver
        self.r_nic_ip = "0.0.0.0"
        self.ch     = 2
        self.sr     = 48000
        self.buf    = 500
        self.gain   = 1.0
        self.port   = 5005
        self.tolerance = 100
        self.out_dev = None


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

        if target_ip is not None:
            try: self.set_target_ip(target_ip)
            except Exception: pass

        if tolerance is not None:
            try: self.set_tolerance(tolerance)
            except Exception: pass

        if t_nic_ip is not None:
            try: self.set_t_nic_ip(t_nic_ip)
            except Exception: pass

        if r_nic_ip is not None:
            try: self.set_r_nic_ip(r_nic_ip)
            except Exception: pass

        if target_port is not None:
            try: self.set_target_port(target_port)
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
                top_keys = set(data.keys())
                allowed_top = {"mode", "transmitter-config", "receiver-config"}
                unknown = top_keys - allowed_top
                if unknown:
                    raise ValueError(f"Invalid path: {path} — unrecognised top-level keys {unknown}, possibly config for another program?")
                allowed_tx = {"nic_ip", "target_ip", "target_port", "in_dev"}
                allowed_rx = {"nic_ip", "port", "ch", "sr", "buf", "tolerance", "gain", "out_dev"}
                if "transmitter-config" in data:
                    unknown_tx = set(data["transmitter-config"].keys()) - allowed_tx
                    if unknown_tx:
                        raise ValueError(f"Invalid path: {path} — unrecognised transmitter-config keys {unknown_tx}")
                if "receiver-config" in data:
                    unknown_rx = set(data["receiver-config"].keys()) - allowed_rx
                    if unknown_rx:
                        raise ValueError(f"Invalid path: {path} — unrecognised receiver-config keys {unknown_rx}")
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
        if self.buf > 0:
            ratio = buf / self.buf
            self.tolerance = max(1, round(self.tolerance * ratio))
        self.buf = buf

    def set_gain(self, gain:float):
        if gain <= 0.0 or gain > 8.0: raise ValueError(f"Invalid gain: {str(gain)} - must be greater than 0.0 and less than (or equal to) 8.0")
        else: self.gain = gain

    def set_target_port(self, port: int):
        if port < 1024 or port > 65535:
            raise ValueError(f"Invalid target_port: {port} — must be 1024–65535")
        self.target_port = port

    def set_port(self, port:int):
        if port < 1024 or port > 65535: raise ValueError(f"Invalid port: {str(port)} - must be greater than or equal to 1024 and less than or equal to 65535")
        elif port_in_use(port): raise ValueError(f"Invalid port: {str(port)} - port in use by another program on this host")
        else: self.port = port

    def set_tolerance(self, tolerance: int):
        if tolerance < 1: raise ValueError(f"Invalid tolerance: {str(tolerance)} - must be at least 1ms")
        else: self.tolerance = tolerance

    def set_in_dev(self, in_dev: str):
        if in_dev is not None and not isinstance(in_dev, str): # allow missing devices to keep config, check should be done on transmit/recieve start
            raise ValueError(f"Invalid input device: {in_dev} — must be a string name or None for defautl")
        self.in_dev = in_dev

    def set_out_dev(self, out_dev: str):
        if out_dev is not None and not isinstance(out_dev, str): # same again
            raise ValueError(f"Invalid output device: {out_dev} — must be a string name or None for default")
        self.out_dev = out_dev

    def set_t_nic_ip(self, nic_ip: str):
        self.t_nic_ip = self.check_valid_ip(nic_ip, allow_wildcard=True)

    def set_r_nic_ip(self, nic_ip: str):
        self.r_nic_ip = self.check_valid_ip(nic_ip, allow_wildcard=True)

    def set_target_ip(self, target_ip: str):
        if target_ip is None:
            self.target_ip = None
            return
        self.target_ip = self.check_valid_ip(target_ip, allow_wildcard=False)

    def check_valid_ip(self, ip: str, allow_wildcard: bool) -> str:
        if not isinstance(ip, str):
            raise ValueError(f"IP must be a string, got {type(ip)}")
        if allow_wildcard and ip == "0.0.0.0":
            return ip
        parts = ip.split(".")
        if len(parts) != 4 or not all(p.isdigit() and 0 <= int(p) <= 255 for p in parts):
            raise ValueError(f"Invalid target IP: {ip} — must be a valid IPv4 address")
        return ip

    def save(self):
        to_save = {
            "mode": self.mode,
            "transmitter-config": {
                "nic_ip": self.t_nic_ip,
                "target_ip": self.target_ip,
                "target_port": self.target_port,
                "in_dev": self.in_dev,
            },
            "receiver-config": {
                "nic_ip": self.r_nic_ip,
                "port": self.port,
                "ch": self.ch,
                "sr": self.sr,
                "buf": self.buf,
                "tolerance": self.tolerance,
                "gain": self.gain,
                "out_dev": self.out_dev,
            },
        }

        with open(self.path, 'w') as f:
            json.dump(to_save, f, indent=4)

    def load(self):
        with open(self.path, 'r') as f:
            data = json.load(f)

        self._try(self.set_mode, data.get("mode", self.mode))

        tx = data.get("transmitter-config", {})
        self._try(self.set_t_nic_ip, tx.get("nic_ip", self.t_nic_ip))
        self._try(self.set_target_ip, tx.get("target_ip", self.target_ip))
        self._try(self.set_target_port, tx.get("target_port", self.target_port))
        self._try(self.set_in_dev, tx.get("in_dev", self.in_dev))

        rx = data.get("receiver-config", {})
        self._try(self.set_r_nic_ip, rx.get("nic_ip", self.r_nic_ip))
        self._try(self.set_port, rx.get("port", self.port))
        self._try(self.set_ch, rx.get("ch", self.ch))
        self._try(self.set_sr, rx.get("sr", self.sr))
        self._try(self.set_buf, rx.get("buf", self.buf))
        self._try(self.set_tolerance, rx.get("tolerance", self.tolerance))
        self._try(self.set_gain, rx.get("gain", self.gain))
        self._try(self.set_out_dev, rx.get("out_dev", self.out_dev))

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
        self.pop_count = 0
        self.depth_acc = 0
        self.WINDOW = 200
        self.correction = None
        self.last_frame = None

    def push(self, frames):
        self.queue.put(frames)

    def pop(self):
        silence = np.zeros((BLOCKSIZE, self.config.ch), dtype="float32")

        with self.lock:
            if not self.pfilled:
                queued_ms = (self.queue.qsize() * BLOCKSIZE / self.config.sr) * 1000
                log.debug(f"[Buffer] prefilling {queued_ms:.0f}/{self.config.buf}ms qsize={self.queue.qsize()}")
                if queued_ms < self.config.buf:
                    return silence
                log.info(f"[Buffer] prefill complete at {queued_ms:.0f}ms")
                self.pfilled = True

        # Apply correction decided at end of last window
        if self.correction == "skip":
            self.correction = None
            try:
                self.queue.get_nowait()   # discard one frame
                log.debug("[Buffer] drift correction: skipped frame (running hot)")
            except queue.Empty:
                pass

        elif self.correction == "repeat" and self.last_frame is not None:
            self.correction = None
            log.debug("[Buffer] drift correction: repeated frame (running cold)")
            return (self.last_frame * self.config.gain).astype(np.float32)

        # Normal pop
        try:
            frames = self.queue.get_nowait()
        except queue.Empty:
            log.warning("[Buffer] UNDERRUN — queue ran dry")
            with self.lock:
                self.pfilled = False
            return silence

        self.last_frame = frames.copy()

        # Accumulate for rolling window
        self.depth_acc += self.queue.qsize()
        self.pop_count += 1

        if self.pop_count >= self.WINDOW:
            avg_ms = (self.depth_acc / self.WINDOW * BLOCKSIZE / self.config.sr) * 1000
            target = self.config.buf
            error  = avg_ms - target

            tolerance_ms = self.config.tolerance

            log.debug(f"[Buffer] drift check: avg={avg_ms:.0f}ms target={target}ms error={error:+.0f}ms tolerance=±{tolerance_ms:.0f}ms")


            if error > tolerance_ms:
                self.correction = "skip"
            elif error < -tolerance_ms:
                self.correction = "repeat"

            self.pop_count = 0
            self.depth_acc = 0

        return (frames * self.config.gain).astype(np.float32)

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
            self.pop_count = 0
            self.depth_acc = 0
            self.correction = None

    def reset(self):
        with self.lock:
            self.queue = queue.Queue()
            self.pfilled = False
            self.pop_count = 0
            self.depth_acc = 0
            self.correction = None
            self.last_frame = None



class Connection:
    def __init__(self, config):
        self.config = config
        self.sock = None
        self.server = None
        self.running = False
        self.send_lock = threading.Lock()
        self.on_message = None
        self.on_connect = None

    def connect(self, host: str, on_message):
        self.on_message = on_message
        self.running = True

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        nic_ip = self.config.t_nic_ip
        if nic_ip and nic_ip != "0.0.0.0":
            s.bind((nic_ip, 0))

        s.connect((host, self.config.target_port))
        self.sock = s
        print(f"[Connection] Connected to {host}:{self.config.target_port}")

        threading.Thread(target=self.reader, daemon=True).start()

    def listen(self, on_message, on_connect=None):
        self.on_message = on_message
        self.on_connect = on_connect
        self.running = True

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        nic_ip = self.config.r_nic_ip
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
                if self.on_connect:
                    self.on_connect()   # runs once connection is established
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
            log.warning(f"[Connection] send called but no socket type={msg_type:#04x}")
            return
        with self.send_lock:
            try:
                send_frame(self.sock, msg_type, payload)
            except OSError as e:
                log.error(f"[Connection] send failed: {e}")

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
    def __init__(self, config, connection, role:str, on_command=None):
        self.config = config
        self.connection = connection
        self.role = role

        self.on_command = on_command

        self.remote_input_devices  = []
        self.remote_output_devices = []

    def send_setting(self, key:str, value):
        data = {"type": "setting", "key": key, "value": value}
        self.connection.send(MSG_CONTROL, json.dumps(data).encode())

    def send_command(self, action: str):
        data = {"type": "command", "action": action}
        self.connection.send(MSG_CONTROL, json.dumps(data).encode())

    def send_device_list(self, kind:str):
        if kind == "input": devices = list_input_devices()
        elif kind == "output": devices = list_output_devices()
        else: raise ValueError(f"Invalid device type passed to send_device_list: {kind} is neither \"input\" nor \"output\"")

        data = {"type": "device_list", "kind": kind, "devices": devices}
        self.connection.send(MSG_CONTROL, json.dumps(data).encode())

    def send_all_settings(self):
        # only sync receiver settings on new connection
        self.send_setting("sr", self.config.sr)
        self.send_setting("ch", self.config.ch)
        self.send_setting("buf", self.config.buf)
        self.send_setting("gain", self.config.gain)
        self.send_setting("tolerance", self.config.tolerance)
        # self.send_setting("in_dev", self.config.in_dev)
        # self.send_setting("out_dev", self.config.out_dev)

    def handle_message(self, msg_type, payload):
        if msg_type == MSG_CONTROL:
            data = json.loads(payload.decode())

            setters = {
                "sr":      self.config.set_sr,
                "ch":      self.config.set_ch,
                "buf":     self.config.set_buf,
                "gain":    self.config.set_gain,
                "tolerance": self.config.set_tolerance,
                "in_dev":  self.config.set_in_dev,
                "out_dev": self.config.set_out_dev,
            }

            if data["type"] == "setting":
                if data["key"] in setters:
                    try:
                        setters[data["key"]](data["value"])
                    except Exception:
                        pass
                    # only save if it's your setting to save
                    owns = (
                        (self.role == "receiver" and data["key"] in Config.RECEIVER_KEYS) or
                        (self.role == "transmitter" and data["key"] in Config.TRANSMITTER_KEYS)
                    )
                    if owns: self.config.save()

            elif data["type"] == "device_list":
                if data["kind"] == "input":
                    self.remote_input_devices = data["devices"]
                elif data["kind"] == "output":
                    self.remote_output_devices = data["devices"]

            elif data["type"] == "command":
                if self.on_command:
                    self.on_command(data["action"])



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
        self.send_queue = queue.Queue()
        self.send_thread = None

    def connect(self, host):
        self.config.set_target_ip(host)
        self.config.save()
        self.connection.connect(host, self.sync.handle_message)
        self.sync.send_device_list("input")
        self.monitor.start()

    def start_stream(self):
        self.monitor.stop()
        time.sleep(0.1)
        self.running = True

        self.send_thread = threading.Thread(target=self.sender_loop, daemon=True)
        self.send_thread.start()

        self.audio_in = AudioInput(self.config)
        self.audio_in.start(self.on_audio)

    def sender_loop(self):
        while self.running:
            try:
                payload = self.send_queue.get(timeout=0.2)
                self.connection.send(MSG_AUDIO, payload)
            except queue.Empty:
                continue

    def on_audio(self, indata, frames, time_info, status):
        if self.running:
            self.send_queue.put(indata.tobytes())

    def stop_stream(self):
        if self.send_thread is not None:
            self.send_thread.join(timeout=1.0)
            self.send_thread = None
        if self.audio_in is not None:
            self.audio_in.stop()
            self.audio_in = None
        self.running = False
        self.monitor.start()

    def disconnect(self):

        if self.audio_in is not None: self.stop_stream()

        self.monitor.stop()
        self.connection.disconnect()



class ReceiveStream:
    def __init__(self, config, connection, sync, monitor, buffer):
        self.config = config
        self.connection = connection
        self.sync = sync
        self.monitor = monitor
        self.buffer = buffer

        self.audio_out = None
        self.running = False

    def on_message(self, msg_type, payload):
        if msg_type == MSG_AUDIO:
            frames = np.frombuffer(payload, dtype=np.float32).copy()
            if frames.size % self.config.ch != 0:
                log.warning(f"[Receive] malformed frame size={frames.size} ch={self.config.ch}")
                return
            frames = frames.reshape(-1, self.config.ch)
            self.buffer.push(frames)
        elif msg_type == MSG_CONTROL:
            old_buf = self.config.buf
            self.sync.handle_message(msg_type, payload)
            if self.config.buf != old_buf:
                self.buffer.update_buf()

    def listen(self):
        self.monitor.start()
        self.connection.listen(
            on_message=self.on_message,
            on_connect=self.on_connected
        )

    def on_connected(self):
        self.sync.send_all_settings()
        self.sync.send_device_list("output")

    def start_stream(self):
        self.monitor.stop()
        self.running   = True
        self.audio_out = AudioOutput(self.config)

        def on_playback(outdata, frames, time_info, status):
            block = self.buffer.pop()
            outdata[:] = block[:frames]

        self.audio_out.start(on_playback)

    def stop_stream(self):
        if self.audio_out is not None:
            self.audio_out.stop()
            self.audio_out = None
        self.buffer.reset()
        self.running = False
        self.monitor.start()

    def disconnect(self):
        if self.audio_out is not None:
            self.stop_stream()
        self.monitor.stop()
        self.connection.disconnect()



class App:
    def __init__(self, config: Config):
        self.config = config
        self.stream = None
        self.connection = None
        self.sync = None
        self.monitor = None
        self.buffer = None

    def on_command(self, action: str):
        if action == "start":
            self.start_stream()
        elif action == "stop":
            self.stop_stream()

    def build_transmitter(self):
        self.connection = Connection(self.config)
        self.sync       = SettingsSync(self.config, self.connection, role="transmitter", on_command=self.on_command)
        self.monitor    = DeviceMonitor(self.sync, "input")
        self.stream     = TransmitStream(self.config, self.connection, self.sync, self.monitor)

    def build_receiver(self):
        self.connection = Connection(self.config)
        self.sync       = SettingsSync(self.config, self.connection, role="receiver", on_command=self.on_command)
        self.monitor    = DeviceMonitor(self.sync, "output")
        self.buffer     = PlaybackBuffer(self.config)
        self.stream     = ReceiveStream(self.config, self.connection, self.sync, self.monitor, self.buffer)

    def pair(self, host: str = None):
        if self.config.mode == "transmitter":
            if host is None:
                raise ValueError("host is required for transmitter mode")
            self.build_transmitter()
            self.stream.connect(host)
        elif self.config.mode == "receiver":
            self.build_receiver()
            self.stream.listen()

    def start_stream(self):
        if self.stream is None:
            raise RuntimeError("Not paired — call pair() first")
        self.stream.start_stream()

    def stop_stream(self):
        if self.stream is None:
            return
        self.stream.stop_stream()

    def unpair(self):
        if self.stream is None:
            return
        self.stream.disconnect()
        self.stream = None
        self.connection = None
        self.sync = None
        self.monitor = None
        self.buffer = None

    def push_setting(self, key: str, value):
        setter = {
            "sr":       self.config.set_sr,
            "ch":       self.config.set_ch,
            "buf":      self.config.set_buf,
            "gain":     self.config.set_gain,
            "tolerance": self.config.set_tolerance,
            "in_dev":   self.config.set_in_dev,
            "out_dev":  self.config.set_out_dev,
            "mode":     self.config.set_mode,
            "port":     self.config.set_port,
            "r_nic_ip": self.config.set_r_nic_ip,
            "t_nic_ip": self.config.set_t_nic_ip,
            "target_ip": self.config.set_target_ip,
            "target_port": self.config.set_target_port,
        }
        if key not in setter:
            print(f"[App] Unknown setting: {key}")
            return
        try:
            setter[key](value)
        except Exception as e:
            print(f"[App] Invalid value for {key}: {e}")
            return

        if key == "buf" and self.stream is not None:
            if isinstance(self.stream, ReceiveStream):
                self.stream.buffer.update_buf()
            # buf change scaled tolerance — send updated tolerance too
            if self.sync is not None:
                self.sync.send_setting("tolerance", self.config.tolerance)

        # Persist only if this side owns the key; transmitter-local keys
        # (target_ip, target_port, t_nic_ip, in_dev) are always saved on the
        # transmitter, receiver keys are always saved on the receiver.
        # mode and both nic_ips are always saved regardless.
        always_save = {"mode", "t_nic_ip", "r_nic_ip"}
        role = self.config.mode
        owns = (
            key in always_save or
            (role == "receiver"    and key in Config.RECEIVER_KEYS) or
            (role == "transmitter" and key in Config.TRANSMITTER_KEYS)
        )
        if owns:
            self.config.save()

        # sync shared (receiver) settings
        if self.sync is not None and key in Config.RECEIVER_KEYS:
            self.sync.send_setting(key, value)

    def send_command(self, action: str):
        if self.sync is not None:
            self.sync.send_command(action)

