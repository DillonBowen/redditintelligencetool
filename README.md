# Reddit Intelligence Tool

This is a command-line interface (CLI) tool to gather intelligence from Reddit.

## Prerequisites

- Python 3
- Pip

## Installation

1.  Clone this repository.
2.  Create a virtual environment:
    ```bash
    python3 -m venv venv
    ```
3.  Activate the virtual environment:
    ```bash
    source venv/bin/activate
    ```
4.  Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

1.  Create a Reddit application to get your API credentials. You can do this by going to [https://www.reddit.com/prefs/apps](https://www.reddit.com/prefs/apps) and clicking "are you a developer? create an app...".
2.  Copy `config.example.ini` to `config.ini` in the project root (or point the CLI at a different path via `--config`).
3.  Add your Reddit API credentials to the `config.ini` file in the following format:

    ```ini
    [reddit]
    client_id = 
    client_secret = 
    user_agent = YOUR_USER_AGENT
    ```

## Usage

```bash
python3 main.py --subreddit <rsmallbusiness> --report-type <overview|detailed|summary> [--sort <hot|new|top>] [--limit <15>] [--time-filter <week>] [--output <redditreporttest.csv>] [--config <config.ini>] [--demo]
```

### Arguments

-   `--subreddit`: The subreddit to analyze.
-   `--report-type`: The type of report to generate.
    -   `overview`: A concise list of the hottest posts with scores and comment counts.
    -   `detailed`: Richer output including timestamps and authors.
    -   `summary`: Aggregated metrics (averages, top contributors, and highest-scoring posts).
-   `--sort`: Optional. How to sort posts before analysis. Choices are `hot`, `new`, and `top`.
-   `--limit`: Optional. Number of posts to analyze (default: 15).
-   `--time-filter`: Optional. Only used when `--sort top` is provided. Choices are `all`, `day`, `hour`, `month`, `week`, `year` (default: `week`).
-   `--output`: Optional. Output filename for CSV export. If provided, the report data will be saved to this CSV file.
-   `--config`: Optional. Path to a configuration file containing Reddit credentials. Defaults to `config.ini` in the project root.
-   `--demo`: Optional. Use built-in sample posts so you can try the CLI without Reddit credentials or network access.

### Examples

```bash
# Generate an overview report for r/learnpython
python3 main.py --subreddit learnpython --report-type overview

# Generate a detailed report for the top posts this month
python3 main.py --subreddit learnpython --report-type detailed --sort top --time-filter month

# Generate a summary report and save to a CSV file
python3 main.py --subreddit learnpython --report-type summary --output learnpython_summary.csv

# Try the tool without Reddit credentials using demo data
python3 main.py --subreddit smallbusiness --report-type overview --demo
```
