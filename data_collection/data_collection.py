#!/usr/bin/python3
import sys
sys.stdout = open('output.out', 'w')

import dota2api

MY_API_KEY = '9CDC370E485F4DF1EE5615AEB59B1A98'
api = dota2api.Initialise(MY_API_KEY)

match = api.get_match_details(match_id=3983328713)
print(match['radiant_win'])
