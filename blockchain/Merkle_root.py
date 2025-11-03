# ================================================================
# Teste isolado da Merkle Root
# ================================================================

import hashlib
import json


def sha256(x: bytes) -> str:
    """Retorna o hash SHA-256 de bytes."""
    return hashlib.sha256(x).hexdigest()


def merkle_root(hashes: list[str]) -> str:
    """Calcula a Merkle Root a partir de uma lista de hashes (strings hexadecimais)."""
    if not hashes:
        return sha256(b"")  # Raiz do vazio

    layer = hashes[:]
    while len(layer) > 1:
        if len(layer) % 2 == 1:
            layer.append(layer[-1])  # Duplica o último (padrão comum)

        next_layer = []
        for i in range(0, len(layer), 2):
            combined = bytes.fromhex(layer[i]) + bytes.fromhex(layer[i + 1])
            next_layer.append(sha256(combined))

        layer = next_layer

    return layer[0]


# Demonstração
if __name__ == "__main__":
    tx_hashes = [sha256(f"tx{i}".encode()) for i in range(5)]
    print("Hashes de transações:", tx_hashes)
    print("Merkle root (5 txs):", merkle_root(tx_hashes))
