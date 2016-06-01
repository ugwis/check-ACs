#!/bin/sh
cd `dirname $0`
python solved_crawler.py
python tweet_graph.py
