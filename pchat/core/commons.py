import os
import rsa


log_str: str = os.getenv("LOG_FORMAT", f"%(asctime)s | %(name)s | %(lineno)d | %(levelname)s | %(message)s")
log_lvl: str = os.getenv("LOG_LEVEL", "debug")
host: str = os.getenv("HOST", "192.168.1.37")
port: int = int(os.getenv("PORT", 9999))
public_key, private_key = rsa.newkeys(1024)
