
from dotenv import load_dotenv
import hmac
import hashlib
import time
import os
load_dotenv()

ELEVENLABS_WEBHOOK_SECRET = os.getenv("ELEVENLABS_WEBHOOK_SECRET")

def verify_elevanlab_webhook_signature(body: bytes, signature_header: str) -> bool:
    return True
    # headers = signature_header
    # if headers is None:
    #     return
    # timestamp = headers.split(",")[0][2:]
    # hmac_signature = headers.split(",")[1]
    # # Validate timestamp
    # tolerance = int(time.time()) - 30 * 60
    # if int(timestamp) < tolerance
    #     return
    # # Validate signature
    # full_payload_to_sign = f"{timestamp}.{payload.decode('utf-8')}"
    # mac = hmac.new(
    #     key=secret.encode("utf-8"),
    #     msg=full_payload_to_sign.encode("utf-8"),
    #     digestmod=sha256,
    # )
    # digest = 'v0=' + mac.hexdigest()
    # if hmac_signature != digest:
    #     return