#!/bin/sh

psql -U postgres -h pgsql -f create_database.sql atcoderdb

python contest_crawler.py
python solved_crawler.py
psql -U postgres -c 'UPDATE solved SET checked=True;' atcoderdb

sh crawl.sh
