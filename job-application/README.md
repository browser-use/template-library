# Job Application Template

Automate job application form submission using Browser-Use with AI-powered form filling.

## What This Does

This template demonstrates automated job application submission for Rochester Regional Health. The agent will:

1. Navigate to the job application page
2. Fill out personal information (name, email, phone, address)
3. Upload your resume/CV file
4. Complete demographic and optional fields
5. Submit the application and confirm success

The template uses Google's `gemini-3-pro-preview` model which excels at complex multi-step tasks like form filling.

## Setup

### 1. Get Your API Key

You'll need a Google Gemini API key to use the gemini-3-pro-preview model:
1. Go to [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
2. Create a new API key
3. Copy the key

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and add your Google API key:
```bash
GOOGLE_API_KEY=your-google-api-key-here
```

### 3. Install Dependencies

```bash
uv sync
```

## Usage

### Basic Usage (with included example data)

```bash
uv run main.py --resume example_resume.pdf
```

This will use the included `applicant_data.json` with example information.

### With Your Own Data

1. Create your own applicant data JSON file (see format below)
2. Prepare your resume as a PDF file
3. Run the script:

```bash
uv run main.py --data my_info.json --resume my_resume.pdf
```

### Applicant Data Format

Create a JSON file with your information:

```json
{
	"first_name": "Your",
	"last_name": "Name",
	"email": "your.email@example.com",
	"phone": "5551234567",
	"age": "21",
	"US_citizen": true,
	"sponsorship_needed": false,
	"postal_code": "12345",
	"country": "United States",
	"city": "YourCity",
	"address": "123 Your Street",
	"gender": "Your Gender",
	"race": "Your Race/Ethnicity",
	"Veteran_status": "I am not a veteran",
	"disability_status": "No, I do not have a disability"
}
```

## How It Works

### 8-Step Application Process

The agent follows a detailed 8-step process:

1. **Personal Info**: First name, last name, email, phone
2. **Resume Upload**: Upload your CV/resume file
3. **Address Info**: Postal code, country, state, city, address, age
4. **Authorization**: Work authorization, visa sponsorship, professional license
5. **Healthcare Interest**: Write about what drew you to healthcare
6. **Demographics**: Experience, gender, race, veteran status, disability status
7. **Date**: Today's date
8. **Submit**: Click submit button and verify success

### Why gemini-3-pro-preview Model?

This template uses Google's `gemini-3-pro-preview` model because:
- **Complex reasoning**: Job applications require understanding context and making decisions
- **Multi-step planning**: The agent needs to plan and execute 8 sequential steps
- **Form field detection**: Accurately identifies and fills the right fields
- **Error handling**: Can adapt when fields don't match exactly

**Note**: For simpler forms, you might want to try `gemini-flash-latest` instead for faster and cheaper processing.

### Cross-Origin iFrame Support

The Rochester Regional Health application uses an embedded iframe for the form. This template enables `cross_origin_iframes=True` in the browser configuration to handle this correctly.

## Customization

### For Different Job Applications

To adapt this template for other job applications:

1. **Update the URL**: Change the job application URL in `main.py` (line ~68):
   ```python
   - Navigate to https://your-job-application-url.com
   ```

2. **Modify the task steps**: Update the 8-step instructions to match the new form structure

3. **Adjust applicant data**: Add or remove fields in your JSON file as needed

4. **Update custom tools**: If the form requires special interactions, add custom tool actions

### Example: Generic Application

For a more generic job application template:

```python
task = f"""
Navigate to {job_url} and fill out the job application with this data: {applicant_info}

Steps:
1. Identify all form fields on the page
2. Match form fields to data in applicant_info
3. Fill out each field sequentially from top to bottom
4. Upload resume when you find a file upload field
5. Submit the application
6. Confirm successful submission
"""
```

### Changing the Model

To use a different model, edit `main.py`:

```python
# For faster and cheaper:
llm = ChatGoogle(model='gemini-flash-latest')

# For other providers like OpenAI:
from browser_use import ChatOpenAI
llm = ChatOpenAI(model='gpt-4o')
```

## Troubleshooting

### Application Not Submitting

- **Check field matching**: The form fields might have changed. Review the agent's logs to see which fields it's trying to fill
- **Manual verification**: Run in headful mode to watch the agent work and identify issues
- **Update task prompt**: Adjust the step-by-step instructions to match the current form

### Resume Upload Failing

- **File format**: Ensure your resume is in PDF format
- **File path**: Use absolute paths or ensure the file is in the correct location
- **File permissions**: Make sure the resume file is readable

### Gemini API Errors

- **Rate limits**: If you hit rate limits, wait a few minutes between runs
- **Quota**: Check your Google Cloud quota to ensure you haven't hit limits
- **API key**: Verify your API key is correct and has Gemini API access enabled

### Form Fields Changed

Job application forms change frequently. If the template stops working:

1. Visit the application URL manually to see what changed
2. Update the task prompt with the new field names
3. Adjust the 8-step process if fields were added/removed
4. Test with `--help` flag to see agent's reasoning

## Model Costs

The gemini-3-pro-preview model offers competitive pricing:
- Google Gemini API has generous free tier for development
- Production usage is cost-effective compared to other frontier models

A typical job application uses moderate tokens. For high-volume usage, consider the free tier limits and pricing structure.

For reference on costs and capabilities, see: [https://ai.google.dev/pricing](https://ai.google.dev/pricing)

## Advanced Usage

### Batch Applications

To apply to multiple jobs, create a script:

```python
import asyncio
from pathlib import Path

jobs = [
	("job1_data.json", "https://job1-url.com"),
	("job2_data.json", "https://job2-url.com"),
]

for data_file, url in jobs:
	# Update URL in code or pass as parameter
	# Run application
	await main(data_file, "resume.pdf")
	await asyncio.sleep(60)  # Be respectful with rate limits
```

### Integration with ATS Systems

Many companies use Applicant Tracking Systems (ATS) like:
- Workday
- Greenhouse
- Lever
- iCIMS

Each has different form structures. You'll need to customize the task prompt for each ATS type.

## Privacy & Ethics

**Important considerations**:

- Only use this for legitimate job applications where you're a qualified candidate
- Do not spam companies with applications
- Be honest in your application data
- Respect rate limits and server load
- Some companies prohibit automated applications - check their terms of service
- This tool fills forms but doesn't write cover letters or fabricate experience

## Support

For issues specific to Browser-Use, see:
- Documentation: [https://docs.browser-use.com](https://docs.browser-use.com)
- GitHub: [https://github.com/browser-use/browser-use](https://github.com/browser-use/browser-use)

For job application best practices, consult career resources and ensure your applications are genuine and compliant with employer requirements.
