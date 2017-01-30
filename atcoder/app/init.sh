#!/bin/sh

psql -U postgres -h pgsql -f create_database.sql atcoderdb

sh contest_crawler.sh
sh solved_crawler.sh
psql -U postgres -c 'UPDATE solved SET checked=True;' atcoderdb

sh crawl.sh
