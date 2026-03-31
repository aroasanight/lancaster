import json
import socket
import sounddevice



# check if port is free
# code adapted from https://www.geeksforgeeks.org/python/python-simple-port-scanner-with-sockets/ 
def port_in_use(port:int):
    with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:
        try: 
            s.bind(("",port))
            return False
        except OSError:
            return True


def find_device_by_name(name:str, kind:str):
    for i, device in enumerate(sounddevice.query_devices()):
        if kind == "input" and device["max_input_channels"] == 0: continue
        if kind == "output" and device["max_output_channels"] == 0: continue
        if name.lower() == device["name"].lower(): return i

    raise ValueError(f"No {kind} device found matching '{name}'")



class Config:
    def __init__(self, path="config.json", mode=None, ch=None, sr=None, buf=None, gain=None, port=None, in_dev=None, out_dev=None):
        self.path   = path
        self.mode   = "transmitter"
        self.ch     = 2
        self.sr     = 48000
        self.buf    = 500
        self.gain   = 1.0
        self.port   = 5005
        self.in_dev = None  # none will use system defaults
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
                    if not key in ["mode", "ch", "sr", "buf", "gain", "port", "in_dev", "out_dev"]:
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
            channels=2,
            dtype="float32",
            blocksize=1024,
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
            channels=2,
            dtype="float32",
            blocksize=1024,
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



# LOOPBACK TEST

# if __name__ == "__main__":
#     import time
#     import queue
    
#     config = Config(path="config.json")
#     q = queue.Queue()

#     audio_in  = AudioInput(config)
#     audio_out = AudioOutput(config)

#     def on_input(indata, frames, time, status):
#         q.put(indata.copy())

#     def on_output(outdata, frames, time, status):
#         try:
#             outdata[:] = q.get_nowait()
#         except queue.Empty:
#             outdata[:] = 0

#     audio_out.start(on_output)
#     audio_in.start(on_input)

#     time.sleep(30)
#     audio_in.stop()
#     audio_out.stop()