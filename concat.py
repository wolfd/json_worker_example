from io import StringIO
import json
import select
import os
import sys
import traceback

# This is a pretty cumbersome way of getting work requests.
# It waits for something to be available on stdin, and then tries parsing
# whatever text is available as JSON. It keeps accumulating more text until a
# full work request is available.
def wait_for_stdin_json():
    stdin = open("/dev/stdin", "rb")
    os.set_blocking(stdin.fileno(), False)
    stream_bytes = b""
    while True:
        _, _, _ = select.select([stdin.fileno()], [], [])
        maybe_bytes = stdin.read()
        if maybe_bytes is None:
            continue
        stream_bytes += maybe_bytes
        try:
            work_request = json.loads(stream_bytes)
        except json.decoder.JSONDecodeError:
            # stream couldn't decode, wait until next select
            sys.stderr.write(f"failed to decode: {stream_bytes.decode('utf-8')}\n")
            sys.stderr.flush()
            continue

        yield work_request
        stream_bytes = b""  # reset


def concat(input_paths, out_path):
    with open(out_path, "wb") as out_f:
        for input_path in input_paths:
            with open(input_path, "rb") as input_f:
                out_f.write(input_f.read())


if __name__ == "__main__":
    # parse work requests from stdin
    for work_request in wait_for_stdin_json():
        response = {
            "exitCode": 1,
            "output": "",
        }

        try:
            out_path = work_request["arguments"][0]
            input_paths = work_request["arguments"][1:]
            concat(input_paths, out_path)

            response["exitCode"] = 0

        except Exception:
            output = StringIO()
            traceback.print_exc(file=output)
            response["exitCode"] = 1
            response["output"] = output.getvalue()

        os.write(1, json.dumps(response).encode("utf-8"))
