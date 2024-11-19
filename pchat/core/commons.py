import os
import rsa


log_str: str = os.getenv("LOG_FORMAT", f"%(asctime)s | %(name)s | %(lineno)d | %(levelname)s | %(message)s")
log_lvl: str = os.getenv("LOG_LEVEL", "debug")
server_host: str = os.getenv("SERVER_HOST", "0.0.0.0")
server_port: int = int(os.getenv("SERVER_PORT", 5000))
client_host: str = os.getenv("CLIENT_HOST", "0.0.0.0")
client_port: int = int(os.getenv("CLIENT_PORT", 5001))
public_key, private_key = rsa.newkeys(1024)
