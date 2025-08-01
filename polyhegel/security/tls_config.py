"""
TLS/SSL Configuration for A2A Agents

Provides TLS certificate management and secure connection configuration
for polyhegel A2A agent communication.
"""

import os
import ssl
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict, Any
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import datetime

logger = logging.getLogger(__name__)


@dataclass
class TLSConfig:
    """TLS configuration for A2A agents"""
    
    # Certificate files
    cert_file: Optional[str] = None
    key_file: Optional[str] = None
    ca_file: Optional[str] = None
    
    # TLS settings
    verify_ssl: bool = True
    ssl_context: Optional[ssl.SSLContext] = None
    require_client_cert: bool = False
    
    # Certificate generation settings
    auto_generate_certs: bool = False
    cert_dir: str = "./certs"
    cert_validity_days: int = 365
    
    @classmethod
    def from_env(cls) -> "TLSConfig":
        """Create TLS config from environment variables"""
        return cls(
            cert_file=os.getenv("POLYHEGEL_TLS_CERT_FILE"),
            key_file=os.getenv("POLYHEGEL_TLS_KEY_FILE"),
            ca_file=os.getenv("POLYHEGEL_TLS_CA_FILE"),
            verify_ssl=os.getenv("POLYHEGEL_TLS_VERIFY_SSL", "true").lower() == "true",
            require_client_cert=os.getenv("POLYHEGEL_TLS_REQUIRE_CLIENT_CERT", "false").lower() == "true",
            auto_generate_certs=os.getenv("POLYHEGEL_TLS_AUTO_GENERATE", "false").lower() == "true",
            cert_dir=os.getenv("POLYHEGEL_TLS_CERT_DIR", "./certs"),
            cert_validity_days=int(os.getenv("POLYHEGEL_TLS_CERT_VALIDITY_DAYS", "365"))
        )
    
    def create_ssl_context(self, server_side: bool = True) -> ssl.SSLContext:
        """Create SSL context with configured settings"""
        if self.ssl_context:
            return self.ssl_context
        
        # Create SSL context
        if server_side:
            context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            context.check_hostname = False  # Allow internal agent communication
        else:
            context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        
        # Configure certificate verification
        if not self.verify_ssl:
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
        
        # Load certificates
        if self.cert_file and self.key_file:
            try:
                context.load_cert_chain(self.cert_file, self.key_file)
                logger.info(f"Loaded TLS certificate from {self.cert_file}")
            except Exception as e:
                logger.error(f"Failed to load TLS certificate: {e}")
                raise
        
        # Load CA certificate
        if self.ca_file and self.verify_ssl:
            try:
                context.load_verify_locations(self.ca_file)
                logger.info(f"Loaded CA certificate from {self.ca_file}")
            except Exception as e:
                logger.error(f"Failed to load CA certificate: {e}")
                raise
        
        # Client certificate requirement
        if self.require_client_cert and server_side:
            context.verify_mode = ssl.CERT_REQUIRED
        
        return context
    
    def get_uvicorn_ssl_config(self) -> Dict[str, Any]:
        """Get SSL configuration for uvicorn server"""
        if not self.cert_file or not self.key_file:
            return {}
        
        config = {
            "ssl_keyfile": self.key_file,
            "ssl_certfile": self.cert_file,
        }
        
        if self.ca_file:
            config["ssl_ca_certs"] = self.ca_file
        
        if self.require_client_cert:
            config["ssl_cert_reqs"] = ssl.CERT_REQUIRED
        
        return config


class CertificateManager:
    """Manages TLS certificates for A2A agents"""
    
    def __init__(self, config: TLSConfig):
        self.config = config
        self.cert_dir = Path(config.cert_dir)
        self.cert_dir.mkdir(exist_ok=True, parents=True)
    
    def generate_ca_certificate(self) -> tuple[str, str]:
        """Generate a self-signed CA certificate"""
        # Generate private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        
        # Create certificate
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "CA"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "San Francisco"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Polyhegel"),
            x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "A2A Agents"),
            x509.NameAttribute(NameOID.COMMON_NAME, "Polyhegel CA"),
        ])
        
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.datetime.utcnow()
        ).not_valid_after(
            datetime.datetime.utcnow() + datetime.timedelta(days=self.config.cert_validity_days)
        ).add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName("localhost"),
                x509.IPAddress("127.0.0.1"),
            ]),
            critical=False,
        ).add_extension(
            x509.BasicConstraints(ca=True, path_length=None),
            critical=True,
        ).add_extension(
            x509.KeyUsage(
                key_cert_sign=True,
                crl_sign=True,
                digital_signature=False,
                key_encipherment=False,
                content_commitment=False,
                data_encipherment=False,
                key_agreement=False,
                encipher_only=False,
                decipher_only=False
            ),
            critical=True,
        ).sign(private_key, hashes.SHA256())
        
        # Save files
        ca_cert_path = self.cert_dir / "ca.crt"
        ca_key_path = self.cert_dir / "ca.key"
        
        # Write certificate
        with open(ca_cert_path, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
        
        # Write private key
        with open(ca_key_path, "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        logger.info(f"Generated CA certificate: {ca_cert_path}")
        return str(ca_cert_path), str(ca_key_path)
    
    def generate_agent_certificate(
        self, 
        agent_name: str, 
        ca_cert_path: str, 
        ca_key_path: str,
        hostnames: list[str] = None
    ) -> tuple[str, str]:
        """Generate agent certificate signed by CA"""
        
        # Load CA certificate and key
        with open(ca_cert_path, "rb") as f:
            ca_cert = x509.load_pem_x509_certificate(f.read())
        
        with open(ca_key_path, "rb") as f:
            ca_key = serialization.load_pem_private_key(f.read(), password=None)
        
        # Generate agent private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        
        # Create certificate subject
        subject = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "CA"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "San Francisco"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Polyhegel"),
            x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "A2A Agents"),
            x509.NameAttribute(NameOID.COMMON_NAME, agent_name),
        ])
        
        # Default hostnames
        if not hostnames:
            hostnames = ["localhost", "127.0.0.1", agent_name]
        
        # Create subject alternative names
        san_list = []
        for hostname in hostnames:
            try:
                # Try as IP address first
                import ipaddress
                ip = ipaddress.ip_address(hostname)
                san_list.append(x509.IPAddress(ip))
            except ValueError:
                # Treat as DNS name
                san_list.append(x509.DNSName(hostname))
        
        # Create certificate
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            ca_cert.subject
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.datetime.utcnow()
        ).not_valid_after(
            datetime.datetime.utcnow() + datetime.timedelta(days=self.config.cert_validity_days)
        ).add_extension(
            x509.SubjectAlternativeName(san_list),
            critical=False,
        ).add_extension(
            x509.KeyUsage(
                key_cert_sign=False,
                crl_sign=False,
                digital_signature=True,
                key_encipherment=True,
                content_commitment=False,
                data_encipherment=False,
                key_agreement=False,
                encipher_only=False,
                decipher_only=False
            ),
            critical=True,
        ).add_extension(
            x509.ExtendedKeyUsage([
                x509.oid.ExtendedKeyUsageOID.SERVER_AUTH,
                x509.oid.ExtendedKeyUsageOID.CLIENT_AUTH,
            ]),
            critical=True,
        ).sign(ca_key, hashes.SHA256())
        
        # Save files
        agent_cert_path = self.cert_dir / f"{agent_name}.crt"
        agent_key_path = self.cert_dir / f"{agent_name}.key"
        
        # Write certificate
        with open(agent_cert_path, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
        
        # Write private key
        with open(agent_key_path, "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        logger.info(f"Generated agent certificate for {agent_name}: {agent_cert_path}")
        return str(agent_cert_path), str(agent_key_path)
    
    def setup_agent_certificates(self) -> Dict[str, tuple[str, str]]:
        """Setup certificates for all agents"""
        if not self.config.auto_generate_certs:
            return {}
        
        # Generate CA certificate if it doesn't exist
        ca_cert_path = self.cert_dir / "ca.crt"
        ca_key_path = self.cert_dir / "ca.key"
        
        if not ca_cert_path.exists() or not ca_key_path.exists():
            ca_cert_path, ca_key_path = self.generate_ca_certificate()
        
        # Generate agent certificates
        agents = ["polyhegel-leader", "polyhegel-follower-resource", 
                 "polyhegel-follower-security", "polyhegel-follower-value", 
                 "polyhegel-follower-general", "polyhegel-simulation"]
        
        certificates = {}
        for agent in agents:
            cert_path, key_path = self.generate_agent_certificate(
                agent, ca_cert_path, ca_key_path
            )
            certificates[agent] = (cert_path, key_path)
        
        return certificates


def setup_tls_for_agent(agent_name: str, config: TLSConfig = None) -> TLSConfig:
    """Setup TLS configuration for a specific agent"""
    if not config:
        config = TLSConfig.from_env()
    
    if config.auto_generate_certs:
        cert_manager = CertificateManager(config)
        certificates = cert_manager.setup_agent_certificates()
        
        if agent_name in certificates:
            cert_path, key_path = certificates[agent_name]
            config.cert_file = cert_path
            config.key_file = key_path
            config.ca_file = str(cert_manager.cert_dir / "ca.crt")
    
    return config