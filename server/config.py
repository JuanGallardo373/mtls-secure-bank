# 🔧 Configuración Central del Proyecto

import os
from pathlib import Path
from typing import Dict, List

# ═══════════════════════════════════════════════════════════════
# 📁 RUTAS DEL PROYECTO
# ═══════════════════════════════════════════════════════════════

PROJECT_ROOT = Path(__file__).parent.parent
CERTS_DIR = PROJECT_ROOT / "certs"
LOGS_DIR = PROJECT_ROOT / "logs"
SERVER_DIR = PROJECT_ROOT / "server"

# Crear directorios si no existen
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# ═══════════════════════════════════════════════════════════════
# 🔐 CERTIFICADOS Y CLAVES
# ═══════════════════════════════════════════════════════════════

# Autoridad de Certificación
CA_CERT = CERTS_DIR / "ca-cert.pem"
CA_KEY = CERTS_DIR / "ca-key.pem"

# Servidor (VVBA Bank)
SERVER_CERT = CERTS_DIR / "server-cert.pem"
SERVER_KEY = CERTS_DIR / "server-key.pem"

# Clientes legítimos (billeteras virtuales)
CLIENTS_CERTS = {
    "mercado-pago": {
        "name": "Mercado Pago",
        "cert": CERTS_DIR / "mercado-pago-cert.pem",
        "key": CERTS_DIR / "mercado-pago-key.pem",
        "trusted": True,
    },
    "uala-wallet": {
        "name": "Ualá Wallet",
        "cert": CERTS_DIR / "uala-wallet-cert.pem",
        "key": CERTS_DIR / "uala-wallet-key.pem",
        "trusted": True,
    },
    "brubank": {
        "name": "BruBank",
        "cert": CERTS_DIR / "brubank-cert.pem",
        "key": CERTS_DIR / "brubank-key.pem",
        "trusted": True,
    },
    "naranja-x": {
        "name": "Naranja X",
        "cert": CERTS_DIR / "naranja-x-cert.pem",
        "key": CERTS_DIR / "naranja-x-key.pem",
        "trusted": True,
    },
}

# ═══════════════════════════════════════════════════════════════
# 🖥️  CONFIGURACIÓN DEL SERVIDOR
# ═══════════════════════════════════════════════════════════════

# Dirección de escucha
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8443

# Configuración de socket
SOCKET_TIMEOUT = 30  # segundos
SOCKET_BACKLOG = 5  # conexiones pendientes

# Configuración TLS/SSL
TLS_VERSION = "TLSv1.2"  # Mínimo TLS 1.2
CIPHER_SUITE = (
    "HIGH:!aNULL:!MD5"  # Solo cifrados seguros
)

# Verificación de certificados de clientes
REQUIRE_CLIENT_CERT = True
VERIFY_MODE = "CERT_REQUIRED"  # Requiere certificado del cliente

# ═══════════════════════════════════════════════════════════════
# 📊 LOGGING Y LOGS
# ═══════════════════════════════════════════════════════════════

# Archivo de logs
TLS_HANDSHAKE_LOG = LOGS_DIR / "tls_handshakes.log"
SERVER_LOG = LOGS_DIR / "server.log"
ANALYSIS_LOG = LOGS_DIR / "analysis.log"

# Configuración de logging
LOG_FORMAT_JSON = True  # Usar JSON Lines (JSONL)
LOG_LEVEL = "INFO"
LOG_MAX_SIZE = 10 * 1024 * 1024  # 10 MB

# ═══════════════════════════════════════════════════════════════
# 🚨 DETECCIÓN DE ANOMALÍAS
# ═══════════════════════════════════════════════════════════════

# Umbrales de anomalías
ANOMALY_THRESHOLDS = {
    "failed_attempts": 5,  # Intentos fallidos en 1 minuto
    "handshake_timeout_ms": 5000,  # Handshake lento (5 segundos)
    "unknown_client": True,  # Cliente no en whitelist
    "invalid_certificate": True,  # Certificado inválido
}

# Ventanas de tiempo para análisis
TIME_WINDOW_SECONDS = 60  # 1 minuto
ANALYSIS_INTERVAL_SECONDS = 300  # Analizar cada 5 minutos

# ═══════════════════════════════════════════════════════════════
# 🤖 CONFIGURACIÓN DEL LLM (Ollama)
# ═══════════════════════════════════════════════════════════════

LLM_BASE_URL = "http://localhost:11434"  # Ollama local
LLM_MODEL = "mistral"  # Modelo a usar
LLM_TIMEOUT = 30  # segundos
LLM_TEMPERATURE = 0.7  # Creatividad (0-1)
LLM_MAX_TOKENS = 500  # Máximo de tokens en respuesta

# ═══════════════════════════════════════════════════════════════
# 🎯 CLIENTES CONOCIDOS (WHITELIST)
# ═══════════════════════════════════════════════════════════════

KNOWN_CLIENTS = {
    "Mercado Pago": "mercado-pago",
    "Ualá Wallet": "uala-wallet",
    "BruBank": "brubank",
    "Naranja X": "naranja-x",
}

# ═══════════════════════════════════════════════════════════════
# 🔍 PATRONES DE ANOMALÍAS CONOCIDAS
# ═══════════════════════════════════════════════════════════════

ANOMALY_PATTERNS = {
    "brute_force": {
        "description": "Múltiples intentos de conexión fallida",
        "threshold": 5,
        "window_seconds": 60,
    },
    "certificate_tampering": {
        "description": "Intentos con certificados inválidos",
        "threshold": 3,
        "window_seconds": 300,
    },
    "port_scanning": {
        "description": "Conexiones rápidas desde múltiples puertos",
        "threshold": 10,
        "window_seconds": 60,
    },
    "credential_stuffing": {
        "description": "Intentos con clientes desconocidos",
        "threshold": 7,
        "window_seconds": 120,
    },
}

# ═══════════════════════════════════════════════════════════════
# 📋 VALIDACIONES
# ═══════════════════════════════════════════════════════════════

def validate_certificates():
    """Valida que todos los certificados requeridos existan."""
    required = [CA_CERT, SERVER_CERT, SERVER_KEY]
    missing = [cert for cert in required if not cert.exists()]
    
    if missing:
        raise FileNotFoundError(
            f"Certificados faltantes: {missing}\n"
            f"Ejecuta: bash certs/generate-*.sh"
        )

def get_client_cert_path(client_id: str) -> tuple:
    """Retorna la ruta del certificado y clave de un cliente."""
    if client_id in CLIENTS_CERTS:
        client = CLIENTS_CERTS[client_id]
        return client["cert"], client["key"]
    return None, None

# ═══════════════════════════════════════════════════════════════
# 🎨 COLORES PARA TERMINAL
# ═══════════════════════════════════════════════════════════════

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

    @staticmethod
    def success(text):
        return f"{Colors.GREEN}✓ {text}{Colors.RESET}"

    @staticmethod
    def error(text):
        return f"{Colors.RED}✗ {text}{Colors.RESET}"

    @staticmethod
    def warning(text):
        return f"{Colors.YELLOW}⚠ {text}{Colors.RESET}"

    @staticmethod
    def info(text):
        return f"{Colors.BLUE}ℹ {text}{Colors.RESET}"

    @staticmethod
    def anomaly(text):
        return f"{Colors.RED}{Colors.BOLD}🚨 {text}{Colors.RESET}"
