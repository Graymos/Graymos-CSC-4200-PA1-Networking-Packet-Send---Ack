# Author: Grayson Mosley
# Date: 9/15/2024
# Description: This program creates a server that listens for incoming connections and receives packets from clients. 
# The server unpacks the received packets and echoes back the packet fields to the client. 
# The server uses the create_packet and unpack_packet functions to create and unpack packets, respectively.

import socket
import struct

"""
create_packet(version, header_length, service_type, payload): Creates a packet by encoding the payload based on the service type and combining it with a fixed-length header.
    - version (int): The version of the protocol.
    - header_length (int): The length of the header in bytes.
    - service_type (int): The type of service.
    - payload (str): The payload to be encoded and included in the packet.
    - Returns: The created packet (delimited by '|').
"""
def create_packet(version, header_length, service_type, payload):
    # Encode the payload based on the service type
    payload_length = len(payload)
    if service_type == 1:
        payload = struct.pack('!h', int(payload))  # 2-byte int
    elif service_type == 2:
        payload = struct.pack('!e', float(payload))  # 2-byte float 
    elif service_type == 3:
        payload = payload.encode()  # string
    else:
        raise ValueError("Unsupported service type")

    # Create the fixed-length header
    header = struct.pack('!BBBB', version, header_length, service_type, payload_length)

    # Combine header and payload into a single packet
    packet = header + payload
    return packet

"""
unpack_packet(conn, header_format): Unpacks a received packet by extracting the header and payload.
    - conn (socket): The socket connection to receive the packet from.
    - header_format (str): The format string specifying the structure of the header.
    - Returns: A string representation of the unpacked packet header and payload.
"""

def unpack_packet(conn, header_format):
    # Receive the fixed-length header
    header_size = struct.calcsize(header_format)
    header_data = conn.recv(header_size)
    
    if not header_data:
        return None
    
    # Unpack the header
    version, header_length, service_type, payload_length = struct.unpack(header_format, header_data)
    # Receive the payload based on the payload length
    payload_data = conn.recv(payload_length)
    payload = payload_data.decode('utf-8')
    ##print("payload coming back: ", payload)

    
    # Create a string from the header fields and payload
    packet_header_as_string = f"{version}| {header_length}| {service_type}| {payload_length}| {payload}"
    
    return packet_header_as_string

if __name__ == '__main__':
    host = 'localhost'
    port = 12345

    # Fixed length header -> Version (1 byte), Header Length (1 byte), Service Type (1 byte), Payload Length (2 bytes)
    header_format = 'BBBB'  # 1 byte for version, header length, service type; 2 bytes for payload length
while True:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        conn, addr = s.accept()
        with conn:
            print(f"Connected by: {addr}")
            while True:
                try:
                    # Receive and unpack packet using the unpack_packet function
                    payload_string = unpack_packet(conn, header_format)
                    if payload_string:
                        # Echo back the packet fields
                        packet_fields = payload_string.split('|')
                        version = packet_fields[0]
                        header_length = packet_fields[1]
                        service_type = packet_fields[2]
                        payload_length = packet_fields[3]
                        payload = packet_fields[4]
                        payload_string = payload_string.encode('utf-8')
                        print(f"Received packet headers - Version: {version}, Header Length: {header_length}, Service Type: {service_type}, Payload Length: {payload_length}")
                        print(f"Received packet payload: {payload}")
                        send_packet = create_packet(int(version), int(header_length), int(service_type), payload)
                        conn.sendall(send_packet)
                    else:
                        break
                except Exception as e:
                    print(f"Connection closed or an error occurred: {e}")
                    break