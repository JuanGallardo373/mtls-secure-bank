#!/bin/bash

# 🖥️  Generar Certificado del Servidor (VVBA Bank)
# Este script crea el certificado para el servidor mTLS

set -e

echo "🖥️  Generando Certificado del Servidor VVBA Bank..."
echo "===================================================="

# Verificar si la CA existe
if [ ! -f "certs/ca-key.pem" ] || [ ! -f "certs/ca-cert.pem" ]; then
    echo "❌ Error: La CA no existe."
    echo "   Ejecuta primero: bash generate-ca.sh"
    exit 1
fi

mkdir -p certs 2>/dev/null || true

# 1. Generar clave privada del servidor
echo "[1/4] Generando clave privada del servidor..."
openssl genrsa -out certs/server-key.pem 2048 2>/dev/null

# 2. Crear solicitud de firma de certificado (CSR)
echo "[2/4] Creando solicitud de firma de certificado (CSR)..."
openssl req -new -key certs/server-key.pem -out certs/server.csr \
  -subj "/C=AR/ST=Buenos Aires/L=CABA/O=VVBA/OU=Banking/CN=localhost" \
  -addext "subjectAltName=DNS:localhost,DNS:127.0.0.1,IP:127.0.0.1"

# 3. Firmar el certificado con la CA (válido por 1 año)
# Usando -copy_extensions copyall para preservar las extensiones del CSR
echo "[3/4] Firmando certificado con la CA (válido 1 año)..."
openssl x509 -req -in certs/server.csr \
  -CA certs/ca-cert.pem -CAkey certs/ca-key.pem \
  -CAcreateserial -out certs/server-cert.pem \
  -days 365 -copy_extensions copyall

# Verificar que se creó el certificado
if [ ! -f "certs/server-cert.pem" ]; then
    echo "❌ Error: No se pudo crear server-cert.pem"
    echo "   Verifica que ca-key.pem y ca-cert.pem existan"
    exit 1
fi

# Limpiar archivos temporales
rm -f certs/server.csr

echo ""
echo "✅ Certificado del Servidor generado exitosamente!"
echo ""
echo "📋 Información del Certificado:"
openssl x509 -in certs/server-cert.pem -text -noout | grep -E "Subject:|Issuer:|Not Before|Not After|DNS:|Public-Key|Alternative"

echo ""
echo "📁 Archivos generados:"
echo "  • certs/server-key.pem    (Clave privada - CONFIDENCIAL)"
echo "  • certs/server-cert.pem   (Certificado público)"
echo ""
echo "✨ Próximo paso: Ejecutar generate-client.sh"
