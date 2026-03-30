import json

class Config:
    def __init__(self, path="config.json", sr=48000, buf=500, gain=1.0, port=5005, in_dev=None, out_dev=None):
        self.path = path
        self.sr = sr
        self.buf = buf
        self.gain = gain
        self.port = port
        self.in_dev = in_dev
        self.out_dev = out_dev

        try:
            self.load()
        except FileNotFoundError:
            pass
    
    # to GET use config.var_name as a direct reference


    # SET methods w/ validation

    def set_path(self, path:str):
        if path.split(".")[-1] != "json": raise ValueError(f"Invalid path: {path} - filename must end in .json")

        # TODO check if file either doesn't exist or exists but is valid config
        # if file exists and is invalid config refuse to change path and throw error
        # to avoid overwriting existing config files for other programs

        else: self.path = path

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

        # TODO check if port is in use

        else: self.port = port
    

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
        
        self.set_sr(data.get("sr", self.sr))
        self.set_buf(data.get("buf", self.buf))
        self.set_gain(data.get("gain", self.gain))
        self.set_port(data.get("port", self.port))
        self.set_in_dev(data.get("in_dev", self.in_dev))
        self.set_out_dev(data.get("out_dev", self.out_dev))
        
config = Config()

