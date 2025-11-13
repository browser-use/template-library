#!/usr/bin/env python3
"""
Validate templates.json and template file structure.

This script checks:
1. templates.json is valid JSON
2. All referenced files exist
3. Complex templates have required files
4. Schema is correct
"""

import json
import sys
from pathlib import Path


def validate_json_file(templates_json_path: Path) -> dict:
    """Validate templates.json is valid JSON and return parsed data."""
    try:
        with open(templates_json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✓ {templates_json_path} is valid JSON")
        return data
    except json.JSONDecodeError as e:
        print(f"✗ {templates_json_path} is not valid JSON: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print(f"✗ {templates_json_path} not found")
        sys.exit(1)


def validate_template_entry(name: str, config: dict, repo_root: Path) -> list[str]:
    """Validate a single template entry. Returns list of errors."""
    errors = []

    # Check required fields
    if 'file' not in config:
        errors.append(f"Template '{name}' missing required field 'file'")
    if 'description' not in config:
        errors.append(f"Template '{name}' missing required field 'description'")

    if 'file' not in config:
        return errors  # Can't continue without file field

    # Check main file exists
    main_file = repo_root / config['file']
    if not main_file.exists():
        errors.append(f"Template '{name}': main file '{config['file']}' does not exist")

    # Validate featured field if present (optional)
    if 'featured' in config:
        if not isinstance(config['featured'], bool):
            errors.append(f"Template '{name}': 'featured' field must be a boolean")

    # Validate author field if present (optional)
    if 'author' in config:
        author = config['author']
        if not isinstance(author, dict):
            errors.append(f"Template '{name}': 'author' field must be an object")
        else:
            # All author fields are optional, but validate types if present
            optional_author_fields = {
                'name': str,
                'github_profile': str,
                'last_modified_date': str
            }
            for field, expected_type in optional_author_fields.items():
                if field in author and not isinstance(author[field], expected_type):
                    errors.append(
                        f"Template '{name}': author.{field} must be a {expected_type.__name__}"
                    )

    # Check files array if present
    if 'files' in config:
        for file_spec in config['files']:
            if 'source' not in file_spec:
                errors.append(f"Template '{name}': file entry missing 'source' field")
                continue
            if 'dest' not in file_spec:
                errors.append(f"Template '{name}': file entry missing 'dest' field")
                continue

            source_path = repo_root / file_spec['source']
            if not source_path.exists():
                errors.append(f"Template '{name}': source file '{file_spec['source']}' does not exist")

        # For complex templates, check required files exist
        is_complex = len(config['files']) > 1
        if is_complex:
            template_dir = Path(config['file']).parent
            required_files = ['README.md', 'pyproject.toml.template', '.env.example.template']

            for required in required_files:
                # Check if it's in the files array
                found = any(
                    Path(f['source']).name == required
                    for f in config['files']
                )
                if not found:
                    errors.append(
                        f"Template '{name}': complex template missing '{required}' in files array"
                    )

    return errors


def main():
    repo_root = Path(__file__).parent.parent.parent
    templates_json = repo_root / 'templates.json'

    print("Validating template registry...\n")

    # Validate JSON
    templates = validate_json_file(templates_json)

    # Validate each template entry
    all_errors = []
    for name, config in templates.items():
        errors = validate_template_entry(name, config, repo_root)
        all_errors.extend(errors)

        if not errors:
            print(f"✓ Template '{name}' is valid")
        else:
            for error in errors:
                print(f"✗ {error}")

    # Summary
    print(f"\n{'='*60}")
    if all_errors:
        print(f"Validation failed with {len(all_errors)} error(s)")
        sys.exit(1)
    else:
        print(f"✓ All {len(templates)} templates are valid!")
        sys.exit(0)


if __name__ == '__main__':
    main()
