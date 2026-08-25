#!/usr/bin/env python3
"""TCP client that requests interface data from the server and prints it.

Takes the server IP and port on the command line, opens a connection,
reads the JSON payload the server sends, and pretty-prints it.
"""

import argparse
import json
import socket
from pprint import pprint

BUFFER_SIZE = 4096


def main():
    parser = argparse.ArgumentParser(
        description="Fetch network interface data from an ifinfo server."
    )
    parser.add_argument("--ip", help="Server IP address", required=True)
    parser.add_argument("--port", help="Server port number", type=int, required=True)
    args = parser.parse_args()

    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_sock.connect((args.ip, args.port))
    print("Connected to server at {}:{}".format(args.ip, args.port))

    try:
        data = client_sock.recv(BUFFER_SIZE)
        if data:
            # Decode the bytes and parse the JSON into a dict
            received_data = json.loads(data.decode("utf-8"))
            print("Data received from server")
            pprint(received_data)
        else:
            print("No data received from server")
    except Exception as e:
        print("Error receiving data: {}".format(e))
    finally:
        # Always close the socket, whether or not the read succeeded
        client_sock.close()


if __name__ == "__main__":
    main()
