#!/bin/bash
nohup python -u startDailySearchHistoryCrawler.py >> logs/dailySearchCrawler.log 2>&1 &