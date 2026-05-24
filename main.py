import urllib.request
import json
import time
import os

# Configuration
# Use a public Ethereum RPC endpoint. Cloudflare provides one.
# For production, you'd typically use a service like Infura/Alchemy with an API key
# and potentially environment variables for security.
RPC_URL = os.getenv("ETH_RPC_URL", "https://cloudflare-eth.com/")
POLLING_INTERVAL_SECONDS = 10 # Check every 10 seconds for new blocks

def get_latest_block_number(rpc_url):
    """
    Fetches the latest Ethereum block number using a JSON-RPC call
    without relying on any specialized blockchain libraries.
    """
    headers = {'Content-Type': 'application/json'}
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_blockNumber",
        "params": [],
        "id": 1
    }

    try:
        # Encode the payload to JSON and then to bytes for the request body
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(rpc_url, data=data, headers=headers, method='POST')

        with urllib.request.urlopen(req) as response:
            response_data = response.read().decode('utf-8')
            result = json.loads(response_data)

            if "result" in result:
                # The block number is returned in hexadecimal format (e.g., "0x123abc")
                hex_block_number = result["result"]
                decimal_block_number = int(hex_block_number, 16)
                return decimal_block_number
            elif "error" in result:
                print(f"RPC Error: {result['error']['message']}")
                return None
            else:
                print(f"Unexpected RPC response: {result}")
                return None
    except urllib.error.URLError as e:
        print(f"Network or URL error: {e.reason}")
        return None
    except json.JSONDecodeError as e:
        print(f"JSON decoding error: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

def main():
    print(f"Starting on-chain block monitor. Polling every {POLLING_INTERVAL_SECONDS} seconds...")
    print(f"Using RPC URL: {RPC_URL}")

    last_known_block = None

    while True:
        current_block = get_latest_block_number(RPC_URL)

        if current_block is not None:
            if last_known_block is None:
                print(f"Initial block: {current_block}")
                last_known_block = current_block
            elif current_block > last_known_block:
                # This is the core "alert" logic: a new block has been detected on-chain.
                print(f"ALERT! New block detected: {current_block} (Previous: {last_known_block})")
                last_known_block = current_block
            else:
                print(f"Current block: {current_block} (No new block yet)")
        else:
            print("Failed to retrieve block number. Retrying...")

        time.sleep(POLLING_INTERVAL_SECONDS)

if __name__ == "__main__":
    main()
