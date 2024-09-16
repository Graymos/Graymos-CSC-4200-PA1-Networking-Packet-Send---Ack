# Author: Grayson Mosley
# Date: 9/15/2024
# Description: Client for packet creation and sending. 
# Have --version, --header_length, --service_type, --payload, --host, and --port as arguments for the client.

import argparse
import socket
import struct

"""
Creates a packet by encoding the payload based on the service type and combining it with a fixed-length header.
Parameters:
    - version (int): The version of the packet.
    - header_length (int): The length of the header.
    - service_type (int): The type of service.
    - payload (int, float, or str): The payload to be encoded.
    - Returns:
        bytes: The packet containing the header and encoded payload.
"""
def create_packet(version, header_length, service_type, payload):
     
    payload = " " + payload # fix for payload cutting off the first character when sent
    payload_length = len(payload) # Calculate payload length
    
    # Encode the payload based on the service type
    if service_type == 1:
        payload = struct.pack('!Q', int(payload))  # 8-byte int
    elif service_type == 2:
        payload = struct.pack('!d', float(payload))  # 8-byte float 
    elif service_type == 3:
        payload = payload.encode()  # string
    else:
        raise ValueError("Unsupported service type")

    # Create the fixed-length header
    header = struct.pack('!BBBH', version, header_length, service_type, payload_length)

    # Combine header and payload into a single packet
    packet = header + payload
    return packet


"""
Extracts the header and payload from the received data.
    - Args:
        data (bytes): The data received.
    - Returns:
       None
    - Prints:
       The version, header length, service type, and payload length of the received packet.
       The payload data.
"""

def handle_packet(data):
    # Rest of the code...
    # Extract header and payload from the received data
    header_format = '!BBBH'
    header_size = struct.calcsize(header_format)
    header_data = data[:header_size]
    payload_data = data[header_size:]

    version, header_length, service_type, payload_length = struct.unpack(header_format, header_data)
    payload = payload_data.decode('utf-8')

    print(f"Received packet headers - Version: {version}, Header Length: {header_length}, Service Type: {service_type}, Payload Length: {payload_length}")
    print(f"Received packet payload - {payload}")
    return version, header_length, service_type, payload_length, payload

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Client for packet creation and sending.")
    parser.add_argument('--version', type=int, required=True, help='Packet version')
    parser.add_argument('--header_length', type=int, required=True, help='Length of the packet header')
    parser.add_argument('--service_type', type=int, required=True, help='Service type of the payload (1 for int, 2 for float, 3 for string)')
    parser.add_argument('--payload', type=str, required=True, help='Payload to be packed into the packet')
    parser.add_argument('--host', type=str, default='localhost', help='Server host')
    parser.add_argument('--port', type=int, default=12345, help='Server port')

    args = parser.parse_args()

    # Create and send packet using the create_packet function
    packet = create_packet(args.version, args.header_length, args.service_type, args.payload)

    # Connect to the server
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
           s.connect((args.host, args.port)) # make connection to server

           s.sendall(packet) # Send the packet
        except Exception as e:
            print(f"Connection closed or an error occurred: {e}")
            exit(1)

        # Receive the response from the server
        response = s.recv(1024)
        version, header_length, service_type, payload_length, payload = handle_packet(response)
        if version == args.version and header_length == args.header_length and service_type == args.service_type and payload[1:] == args.payload:
            print("Packet sent successfully (ACK)")