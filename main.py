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
    

    # turns out you don't ned get methods, you can just do config.sr from outside the class

    # # GET methods

    # def get_path(self): return(self.path)
    
    # def get_sr(self): return(self.sr)
    
    # def get_buf(self): return(self.buf)
    
    # def get_gain(self): return(self.gain)
    
    # def get_port(self): return(self.port)
    
    # def get_in_dev(self): return(self.in_dev)
    
    # def get_out_dev(self): return(self.out_dev)


    # SET methods w/ validation

    def set_path(self, path):
        if path.split(".")[-1] != "json": raise ValueError

        
        # TODO check if file either doesn't exist or exists but is valid config
        # if file exists and is invalid config refuse to change path and throw error
        # to avoid overwriting existing config files for other programs
    
    def set_sr(self, sr:int):
        if not sr in [8000, 11025, 22050, 32000, 44100, 48000, 88200, 96000, 176400, 192000]: raise ValueError
        else: self.sr = sr
    
    def set_buf(self, buf:int):
        if buf < 0: raise ValueError
        else: self.buf = buf
    
    def set_gain(self, gain:float):
        if gain <= 0.0 or gain >= 8.0: raise ValueError
        else: self.gain = gain
    
    def set_port(self, port:int):
        if port < 1024 or port > 65535: raise ValueError
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
        
        self.set_sr(data["sr"])
        self.set_buf(data["buf"])
        self.set_gain(data["gain"])
        self.set_port(data["port"])
        self.set_in_dev(data["in_dev"])
        self.set_out_dev(data["out_dev"])
        
config = Config()

