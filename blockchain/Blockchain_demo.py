# ================================================================
# Projeto: Mini Blockchain em Python (versão interativa)
# Autor: [Natan Derick de Souza Leite]
# Professor: Francisco Calaça Xavier
# Descrição:
#   Implementação didática de uma blockchain com menu interativo.
#   Recursos:
#     - Classe Transacao
#     - Classe Bloco
#     - Token (recompensa de mineração)
#     - Bloco gênesis
#     - Validação e exibição em tempo real
# ================================================================

from __future__ import annotations
import time
import json
import hashlib
from dataclasses import dataclass, asdict
from typing import List, Optional


# ------------------------------------------------------------
# Funções utilitárias
# ------------------------------------------------------------
def sha256(b: bytes) -> str:
    """Retorna o hash SHA-256 de um conjunto de bytes."""
    return hashlib.sha256(b).hexdigest()


def jhash(obj) -> str:
    """Hash estável (JSON com chaves ordenadas)."""
    return sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode())


def merkle_root(hashes: List[str]) -> str:
    """Calcula a Merkle Root a partir de uma lista de hashes."""
    if not hashes:
        return sha256(b"")
    layer = hashes[:]
    while len(layer) > 1:
        if len(layer) % 2 == 1:
            layer.append(layer[-1])  # Duplica o último se for ímpar
        next_layer = []
        for i in range(0, len(layer), 2):
            next_layer.append(
                sha256(bytes.fromhex(layer[i]) + bytes.fromhex(layer[i + 1]))
            )
        layer = next_layer
    return layer[0]


# Dificuldade de mineração (mais zeros = mais difícil)
DIFFICULTY_PREFIX = "0000"


# ------------------------------------------------------------
# Classe Transacao
# ------------------------------------------------------------
@dataclass
class Transacao:
    """Representa uma transação simples entre duas carteiras."""

    remetente: str
    destinatario: str
    valor: float

    def hash(self) -> str:
        """Retorna o hash da transação."""
        return jhash(asdict(self))


# ------------------------------------------------------------
# Classe Bloco
# ------------------------------------------------------------
@dataclass
class Bloco:
    """Representa um bloco na blockchain."""

    indice: int
    timestamp: float
    hash_anterior: str
    merkle_root: str
    nonce: int
    transacoes: List[Transacao]

    def cabecalho(self) -> dict:
        """Retorna apenas os dados que compõem o cabeçalho do bloco."""
        return {
            "indice": self.indice,
            "timestamp": round(self.timestamp, 6),
            "hash_anterior": self.hash_anterior,
            "merkle_root": self.merkle_root,
            "nonce": self.nonce,
        }

    def hash(self) -> str:
        """Calcula o hash do cabeçalho."""
        return jhash(self.cabecalho())


# ------------------------------------------------------------
# Classe Blockchain
# ------------------------------------------------------------
class Blockchain:
    """Blockchain simples com prova de trabalho e transações."""

    def __init__(self):
        self.chain: List[Bloco] = []
        self.mem_pool: List[Transacao] = []
        self.criar_bloco_genesis()

    def criar_bloco_genesis(self):
        """Cria o primeiro bloco (gênesis)."""
        genesis_tx = Transacao(remetente="network", destinatario="satoshi", valor=50.0)
        root = merkle_root([genesis_tx.hash()])
        genesis = Bloco(
            indice=0,
            timestamp=time.time(),
            hash_anterior="0" * 64,
            merkle_root=root,
            nonce=0,
            transacoes=[genesis_tx],
        )
        self.chain.append(genesis)

    @property
    def ultimo_bloco(self) -> Bloco:
        return self.chain[-1]

    def adicionar_transacao(self, remetente: str, destinatario: str, valor: float):
        """Adiciona uma nova transação ao pool de memória."""
        self.mem_pool.append(Transacao(remetente, destinatario, valor))

    def minerar(
        self, minerador: str, max_tentativas: int = 1_000_000
    ) -> Optional[Bloco]:
        """Tenta minerar um novo bloco e adicioná-lo à blockchain."""
        # Transação de recompensa (coinbase)
        recompensa = Transacao(remetente="network", destinatario=minerador, valor=6.25)
        transacoes = [recompensa] + self.mem_pool
        tx_hashes = [t.hash() for t in transacoes]
        root = merkle_root(tx_hashes)

        novo_bloco = Bloco(
            indice=len(self.chain),
            timestamp=time.time(),
            hash_anterior=self.ultimo_bloco.hash(),
            merkle_root=root,
            nonce=0,
            transacoes=transacoes,
        )

        # Prova de trabalho
        print("\n⛏️ Minerando bloco... (pode levar alguns segundos)")
        for n in range(max_tentativas):
            novo_bloco.nonce = n
            h = novo_bloco.hash()
            if h.startswith(DIFFICULTY_PREFIX):
                self.chain.append(novo_bloco)
                self.mem_pool = []  # limpa o mempool
                print(f"✔️ Bloco {novo_bloco.indice} minerado com sucesso! Hash: {h}")
                return novo_bloco

        print("❌ Falha na mineração: limite de tentativas atingido.")
        return None

    def validar(self) -> bool:
        """Verifica a integridade da blockchain."""
        for i in range(1, len(self.chain)):
            atual = self.chain[i]
            anterior = self.chain[i - 1]

            if atual.hash_anterior != anterior.hash():
                return False
            if not atual.hash().startswith(DIFFICULTY_PREFIX):
                return False
            if merkle_root([t.hash() for t in atual.transacoes]) != atual.merkle_root:
                return False
        return True

    def exibir_cadeia(self):
        """Exibe todos os blocos da blockchain."""
        for bloco in self.chain:
            print(f"\n===== BLOCO {bloco.indice} =====")
            print(json.dumps(bloco.cabecalho(), indent=2))
            print("Transações:")
            for t in bloco.transacoes:
                print(f"  - {t.remetente} → {t.destinatario}: {t.valor} tokens")


# ------------------------------------------------------------
# Menu interativo
# ------------------------------------------------------------
def menu_interativo():
    bc = Blockchain()
    print("\nBlockchain inicializada com bloco gênesis!")

    while True:
        print("\n==================== MENU ====================")
        print("1 - Adicionar nova transação")
        print("2 - Minerar novo bloco")
        print("3 - Validar blockchain")
        print("4 - Exibir todos os blocos")
        print("0 - Sair")
        print("=============================================")
        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            remetente = input("Remetente: ")
            destinatario = input("Destinatário: ")
            try:
                valor = float(input("Valor da transação: "))
                bc.adicionar_transacao(remetente, destinatario, valor)
                print("✅ Transação adicionada ao mempool!")
            except ValueError:
                print("❌ Valor inválido! Use números.")

        elif opcao == "2":
            minerador = input("Nome ou carteira do minerador: ")
            bc.minerar(minerador)

        elif opcao == "3":
            print("⏳ Validando blockchain...")
            print(
                "✅ Blockchain válida!" if bc.validar() else "❌ Blockchain inválida!"
            )

        elif opcao == "4":
            bc.exibir_cadeia()

        elif opcao == "0":
            print("\n👋 Encerrando o sistema...")
            break

        else:
            print("❌ Opção inválida. Tente novamente.")


# ------------------------------------------------------------
# Execução principal
# ------------------------------------------------------------
if __name__ == "__main__":
    menu_interativo()
