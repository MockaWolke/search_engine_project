import os
from src import REPO_PATH, INDEXES_DIR
from src.crawl import parse_domain_index
import argparse
import json

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--domain", type=str)
parser.add_argument("-s", "--save_to", type=str)
parser.add_argument("-t", "--total", type=int, default=200)
parser.add_argument("-o", "--timeout", type=int, default=3)
parser.add_argument("-n", "--new_pages_limit", type=int, default=20)
parser.add_argument("-w", "--weight_by_length", type=bool, default=True)
parser.add_argument("-m", "--max_url_len", type=int, default=200)

args = parser.parse_args()


os.chdir(REPO_PATH)

save_to = os.path.join(INDEXES_DIR, args.save_to)

parse_domain_index(
    args.domain,
    save_to,
    args.total,
    args.timeout,
    args.new_pages_limit,
    args.weight_by_length,
    args.max_url_len,
)

with open(
    os.path.join(
        save_to,
        "args.json",
    ),
    "w",
) as f:
    json.dump(vars(args), f)
