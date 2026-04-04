# same as test-network.py but works using the app wrapper instead of
# manually wiring stuff together. if test-network works and this
# doesn't, the problem is most likely in the app wrapper class somewhere


import logging
from main import Config, App

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s.%(msecs)03d [%(name)s] %(message)s",
    datefmt="%H:%M:%S"
)
log = logging.getLogger("cli")

if __name__ == "__main__":

    config = Config(path="config.json")
    app    = App(config)

    print("lancaster test CLI (verbose logging)")
    print("commands: mode, pair, listen, start, stop, unpair, set, status, quit")
    print()

    running = True
    while running:
        try:
            raw = input("lancaster> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if not raw:
            continue

        parts = raw.split()
        cmd   = parts[0].lower()

        if cmd == "quit":
            log.info("quit received")
            if app.stream is not None:
                app.stop_stream()
                app.unpair()
            running = False

        elif cmd == "mode":
            if len(parts) < 2:
                print(f"  current mode: {config.mode}")
            else:
                app.push_setting("mode", parts[1])
                log.info(f"mode set to {config.mode}")

        elif cmd == "pair":
            host = parts[1] if len(parts) > 1 else config.target_ip
            if not host:
                print("  usage: pair <host>")
            else:
                log.info(f"pairing with {host}")
                try:
                    app.pair(host=host)
                    log.info(f"paired with {host}")
                except Exception as e:
                    log.error(f"pair failed: {e}")

        elif cmd == "listen":
            if config.mode != "receiver":
                print("  must be in receiver mode — run: mode receiver")
            else:
                log.info(f"listening on port {config.port}")
                try:
                    app.pair()
                    log.info("listening — waiting for transmitter")
                except Exception as e:
                    log.error(f"listen failed: {e}")

        elif cmd == "start":
            log.info("starting stream")
            try:
                app.start_stream()
                app.send_command("start")
                log.info("stream started")
            except Exception as e:
                log.error(f"start failed: {e}")

        elif cmd == "stop":
            log.info("stopping stream")
            app.stop_stream()
            app.send_command("stop")
            log.info("stream stopped")

        elif cmd == "unpair":
            log.info("unpairing")
            app.unpair()
            log.info("unpaired")

        elif cmd == "set":
            if len(parts) < 3:
                print("  usage: set <key> <value>")
            else:
                key     = parts[1]
                raw_val = " ".join(parts[2:])
                try:
                    if key in ("sr", "ch", "buf", "port"):
                        value = int(raw_val)
                    elif key == "gain":
                        value = float(raw_val)
                    elif raw_val.lower() in ("none", "default"):
                        value = None
                    else:
                        value = raw_val
                    log.info(f"setting {key} = {value}")
                    app.push_setting(key, value)
                    log.info(f"set {key} = {value} ok")
                except Exception as e:
                    log.error(f"set failed: {e}")

        elif cmd == "status":
            paired    = app.connection is not None
            connected = paired and app.connection.sock is not None
            streaming = app.stream is not None and app.stream.running
            print(f"  mode:      {config.mode}")
            print(f"  paired:    {'yes' if paired else 'no'}")
            print(f"  connected: {'yes' if connected else 'waiting' if paired else 'no'}")
            print(f"  streaming: {'yes' if streaming else 'no'}")
            if app.sync:
                print(f"  remote inputs:  {app.sync.remote_input_devices}")
                print(f"  remote outputs: {app.sync.remote_output_devices}")

        else:
            print(f"  unknown command: {cmd}")