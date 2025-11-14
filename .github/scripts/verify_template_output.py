#!/usr/bin/env python3
"""
Validate templates.json and verify that all referenced template files exist.

Usage: python verify_template_output.py
"""

import json
import sys
from pathlib import Path


def main():
    repo_root = Path(__file__).parent.parent.parent
    templates_json = repo_root / 'templates.json'

    # Validate templates.json is valid JSON
    try:
        with open(templates_json) as f:
            templates = json.load(f)
        print(f"✓ templates.json is valid JSON")
    except json.JSONDecodeError as e:
        print(f"✗ templates.json is invalid JSON: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print(f"✗ templates.json not found")
        sys.exit(1)

    errors = []

    # Validate each template
    for template_name, config in templates.items():
        print(f"\nValidating template: {template_name}")

        # Check required fields
        if 'file' not in config:
            errors.append(f"✗ {template_name}: missing 'file' field")
            print(errors[-1])
            continue

        if 'description' not in config:
            errors.append(f"✗ {template_name}: missing 'description' field")
            print(errors[-1])

        # Check main file exists
        main_file = repo_root / config['file']
        if main_file.exists():
            print(f"  ✓ Main file exists: {config['file']}")

            # Try to compile Python files
            if config['file'].endswith('.py'):
                try:
                    import py_compile
                    py_compile.compile(main_file, doraise=True)
                    print(f"  ✓ Python file compiles: {config['file']}")
                except py_compile.PyCompileError as e:
                    errors.append(f"✗ {template_name}: Python compilation error in {config['file']}: {e}")
                    print(errors[-1])
        else:
            errors.append(f"✗ {template_name}: main file not found: {config['file']}")
            print(errors[-1])

        # Check all files in complex templates
        if 'files' in config:
            for file_spec in config['files']:
                source = file_spec.get('source')
                if not source:
                    errors.append(f"✗ {template_name}: file spec missing 'source' field")
                    print(errors[-1])
                    continue

                source_file = repo_root / source
                if source_file.exists():
                    print(f"  ✓ File exists: {source}")

                    # Try to compile Python files
                    if source.endswith('.py'):
                        try:
                            import py_compile
                            py_compile.compile(source_file, doraise=True)
                            print(f"  ✓ Python file compiles: {source}")
                        except py_compile.PyCompileError as e:
                            errors.append(f"✗ {template_name}: Python compilation error in {source}: {e}")
                            print(errors[-1])
                else:
                    errors.append(f"✗ {template_name}: source file not found: {source}")
                    print(errors[-1])

    # Print summary
    print("\n" + "="*50)
    if errors:
        print(f"✗ Validation failed with {len(errors)} error(s)")
        for error in errors:
            print(f"  {error}")
        sys.exit(1)
    else:
        print(f"✓ All {len(templates)} template(s) validated successfully")
        sys.exit(0)


if __name__ == '__main__':
    main()
