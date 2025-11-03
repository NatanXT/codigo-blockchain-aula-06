# ================================================================
# Teste simples de funções hash
# ================================================================

import hashlib
import json


def sha256(x: bytes) -> str:
    """Retorna o hash SHA-256 de um conjunto de bytes."""
    return hashlib.sha256(x).hexdigest()


print("hash('Ola') =", sha256(b"Ola"))
print(
    "hash de JSON estável =",
    sha256(json.dumps({"a": 1, "b": 2}, sort_keys=True).encode()),
)
