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
2.  Create a file named `config.ini` in the `reddit-intelligence-tool` directory.
3.  Add your Reddit API credentials to the `config.ini` file in the following format:

    ```ini
    [reddit]
    client_id = 
    client_secret = 
    user_agent = YOUR_USER_AGENT
    ```

## Usage

```bash
python3 main.py --subreddit <rsmallbusiness> --report-type <overview> [--output <redditreporttest.csv>]
```

### Arguments

-   `--subreddit`: The subreddit to analyze.
-   `--report-type`: The type of report to generate.
    -   `overview`: A brief overview of the subreddit.
    -   `detailed`: A more detailed analysis.
-   `--output`: Optional. Output filename for CSV export. If provided, the report data will be saved to this CSV file.

### Examples

```bash
# Generate an overview report for r/learnpython
python3 main.py --subreddit learnpython --report-type overview

# Generate a detailed report for r/learnpython and save to a CSV file
python3 main.py --subreddit learnpython --report-type detailed --output learnpython_detailed.csv
```
