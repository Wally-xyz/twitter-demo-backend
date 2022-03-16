from dataclasses import dataclass

BASE_URL = "https://api.pinata.cloud"
PIN_URL = f"{BASE_URL}/pinning/pinFileToIPFS"

PIN_JSON_URL = f"{BASE_URL}/pinning/pinJSONToIPFS"

@dataclass
class PinFileResponse:
    IpfsHash: str
    PinSize: int

    # ipfs_hash = result.json()["IpfsHash"]
    # pin_size = result.json()["PinSize"]

