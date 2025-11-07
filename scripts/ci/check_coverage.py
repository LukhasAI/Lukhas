import argparse
import xml.etree.ElementTree as ET

import yaml


def check_coverage(coverage_xml, thresholds_yml):
    with open(thresholds_yml) as f:
        thresholds = yaml.safe_load(f)

    tree = ET.parse(coverage_xml)
    root = tree.getroot()

    packages = root.find('packages')
    failures = []

    for package in packages:
        package_name = package.get('name')
        line_rate = float(package.get('line-rate')) * 100

        for threshold_name, threshold_value in thresholds.items():
            if package_name.startswith(threshold_name):
                if line_rate < threshold_value:
                    failures.append(f"Package '{package_name}' is below threshold. Got {line_rate:.2f}%, expected {threshold_value}%.")
                break

    if failures:
        print("Coverage checks failed:")
        for failure in failures:
            print(failure)
        exit(1)
    else:
        print("All packages meet coverage thresholds.")
        exit(0)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Check per-module code coverage.')
    parser.add_argument('--coverage-xml', required=True, help='Path to coverage.xml file')
    parser.add_argument('--thresholds', required=True, help='Path to coverage_thresholds.yml file')
    args = parser.parse_args()

    check_coverage(args.coverage_xml, args.thresholds)
