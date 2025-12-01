import argparse
import configparser
import csv
import os
from collections import Counter
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Iterable, List, Optional

import praw

os.environ['PYTHON_KEYRING_BACKEND'] = 'keyring.backends.null.Keyring'


@dataclass
class PostRecord:
    title: str
    author: str
    score: int
    comments: int
    url: str
    created_at: datetime


def get_reddit_instance(config_file: str = 'config.ini') -> praw.Reddit:
    """Create an authenticated Reddit client from a config file."""

    if not os.path.exists(config_file):
        raise FileNotFoundError(
            f"Configuration file '{config_file}' not found. Please create it using config.example.ini as a template."
        )

    config = configparser.ConfigParser()
    config.read(config_file)

    if 'reddit' not in config:
        raise ValueError(f"Missing 'reddit' section in {config_file}")

    credentials = config['reddit']
    required_fields = ['client_id', 'client_secret', 'user_agent']
    missing_fields = [field for field in required_fields if not credentials.get(field)]
    if missing_fields:
        raise ValueError(f"Missing required credentials in {config_file}: {', '.join(missing_fields)}")

    return praw.Reddit(
        client_id=credentials.get('client_id'),
        client_secret=credentials.get('client_secret'),
        user_agent=credentials.get('user_agent'),
        username=credentials.get('username'),
        password=credentials.get('password')
    )


def _format_author(author: Optional[praw.models.Redditor]) -> str:
    return f"u/{author.name}" if author else "[deleted]"


def fetch_posts(reddit: praw.Reddit, subreddit_name: str, sort: str, limit: int, time_filter: str) -> List[PostRecord]:
    subreddit = reddit.subreddit(subreddit_name)

    if sort == 'new':
        submissions: Iterable = subreddit.new(limit=limit)
    elif sort == 'top':
        submissions = subreddit.top(time_filter=time_filter, limit=limit)
    else:
        submissions = subreddit.hot(limit=limit)

    posts: List[PostRecord] = []
    for submission in submissions:
        author_name = _format_author(submission.author)
        posts.append(
            PostRecord(
                title=submission.title,
                author=author_name,
                score=submission.score,
                comments=submission.num_comments,
                url=submission.url,
                created_at=datetime.fromtimestamp(submission.created_utc)
            )
        )
    return posts


def generate_overview_report(posts: List[PostRecord]) -> None:
    print("\nTop posts:")
    for post in posts:
        print(f"- {post.title} ({post.score} pts, {post.comments} comments)")


def generate_detailed_report(posts: List[PostRecord]) -> None:
    print("\nDetailed posts:")
    for post in posts:
        print("---")
        print(f"Title: {post.title}")
        print(f"Author: {post.author}")
        print(f"Score: {post.score}")
        print(f"Comments: {post.comments}")
        print(f"Posted: {post.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"URL: {post.url}")


def generate_summary(posts: List[PostRecord]) -> None:
    if not posts:
        print("No posts found to summarize.")
        return

    scores = [post.score for post in posts]
    comments = [post.comments for post in posts]
    authors = Counter(post.author for post in posts)

    print("\nSummary:")
    print(f"Total posts analyzed: {len(posts)}")
    print(f"Average score: {sum(scores) / len(scores):.2f}")
    print(f"Average comments: {sum(comments) / len(comments):.2f}")

    most_common_authors = authors.most_common(3)
    if most_common_authors:
        author_summary = ', '.join(f"{author} ({count})" for author, count in most_common_authors)
        print(f"Top contributors: {author_summary}")

    top_posts = sorted(posts, key=lambda post: post.score, reverse=True)[:3]
    print("\nTop posts by score:")
    for post in top_posts:
        print(f"- {post.title} by {post.author} ({post.score} pts)")


def save_to_csv(posts: List[PostRecord], filename: str) -> None:
    if not posts:
        print("No data to save.")
        return

    rows = [asdict(post) for post in posts]
    keys = rows[0].keys()
    with open(filename, 'w', newline='', encoding='utf-8') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(rows)
    print(f"Data saved to {filename}")


def main() -> None:
    parser = argparse.ArgumentParser(description='A CLI tool to gather intelligence from Reddit.')
    parser.add_argument('--subreddit', type=str, required=True, help='The subreddit to analyze.')
    parser.add_argument('--report-type', type=str, required=True, choices=['overview', 'detailed', 'summary'], help='The type of report to generate.')
    parser.add_argument('--sort', type=str, choices=['hot', 'new', 'top'], default='hot', help='How to sort posts before analysis.')
    parser.add_argument('--limit', type=int, default=15, help='Number of posts to analyze.')
    parser.add_argument('--time-filter', type=str, choices=['all', 'day', 'hour', 'month', 'week', 'year'], default='week', help='Time filter when sorting by top posts.')
    parser.add_argument('--output', type=str, help='Output filename for CSV export.')

    args = parser.parse_args()

    try:
        reddit = get_reddit_instance()
        posts = fetch_posts(reddit, args.subreddit, args.sort, args.limit, args.time_filter)

        print(f"Generating {args.report_type} report for r/{args.subreddit} ({len(posts)} posts)...")
        if args.report_type == 'overview':
            generate_overview_report(posts)
        elif args.report_type == 'detailed':
            generate_detailed_report(posts)
        elif args.report_type == 'summary':
            generate_summary(posts)

        if args.output:
            save_to_csv(posts, args.output)

    except (ValueError, FileNotFoundError, configparser.Error) as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == '__main__':
    main()

