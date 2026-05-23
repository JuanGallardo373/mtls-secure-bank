# 🏦 mTLS Secure Banking - VVBA Bank Simulation

Sistema de demostración de seguridad con **Mutual TLS (mTLS)**, **CA propia**, **logging de handshakes TLS** y **detección de anomalías con LLM** usando Ollama.

## 📋 Descripción del Proyecto

Este proyecto simula un **banco central (VVBA Bank)** que se comunica de forma segura con múltiples **billeteras virtuales (clientes)**:

- **Servidor**: VVBA Bank (Banco Virtual con Validación Bilateral)
- **Clientes Legítimos**:
  - Mercado Pago ✅
  - Ualá Wallet ✅
  - BruBank ✅
  - Naranja X ✅
- **Cliente Atacante**: Sin certificado válido ❌

### Características Principales

✨ **mTLS (Mutual TLS)**
- Validación bidireccional de certificados
- Servidor y clientes se autentican mutuamente

🔐 **CA Propia**
- Autoridad de Certificación autogenerada
- Certificados firmados y validables

📊 **Logging Estructurado**
- Registro de todos los handshakes TLS
- Formato JSONL para análisis
- Captura de anomalías en tiempo real

🤖 **Detección de Anomalías con LLM**
- Integración con Ollama (LLM local)
- Análisis automático de logs
- Identificación de patrones sospechosos

## 📁 Estructura del Proyecto

```
mtls-secure-bank/
├── certs/                          # Certificados y scripts
│   ├── generate-ca.sh             # Generar CA raíz
│   ├── generate-server.sh         # Generar certificado servidor
│   ├── generate-client.sh         # Generar certificados clientes
│   ├── README_CERTS.md            # Documentación de certificados
│   └── .gitkeep
├── server/                         # Servidor del banco
│   ├── vvba_server.py             # Servidor mTLS principal
│   ├── tls_logger.py              # Sistema de logging TLS
│   ├── config.py                  # Configuración centralizada
│   └── .gitkeep
├── clients/                        # Clientes de prueba
│   ├── mercado_pago_client.py    # Cliente legítimo (Mercado Pago)
│   ├── attacker_client.py         # Cliente atacante
│   └── .gitkeep
├── analysis/                       # Análisis con LLM
│   ├── log_analyzer.py            # Analizador de logs
│   ├── llm_anomaly_detector.py    # Detector de anomalías con Ollama
│   └── .gitkeep
├── logs/                          # Logs generados
│   └── .gitkeep
├── requirements.txt               # Dependencias Python
├── .gitignore                     # Archivos a ignorar en Git
└── README.md                      # Este archivo
```

## 🚀 Inicio Rápido

### 1. Clonar el Repositorio

```bash
git clone https://github.com/JuanGallardo373/mtls-secure-bank.git
cd mtls-secure-bank
```

### 2. Generar Certificados

```bash
cd certs
bash generate-ca.sh
bash generate-server.sh
bash generate-client.sh
cd ..
```

Esto generará:
- `ca-key.pem` y `ca-cert.pem` (Autoridad de Certificación)
- `server-key.pem` y `server-cert.pem` (Servidor VVBA Bank)
- Certificados individuales para cada cliente

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Iniciar el Servidor

```bash
python server/vvba_server.py
```

El servidor escuchará en `localhost:8443` con mTLS habilitado.

### 5. Ejecutar Clientes (en otra terminal)

**Cliente Legítimo (Mercado Pago):**
```bash
python clients/mercado_pago_client.py
```

**Cliente Atacante:**
```bash
python clients/attacker_client.py
```

### 6. Analizar Logs

```bash
python analysis/log_analyzer.py
python analysis/llm_anomaly_detector.py
```

## 🔑 Escenarios de Prueba

### Escenario 1: Cliente Legítimo
- Cliente con certificado válido
- Handshake TLS exitoso ✅
- Conexión establecida
- Log: SUCCESS

### Escenario 2: Cliente Atacante (sin certificado)
- Intenta conectar sin certificado
- Handshake rechazado ❌
- Servidor detecta anomalía
- Log: REJECTED, ANOMALY

### Escenario 3: Múltiples Clientes Simultáneos
- Varios clientes legítimos conectados
- Servidor maneja múltiples conexiones
- Cada una con su propio certificado
- Logs diferenciados por cliente

## 📊 Formato de Logs

Los logs se guardan en `logs/tls_handshakes.log` en formato JSONL:

```json
{
  "timestamp": "2026-05-22T10:30:45.123456",
  "client_ip": "127.0.0.1",
  "client_port": 54321,
  "status": "SUCCESS",
  "subject": "CN=Mercado Pago",
  "issuer": "CN=VVBA-CA",
  "handshake_time_ms": 45.23,
  "anomaly": false,
  "error_message": null
}
```

## 🤖 Detección de Anomalías con LLM

El sistema analiza automáticamente los logs usando **Ollama** para detectar:

- Múltiples intentos de conexión fallida
- Clientes desconocidos
- Handshakes inusualmente lentos
- Patrones de ataque sospechosos

## 📋 Requisitos

- **Python 3.8+**
- **OpenSSL** (para generar certificados)
- **Ollama** (para análisis con LLM)
- **Ubuntu/Linux** (recomendado)

## 🔒 Seguridad

⚠️ **IMPORTANTE**: Este es un proyecto educativo.

- Los certificados privados (`*-key.pem`) NUNCA deben compartirse
- Están excluidos en `.gitignore` por seguridad
- En producción, usar una CA profesional
- Implementar rotación de certificados
- Usar HTTPS en lugar de HTTP

## 📚 Documentación Adicional

- `certs/README_CERTS.md` - Detalles sobre generación de certificados
- Comentarios en código fuente
- Docstrings en funciones Python

## 🛠️ Tecnologías Utilizadas

- **Python 3**: Lenguaje principal
- **ssl/socket**: Comunicación mTLS
- **OpenSSL**: Generación de certificados
- **Ollama**: LLM local
- **JSON**: Formato de logs

## 👨‍💻 Autor

Juan Gallardo (@JuanGallardo373)

## 📄 Licencia

MIT License - Libre para usar con fines educativos

---

**¡Listo para comenzar!** 🚀

Primero genera los certificados con los scripts en `certs/`.
