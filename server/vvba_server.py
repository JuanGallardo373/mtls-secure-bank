#!/usr/bin/env python3

# 🏦 VVBA Bank - Servidor mTLS Central
# Simula un banco central que se comunica de forma segura con billeteras virtuales

import socket
import ssl
import threading
import time
from datetime import datetime
from pathlib import Path
import sys
import os

# Agregar el directorio server al path para importar módulos locales
sys.path.insert(0, str(Path(__file__).parent))

from config import (
    SERVER_HOST, SERVER_PORT, SOCKET_TIMEOUT, SOCKET_BACKLOG,
    TLS_VERSION, SERVER_CERT, SERVER_KEY, CA_CERT,
    REQUIRE_CLIENT_CERT, Colors, CLIENTS_CERTS, validate_certificates
)
from tls_logger import tls_logger


class VVBAServer:
    """Servidor mTLS del Banco VVBA"""

    def __init__(self, host=SERVER_HOST, port=SERVER_PORT):
        """
        Inicializa el servidor mTLS.
        
        Args:
            host: Host donde escuchar
            port: Puerto donde escuchar
        """
        self.host = host
        self.port = port
        self.server_socket = None
        self.running = False
        self.client_count = 0
        self.lock = threading.Lock()
        
        print(Colors.info("🏦 VVBA Bank - Servidor mTLS"))
        print("=" * 60)
        print(f"Host: {self.host}")
        print(f"Puerto: {self.port}")
        print(f"mTLS: Activado (Cliente y Servidor se validan mutuamente)")
        print("=" * 60)

    def setup_tls(self):
        """Configura el contexto SSL/TLS para mTLS"""
        
        # Crear contexto SSL/TLS
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        
        # Cargar certificado del servidor
        context.load_cert_chain(
            certfile=str(SERVER_CERT),
            keyfile=str(SERVER_KEY),
            password=None
        )
        
        # Cargar certificado de la CA para validar clientes
        context.load_verify_locations(cafile=str(CA_CERT))
        
        # Configurar validación de certificados de clientes
        context.verify_mode = ssl.CERT_REQUIRED
        
        # Configurar versión mínima de TLS
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        
        # Configurar cifrados seguros
        context.set_ciphers("HIGH:!aNULL:!MD5")
        
        return context

    def get_certificate_info(self, cert_dict):
        """Extrae información legible del certificado."""
        try:
            subject = dict(x[0] for x in cert_dict['subject'])
            issuer = dict(x[0] for x in cert_dict['issuer'])
            
            return {
                'cn': subject.get('commonName', 'Unknown'),
                'org': subject.get('organizationName', 'Unknown'),
                'issuer_cn': issuer.get('commonName', 'Unknown'),
                'serial': cert_dict.get('serialNumber', 'Unknown'),
                'version': cert_dict.get('version', 'Unknown'),
            }
        except Exception as e:
            return {'error': str(e)}

    def identify_client(self, cert_info):
        """Identifica qué cliente se conectó basándose en el certificado."""
        cn = cert_info.get('cn', '')
        
        for client_id, client_data in CLIENTS_CERTS.items():
            if client_data['name'] in cn or cn in client_data['name']:
                return client_id, client_data['name'], client_data['trusted']
        
        return None, cn, False

    def handle_client(self, ssl_socket, client_address, start_time):
        """
        Maneja la conexión de un cliente.
        
        Args:
            ssl_socket: Socket SSL establecido
            client_address: Tupla (IP, Puerto) del cliente
            start_time: Tiempo de inicio del handshake
        """
        client_ip, client_port = client_address
        handshake_time_ms = (time.time() - start_time) * 1000
        
        try:
            # Obtener certificado del cliente
            cert_dict = ssl_socket.getpeercert()
            cert_info = self.get_certificate_info(cert_dict)
            client_id, client_name, is_trusted = self.identify_client(cert_info)
            
            # Log de conexión exitosa
            tls_logger.log_connection_success(
                client_ip=client_ip,
                client_port=client_port,
                cert_subject=cert_info.get('cn', 'Unknown'),
                cert_issuer=cert_info.get('issuer_cn', 'Unknown'),
                serial_number=cert_info.get('serial', 'Unknown'),
                version=cert_info.get('version', 'Unknown'),
                handshake_time_ms=handshake_time_ms,
                client_id=client_id,
                trusted=is_trusted
            )
            
            # Imprimir en consola
            status = Colors.success if is_trusted else Colors.warning
            print(status(f"✓ [{client_name}] {client_ip}:{client_port} - {handshake_time_ms:.2f}ms"))
            
            # Recibir datos del cliente
            data = ssl_socket.recv(1024)
            if data:
                message = data.decode('utf-8', errors='ignore')
                print(Colors.info(f"  Mensaje: {message[:100]}"))
                
                # Responder al cliente
                response = f"VVBA Bank: Mensaje recibido ({len(message)} bytes)"
                ssl_socket.send(response.encode('utf-8'))
            
        except ssl.SSLError as e:
            # Error SSL - Certificado inválido
            error_msg = str(e)
            
            tls_logger.log_connection_rejected(
                client_ip=client_ip,
                client_port=client_port,
                reason=error_msg,
                cert_subject=None
            )
            
            print(Colors.error(f"✗ [{client_ip}:{client_port}] SSL Error: {error_msg}"))
            
        except Exception as e:
            # Otros errores
            error_msg = str(e)
            
            tls_logger.log_connection_failed(
                client_ip=client_ip,
                client_port=client_port,
                error_message=error_msg,
                is_anomaly=True,
                anomaly_type="connection_error"
            )
            
            print(Colors.error(f"✗ [{client_ip}:{client_port}] Error: {error_msg}"))
            
        finally:
            try:
                ssl_socket.close()
            except:
                pass
            
            with self.lock:
                self.client_count -= 1

    def start(self):
        """Inicia el servidor mTLS."""
        
        try:
            # Validar certificados
            validate_certificates()
            
            # Configurar TLS
            context = self.setup_tls()
            
            # Crear socket
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(SOCKET_BACKLOG)
            
            self.running = True
            
            print(Colors.success(f"✓ Servidor iniciado en {self.host}:{self.port}"))
            print(Colors.info("  Escuchando conexiones mTLS..."))
            print("=" * 60)
            print()
            
            # Aceptar conexiones
            while self.running:
                try:
                    # Aceptar conexión cliente
                    sock, addr = self.server_socket.accept()
                    start_time = time.time()
                    
                    with self.lock:
                        self.client_count += 1
                    
                    # Envolver con SSL/TLS
                    try:
                        ssl_socket = context.wrap_socket(
                            sock,
                            server_side=True
                        )
                        
                        # Manejar cliente en thread
                        client_thread = threading.Thread(
                            target=self.handle_client,
                            args=(ssl_socket, addr, start_time),
                            daemon=True
                        )
                        client_thread.start()
                        
                    except ssl.SSLError as e:
                        # Error en handshake TLS
                        client_ip, client_port = addr
                        
                        tls_logger.log_connection_rejected(
                            client_ip=client_ip,
                            client_port=client_port,
                            reason=f"TLS Handshake Failed: {str(e)}"
                        )
                        
                        print(Colors.error(f"✗ [{client_ip}:{client_port}] Handshake TLS fallido"))
                        sock.close()
                        
                        with self.lock:
                            self.client_count -= 1
                
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    print(Colors.error(f"Error aceptando conexión: {e}"))
                    continue
                    
        except FileNotFoundError as e:
            print(Colors.error(f"Error: Certificados no encontrados"))
            print(f"  {e}")
            print(Colors.info("Ejecuta: bash certs/generate-*.sh"))
            sys.exit(1)
            
        except Exception as e:
            print(Colors.error(f"Error iniciando servidor: {e}"))
            sys.exit(1)
            
        finally:
            self.stop()

    def stop(self):
        """Detiene el servidor."""
        self.running = False
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        
        print()
        print("=" * 60)
        print(Colors.info("🛑 Servidor detenido"))
        
        # Imprimir resumen de logs
        tls_logger.print_summary()


def main():
    """Función principal."""
    server = VVBAServer(host=SERVER_HOST, port=SERVER_PORT)
    
    try:
        server.start()
    except KeyboardInterrupt:
        print()
        print(Colors.warning("Deteniendo servidor..."))
        server.stop()


if __name__ == "__main__":
    main()
