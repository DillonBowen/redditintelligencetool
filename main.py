import argparse
import configparser

from app.core import generate_report, get_reddit_instance, save_to_csv


def main():
    parser = argparse.ArgumentParser(description='A CLI tool to gather intelligence from Reddit.')
    parser.add_argument('--subreddit', type=str, required=True, help='The subreddit to analyze.')
    parser.add_argument('--report-type', type=str, required=True, choices=['overview', 'detailed'], help='The type of report to generate.')
    parser.add_argument('--output', type=str, help='Output filename for CSV export.')

    args = parser.parse_args()

    try:
        reddit = get_reddit_instance()
        posts_data = generate_report(reddit, args.subreddit, args.report_type)

        if args.output:
            save_to_csv(posts_data, args.output)
    except (ValueError, configparser.Error) as exc:
        print(f"Error: {exc}")
    except Exception as exc:
        print(f"An unexpected error occurred: {exc}")


if __name__ == '__main__':
    main()
