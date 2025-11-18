import argparse
import praw
import configparser
import csv
import os
os.environ['PYTHON_KEYRING_BACKEND'] = 'keyring.backends.null.Keyring'

def get_reddit_instance(config_file='config.ini'):
    config = configparser.ConfigParser()
    config.read(config_file)

    if 'reddit' not in config:
        raise ValueError(f"Missing 'reddit' section in {config_file}")

    credentials = config['reddit']
    
    return praw.Reddit(
        client_id=credentials.get('client_id'),
        client_secret=credentials.get('client_secret'),
        user_agent=credentials.get('user_agent'),
        username=credentials.get('username'),
        password=credentials.get('password')
    )

def generate_overview_report(reddit, subreddit_name):
    print(f"Generating overview report for r/{subreddit_name}...")
    subreddit = reddit.subreddit(subreddit_name)
    posts_data = []
    for submission in subreddit.hot(limit=10):
        print(f"- {submission.title}")
        posts_data.append({
            'title': submission.title,
            'author': submission.author.name,
            'score': submission.score,
            'comments': submission.num_comments,
            'url': submission.url
        })
    return posts_data

def generate_detailed_report(reddit, subreddit_name):
    print(f"Generating detailed report for r/{subreddit_name}...")
    subreddit = reddit.subreddit(subreddit_name)
    posts_data = []
    for submission in subreddit.hot(limit=10):
        print(f"---")
        print(f"Title: {submission.title}")
        print(f"Author: u/{submission.author.name}")
        print(f"Score: {submission.score}")
        print(f"Comments: {submission.num_comments}")
        print(f"URL: {submission.url}")
        posts_data.append({
            'title': submission.title,
            'author': submission.author.name,
            'score': submission.score,
            'comments': submission.num_comments,
            'url': submission.url
        })
    print(f"---")
    return posts_data

def save_to_csv(data, filename):
    if not data:
        print("No data to save.")
        return

    keys = data[0].keys()
    with open(filename, 'w', newline='', encoding='utf-8') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)
    print(f"Data saved to {filename}")

def main():
    parser = argparse.ArgumentParser(description='A CLI tool to gather intelligence from Reddit.')
    parser.add_argument('--subreddit', type=str, required=True, help='The subreddit to analyze.')
    parser.add_argument('--report-type', type=str, required=True, choices=['overview', 'detailed'], help='The type of report to generate.')
    parser.add_argument('--output', type=str, help='Output filename for CSV export.')

    args = parser.parse_args()

    try:
        reddit = get_reddit_instance()
        posts_data = []
        if args.report_type == 'overview':
            posts_data = generate_overview_report(reddit, args.subreddit)
        elif args.report_type == 'detailed':
            posts_data = generate_detailed_report(reddit, args.subreddit)
        
        if args.output:
            save_to_csv(posts_data, args.output)

    except (ValueError, configparser.Error) as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == '__main__':
    main()

