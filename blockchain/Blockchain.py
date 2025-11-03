from __future__ import annotations
import time, json, hashlib, random
from dataclasses import dataclass, asdict
from typing import List, Optional


# ------------------------------------------------------
# Funções utilitárias de hash
# ------------------------------------------------------
def sha256(x: bytes) -> str:
    return hashlib.sha256(x).hexdigest()


def jhash(obj) -> str:
    """Hash de um objeto JSON com chaves ordenadas (estável)."""
    return sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode())


def merkle_root(hashes: List[str]) -> str:
    """Calcula a Merkle Root a partir de uma lista de hashes."""
    if not hashes:
        return sha256(b"")
    layer = hashes[:]
    while len(layer) > 1:
        if len(layer) % 2 == 1:
            layer.append(layer[-1])
        nxt = []
        for i in range(0, len(layer), 2):
            nxt.append(sha256(bytes.fromhex(layer[i]) + bytes.fromhex(layer[i + 1])))
        layer = nxt
    return layer[0]


# ------------------------------------------------------
# Configurações de dificuldade
# ------------------------------------------------------
DIFFICULTY_PREFIX = "00000"  # quanto mais zeros, mais difícil


# ------------------------------------------------------
# Estruturas principais
# ------------------------------------------------------
@dataclass
class Transaction:
    sender: str
    recipient: str
    amount: float

    def hash(self) -> str:
        return jhash(asdict(self))


@dataclass
class Block:
    index: int
    timestamp: float
    prev_hash: str
    merkle_root: str
    nonce: int
    transactions: List[Transaction]

    def header_dict(self):
        return {
            "index": self.index,
            "timestamp": round(self.timestamp, 6),
            "prev_hash": self.prev_hash,
            "merkle_root": self.merkle_root,
            "nonce": self.nonce,
        }

    def hash(self) -> str:
        return jhash(self.header_dict())


# ------------------------------------------------------
# Blockchain principal
# ------------------------------------------------------
class Blockchain:
    def __init__(self):
        self.chain: List[Block] = []
        self.mem_pool: List[Transaction] = []
        self.create_genesis()

    def create_genesis(self):
        """Cria o bloco gênesis inicial."""
        genesis_tx = Transaction(sender="network", recipient="satoshi", amount=50.0)
        root = merkle_root([genesis_tx.hash()])
        genesis = Block(
            index=0,
            timestamp=time.time(),
            prev_hash="0" * 64,
            merkle_root=root,
            nonce=0,
            transactions=[genesis_tx],
        )
        self.chain.append(genesis)

    @property
    def last_block(self) -> Block:
        return self.chain[-1]

    def add_transaction(self, sender: str, recipient: str, amount: float):
        """Adiciona uma nova transação ao mempool."""
        self.mem_pool.append(Transaction(sender, recipient, amount))

    def mine(self, miner_address: str, max_tries: int = 2_000_000) -> Optional[Block]:
        """Minera um novo bloco (Prova de Trabalho)."""
        reward_tx = Transaction(sender="network", recipient=miner_address, amount=6.25)
        txs = [reward_tx] + self.mem_pool
        tx_hashes = [t.hash() for t in txs]
        root = merkle_root(tx_hashes)

        block = Block(
            index=len(self.chain),
            timestamp=time.time(),
            prev_hash=self.last_block.hash(),
            merkle_root=root,
            nonce=0,
            transactions=txs,
        )

        for n in range(max_tries):
            block.nonce = n
            h = block.hash()
            if h.startswith(DIFFICULTY_PREFIX):
                self.chain.append(block)
                self.mem_pool = []
                return block
        return None

    def valid_chain(self) -> bool:
        """Valida toda a cadeia de blocos."""
        for i in range(1, len(self.chain)):
            b = self.chain[i]
            prev = self.chain[i - 1]

            # 1) Encadeamento
            if b.prev_hash != prev.hash():
                return False

            # 2) Prova de trabalho
            if not b.hash().startswith(DIFFICULTY_PREFIX):
                return False

            # 3) Conferência da Merkle Root
            calc_root = merkle_root([t.hash() for t in b.transactions])
            if calc_root != b.merkle_root:
                return False
        return True

    def to_dict(self):
        """Serializa a blockchain para exibição."""
        return [
            {
                **b.header_dict(),
                "hash": b.hash(),
                "transactions": [asdict(t) for t in b.transactions],
            }
            for b in self.chain
        ]


# ------------------------------------------------------
# Demonstração
# ------------------------------------------------------
def demo():
    bc = Blockchain()
    print("Bloco gênesis:", bc.to_dict()[0])

    # Adiciona transações
    bc.add_transaction("Alice", "Bob", 1.2)
    bc.add_transaction("Carol", "Dave", 0.7)

    print("\nMinerando Bloco 1...")
    b1 = bc.mine(miner_address="miner1")
    if b1:
        print("Bloco minerado:", b1.index, b1.hash())
    else:
        print("Falhou na mineração.")

    # Novas transações aleatórias
    for _ in range(3):
        a = random.choice(["Alice", "Bob", "Carol", "Dave"])
        r = random.choice(["Alice", "Bob", "Carol", "Dave"])
        if a == r:
            r = "miner1"
        bc.add_transaction(a, r, round(random.uniform(0.1, 2.0), 2))

    print("\nMinerando Bloco 2...")
    b2 = bc.mine(miner_address="miner2")
    if b2:
        print("Bloco minerado:", b2.index, b2.hash())

    print("\nBlockchain válida?", bc.valid_chain())
    print(json.dumps(bc.to_dict(), indent=2))


if __name__ == "__main__":
    demo()
