import json
import os
import subprocess
import argparse

def collect_attestations(att_dir, cosign_pub, output_file):
    report = {
        'total_modules': 0,
        'attested': 0,
        'verified': 0,
        'coverage_percent': 0.0,
        'failed': [],
    }

    attestation_files = [f for f in os.listdir(att_dir) if f.endswith('-attestation.json')]
    report['total_modules'] = len(attestation_files)
    report['attested'] = len(attestation_files)

    for att_file in attestation_files:
        att_path = os.path.join(att_dir, att_file)
        try:
            subprocess.run(
                ['python3', '/Users/agi_dev/LOCAL-REPOS/Lukhas/scripts/verify_attestation.py', '--att', att_path, '--cosign-pub', cosign_pub],
                check=True,
                capture_output=True,
            )
            report['verified'] += 1
        except subprocess.CalledProcessError as e:
            module_name = att_file.replace('-attestation.json', '')
            report['failed'].append({
                'module': module_name,
                'error': e.stderr.decode(),
            })

    if report['total_modules'] > 0:
        report['coverage_percent'] = (report['verified'] / report['total_modules']) * 100

    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"Security posture report written to {output_file}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Collect and verify SLSA attestations.')
    parser.add_argument('--att-dir', required=True, help='Directory containing attestation files')
    parser.add_argument('--cosign-pub', required=True, help='Path to cosign public key')
    parser.add_argument('--out', required=True, help='Output file for the security posture report')
    args = parser.parse_args()

    collect_attestations(args.att_dir, args.cosign_pub, args.out)
