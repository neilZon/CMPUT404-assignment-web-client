#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust, Neilzon Viloria
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
from urllib.parse import urlparse, urlencode

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    def __init__(self):
        self.socket = None

    def build_post_body_args(self, args):
        return urlencode(args)

    def get_host_port(self, url):
        parsed_url = urlparse(url)
        port = 0

        if parsed_url.port is not None:
            port = parsed_url.port
        elif parsed_url.scheme == "https": 
            port = 443
        elif parsed_url.scheme == "http":
            port = 80

        return parsed_url.hostname, port, parsed_url.netloc

    def get_path(self, url):
        parsed_url = urlparse(url)
        if (parsed_url.path is None) or (len(parsed_url.path) == 0):
            return '/'
        return parsed_url.path

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, response_line):
        return int(response_line.split(" ")[1])

    def get_headers(self, data):
        header_break_idx = data.index("")
        return data[1:header_break_idx]

    def get_body(self, data):
        header_break_idx = data.index("")
        body_lines = data[header_break_idx+1:]
        return "".join(body_lines)
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        host, port, netloc = self.get_host_port(url)
        path = self.get_path(url)

        print("sdjflksd", path, url)

        self.connect(host, port)

        self.sendall(
            f"GET {path} HTTP/1.1\r\n" +
            f"Host: {netloc}\r\n" +
            "User-Agent: Mozilla/5.0\r\n" +
            "Accept-Charset: UTF-8\r\n" +
            "Accept: */*\r\n" +
            "Connection: close\r\n\r\n"
            )

        response = self.recvall(self.socket)

        response_lines = response.split("\r\n")

        code = self.get_code(response)
        headers = self.get_headers(response_lines)
        body = self.get_body(response_lines)

        print(body)
        self.close()
        return HTTPResponse(code, body)
    
    def build_post_header_string(self, data):
        return f"Content-Length: {len(data)}\r\nContent-Type: application/x-www-form-urlencoded"                

    def POST(self, url, args=None):
        host, port, netloc = self.get_host_port(url)
        path = self.get_path(url)

        post_body=""
        if args:
            post_body = self.build_post_body_args(args)
        
        self.connect(host, port)

        req_headers = self.build_post_header_string(post_body)

        self.sendall(
            f"POST {path} HTTP/1.1\r\n" +
            "Host: {netloc}\r\n" + 
            "User-Agent: Mozilla/5.0\r\n" + 
            "Accept-Charset: UTF-8\r\n" +
            "Accept: */*\r\n" +
            "Connection: close\r\n" +
            f"{req_headers}\r\n" +
            "\r\n" + 
            f"{post_body}"
            )

        response = self.recvall(self.socket)

        response_lines = response.split("\r\n")

        code = self.get_code(response)
        headers = self.get_headers(response_lines)
        body = self.get_body(response_lines)

        self.close()
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
