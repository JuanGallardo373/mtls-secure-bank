# 📊 Sistema de Logging para Handshakes TLS

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict

from config import TLS_HANDSHAKE_LOG, LOG_LEVEL, Colors


@dataclass
class TLSHandshakeRecord:
    """Registro de un handshake TLS"""
    timestamp: str
    client_ip: str
    client_port: int
    status: str  # SUCCESS, FAILED, REJECTED, TIMEOUT
    subject: Optional[str] = None
    issuer: Optional[str] = None
    serial_number: Optional[str] = None
    version: Optional[str] = None
    handshake_time_ms: Optional[float] = None
    anomaly: bool = False
    anomaly_type: Optional[str] = None
    error_message: Optional[str] = None
    client_id: Optional[str] = None
    trusted: bool = False


class TLSLogger:
    """Logger especializado para handshakes TLS"""

    def __init__(self, log_file: Path = TLS_HANDSHAKE_LOG):
        """
        Inicializa el logger TLS.
        
        Args:
            log_file: Ruta del archivo de log
        """
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Configurar logging estándar
        self.logger = logging.getLogger("TLSLogger")
        self.logger.setLevel(LOG_LEVEL)
        
        if not self.logger.handlers:
            handler = logging.FileHandler(str(self.log_file))
            formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def log_handshake(self, record: TLSHandshakeRecord) -> None:
        """
        Registra un handshake TLS en formato JSONL.
        
        Args:
            record: Registro del handshake
        """
        try:
            with open(self.log_file, 'a') as f:
                json_line = json.dumps(asdict(record))
                f.write(json_line + '\n')
            
            # Log también en sistema estándar
            status_emoji = {
                'SUCCESS': '✓',
                'FAILED': '✗',
                'REJECTED': '🚫',
                'TIMEOUT': '⏱'
            }.get(record.status, '?')
            
            log_msg = f"{status_emoji} [{record.status}] {record.client_ip}:{record.client_port}"
            
            if record.anomaly:
                self.logger.warning(
                    f"ANOMALY: {log_msg} - {record.anomaly_type}"
                )
            else:
                self.logger.info(log_msg)
                
        except Exception as e:
            self.logger.error(f"Error escribiendo log: {e}")

    def log_connection_success(
        self,
        client_ip: str,
        client_port: int,
        cert_subject: str,
        cert_issuer: str,
        serial_number: str,
        version: str,
        handshake_time_ms: float,
        client_id: Optional[str] = None,
        trusted: bool = True
    ) -> None:
        """Registra una conexión exitosa."""
        record = TLSHandshakeRecord(
            timestamp=datetime.utcnow().isoformat(),
            client_ip=client_ip,
            client_port=client_port,
            status="SUCCESS",
            subject=cert_subject,
            issuer=cert_issuer,
            serial_number=serial_number,
            version=version,
            handshake_time_ms=handshake_time_ms,
            anomaly=False,
            client_id=client_id,
            trusted=trusted
        )
        self.log_handshake(record)

    def log_connection_failed(
        self,
        client_ip: str,
        client_port: int,
        error_message: str,
        is_anomaly: bool = False,
        anomaly_type: Optional[str] = None
    ) -> None:
        """Registra una conexión fallida."""
        record = TLSHandshakeRecord(
            timestamp=datetime.utcnow().isoformat(),
            client_ip=client_ip,
            client_port=client_port,
            status="FAILED",
            error_message=error_message,
            anomaly=is_anomaly,
            anomaly_type=anomaly_type
        )
        self.log_handshake(record)

    def log_connection_rejected(
        self,
        client_ip: str,
        client_port: int,
        reason: str,
        cert_subject: Optional[str] = None
    ) -> None:
        """Registra una conexión rechazada (certificado inválido)."""
        record = TLSHandshakeRecord(
            timestamp=datetime.utcnow().isoformat(),
            client_ip=client_ip,
            client_port=client_port,
            status="REJECTED",
            subject=cert_subject,
            error_message=reason,
            anomaly=True,
            anomaly_type="invalid_certificate"
        )
        self.log_handshake(record)

    def log_timeout(
        self,
        client_ip: str,
        client_port: int,
        timeout_seconds: float
    ) -> None:
        """Registra un timeout de conexión."""
        record = TLSHandshakeRecord(
            timestamp=datetime.utcnow().isoformat(),
            client_ip=client_ip,
            client_port=client_port,
            status="TIMEOUT",
            error_message=f"Timeout after {timeout_seconds}s",
            anomaly=True,
            anomaly_type="timeout"
        )
        self.log_handshake(record)

    def log_anomaly(
        self,
        client_ip: str,
        client_port: int,
        anomaly_type: str,
        details: Dict[str, Any]
    ) -> None:
        """Registra una anomalía detectada."""
        record = TLSHandshakeRecord(
            timestamp=datetime.utcnow().isoformat(),
            client_ip=client_ip,
            client_port=client_port,
            status="FAILED",
            anomaly=True,
            anomaly_type=anomaly_type,
            error_message=json.dumps(details)
        )
        self.log_handshake(record)

    def read_logs(self, limit: Optional[int] = None) -> list:
        """
        Lee los logs en formato JSONL.
        
        Args:
            limit: Máximo número de registros a leer
            
        Returns:
            Lista de diccionarios con los registros
        """
        records = []
        try:
            with open(self.log_file, 'r') as f:
                for i, line in enumerate(f):
                    if limit and i >= limit:
                        break
                    try:
                        record = json.loads(line.strip())
                        records.append(record)
                    except json.JSONDecodeError:
                        continue
        except FileNotFoundError:
            return []
        
        return records

    def get_recent_logs(self, minutes: int = 5, limit: int = 100) -> list:
        """
        Obtiene logs recientes.
        
        Args:
            minutes: Últimos N minutos
            limit: Máximo de registros
            
        Returns:
            Lista de registros recientes
        """
        from datetime import timedelta
        
        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
        records = self.read_logs(limit=limit * 2)
        
        recent = [
            r for r in records
            if datetime.fromisoformat(r.get('timestamp', '')) > cutoff_time
        ]
        
        return recent[:limit]

    def get_anomalies(self, limit: int = 50) -> list:
        """
        Obtiene registros de anomalías.
        
        Args:
            limit: Máximo de registros
            
        Returns:
            Lista de anomalías detectadas
        """
        records = self.read_logs(limit=limit * 3)
        anomalies = [r for r in records if r.get('anomaly', False)]
        return anomalies[-limit:]

    def get_stats(self) -> Dict[str, Any]:
        """
        Genera estadísticas de los logs.
        
        Returns:
            Diccionario con estadísticas
        """
        records = self.read_logs()
        
        if not records:
            return {}
        
        stats = {
            'total_connections': len(records),
            'successful': sum(1 for r in records if r['status'] == 'SUCCESS'),
            'failed': sum(1 for r in records if r['status'] == 'FAILED'),
            'rejected': sum(1 for r in records if r['status'] == 'REJECTED'),
            'anomalies': sum(1 for r in records if r.get('anomaly', False)),
            'unique_ips': len(set(r['client_ip'] for r in records)),
            'average_handshake_ms': sum(
                r['handshake_time_ms'] or 0 for r in records
                if r['handshake_time_ms']
            ) / sum(1 for r in records if r['handshake_time_ms']),
        }
        
        # Contar anomalías por tipo
        anomaly_types = {}
        for r in records:
            if r.get('anomaly_type'):
                anomaly_types[r['anomaly_type']] = \
                    anomaly_types.get(r['anomaly_type'], 0) + 1
        
        stats['anomalies_by_type'] = anomaly_types
        
        return stats

    def print_summary(self) -> None:
        """Imprime un resumen de los logs."""
        stats = self.get_stats()
        
        if not stats:
            print(Colors.warning("No hay registros de logs"))
            return
        
        print("\n" + "=" * 60)
        print(Colors.info("📊 RESUMEN DE HANDSHAKES TLS"))
        print("=" * 60)
        
        print(f"Total de conexiones: {stats['total_connections']}")
        print(Colors.success(f"Exitosas: {stats['successful']}"))
        print(Colors.error(f"Fallidas: {stats['failed']}"))
        print(Colors.error(f"Rechazadas: {stats['rejected']}"))
        print(Colors.anomaly(f"Anomalías detectadas: {stats['anomalies']}"))
        print(f"IPs únicas: {stats['unique_ips']}")
        print(f"Promedio handshake: {stats['average_handshake_ms']:.2f}ms")
        
        if stats.get('anomalies_by_type'):
            print("\nTipos de anomalías:")
            for atype, count in stats['anomalies_by_type'].items():
                print(f"  • {atype}: {count}")
        
        print("=" * 60 + "\n")


# Instancia global del logger
tls_logger = TLSLogger()
