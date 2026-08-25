<h1 align="center">Network Interface Reporting Service</h1>

<p align="center">
  A TCP client/server pair that collects a Linux host's network interface<br>
  configuration and returns it as structured JSON.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3-3776AB?logo=python&logoColor=white" alt="Python 3">
  <img src="https://img.shields.io/badge/sockets-AF__INET%20%2F%20SOCK__STREAM-4B8BBE" alt="Sockets">
  <img src="https://img.shields.io/badge/pexpect-process%20control-8F0000" alt="pexpect">
  <img src="https://img.shields.io/badge/verified-Wireshark-1679A7?logo=wireshark&logoColor=white" alt="Wireshark">
</p>

<p align="center">
  <img src="docs/tcp-flow.png" alt="Wireshark flow graph of a full client-server exchange" width="760">
</p>

<p align="center">
  <sub>A complete exchange captured in Wireshark — three-way handshake, a single 415-byte
  push of JSON, then a clean four-way teardown.</sub>
</p>

---

**Programming for Networks — BSc (Hons) Cloud Computing, TU Dublin.**
Cathal Flood

---

## What it does

The server listens on a TCP port. When a client connects, it enumerates every network
interface on the host, shells out to `ifconfig` for each one, parses the output for the
values that matter, and sends the whole lot back as a single JSON document before closing
the connection.

The point of the exercise was to work at the socket layer directly — no HTTP library, no
framework — and to be able to prove what went over the wire.

- **Interface discovery** — `socket.if_nameindex()` enumerates interfaces at runtime, so
  the server adapts to whatever host it runs on rather than using a hardcoded list.
- **Structured extraction** — regular expressions pull MTU, IPv4 address and MAC address
  out of unstructured `ifconfig` text.
- **Fault isolation** — an interface that fails to parse returns `"unknown"` for its
  fields instead of taking down the response for every other interface.
- **JSON over raw sockets** — the payload is serialised, encoded and sent with
  `sendall()`, so a partial write can't silently truncate the response.

## How it works

<p align="center">
  <img src="docs/server-block.png" alt="Server block diagram" height="420">
  &nbsp;&nbsp;&nbsp;&nbsp;
  <img src="docs/client-block.png" alt="Client block diagram" height="420">
</p>

<p align="center"><sub>Server (left) and client (right).</sub></p>

The server holds the connection open only as long as it takes to gather and send the data,
then closes it — visible in the capture above as the `FIN, ACK` immediately following the
415-byte `PSH, ACK`. Detailed flowcharts for each side are in [`docs/`](docs/).

## Running it

The server needs `pexpect`, and expects `ifconfig` to be available:

```bash
pip install -r requirements.txt
```

Start the server on the machine you want to inspect — it binds to `0.0.0.0:6794`:

```bash
python3 server.py
```

Then query it from anywhere that can reach that port:

```bash
python3 client.py --ip 10.156.5.146 --port 6794
```

## Example output

```json
{
    "hostname": "cathal-VirtualBox",
    "Platform": "Linux-4.4.0-142-generic-x86_64-with-Ubuntu-14.04-trusty",
    "interfaces": [
        { "interface": "lo",   "MTU": "65536", "ip address": "127.0.0.1",     "mac address": "unknown" },
        { "interface": "eth0", "MTU": "1500",  "ip address": "10.0.2.15",     "mac address": "unknown" },
        { "interface": "eth1", "MTU": "1500",  "ip address": "192.168.0.235", "mac address": "unknown" }
    ]
}
```

[`examples/interface.json`](examples/interface.json) holds a response captured from the
running server on the lab VM. It predates the current key names — that iteration emitted
`Hostname` / `IPv4` / `MAC` where the code above emits `hostname` / `ip address` /
`mac address` — but the values are genuine, and it shows the MAC regex falling through to
`unknown` on the virtual adapters.

## A note on `ifconfig` output

The parsing targets the **legacy net-tools format**, where `ifconfig` prints
`inet addr:10.0.2.15` and `HWaddr 08:00:27:...`. That is what shipped on the Ubuntu 14.04
lab image this was written against.

Modern distributions print `inet 10.0.2.15` with no `addr:` prefix, and report the MAC as
`ether` rather than `HWaddr` — so on a current system the IPv4 and MAC regexes fall through
to `"unknown"` while MTU still matches. Supporting both would mean widening the patterns to
accept either spelling; `iproute2` or `psutil` would be the better foundation for anything
beyond this exercise.

## Repository layout

```
server.py               TCP server - interface discovery, parsing, JSON response
client.py               CLI client - argparse, connect, receive, pretty-print
requirements.txt        pexpect
examples/
  interface.json        A captured server response
docs/
  server-block.png      Server block diagram
  client-block.png      Client block diagram
  server-flow.png       Server flowchart
  client-flow.png       Client flowchart
  tcp-flow.png          Wireshark flow graph of a full exchange
```
