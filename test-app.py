# same as test-network.py but works using the app wrapper instead of
# manually wiring stuff together. if test-network works and this
# doesn't, the problem is most likely in the app wrapper class somewhere

import sys
import time
from main import Config, App

if __name__ == "__main__":

    if len(sys.argv) < 2 or sys.argv[1] not in ["transmitter", "receiver"]:
        sys.exit(1)

    mode   = sys.argv[1]
    config = Config(path="config.json", mode=mode)

    # i/o device overrides, should use defaults if commented out
    config.set_in_dev("Coursework Loopback")
    config.set_out_dev("UMC404HD 192k")

    app = App(config)

    if mode == "transmitter":
        print("starting as transmitter")
        app.pair(host="127.0.0.1")
        print("connected, starting stream")
        app.start_stream()
        print("streaming for 30s")
        try:
            time.sleep(30)
        except KeyboardInterrupt:
            pass
        print("shutting down *insert windows xp shutdown sound*")
        app.stop_stream()
        app.unpair()

    elif mode == "receiver":
        print("waiting for transmitter")
        app.pair()
        print("still waiting for transmitter to connect")
        deadline = time.time() + 10
        while time.time() < deadline:
            if app.connection.sock is not None:
                print("transmitter arrived, starting playback")
                app.start_stream()
                break
            time.sleep(0.1)
        print("receiving audio")
        try:
            time.sleep(30)
        except KeyboardInterrupt:
            pass
        print("shutting down *insert windows xp shutdown sound*")
        app.stop_stream()
        app.unpair()