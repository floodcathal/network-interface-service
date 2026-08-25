#!/usr/bin/env python3
"""TCP server that reports the host's network interface configuration.

Listens on a port, and on each client connection gathers the hostname,
platform string and per-interface details (MTU, IPv4 address, MAC address)
by shelling out to ifconfig, then sends the result back as JSON.
"""

import json
import platform
import re
import socket
from pprint import pprint

import pexpect

HOST = "0.0.0.0"
PORT = 6794


def get_interface_data(interface_name):
    """Return MTU, IPv4 and MAC for one interface by parsing ifconfig output."""
    try:
        # Spawn a child process to run ifconfig against this interface
        child = pexpect.spawn("ifconfig {}".format(interface_name))
        # Read until the process ends (or times out)
        child.expect([pexpect.EOF, pexpect.TIMEOUT])
        # Everything the child printed, as a decoded string
        output = child.before.decode("utf-8")

        # Extract the MTU value
        mtu_match = re.search(r"\bMTU:(\d+)", output)
        mtu = mtu_match.group(1) if mtu_match else "unknown"

        # Extract the IPv4 address
        ip_match = re.search(r"inet\s+addr:(\d+\.\d+\.\d+\.\d+)", output)
        ip_address = ip_match.group(1) if ip_match else "unknown"

        # Extract the MAC address
        mac_match = re.search(r"HWaddr\s+([0-9a-fA-F:]+)", output)
        mac_address = mac_match.group(1) if mac_match else "unknown"

        return {
            "interface": interface_name,
            "MTU": mtu,
            "ip address": ip_address,
            "mac address": mac_address,
        }

    # If anything above fails, report the interface with unknown values
    # rather than taking the whole server down.
    except Exception as e:
        print("Error retrieving data for {}: {}".format(interface_name, e))
        return {
            "interface": interface_name,
            "MTU": "unknown",
            "ip address": "unknown",
            "mac address": "unknown",
        }


def get_sys_data():
    """Collect hostname, platform and data for every interface on the host."""
    hostname = socket.gethostname()
    system_platform = platform.platform()
    # if_nameindex() returns (index, name) tuples - we only want the names
    interfaces = [iface[1] for iface in socket.if_nameindex()]
    interface_data = [get_interface_data(interface) for interface in interfaces]

    return {
        "hostname": hostname,
        "Platform": system_platform,
        "interfaces": interface_data,
    }


def start_server():
    """Accept client connections and send each one the system data as JSON."""
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind((HOST, PORT))
    server_sock.listen(1)

    print("Server is listening on {}:{}".format(HOST, PORT))

    while True:
        connect_sock, addr = server_sock.accept()
        print("Connection established with {}".format(addr))
        try:
            data = get_sys_data()
            pprint("System Data Collected: {}".format(data))
            # Serialise to JSON, encode to bytes, and send the lot
            connect_sock.sendall(json.dumps(data).encode("utf-8"))
        except Exception as e:
            print("Error during client communication: {}".format(e))
        finally:
            connect_sock.close()


if __name__ == "__main__":
    start_server()
