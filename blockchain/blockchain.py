import hashlib
import json
import os

from datetime import datetime, timezone
from pathlib import Path


# ==========================================================
# BLOCKCHAIN STORAGE CONFIGURATION
# ==========================================================

BLOCKCHAIN_DIR = Path(__file__).resolve().parent

STORAGE_PATH = Path(
    os.getenv(
        "BLOCKCHAIN_STORAGE_PATH",
        str(BLOCKCHAIN_DIR / "chain_storage.json")
    )
)


# ==========================================================
# BLOCK CLASS
# ==========================================================

class Block:
    """Represent one block in the blockchain."""

    def __init__(
        self,
        index: int,
        timestamp: str,
        data: dict,
        previous_hash: str
    ):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        """Calculate SHA-256 hash of the block."""

        block_content = {
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash
        }

        serialized = json.dumps(
            block_content,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False
        )

        return hashlib.sha256(
            serialized.encode("utf-8")
        ).hexdigest()

    def to_dict(self) -> dict:
        """Convert block into JSON format."""

        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "hash": self.hash
        }

    @classmethod
    def from_dict(cls, saved_block: dict):
        """Reconstruct a block from saved JSON data."""

        block = cls(
            index=saved_block["index"],
            timestamp=saved_block["timestamp"],
            data=saved_block["data"],
            previous_hash=saved_block["previous_hash"]
        )

        # Preserve the stored hash for validation.
        block.hash = saved_block["hash"]

        return block


# ==========================================================
# BLOCKCHAIN CLASS
# ==========================================================

class Blockchain:
    """Create, validate, save and load blockchain records."""

    def __init__(self, storage_path=STORAGE_PATH):
        """Initialize or load the persistent blockchain."""

        self.storage_path = Path(storage_path)

        # Check whether storage exists and contains data.
        if (
            self.storage_path.exists()
            and self.storage_path.stat().st_size > 0
        ):
            self.load_chain()
            print("Existing blockchain loaded successfully.")

        else:
            # Create a new chain if the file is missing or empty.
            print("Creating a new blockchain...")

            self.chain = [
                self.create_genesis_block()
            ]

            self.save_chain()

            print("Genesis block created and saved.")

        # Validate the blockchain after initialization.
        if not self.is_chain_valid():
            raise ValueError(
                "Blockchain validation failed. "
                "Stored data may have been changed or corrupted."
            )

    def create_genesis_block(self) -> Block:
        """Create the first block."""

        return Block(
            index=0,
            timestamp=datetime.now(timezone.utc).isoformat(),
            data={"event": "GENESIS"},
            previous_hash="0"
        )

    def get_latest_block(self) -> Block:
        """Return the latest block."""

        return self.chain[-1]

    def add_record(self, record: dict) -> Block:
        """Add a record and save the updated blockchain."""

        if not isinstance(record, dict):
            raise TypeError("Record must be a dictionary.")

        # Ensure record can be serialized as JSON.
        json.dumps(
            record,
            sort_keys=True,
            allow_nan=False
        )

        if not self.is_chain_valid():
            raise ValueError(
                "Cannot add a record to an invalid blockchain."
            )

        previous_block = self.get_latest_block()

        new_block = Block(
            index=len(self.chain),
            timestamp=datetime.now(timezone.utc).isoformat(),
            data=record,
            previous_hash=previous_block.hash
        )

        self.chain.append(new_block)

        try:
            self.save_chain()

        except OSError:
            self.chain.pop()
            raise

        return new_block

    def is_chain_valid(self) -> bool:
        """Validate block contents and hash connections."""

        if not self.chain:
            return False

        for index, block in enumerate(self.chain):

            # Validate block index.
            if block.index != index:
                return False

            # Validate block hash.
            if block.hash != block.calculate_hash():
                return False

            if index == 0:

                # Validate genesis block.
                if block.previous_hash != "0":
                    return False

                if block.data != {"event": "GENESIS"}:
                    return False

            else:
                previous_block = self.chain[index - 1]

                # Validate previous block connection.
                if block.previous_hash != previous_block.hash:
                    return False

        return True

    def save_chain(self):
        """Save blockchain records to JSON storage."""

        self.storage_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        content = json.dumps(
            [block.to_dict() for block in self.chain],
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
            allow_nan=False
        )

        # Save using a temporary file.
        temporary_path = self.storage_path.with_suffix(".tmp")

        temporary_path.write_text(
            content + "\n",
            encoding="utf-8"
        )

        temporary_path.replace(self.storage_path)

    def load_chain(self):
        """Load blockchain records from JSON storage."""

        try:
            saved_blocks = json.loads(
                self.storage_path.read_text(
                    encoding="utf-8"
                )
            )

            if (
                not isinstance(saved_blocks, list)
                or not saved_blocks
            ):
                raise ValueError(
                    "Stored blockchain is empty or invalid."
                )

            self.chain = [
                Block.from_dict(saved_block)
                for saved_block in saved_blocks
            ]

        except (
            OSError,
            json.JSONDecodeError,
            KeyError,
            TypeError
        ) as error:

            raise ValueError(
                "Could not load the saved blockchain."
            ) from error

    def export_chain(self) -> list:
        """Export blockchain as a JSON-compatible list."""

        return [
            block.to_dict()
            for block in self.chain
        ]


# ==========================================================
# DIRECT EXECUTION TEST
# ==========================================================

if __name__ == "__main__":

    print("=" * 50)
    print("BLOCKCHAIN INITIALIZATION")
    print("=" * 50)

    blockchain = Blockchain()

    print("\nTotal blocks:", len(blockchain.chain))
    print("Blockchain valid:", blockchain.is_chain_valid())
    print("Storage location:", STORAGE_PATH)

    print("\nBlockchain initialization completed.")