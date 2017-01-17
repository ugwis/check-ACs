#!/bin/sh
cd `dirname $0`
python contest_crawler.py
python solved_crawler.py
python tweet_graph.py
