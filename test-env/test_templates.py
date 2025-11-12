#!/usr/bin/env python3
"""
Local template testing script for template-library development.

This script monkey-patches browser-use CLI to use local template files
instead of fetching from GitHub, allowing you to test templates before
submitting PRs.

Setup (first time):
    cd test-env
    uv sync

Usage:
    cd test-env
    uv run test_templates.py --template <name> --output <path>

Example:
    cd test-env
    uv run test_templates.py --template shopping --output my-shopping-bot
"""

import json
import sys
from pathlib import Path
from unittest.mock import patch
from urllib import request


def get_local_template_list() -> dict:
    """Read templates.json from local repository."""
    # Go up one level from test-env to template-library root
    templates_path = Path(__file__).parent.parent / 'templates.json'
    if not templates_path.exists():
        raise FileNotFoundError(f'templates.json not found at {templates_path}')

    with open(templates_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_local_template_content(template_file: str) -> str:
    """Read template file content from local repository."""
    # Go up one level from test-env to template-library root
    template_path = Path(__file__).parent.parent / template_file
    if not template_path.exists():
        raise FileNotFoundError(f'Template file not found: {template_path}')

    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()


def get_local_template_file(template_file: str) -> bytes:
    """Read template file content as bytes (for binary files)."""
    # Go up one level from test-env to template-library root
    template_path = Path(__file__).parent.parent / template_file
    if not template_path.exists():
        raise FileNotFoundError(f'Template file not found: {template_path}')

    with open(template_path, 'rb') as f:
        return f.read()


def mock_urlopen(url: str, timeout: int = 5):
    """Mock urllib.request.urlopen to serve local files."""

    class MockResponse:
        def __init__(self, data: bytes):
            self.data = data

        def read(self) -> bytes:
            return self.data

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

    # Extract the file path from the GitHub raw URL
    # Format: https://raw.githubusercontent.com/browser-use/template-library/main/{file_path}
    # Go up one level from test-env to template-library root
    repo_root = Path(__file__).parent.parent

    if 'templates.json' in url:
        templates_path = repo_root / 'templates.json'
        with open(templates_path, 'rb') as f:
            return MockResponse(f.read())
    else:
        # Extract file path after '/main/'
        parts = url.split('/main/')
        if len(parts) > 1:
            file_path = parts[1]
            local_path = repo_root / file_path
            if local_path.exists():
                with open(local_path, 'rb') as f:
                    return MockResponse(f.read())

        raise FileNotFoundError(f'Local file not found for URL: {url}')


def main():
    """Run browser-use init with local template files."""
    try:
        # Import browser-use CLI (will fail if not installed)
        from browser_use import init_cmd

        # Patch the URL fetching to use local files
        with patch.object(request, 'urlopen', side_effect=mock_urlopen):
            # Run the actual browser-use init command
            init_cmd.main()

    except ImportError:
        print('Error: browser-use is not installed.')
        print('Run `uv sync` from the test-env directory first.')
        sys.exit(1)
    except Exception as e:
        print(f'Error: {e}')
        sys.exit(1)


if __name__ == '__main__':
    main()
