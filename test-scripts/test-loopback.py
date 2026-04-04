# this creates a loopback between input and output devices/classes 
# on the same host to test those directly without any network involvment
#
# if you're actually coming here to use this code, I wish you luck
# debugging whatever's gone wrong <3
#   - past Ari

from main import Config, AudioInput, AudioOutput

if __name__ == "__main__":
    import time
    import queue
    
    config = Config(path="config.json")
    q = queue.Queue()

    audio_in  = AudioInput(config)
    audio_out = AudioOutput(config)

    def on_input(indata, frames, time, status):
        q.put(indata.copy())

    def on_output(outdata, frames, time, status):
        try:
            outdata[:] = q.get_nowait()
        except queue.Empty:
            outdata[:] = 0

    audio_out.start(on_output)
    audio_in.start(on_input)

    time.sleep(30)
    audio_in.stop()
    audio_out.stop()