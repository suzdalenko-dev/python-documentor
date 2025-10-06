import base64, json, hmac, hashlib
from datetime import datetime, timedelta, timezone


class JWTManager:
    def __init__(self, secret_key: str = "super_secret_key_2025_suzdalenko"):
        """Inicializa el gestor JWT."""
        self.secret_key = secret_key.encode() if isinstance(secret_key, str) else secret_key

    def _b64url(self, data: bytes, decode=False):
        """Codifica o decodifica en base64 URL-safe sin padding '='."""
        if decode:
            padding = '=' * (-len(data) % 4)
            return base64.urlsafe_b64decode(data + padding)
        return base64.urlsafe_b64encode(data).decode().rstrip("=")

    # 🔹 CODIFICAR (crear token)
    def encode(self, payload: dict, days: int = 1) -> str:
        """Crea un JWT válido por `days` días."""
        header = {"alg": "HS256", "typ": "JWT"}
        payload["exp"] = int((datetime.now(timezone.utc) + timedelta(days=days)).timestamp())

        h64 = self._b64url(json.dumps(header, separators=(',', ':')).encode())
        p64 = self._b64url(json.dumps(payload, separators=(',', ':')).encode())
        msg = f"{h64}.{p64}".encode()

        sig = self._b64url(hmac.new(self.secret_key, msg, hashlib.sha256).digest())
        return f"{h64}.{p64}.{sig}"

    # 🔹 DESCODIFICAR (verificar token)
    def decode(self, token: str):
        """
        Verifica el JWT y devuelve (True, payload) si es válido,
        o (False, None) si está caducado o es inválido.
        """
        try:
            h64, p64, s64 = token.split(".")
            msg = f"{h64}.{p64}".encode()

            # recalcular la firma
            sig = self._b64url(hmac.new(self.secret_key, msg, hashlib.sha256).digest())
            if not hmac.compare_digest(sig, s64):
                return False, None  # firma incorrecta

            # decodificar payload
            payload = json.loads(self._b64url(p64, decode=True))

            # comprobar expiración
            exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
            if exp < datetime.now(timezone.utc):
                return False, None  # token caducado

            return True, payload
        except Exception:
            return False, None
