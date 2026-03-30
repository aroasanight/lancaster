import json
import socket


# check if port is free
# code adapted from https://www.geeksforgeeks.org/python/python-simple-port-scanner-with-sockets/ 
def port_in_use(port:int):
    with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:
        try: 
            s.bind(("",port))
            return False
        except OSError:
            return True



class Config:
    def __init__(self, path="config.json", sr=None, buf=None, gain=None, port=None, in_dev=None, out_dev=None):
        self.path   = path
        self.sr     = 48000
        self.buf    = 500
        self.gain   = 1.0
        self.port   = 5005
        self.in_dev = None
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
                    if not key in ["sr", "buf", "gain", "port", "in_dev", "out_dev"]:
                        raise ValueError(f"Invalid path: {path} - file exists but contains keys this program can't generate, possibly config file for another program?")
            except FileNotFoundError:
                pass
            self.path = path

    def set_sr(self, sr:int):
        if not sr in [8000, 11025, 22050, 32000, 44100, 48000, 88200, 96000, 176400, 192000]: raise ValueError(f"Invalid Sample rate: {str(sr)} - must be one of 8000, 11025, 22050, 32000, 44100, 48000, 88200, 96000, 176400, or 192000")
        else: self.sr = sr

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
    
    # TODO in_dev and out_dev setters
    

    # save/load to/from json

    def save(self):
        to_save = {
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
        
        try: self.set_sr(data.get("sr", self.sr))
        except Exception: pass

        try: self.set_buf(data.get("buf", self.buf))
        except Exception: pass

        try: self.set_gain(data.get("gain", self.gain))
        except Exception: pass

        try: self.set_port(data.get("port", self.port))
        except Exception: pass

        # TODO load in_dev and out_dev once setters exist

        self.save()
        
