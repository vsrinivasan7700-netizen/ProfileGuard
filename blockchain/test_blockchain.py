import json
import tempfile
from pathlib import Path

from blockchain import Blockchain


def main():
    print("=" * 50)
    print("PERSISTENT BLOCKCHAIN TEST")
    print("=" * 50)

    # Use a temporary file to protect the project's real blockchain.
    with tempfile.TemporaryDirectory() as temporary_folder:

        storage_path = Path(temporary_folder) / "test_chain.json"

        # TEST 1: Create a new blockchain.
        chain = Blockchain(storage_path)

        print("\nTest 1: New chain is valid:", chain.is_chain_valid())

        # TEST 2: Add an analysis record.
        saved_record = {
            "profile_id": "demo_1001",
            "platform": "instagram",
            "predicted_label": 0,
            "detection_method": "random_forest"
        }

        added_block = chain.add_record(saved_record)

        print("Test 2: Record added at block:", added_block.index)
        print("Chain saved to disk:", storage_path.exists())

        original_hash = added_block.hash

        # TEST 3: Reload the blockchain from disk.
        reloaded_chain = Blockchain(storage_path)

        print(
            "\nTest 3: Chain valid after reload:",
            reloaded_chain.is_chain_valid()
        )

        print(
            "Saved hash preserved:",
            reloaded_chain.chain[1].hash == original_hash
        )

        print(
            "Record preserved:",
            reloaded_chain.chain[1].data == saved_record
        )

        # TEST 4: Modify a stored record without updating its hash.
        saved_data = json.loads(
            storage_path.read_text(encoding="utf-8")
        )

        saved_data[1]["data"]["predicted_label"] = 1

        storage_path.write_text(
            json.dumps(saved_data, indent=2),
            encoding="utf-8"
        )

        try:
            Blockchain(storage_path)
            print("\nTest 4: Tampering detection FAILED")

        except ValueError:
            print("\nTest 4: Tampering detected successfully")

    print("\nAll persistence tests completed.")


if __name__ == "__main__":
    main()

