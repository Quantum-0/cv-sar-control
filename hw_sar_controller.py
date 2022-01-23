#!/usr/bin/env python3

# Copyright (c) Quantum0 2022

# ===== CONFIG =====

YES_AXIS = 'Y'
NO_AXIS = 'X'
PORT = 18782
PRINT_RECEIVED_AXIS = False

# ==================

import json
import select
from time import sleep
from sar_adapter import SARCommand, execute_in_sar
from socket import socket, AF_INET, SOCK_DGRAM


def main():
    sock = socket(AF_INET, SOCK_DGRAM)
    sock.bind(('', PORT))

    while True:
        # Check if data was received
        r, _, _ = select.select([sock], [], [], 0)
        if sock not in r:
            sleep(0.1)
            continue

        # Process data
        packet = sock.recvfrom(4096)
        data = json.loads(packet[0].decode())
        if data.get('action') != 'shake':
            continue

        if PRINT_RECEIVED_AXIS:
            print(data.get('axis'))

        axis = data.get('axis')
        if axis == YES_AXIS:
            execute_in_sar(SARCommand.Yes)
        else:
            execute_in_sar(SARCommand.No)


if __name__ == '__main__':
    main()
