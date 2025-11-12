# Browser-Use Template Library

Template collection for the `browser-use` CLI init command.

## Structure

```
.
├── templates.json               # Template registry and metadata
├── gitignore.template           # Shared .gitignore for complex templates
│
├── Simple Templates (single Python files)
├── default_template.py          # Example: Minimal setup
├── ...                          # See templates.json for complete list
│
└── Complex Templates (full project scaffolding)
    └── shopping/                # Example: E-commerce automation
        ├── main.py
        ├── launch_chrome_debug.py
        ├── README.md
        ├── pyproject.toml.template
        └── .env.example.template
    └── ...                      # See templates.json for complete list
```

For a complete list of all available templates, see [`templates.json`](templates.json).

## Usage

This repository is used as a git submodule by the main [browser-use](https://github.com/browser-use/browser-use) repository.

Templates are loaded by the `browser-use init` CLI command:

```bash
uvx browser-use init --template default
uvx browser-use init --template shopping
uvx browser-use init --template job-application
uvx browser-use init --template agentmail
```

## Testing Templates Locally

Before submitting a PR, you can test your templates locally using the included test environment:

```bash
# First time setup
cd test-env
uv sync

# Test a simple template
uv run test_templates.py --template default --output my_test.py

# Test a complex template
uv run test_templates.py --template shopping --output my_bot
```

The test script monkey-patches browser-use CLI to use your local `templates.json` and template files instead of fetching from GitHub, allowing you to verify:

- ✓ Template files are copied correctly
- ✓ `next_steps` display properly
- ✓ File permissions are set (executable files)
- ✓ Binary files work (PDFs, images, etc.)
- ✓ Variable substitution works (`{template}`, `{output}`)

## Adding New Templates

### Simple Template (Single File)

1. Create your template file in the root directory:
   ```bash
   # Example: my_template.py
   ```

2. Add an entry to `templates.json`:
   ```json
   "my-template": {
       "file": "my_template.py",
       "description": "Brief description of what this template does"
   }
   ```

3. Test it locally:
   ```bash
   cd test-env
   uv run test_templates.py --template my-template --output test.py
   ```

### Complex Template (Multiple Files)

1. Create a new directory with your template files:
   ```bash
   mkdir my-template/
   # Add files: main.py, README.md, pyproject.toml.template, .env.example.template
   ```

2. Add a complete entry to `templates.json`:
   ```json
   "my-template": {
       "file": "my-template/main.py",
       "description": "Brief description of what this template does",
       "files": [
           {
               "source": "my-template/main.py",
               "dest": "main.py"
           },
           {
               "source": "my-template/pyproject.toml.template",
               "dest": "pyproject.toml"
           },
           {
               "source": "gitignore.template",
               "dest": ".gitignore"
           },
           {
               "source": "my-template/.env.example.template",
               "dest": ".env.example"
           },
           {
               "source": "my-template/README.md",
               "dest": "README.md"
           }
       ],
       "next_steps": [
           {
               "title": "Navigate to project directory",
               "commands": ["cd {template}"]
           },
           {
               "title": "Set up your API key",
               "commands": [
                   "cp .env.example .env",
                   "# Edit .env and add your API_KEY"
               ],
               "note": "(Get your key at https://example.com/api-keys)"
           },
           {
               "title": "Install dependencies",
               "commands": ["uv sync"]
           },
           {
               "title": "Run the script",
               "commands": ["uv run {output}"]
           },
           {
               "footer": "📖 See README.md for detailed instructions"
           }
       ]
   }
   ```

3. Test it locally:
   ```bash
   cd test-env
   uv run test_templates.py --template my-template --output my_bot
   ```

## Template Structure Reference

### templates.json Schema

Each template entry in `templates.json` supports the following fields:

#### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `file` | string | Path to the main template file (e.g., `"my_template.py"` or `"my-template/main.py"`) |
| `description` | string | Short description shown in CLI (1-2 sentences) |

#### Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `files` | array | List of files to copy for complex templates (see File Specification below) |
| `next_steps` | array | Custom post-installation instructions (see Next Steps below) |

### File Specification

Each entry in the `files` array:

```json
{
    "source": "path/to/source/file",
    "dest": "destination/filename",
    "binary": true,      // Optional: true for PDFs, images, etc. (default: false)
    "executable": true   // Optional: true to set +x permission (default: false)
}
```

**Examples:**

```json
// Text file
{
    "source": "my-template/main.py",
    "dest": "main.py"
}

// Binary file (PDF, image, etc.)
{
    "source": "my-template/resume.pdf",
    "dest": "resume.pdf",
    "binary": true
}

// Executable script
{
    "source": "my-template/launch_script.py",
    "dest": "launch_script.py",
    "executable": true
}
```

### Next Steps Configuration

Each entry in the `next_steps` array can be:

**Regular step:**
```json
{
    "title": "Step title",
    "commands": ["command1", "command2"],
    "note": "(Optional helpful note)"
}
```

**Footer (shown at the end):**
```json
{
    "footer": "Final message with helpful links or tips"
}
```

**Variable Substitution:**

The CLI automatically replaces these variables in `commands`:
- `{template}` → Template name (e.g., `"shopping"`)
- `{output}` → Output filename specified by user

**Example:**
```json
{
    "title": "Run your script",
    "commands": ["cd {template} && uv run {output}"]
}
// Becomes: "cd shopping && uv run my_bot"
```

### Best Practices

1. **README.md**: Include detailed setup instructions, customization tips, and troubleshooting
2. **.env.example.template**: Document all required environment variables with example values
3. **pyproject.toml.template**: Pin dependencies to working versions
4. **Description**: Be specific about what the template does (e.g., "E-commerce automation with Instacart" vs "Shopping bot")
5. **next_steps**: Provide clear, ordered instructions that work out of the box

## Contributing

### Workflow

1. Fork this repository
2. Create a new branch for your template
3. Add your template files and update `templates.json`
4. Test locally using `test-env/test_templates.py`
5. Submit a PR with:
   - Clear description of what the template does
   - Use case or problem it solves
   - Any special requirements or dependencies

### Quality Checklist

- [ ] Template code is tested and working
- [ ] README.md includes clear setup instructions
- [ ] .env.example.template documents all required API keys
- [ ] pyproject.toml.template has all necessary dependencies
- [ ] next_steps guide users through setup correctly
- [ ] Template name is descriptive and follows kebab-case convention

## License

Same as [browser-use](https://github.com/browser-use/browser-use)
