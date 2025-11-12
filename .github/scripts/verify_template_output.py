#!/usr/bin/env python3
"""
Verify that template initialization created the expected files.

Usage: python verify_template_output.py <template-name>
"""

import json
import sys
from pathlib import Path


def main():
    if len(sys.argv) != 2:
        print("Usage: python verify_template_output.py <template-name>")
        sys.exit(1)

    template_name = sys.argv[1]
    repo_root = Path(__file__).parent.parent.parent
    templates_json = repo_root / 'templates.json'

    # Load templates.json
    with open(templates_json) as f:
        templates = json.load(f)

    if template_name not in templates:
        print(f"✗ Template '{template_name}' not found in templates.json")
        sys.exit(1)

    config = templates[template_name]
    template_dir = repo_root / 'test-env' / template_name

    # Check if template directory was created
    if not template_dir.exists():
        print(f"✗ Template directory '{template_dir}' was not created")
        sys.exit(1)

    print(f"✓ Template directory created: {template_dir}")

    # For simple templates, just check the output file exists
    if 'files' not in config:
        # Simple template - should have created test_output.py
        output_file = template_dir / 'test_output.py'
        if output_file.exists():
            print(f"✓ Output file created: {output_file}")
            sys.exit(0)
        else:
            print(f"✗ Output file not found: {output_file}")
            sys.exit(1)

    # For complex templates, check all expected files
    errors = []
    for file_spec in config['files']:
        dest = file_spec['dest']
        expected_file = template_dir / dest

        if expected_file.exists():
            print(f"✓ File created: {dest}")
        else:
            errors.append(f"✗ Missing file: {dest}")
            print(errors[-1])

    if errors:
        print(f"\n✗ {len(errors)} file(s) missing")
        sys.exit(1)
    else:
        print(f"\n✓ All {len(config['files'])} expected files created")
        sys.exit(0)


if __name__ == '__main__':
    main()
