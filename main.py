import socket
import base64
import struct
import threading
from urllib.parse import urlparse
import requests

class SimpleDNSTunnel:
    def __init__(self):
        self.clients = {}
        
    def extract_data(self, dns_query):
        """Extrae datos de consultas DNS tunnelizadas"""
        try:
            if len(dns_query) < 12: return None
            
            query_data = dns_query[12:]
            domain_parts = []
            pos = 0
            
            while pos < len(query_data) and query_data[pos] != 0:
                length = query_data[pos]
                pos += 1
                if pos + length > len(query_data): break
                part = query_data[pos:pos+length].decode('latin-1')
                domain_parts.append(part)
                pos += length
            
            full_domain = ".".join(domain_parts)
            
            # Buscar nuestros dominios tunnel
            if "amnupower.com" in full_domain or "apnaghost.xyz" in full_domain:
                data_part = full_domain.split('.')[0]
                try:
                    padded = data_part.upper() + '=' * (8 - len(data_part) % 8)
                    decoded = base64.b32decode(padded)
                    return decoded, full_domain
                except: pass
                    
            return None, full_domain
            
        except Exception as e:
            print(f"Error: {e}")
            return None, ""
    
    def process_request(self, http_data):
        """Procesa petición HTTP real"""
        try:
            # Parsear y ejecutar petición real
            request_text = http_data.decode('latin-1', errors='ignore')
            lines = request_text.split('\r\n')
            
            if not lines: return b"HTTP/1.1 400 Bad Request\r\n\r\n"
            
            method, path, version = lines[0].split(' ')
            headers = {}
            host = None
            
            for line in lines[1:]:
                if ': ' in line:
                    key, value = line.split(': ', 1)
                    headers[key] = value
                    if key.lower() == 'host': host = value
            
            if not host: return b"HTTP/1.1 400 No Host\r\n\r\n"
            
            # Construir URL y hacer petición real
            url = f"http://{host}{path}" if not path.startswith('http') else path
            
            print(f"🌐 REQUEST: {method} {url}")
            
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                data=http_data.split(b'\r\n\r\n', 1)[1] if b'\r\n\r\n' in http_data else None,
                timeout=30,
                verify=False
            )
            
            # Construir respuesta
            http_response = f"HTTP/1.1 {response.status_code} {response.reason}\r\n".encode()
            for key, value in response.headers.items():
                if key.lower() not in ['transfer-encoding', 'connection']:
                    http_response += f"{key}: {value}\r\n".encode()
            http_response += b"\r\n" + response.content
            
            print(f"✅ RESPONSE: {response.status_code} - {len(response.content)} bytes")
            return http_response
            
        except Exception as e:
            print(f"❌ ERROR: {e}")
            return f"HTTP/1.1 500 Error\r\n\r\n{e}".encode()
    
    def create_dns_response(self, original_query, response_data):
        """Crea respuesta DNS"""
        transaction_id = original_query[0:2]
        flags = struct.pack(">H", 0x8180)
        counts = struct.pack(">HHHH", 1, 1, 0, 0)
        header = transaction_id + flags + counts
        question = original_query[12:]
        
        answer = b""
        if response_data:
            answer += b"\xc0\x0c"
            answer += struct.pack(">HHIH", 16, 1, 60, len(response_data))
            answer += response_data
        else:
            answer += b"\xc0\x0c"
            answer += struct.pack(">HHIH", 16, 1, 60, 0)
        
        return header + question + answer
    
    def handle_query(self, data, addr, sock):
        try:
            tunnel_data, domain = self.extract_data(data)
            
            if tunnel_data:
                print(f"🔓 TUNNEL DATA: {len(tunnel_data)} bytes from {addr[0]}")
                http_response = self.process_request(tunnel_data)
                
                # Limitar tamaño para DNS
                if len(http_response) > 400:
                    http_response = http_response[:400] + b"...[truncated]"
                
                dns_response = self.create_dns_response(data, http_response)
                sock.sendto(dns_response, addr)
                print(f"📤 SENT: {len(dns_response)} bytes")
                
            else:
                print(f"📡 Normal DNS: {domain}")
                normal_response = self.create_dns_response(data, b"OK")
                sock.sendto(normal_response, addr)
                
        except Exception as e:
            print(f"❌ Handle error: {e}")
    
    def start(self, port=5353):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('0.0.0.0', port))
        
        print(f"🚀 DNS Tunnel Server on port {port}")
        print("💡 Clients can send HTTP traffic hidden in DNS")
        
        while True:
            data, addr = sock.recvfrom(512)
            threading.Thread(target=self.handle_query, args=(data, addr, sock)).start()

if __name__ == "__main__":
    server = SimpleDNSTunnel()
    server.start(5353)
