#!/bin/bash

# 🔐 Generar Autoridad de Certificación (CA) Raíz
# Este script crea la CA que firmará todos los demás certificados

set -e

echo "🔐 Generando Autoridad de Certificación (CA)..."
echo "================================================"

# Crear directorio si no existe
mkdir -p certs 2>/dev/null || true

# 1. Generar clave privada de la CA (4096 bits RSA)
echo "[1/3] Generando clave privada de CA (4096 bits)..."
openssl genrsa -out certs/ca-key.pem 4096 2>/dev/null

# 2. Generar certificado de CA (válido por 10 años)
echo "[2/3] Generando certificado de CA (válido 10 años)..."
openssl req -new -x509 -days 3650 -key certs/ca-key.pem -out certs/ca-cert.pem \
  -subj "/C=AR/ST=Buenos Aires/L=CABA/O=VVBA/OU=Security/CN=VVBA-CA"

# 3. Mostrar información del certificado
echo "[3/3] Verificando certificado..."
echo ""
echo "✅ CA Creada exitosamente!"
echo ""
echo "📋 Información del Certificado:"
openssl x509 -in certs/ca-cert.pem -text -noout | grep -E "Subject:|Issuer:|Not Before|Not After|Public-Key"

echo ""
echo "📁 Archivos generados:"
echo "  • certs/ca-key.pem    (Clave privada - CONFIDENCIAL)"
echo "  • certs/ca-cert.pem   (Certificado público)"
echo ""
echo "⚠️  ADVERTENCIA: Guarda ca-key.pem en un lugar seguro."
echo "    Este archivo no debe compartirse."
echo ""
echo "✨ Próximo paso: Ejecutar generate-server.sh"
