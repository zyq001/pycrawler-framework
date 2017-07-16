#!/bin/bash
nohup python -u startSearchHistoryCrawler.py >> logs/dailySearchCrawler.log 2>&1 &