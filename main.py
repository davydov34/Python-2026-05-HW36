import argparse
import asyncio
from datetime import datetime as dt
from parser import parsing_loop

from logger import logger as to_log

URL = "https://news.ycombinator.com"


def main():
    parser_args = argparse.ArgumentParser()
    parser_args.add_argument("-t", "--time", type=int, default=30)
    parser_args.add_argument("-d", "--dir", type=str, default="parsing_data")
    args = parser_args.parse_args()

    to_log.info(
        'Start parse session with time = %d and dir = "%s" at %s',
        args.time,
        args.dir,
        dt.now().strftime("%d.%m.%Y %H:%M:%S"),
    )
    asyncio.run(parsing_loop(args=args, url=URL))
    to_log.info(
        "The application has been stopped at %s", dt.now().strftime("%d.%m.%Y %H:%M:%S")
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        to_log.info(
            "The work was interrupted by pressing Ctrl+C at %s",
            dt.now().strftime("%d.%m.%Y %H:%M:%S"),
        )
    except Exception as e:
        to_log.error("Error: %s", str(e))
