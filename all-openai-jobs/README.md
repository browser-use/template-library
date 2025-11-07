# Browser-Use fetch all OpenAI jobs

Web scraping automation example using browser-use's CodeAgent to extract job listings from OpenAI's career page.

## What This Does

This template demonstrates:
- **CodeAgent** - uses AI to write code for data extraction
- **Web Scraping** - extracts all job listings from OpenAI's Ashby career page
- **Initial Actions** - pre-navigates to the target URL before agent execution
- **Export to Jupyter** - converts the generated code to a Jupyter notebook

## Setup

### 1. Navigate to Project Directory

```bash
cd all-openai-jobs
```

All commands below should be run from the `all-openai-jobs/` directory.

### 2. Set Up API Key

Copy the example environment file and add your API key:

```bash
cp .env.example .env
```

Edit `.env` and add your Browser-Use API key:
```
BROWSER_USE_API_KEY=your-key-here
```

Get your key at: https://cloud.browser-use.com/dashboard/settings?tab=api-keys&new

### 3. Install Dependencies

```bash
uv sync
```

This installs `browser-use` and all required dependencies (including `pydantic`, `python-dotenv`).

## Usage

Run the job extraction script:

```bash
uv run main.py
```

The agent will:
1. Navigate to OpenAI's job board (https://jobs.ashbyhq.com/openai)
2. Analyze the page structure
3. Generate code to extract all job listings
4. Execute the code and return the job data
5. Export the generated code to `script.ipynb` as a Jupyter notebook

## How It Works

### CodeAgent

The script uses `CodeAgent` which writes and executes code to accomplish the task:

```python
agent = CodeAgent(
    task=task,
    llm=ChatBrowserUse(),  # requires our special LLM
    initial_actions=initial_actions,
)
```

### Initial Actions

Pre-navigate to the target URL before the agent starts:

```python
initial_actions = [{"navigate": {"url": url, "new_tab": False}}]
```

This ensures the agent starts with the page already loaded.

### Task Definition

The task instructs the agent what to extract:

```python
task = f"""
Please go to {url} and extract all the jobs from the page.
Make sure to extract the data, and don't return empty array unless there are no openings.
"""
```

### Export to Jupyter

The generated code is exported to a Jupyter notebook:

```python
script = export_to_ipynb(agent, "script.ipynb")
```

This creates a reusable notebook with the extraction logic.

## Customization

### Change the Target URL

Edit the URL to scrape a different job board or website:
```python
url = "https://jobs.ashbyhq.com/your-company"
```

### Modify the Task

Adjust the task to extract different information:
```python
task = f"""
Please go to {url} and extract all job titles, locations, and departments.
Return the data as a structured list.
"""
```

### Customize Export

Change the output notebook filename:
```python
script = export_to_ipynb(agent, "my_custom_script.ipynb")
```

## Troubleshooting

**No jobs returned?**
- Check if the website structure has changed
- Try adjusting the task prompt to be more specific
- Verify the URL is accessible

**API key issues?**
- Ensure your `.env` file has the correct `BROWSER_USE_API_KEY`
- Get your key at: https://cloud.browser-use.com/dashboard/settings?tab=api-keys&new

**Agent not working as expected?**
- The CodeAgent generates code dynamically, results may vary
- Try running the script multiple times
- Review the generated `script.ipynb` to see the extraction logic

## Learn More

- [Browser-Use Documentation](https://docs.browser-use.com)
- [CodeAgent Documentation](https://docs.browser-use.com/customize/agent/code-agent)
- [Initial Actions Guide](https://docs.browser-use.com/customize/agent/initial-actions)
