# similar to test-loopback.py but it bridges transmitstream and receivestream
# via 127.0.0.1 instead of directly patching the audio devices one to the other
# use with python3 network_test.py transmitter (or reciever, obviously).
# remember to change device overrides in this script to your actual
# in/out devices instead of coursework loopback and UMC404HD 192k like I still
# have set from my testing with this :))
#
# once again, if you're actually coming here to use this code, I wish you luck
# debugging whatever's gone wrong <3
#   - past Ari

import sys
import time
from main import Config, Connection, SettingsSync, DeviceMonitor, PlaybackBuffer, TransmitStream, ReceiveStream

if __name__ == "__main__":

    if len(sys.argv) < 2 or sys.argv[1] not in ["transmitter", "reciever"]: sys.exit(1)

    mode = sys.argv[1]
    config = Config(path="config.json", mode=mode)

    # i/o device overrides, should use defaults if commented out (in theory, haven't tested)
    config.set_in_dev("Coursework Loopback")
    config.set_out_dev("UMC404HD 192k")

    if mode == "transmitter":
        print("starting as transmitter")

        connection = Connection(config)
        sync = SettingsSync(config, connection)
        monitor = DeviceMonitor(sync, "input")
        stream = TransmitStream(config, connection, sync, monitor)

        print("connecting to localhost")
        stream.connect("127.0.0.1")

        print("connected, starting stream")
        stream.start_stream()

        print("streaming for 30s")
        try:
            time.sleep(30)
        except KeyboardInterrupt:
            pass

        print("shutting down *insert windows xp shutdown sound*")
        stream.stop_stream()
        stream.disconnect()

    elif mode == "receiver":
        print("recieving")

        connection = Connection(config)
        sync = SettingsSync(config, connection)
        monitor = DeviceMonitor(sync, "output")
        buffer = PlaybackBuffer(config)
        stream = ReceiveStream(config, connection, sync, monitor, buffer)

        print("waiting for transmitter")
        stream.listen()

        # wait for connection then start playback
        print("still waiting for transmitter")
        import time
        deadline = time.time() + 10
        while time.time() < deadline:
            if stream.connection.sock is not None:
                print("transmitter arrived")
                stream.start_stream()
                break
            time.sleep(0.1)

        print("recieving audio")
        try:
            time.sleep(30)
        except KeyboardInterrupt:
            pass

        print("shutting down *insert windows xp shutdown sound*")
        stream.stop_stream()
        stream.disconnect()