import configparser
import csv
import os
from typing import Callable, Dict, List, Optional

import praw

os.environ['PYTHON_KEYRING_BACKEND'] = 'keyring.backends.null.Keyring'


def get_reddit_instance(config_file: str = 'config.ini') -> praw.Reddit:
    config = configparser.ConfigParser()
    read_files = config.read(config_file)

    if not read_files:
        raise ValueError(f"Configuration file {config_file} not found or unreadable.")
    if 'reddit' not in config:
        raise ValueError(f"Missing 'reddit' section in {config_file}")

    credentials = config['reddit']
    required_fields = ['client_id', 'client_secret', 'user_agent']
    missing = [field for field in required_fields if not credentials.get(field)]
    if missing:
        raise ValueError(f"Missing credentials in {config_file}: {', '.join(missing)}")

    return praw.Reddit(
        client_id=credentials.get('client_id'),
        client_secret=credentials.get('client_secret'),
        user_agent=credentials.get('user_agent'),
        username=credentials.get('username'),
        password=credentials.get('password')
    )


def _extract_submission_data(submission) -> Dict[str, object]:
    author_name = submission.author.name if submission.author else '[deleted]'
    return {
        'title': submission.title,
        'author': author_name,
        'score': submission.score,
        'comments': submission.num_comments,
        'url': submission.url,
    }


def generate_overview_report(
    reddit: praw.Reddit,
    subreddit_name: str,
    limit: int = 10,
    row_callback: Optional[Callable[[Dict[str, object]], None]] = None,
) -> List[Dict[str, object]]:
    subreddit = reddit.subreddit(subreddit_name)
    posts_data: List[Dict[str, object]] = []
    for submission in subreddit.hot(limit=limit):
        row_data = _extract_submission_data(submission)
        posts_data.append(row_data)
        if row_callback:
            row_callback(row_data)
    return posts_data


def generate_detailed_report(
    reddit: praw.Reddit,
    subreddit_name: str,
    limit: int = 10,
    row_callback: Optional[Callable[[Dict[str, object]], None]] = None,
) -> List[Dict[str, object]]:
    subreddit = reddit.subreddit(subreddit_name)
    posts_data: List[Dict[str, object]] = []
    for submission in subreddit.hot(limit=limit):
        row_data = _extract_submission_data(submission)
        posts_data.append(row_data)
        if row_callback:
            row_callback(row_data)
    return posts_data


REPORT_GENERATORS = {
    'overview': generate_overview_report,
    'detailed': generate_detailed_report,
}


def generate_report(
    reddit: praw.Reddit,
    subreddit_name: str,
    report_type: str,
    limit: int = 10,
    row_callback: Optional[Callable[[Dict[str, object]], None]] = None,
) -> List[Dict[str, object]]:
    generator = REPORT_GENERATORS.get(report_type)
    if generator is None:
        raise ValueError(f"Unsupported report type: {report_type}")
    return generator(reddit, subreddit_name, limit=limit, row_callback=row_callback)


def save_to_csv(data: List[Dict[str, object]], filename: str) -> None:
    if not data:
        raise ValueError("No data to save.")

    keys = data[0].keys()
    with open(filename, 'w', newline='', encoding='utf-8') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)
