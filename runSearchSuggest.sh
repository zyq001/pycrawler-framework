#!/bin/bash
nohup python -u startSearchSuggest.py 200000 >> logs/searchSuggest.log 2>&1 &