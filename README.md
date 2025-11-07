# Browser-Use Template Library

Template collection for the `browser-use` CLI init command.

## Structure

```
.
├── default_template.py          # Simplest setup example
├── advanced_template.py         # All configuration options shown
├── tools_template.py            # Custom tool registration example
├── gitignore.template           # Shared .gitignore for complex templates
├── shopping/                    # E-commerce automation template
│   ├── main.py
│   ├── launch_chrome_debug.py
│   ├── README.md
│   ├── pyproject.toml.template
│   └── .env.example.template
├── job-application/             # Job application automation template
│   ├── main.py
│   ├── README.md
│   ├── applicant_data.json
│   ├── example_resume.pdf
│   ├── pyproject.toml.template
│   └── .env.example.template
└── agentmail/                   # Email inbox automation with 2FA template
    ├── main.py
    ├── email_tools.py
    ├── README.md
    ├── pyproject.toml.template
    └── .env.example.template
```

## Usage

This repository is used as a git submodule by the main [browser-use](https://github.com/browser-use/browser-use) repository.

Templates are loaded by the `browser-use init` CLI command:

```bash
uvx browser-use init --template default
uvx browser-use init --template shopping
uvx browser-use init --template job-application
uvx browser-use init --template agentmail
```

## Adding New Templates

### Simple Template

1. Create a new `.py` file in the root directory (e.g., `my_template.py`)
2. Add your template entry in `templates.json`:

```python
'my-template': {
    'file': 'my_template.py',
    'description': 'Description of what this template does',
}
```

### Complex Template (with scaffolding)

1. Create a new subdirectory (e.g., `my-template/`)
2. Add template files:
   - `main.py` - Main script
   - `README.md` - Documentation
   - `pyproject.toml.template` - Project config
   - `.env.example.template` - Environment variables
   - Any additional assets
3. Add entry to `INIT_TEMPLATES` and generation logic in `init_cmd.py`

## License

Same as [browser-use](https://github.com/browser-use/browser-use)
