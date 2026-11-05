#!/usr/bin/env python3

import pexpect
import platform
import socket
import json
import re
from pprint import pprint


def get_interface_data(interface_name):
    try:
        # Spawn a child process to run `ifconfig` for the given interface
        child = pexpect.spawn("ifconfig {}".format(interface_name))
        child.expect([pexpect.EOF, pexpect.TIMEOUT])
        output_bytes = child.before.decode('utf-8')

        # Extract MTU using regex
        mtu_match = re.search(r'\bMTU:(\d+)', output_bytes)
        mtu = mtu_match.group(1) if mtu_match else "unknown"

        # Extract IPv4 address using regex
        ipv4_match = re.search(r'inet\s+addr:(\d+\.\d+\.\d+\.\d+)|inet\s+(\d+\.\d+\.\d+\.\d+)', output_bytes)
        ipv4 = ipv4_match.group(1) if ipv4_match else "unknown"

        # Extract MAC address using regex
        mac_match = re.search(r'HWaddr\s+([0-9a-fA-F:]{17})', output_bytes)
        mac = mac_match.group(1) if mac_match else "unknown"

        return {
            "interface": interface_name,
            "MTU": mtu,
            "IPv4": ipv4,
            "MAC": mac,
        }
    except Exception as e:
        print("Error retrieving data for {}: {}".format(interface_name, e))
        return {
            "interface": interface_name,
            "MTU": "unknown",
            "IPv4": "unknown",
            "MAC": "unknown",
        }


def main():
    # Task 1: Retrieve and display the hostname
    hostname = socket.gethostname()
    print("Host's name is: {}".format(hostname))

    # Task 2: Retrieve and display the OS platform
    system_platform = platform.platform()
    print("You are on the platform: {}".format(system_platform))

    # Task 3: Retrieve data for all network interfaces
    # Dynamically retrieve interface names
    interfaces = [iface[1] for iface in socket.if_nameindex()]
    print("Interfaces detected: {}".format(interfaces))

    # Collect interface data for each interface
    interface_data = [get_interface_data(interface) for interface in interfaces]

    # Task 4: Save the data in a dictionary
    system_data = {
        "Hostname": hostname,
        "Platform": system_platform,
        "Interfaces": interface_data,
    }

    # Task 5: Display the dictionary using pprint for user-friendliness
    print("\nSystem Data:")
    pprint(system_data)

    # Task 6: Write the dictionary to a JSON file
    with open("interface.json", "w") as fout:
        json.dump(system_data, fout, indent=4)
    print("\nInterface data has been saved to 'interface.json'")


if __name__ == "__main__":
    main()

