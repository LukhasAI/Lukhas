import argparse
import base64
import hashlib
import json
import os
import subprocess


def verify_attestation(attestation_file, cosign_pub_key):
    with open(attestation_file, 'r') as f:
        attestation = json.load(f)

    # 1. Verify cosign signature
    signature = base64.b64decode(attestation['signature'])
    statement = json.dumps(attestation['statement'], separators=(',', ':')).encode('utf-8')

    try:
        subprocess.run(
            ['cosign', 'verify-blob', '--key', cosign_pub_key, '--signature', '/dev/stdin', '/dev/stdin'],
            input=statement + signature,
            check=True,
            capture_output=True,
        )
        print("Cosign signature verified.")
    except subprocess.CalledProcessError as e:
        print(f"Cosign signature verification failed: {e.stderr.decode()}")
        return False

    # 2. Verify SHA256 integrity
    subject = attestation['statement']['subject'][0]
    artifact_path = os.path.join(os.path.dirname(attestation_file), subject['name'])
    expected_hash = subject['digest']['sha256']

    with open(artifact_path, 'rb') as f:
        artifact_hash = hashlib.sha256(f.read()).hexdigest()

    if artifact_hash == expected_hash:
        print("SHA256 integrity verified.")
    else:
        print(f"SHA256 integrity check failed. Expected {expected_hash}, got {artifact_hash}")
        return False

    # 3. Verify in-toto link presence
    if attestation['statement']['_type'] == 'https://in-toto.io/Statement/v0.1':
        print("In-toto link present.")
    else:
        print("In-toto link not present.")
        return False

    return True

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Verify SLSA attestation.')
    parser.add_argument('--att', required=True, help='Path to attestation JSON file')
    parser.add_argument('--cosign-pub', required=True, help='Path to cosign public key')
    args = parser.parse_args()

    if verify_attestation(args.att, args.cosign_pub):
        print("Attestation verified successfully.")
        exit(0)
    else:
        print("Attestation verification failed.")
        exit(1)
