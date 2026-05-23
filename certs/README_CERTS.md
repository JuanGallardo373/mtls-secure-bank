# 🔐 Generación de Certificados - Documentación Detallada

## 📜 Información General

Este directorio contiene scripts bash para generar una **Autoridad de Certificación (CA) propia** y certificados para el servidor y clientes del proyecto VVBA Bank.

## 🛠️ Scripts Disponibles

### 1. `generate-ca.sh` - Autoridad de Certificación

Genera la CA raíz que firmará todos los demás certificados.

**Qué genera:**
- `ca-key.pem` - Clave privada de la CA (4096 bits RSA)
- `ca-cert.pem` - Certificado público de la CA

**Validez:** 10 años (3650 días)

**Usar:**
```bash
bash generate-ca.sh
```

**Información del certificado:**
```bash
openssl x509 -in certs/ca-cert.pem -text -noout
```

---

### 2. `generate-server.sh` - Certificado del Servidor

Genera el certificado para el servidor VVBA Bank (mTLS).

**Qué genera:**
- `server-key.pem` - Clave privada del servidor (2048 bits RSA)
- `server-cert.pem` - Certificado público del servidor

**Validez:** 1 año (365 días)

**SANs (Subject Alternative Names):**
- DNS:localhost
- DNS:127.0.0.1
- IP:127.0.0.1

**Usar:**
```bash
bash generate-server.sh
```

**Requisito previo:** `generate-ca.sh` debe ejecutarse primero

---

### 3. `generate-client.sh` - Certificados de Clientes

Genera certificados para 4 billeteras virtuales legítimas.

**Clientes generados:**
1. **Mercado Pago** → `mercado-pago-key.pem`, `mercado-pago-cert.pem`
2. **Ualá Wallet** → `uala-wallet-key.pem`, `uala-wallet-cert.pem`
3. **BruBank** → `brubank-key.pem`, `brubank-cert.pem`
4. **Naranja X** → `naranja-x-key.pem`, `naranja-x-cert.pem`

**Validez:** 1 año (365 días) cada uno

**Usar:**
```bash
bash generate-client.sh
```

**Requisito previo:** `generate-ca.sh` debe ejecutarse primero

---

## 🚀 Orden de Ejecución

```bash
cd certs

# 1. Generar CA (debe ser primero)
bash generate-ca.sh

# 2. Generar certificado del servidor
bash generate-server.sh

# 3. Generar certificados de clientes
bash generate-client.sh

cd ..
```

---

## 📁 Estructura de Archivos Generados

Después de ejecutar todos los scripts, la estructura será:

```
certs/
├── ca-key.pem                 # Clave privada de CA (CONFIDENCIAL)
├── ca-cert.pem               # Certificado de CA
├── ca.srl                     # Serial de CA (auto-generado)
├── server-key.pem            # Clave privada del servidor
├── server-cert.pem           # Certificado del servidor
├── mercado-pago-key.pem      # Clave privada cliente
├── mercado-pago-cert.pem     # Certificado cliente
├── uala-wallet-key.pem       # Clave privada cliente
├── uala-wallet-cert.pem      # Certificado cliente
├── brubank-key.pem           # Clave privada cliente
├── brubank-cert.pem          # Certificado cliente
├── naranja-x-key.pem         # Clave privada cliente
├── naranja-x-cert.pem        # Certificado cliente
├── generate-ca.sh            # Este script
├── generate-server.sh        # Este script
├── generate-client.sh        # Este script
└── README_CERTS.md           # Esta documentación
```

---

## 🔒 Seguridad

### ⚠️ ARCHIVOS CONFIDENCIALES

Los archivos `*-key.pem` contienen claves privadas y **NUNCA deben**:
- Compartirse con nadie
- Subirse a GitHub (están en `.gitignore`)
- Usarse en producción sin permisos correctos
- Exponerse públicamente

### Permisos Recomendados

```bash
chmod 600 certs/*-key.pem      # Solo el propietario puede leer
chmod 644 certs/*-cert.pem     # Público
chmod 600 certs/ca-key.pem     # CA muy confidencial
chmod 644 certs/ca-cert.pem    # CA puede ser pública
```

---

## 🔍 Verificar Certificados

### Ver información de un certificado:

```bash
# Servidor
openssl x509 -in certs/server-cert.pem -text -noout

# Cliente
openssl x509 -in certs/mercado-pago-cert.pem -text -noout

# CA
openssl x509 -in certs/ca-cert.pem -text -noout
```

### Ver información resumida:

```bash
openssl x509 -in certs/server-cert.pem -noout -subject -issuer -dates
```

### Verificar que un certificado está firmado por la CA:

```bash
openssl verify -CAfile certs/ca-cert.pem certs/server-cert.pem
openssl verify -CAfile certs/ca-cert.pem certs/mercado-pago-cert.pem
```

### Ver detalles de una clave privada:

```bash
openssl rsa -in certs/server-key.pem -text -noout | head -20
```

### Ver el índice de seriales:

```bash
cat certs/ca.srl
```

---

## 🧪 Pruebas Básicas

### 1. Verificar cadena de certificados

```bash
# Crear un bundle con CA + Servidor
cat certs/ca-cert.pem certs/server-cert.pem > certs/chain.pem

# Verificar la cadena
openssl verify -untrusted certs/chain.pem certs/server-cert.pem
```

### 2. Probar conexión mTLS con openssl

```bash
# Terminal 1 - Servidor
openssl s_server -key certs/server-key.pem -cert certs/server-cert.pem \
  -CAfile certs/ca-cert.pem -port 8443 -Verify 1

# Terminal 2 - Cliente
openssl s_client -key certs/mercado-pago-key.pem \
  -cert certs/mercado-pago-cert.pem \
  -CAfile certs/ca-cert.pem -connect localhost:8443
```

### 3. Comprobar que los certificados coinciden

```bash
# Los siguientes dos comandos deben mostrar el mismo hash
openssl x509 -noout -modulus -in certs/server-key.pem | openssl md5
openssl x509 -noout -modulus -in certs/server-cert.pem | openssl md5
```

---

## 🔄 Regenerar Certificados

Para regenerar certificados (ej: después de expirar):

```bash
# Opción 1: Regenerar todo
bash generate-ca.sh
bash generate-server.sh
bash generate-client.sh

# Opción 2: Solo regenerar el servidor
bash generate-server.sh

# Opción 3: Solo regenerar clientes
bash generate-client.sh
```

---

## 📋 Requisitos

- `openssl` (generalmente preinstalado en Linux/Mac)
- `bash`
- Permisos de lectura/escritura en el directorio `certs/`

### Verificar OpenSSL:

```bash
openssl version
# Output: OpenSSL 1.1.1 o superior
```

### Instalar en Ubuntu si no está:

```bash
sudo apt-get update
sudo apt-get install openssl
```

---

## 🎯 Próximos Pasos

Una vez generados los certificados:

1. ✅ Certificados listos
2. 🖥️ Iniciar servidor: `python server/vvba_server.py`
3. 💻 Ejecutar clientes: `python clients/mercado_pago_client.py`
4. 🔍 Analizar logs: `python analysis/log_analyzer.py`

---

## 📞 Solución de Problemas

### Error: "No such file or directory" para `ca-key.pem`

**Solución:** Ejecuta primero `generate-ca.sh`

```bash
bash generate-ca.sh
```

### Error: "Permission denied"

**Solución:** Haz los scripts ejecutables:

```bash
chmod +x certs/generate-*.sh
bash generate-ca.sh  # Ahora debería funcionar
```

### Los certificados caducaron

**Solución:** Regenera los certificados (se perderán los antiguos)

```bash
bash generate-ca.sh
bash generate-server.sh
bash generate-client.sh
```

### OpenSSL no encontrado

**Solución:** Instala OpenSSL

```bash
# Ubuntu/Debian
sudo apt-get install openssl

# macOS
brew install openssl
```

---

## 📚 Referencias

- [OpenSSL Documentation](https://www.openssl.org/docs/)
- [PKI Concepts](https://en.wikipedia.org/wiki/Public_key_infrastructure)
- [mTLS Explanation](https://en.wikipedia.org/wiki/Mutual_authentication)
- [X.509 Certificates](https://en.wikipedia.org/wiki/X.509)

---

**Última actualización:** 2026-05-23
