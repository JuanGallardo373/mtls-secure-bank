#!/bin/bash

# 💳 Generar Certificados de Clientes (Billeteras Virtuales)
# Este script crea certificados para 4 billeteras legítimas

set -e

echo "💳 Generando Certificados de Clientes (Billeteras Virtuales)..."
echo "=============================================================="

# Verificar si la CA existe
if [ ! -f "certs/ca-key.pem" ] || [ ! -f "certs/ca-cert.pem" ]; then
    echo "❌ Error: La CA no existe."
    echo "   Ejecuta primero: bash generate-ca.sh"
    exit 1
fi

mkdir -p certs 2>/dev/null || true

# Definir clientes
declare -a CLIENTS=(
    "mercado-pago:Mercado Pago"
    "uala-wallet:Ualá Wallet"
    "brubank:BruBank"
    "naranja-x:Naranja X"
)

for client_info in "${CLIENTS[@]}"; do
    IFS=':' read -r client_code client_name <<< "$client_info"
    
    echo ""
    echo "📱 Generando certificado para: $client_name ($client_code)"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # 1. Generar clave privada del cliente
    echo "  [1/3] Generando clave privada..."
    openssl genrsa -out "certs/${client_code}-key.pem" 2048 2>/dev/null
    
    # 2. Crear CSR (Certificate Signing Request)
    echo "  [2/3] Creando CSR..."
    openssl req -new -key "certs/${client_code}-key.pem" -out "certs/${client_code}.csr" \
      -subj "/C=AR/ST=Buenos Aires/L=CABA/O=VirtualWallet/OU=$client_name/CN=$client_name"
    
    # 3. Firmar el certificado con la CA (válido por 1 año)
    echo "  [3/3] Firmando con CA..."
    openssl x509 -req -days 365 -in "certs/${client_code}.csr" \
      -CA certs/ca-cert.pem -CAkey certs/ca-key.pem \
      -CAcreateserial -out "certs/${client_code}-cert.pem" 2>/dev/null
    
    # Limpiar CSR
    rm -f "certs/${client_code}.csr"
    
    echo "  ✅ $client_name generado exitosamente!"
done

echo ""
echo "=================================================="
echo "✅ Todos los certificados de clientes generados!"
echo ""
echo "📁 Certificados generados:"
for client_info in "${CLIENTS[@]}"; do
    IFS=':' read -r client_code client_name <<< "$client_info"
    echo "  • $client_name"
    echo "    - certs/${client_code}-key.pem"
    echo "    - certs/${client_code}-cert.pem"
done

echo ""
echo "🔍 Resumen de certificados:"
ls -lh certs/*.pem 2>/dev/null | awk '{print "  " $9 " (" $5 ")"}'

echo ""
echo "✨ ¡Todos los certificados están listos!"
echo "   Puedes iniciar el servidor: python server/vvba_server.py"
