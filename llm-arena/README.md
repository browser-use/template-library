# LLM Arena Template

Compare different AI models side-by-side in LLM Arena using Browser-Use to run the same task across multiple LLMs in parallel.

## What This Does

This template enables parallel AI model comparison and evaluation. The tool will:

1. Prompt you to enter a task description
2. Execute the same task across multiple LLMs simultaneously (Browser Use, Google Gemini, OpenAI ChatGPT, and Anthropic Claude)
3. Track completion time for each model
4. Display results with performance rankings

Each LLM operates in its own isolated browser session, allowing for fair side-by-side comparisons. This is perfect for evaluating which model performs best for your specific use cases, testing response quality, or benchmarking task completion speed.

## Setup

### 1. Get Your API Keys

You'll need API keys for each LLM provider you want to test:

#### Browser-Use API Key (Required)
1. Go to [https://browser-use.com/](https://browser-use.com/)
2. Sign up for an account
3. Get your API key from the dashboard
4. Copy the key

#### Google Gemini API Key (Optional but Recommended)
1. Go to [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Create a new API key
4. Copy the key

#### OpenAI API Key (Optional but Recommended)
1. Go to [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Sign up or sign in to your OpenAI account
3. Create a new API key
4. Copy the key

#### Anthropic API Key (Optional but Recommended)
1. Go to [https://console.anthropic.com/settings/keys](https://console.anthropic.com/settings/keys)
2. Sign up or sign in to your Anthropic account
3. Create a new API key
4. Copy the key

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```bash
BROWSER_USE_API_KEY=your-browser-use-api-key-here
GOOGLE_API_KEY=your-google-api-key-here
OPENAI_API_KEY=your-openai-api-key-here
ANTHROPIC_API_KEY=your-anthropic-api-key-here
```

**Note**: You can run the tool with just the Browser-Use API key, but for a true comparison you should configure all four providers.

### 3. Install Dependencies

```bash
uv sync
```

## Usage

### Basic Usage

```bash
uv run main.py
```

You'll be prompted to enter a task. The tool will then run the task across all configured LLMs in parallel.

### Example Tasks

Here are some example tasks you can try:

**Simple Information Retrieval**:
```
Find the number of stars of the browser-use repo on GitHub
```

**E-commerce Task**:
```
Go to amazon.com and find the price of the cheapest laptop
```

**Social Media Task**:
```
Visit reddit.com and find the top post about AI
```

**Research Task**:
```
Go to arxiv.org and find the most recent paper about large language models
```

**Comparison Task**:
```
Visit bestbuy.com and compare the prices of the top 3 gaming laptops
```

### Understanding the Output

The tool provides real-time feedback:
1. **Starting messages**: Shows when each LLM begins the task
2. **Completion messages**: Shows when each LLM finishes with elapsed time
3. **Results**: Displays the output from each LLM
4. **Summary**: Rankings sorted by completion time (fastest to slowest)

Example output:
```
Starting race with 4 LLMs...

Browser Use (bu-0-1) - Starting task...
Google Gemini (gemini-flash-latest) - Starting task...
OpenAI ChatGPT (gpt-4.1-mini) - Starting task...
Anthropic Claude (claude-sonnet-4-0) - Starting task...

Google Gemini (gemini-flash-latest) - Completed in 12.45s
Browser Use (bu-0-1) - Completed in 14.23s
Anthropic Claude (claude-sonnet-4-0) - Completed in 15.67s
OpenAI ChatGPT (gpt-4.1-mini) - Completed in 18.91s

RESULTS SUMMARY
1. Google Gemini (gemini-flash-latest) - 12.45s
2. Browser Use (bu-0-1) - 14.23s
3. Anthropic Claude (claude-sonnet-4-0) - 15.67s
4. OpenAI ChatGPT (gpt-4.1-mini) - 18.91s
```

## How It Works

### Architecture

The tool uses Browser-Use's sandboxed execution environment (`@sandbox()` decorator) to run each LLM in parallel with isolated browser sessions:

1. **Task Input**: You provide a task description via CLI prompt
2. **Parallel Execution**: The tool creates an async task for each configured LLM
3. **Isolated Sessions**: Each LLM gets its own Browser instance
4. **Time Tracking**: Start and end times are recorded for each execution
5. **Results Aggregation**: All results are collected and ranked by completion time

### Supported LLMs

The template comes pre-configured with four LLMs:

1. **Browser Use (bu-0-1)**: Browser-Use's native model
2. **Google Gemini (gemini-flash-latest)**: Fast, efficient model from Google
3. **OpenAI ChatGPT (gpt-4.1-mini)**: Compact version of GPT-4
4. **Anthropic Claude (claude-sonnet-4-0)**: Balanced performance and capability

Each model is initialized with its respective API key from environment variables.

### Sandboxed Execution

The `@sandbox()` decorator ensures:
- Each LLM runs in complete isolation
- Browser sessions don't interfere with each other
- Clean teardown after task completion
- Safe parallel execution without race conditions

## Customization

### Adding More LLMs

To add additional LLMs to the comparison, edit the `llms` list in `main.py`:

```python
llms = [
    ("Browser Use (bu-0-1)", ChatBrowserUse()),
    ("Google Gemini (gemini-flash-latest)", ChatGoogle(model="gemini-flash-latest", api_key=os.getenv("GOOGLE_API_KEY"))),
    ("OpenAI ChatGPT (gpt-4.1-mini)", ChatOpenAI(model="gpt-4.1-mini", api_key=os.getenv("OPENAI_API_KEY"))),
    ("Anthropic Claude (claude-sonnet-4-0)", ChatAnthropic(model="claude-sonnet-4-0", api_key=os.getenv("ANTHROPIC_API_KEY"))),
    # Add your custom LLM here:
    ("Custom Model Name", YourChatModel(model="model-name", api_key=os.getenv("YOUR_API_KEY"))),
]
```

### Using Different Model Versions

Change the model names to test different versions:

```python
# Use different Gemini models
("Gemini Pro", ChatGoogle(model="gemini-pro", api_key=os.getenv("GOOGLE_API_KEY")))

# Use different OpenAI models
("GPT-4", ChatOpenAI(model="gpt-4", api_key=os.getenv("OPENAI_API_KEY")))
("GPT-4o", ChatOpenAI(model="gpt-4o", api_key=os.getenv("OPENAI_API_KEY")))

# Use different Claude models
("Claude Opus", ChatAnthropic(model="claude-opus-4-0", api_key=os.getenv("ANTHROPIC_API_KEY")))
```

### Removing LLMs

To test with fewer LLMs, simply comment out or remove entries from the `llms` list:

```python
llms = [
    ("Browser Use (bu-0-1)", ChatBrowserUse()),
    # ("Google Gemini (gemini-flash-latest)", ChatGoogle(model="gemini-flash-latest", api_key=os.getenv("GOOGLE_API_KEY"))),
    ("OpenAI ChatGPT (gpt-4.1-mini)", ChatOpenAI(model="gpt-4.1-mini", api_key=os.getenv("OPENAI_API_KEY"))),
    # ("Anthropic Claude (claude-sonnet-4-0)", ChatAnthropic(model="claude-sonnet-4-0", api_key=os.getenv("ANTHROPIC_API_KEY"))),
]
```

### Automated Task Lists

To run multiple tasks programmatically without manual input:

```python
async def main():
    tasks = [
        "Find the number of stars of the browser-use repo on GitHub",
        "Go to amazon.com and find the price of the cheapest laptop",
        "Visit reddit.com and find the top post about AI"
    ]

    for task in tasks:
        print(f"\n\nRunning task: {task}")
        # ... rest of the execution logic
```

### Custom Browser Configuration

You can customize browser settings for each execution:

```python
async def execute_task(browser: Browser, task: str, llm: BaseChatModel, llm_name: str):
    agent = Agent(
        browser=browser,
        task=task,
        llm=llm,
        max_steps=20,  # Limit maximum steps
        # Add other Agent configuration options
    )
```

## Troubleshooting

### Missing API Keys

If you see errors about missing API keys:
- Check that `.env` file exists in your project directory
- Verify all required API keys are set in `.env`
- Make sure there are no typos in the environment variable names
- Restart your terminal after updating `.env`

### LLM Failures

If one or more LLMs fail to complete the task:
- The tool will continue running other LLMs and show exceptions in the results
- Check that the API key is valid and has sufficient credits
- Some tasks may be too complex for certain models
- Try simplifying the task or increasing the `max_steps` parameter

### Timeout Issues

For long-running tasks:
- The default Browser-Use timeout is sufficient for most tasks
- If tasks are timing out, the task may be too complex
- Consider breaking complex tasks into simpler subtasks
- Some websites may have slow loading times affecting all models

### Rate Limiting

If you encounter rate limit errors:
- Some API providers have rate limits on requests per minute
- Add delays between runs: `await asyncio.sleep(60)`
- Check your API provider's rate limit documentation
- Consider upgrading your API plan for higher limits

### Import Errors

If you see import errors:
- Make sure you ran `uv sync` to install dependencies
- Verify your Python version is 3.11 or higher: `python --version`
- Try removing and recreating your virtual environment

## Advanced Usage

### Sequential Execution

To run LLMs sequentially instead of in parallel (useful for debugging):

```python
# Replace asyncio.gather with sequential execution
results = []
for name, llm in llms:
    result = await execute_task(task=task_description, llm=llm, llm_name=name)
    results.append(result)
```

### Custom Metrics

Track additional metrics beyond time:

```python
async def execute_task(browser: Browser, task: str, llm: BaseChatModel, llm_name: str):
    start_time = time.time()
    token_count = 0  # Track tokens if available

    agent = Agent(browser=browser, task=task, llm=llm)
    result = await agent.run()
    elapsed = time.time() - start_time

    return {
        'llm': llm_name,
        'result': result,
        'time': elapsed,
        'tokens': token_count,  # Add custom metrics
        'cost': calculate_cost(token_count, llm_name)  # Estimate cost
    }
```

### Logging Results

Save results to a file for later analysis:

```python
import json
from datetime import datetime

async def main():
    # ... run tasks ...

    # Save results
    output = {
        'timestamp': datetime.now().isoformat(),
        'task': task_description,
        'results': valid_results
    }

    with open('llm_comparison_results.json', 'a') as f:
        json.dump(output, f)
        f.write('\n')
```

### Batch Testing

Run multiple tasks and aggregate results:

```python
async def batch_test():
    tasks = ["task1", "task2", "task3"]
    all_results = []

    for task in tasks:
        print(f"\n\nTesting: {task}")
        # ... run comparison ...
        all_results.append({
            'task': task,
            'results': results
        })

    # Analyze aggregate performance
    print("\n\nAGGREGATE PERFORMANCE")
    for llm_name in ["Browser Use", "Google Gemini", "OpenAI ChatGPT", "Anthropic Claude"]:
        avg_time = calculate_average_time(all_results, llm_name)
        print(f"{llm_name}: {avg_time:.2f}s average")
```

## Use Cases

- **Model Selection**: Choose the best LLM for your specific use case
- **Benchmarking**: Compare performance across different tasks
- **Cost Optimization**: Identify which models are most cost-effective
- **Quality Assessment**: Evaluate output quality across models
- **Research**: Study how different models approach the same task
- **Development**: Test automation workflows with multiple AI providers
- **A/B Testing**: Compare model versions or configurations

## Performance Considerations

- **Parallel Execution**: Running 4 LLMs simultaneously requires sufficient system resources
- **Network Bandwidth**: Multiple browser sessions may consume significant bandwidth
- **API Costs**: Running multiple LLMs per task will multiply your API usage
- **Memory Usage**: Each browser instance requires memory (typically 200-500MB each)

## Privacy & Ethics

**Important considerations**:

- API keys should never be committed to version control
- Some websites may prohibit automated access - check terms of service
- Be mindful of rate limits and server load on target websites
- Different LLMs may handle personal data differently - review each provider's privacy policy
- Use for legitimate testing, development, and research purposes only

## Support

For issues specific to:
- **Browser-Use**: [https://docs.browser-use.com](https://docs.browser-use.com)
- **Google AI**: [https://ai.google.dev/docs](https://ai.google.dev/docs)
- **OpenAI**: [https://platform.openai.com/docs](https://platform.openai.com/docs)
- **Anthropic**: [https://docs.anthropic.com](https://docs.anthropic.com)
- **This template**: Check the browser-use/template-library repository
