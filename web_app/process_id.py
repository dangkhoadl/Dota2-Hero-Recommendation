import re
import requests
import json

MY_API = ''
OPEN_DOTA_PLAYER = 'https://api.opendota.com/api/players/{}/?api_key=' + MY_API
OPEN_DOTA_WL = \
    'https://api.opendota.com/api/players/{}/wl?date={}&api_key=' + MY_API


def clean_input(userid_list):
    '''Only allow string with number(0-9), length [1:12] '''
    try:
        userid_list = userid_list.split(',')
        userid_list = list(map(
            lambda x: x.strip(' '),
            userid_list))
        userid_list = list(filter(
            lambda x: bool(re.match('^[\d]{1,12}$', x)),
            userid_list))
    except:
        userid_list = None
    return userid_list


def get_player_response(player_id):
    '''Get player data request'''
    try:
        response = requests \
            .get(OPEN_DOTA_PLAYER.format(str(player_id)))
        data_json = json.loads(response.content.decode('utf-8'))
    except:
        data_json = None
    return data_json


def get_win_lose_response(player_id, period='w'):
    '''Get win lose stats by week/month/year'''
    try:
        days = 7
        if period == 'w':
            days = 7
        elif period == 'm':
            days = 30
        elif period == 'y':
            days = 365
        else:
            days = 7
        response = requests \
            .get(OPEN_DOTA_WL.format(str(player_id), str(days)))
        data_json = json.loads(response.content.decode('utf-8'))
    except:
        data_json = None
    return data_json


def calculate_winrate(win, lose):
    try:
        if (win + lose) == 0:
            return -1.00
        result = round(
            float(win) * 100.0 /
            (float(win) + float(lose)), 2)
    except:
        result = None
    return result


def get_player(player_id):
    '''Print player attributes'''
    try:
        player_data = get_player_response(player_id)

        wl_w_data = get_win_lose_response(player_id, 'w')
        w_winrate = calculate_winrate(
            wl_w_data['win'],
            wl_w_data['lose'])

        wl_m_data = get_win_lose_response(player_id, 'm')
        m_winrate = calculate_winrate(
            wl_m_data['win'],
            wl_m_data['lose'])

        wl_y_data = get_win_lose_response(player_id, 'y')
        y_winrate = calculate_winrate(
            wl_y_data['win'],
            wl_y_data['lose'])

        # some player name contain ', "
        return {
            'player_id': int(player_data['profile']['account_id']),
            'player_name':
                re.sub('[\'\"]', '', player_data['profile']['personaname']),
            'week_wr': w_winrate,
            'month_wr': m_winrate,
            'year_wr': y_winrate
        }
    except:
        return None
