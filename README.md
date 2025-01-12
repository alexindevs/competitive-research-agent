# Competitive Research AI Agent

An AI-powered competitive analysis tool that automatically monitors and analyzes competitors' websites, generating comprehensive weekly reports about market changes, pricing updates, product launches, and strategic shifts.

## Features

- 🔍 Automated website scraping and content analysis
- 📊 Vector-based storage of historical competitor data
- 🤖 LLM-powered analysis using Ollama
- 📈 Weekly report generation with structured insights
- 🔄 Historical change tracking and comparison
- 📝 JSON-formatted competitor data management

## Prerequisites

- Python 3.10+
- Ollama server running (local or remote)
- Virtual environment (recommended)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/alexindevs/competitive-research-agent.git
cd competitive-research-agent
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Linux/Mac
# or
.\venv\Scripts\activate  # On Windows
```

3. Install required packages:
```bash
pip install llama-index-core llama-index-llms-ollama pandas aiohttp beautifulsoup4 llama-index-embeddings-ollama
```

## Configuration

1. Create a `competitors.json` file in the project root:
```json
{
  "competitors": [
    {
      "name": "CompetitorA",
      "website": "https://www.competitora.com",
      "social_media": {
        "twitter": "https://twitter.com/competitorA",
        "linkedin": "https://linkedin.com/company/competitorA"
      }
    }
  ]
}
```

2. Update the Ollama configuration in `agent.py` if needed:
```python
base_url="http://your-ollama-server:11434"
model="your-model-name"
```

## Usage

Run the agent:
```bash
python agent.py
```

The agent will:
1. Load competitor information from competitors.json
2. Scrape each competitor's website
3. Store and analyze the content using LlamaIndex
4. Generate a comprehensive weekly report
5. Save the report in the `reports` directory

## Output

Reports are saved in the `reports` directory with timestamps:
```
reports/
  competitive_analysis_report_20250112.txt
```

Each report includes:
- Executive Summary
- Key Findings by Competitor
- Market Trends
- Historical Changes
- Recommendations

## Project Structure

```
competitive-research-agent/
├── agent.py              # Main agent implementation
├── competitors.json      # Competitor configuration
├── reports/             # Generated reports
├── competitor_data/     # Vector store database
└── README.md            # This file
```

## Automating Execution

To ensure the agent runs automatically on a schedule, you can set it up using either a cron job or systemd service.

### Using Cron Job

1. Open the crontab editor:
```bash
crontab -e
```

2. Add the following entry to run the agent every Monday at 8 AM:
```bash
0 8 * * 1 /path/to/venv/bin/python /path/to/competitive-research-agent/agent.py
```

3. Save and exit. The cron job will now run the script weekly.

### Using Systemd Service

1. Create a new service file:
```bash
sudo nano /etc/systemd/system/competitive-research-agent.service
```

2. Add the following content:
```ini
[Unit]
Description=Competitive Research AI Agent
After=network.target

[Service]
Type=simple
ExecStart=/path/to/venv/bin/python /path/to/competitive-research-agent/agent.py
WorkingDirectory=/path/to/competitive-research-agent
Restart=on-failure
User=your-username

[Install]
WantedBy=multi-user.target
```

3. Save and exit the file.

4. Enable and start the service:
```bash
sudo systemctl enable competitive-research-agent.service
sudo systemctl start competitive-research-agent.service
```

5. Check the status to confirm it’s running:
```bash
sudo systemctl status competitive-research-agent.service
```

The agent will now automatically execute based on the systemd configuration.

## Advanced Usage

### Adding New Competitors

Add new competitors to `competitors.json`:
```json
{
  "competitors": [
    {
      "name": "NewCompetitor",
      "website": "https://www.newcompetitor.com",
      "social_media": {
        "twitter": "https://twitter.com/newcompetitor",
        "linkedin": "https://linkedin.com/company/newcompetitor"
      }
    }
  ]
}
```

### Customizing Analysis

Modify the analysis prompts in `agent.py`:
```python
historical_query = """
Your custom historical analysis prompt here
"""
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request