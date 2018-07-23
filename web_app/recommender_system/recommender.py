import re
import requests
import json
import math
import operator

MY_API_HEROES = ''
OPEN_DOTA_PLAYER_HEROES = \
    'https://api.opendota.com/api/players/{}/heroes/?api_key=' + MY_API_HEROES


def clean_player_id(user_id_input):
    '''Only allow string with number(0-9), length [1:12] '''
    try:
        user_id = user_id_input \
            .split(',')[0] \
            .strip(' ')
        user_id = user_id if bool(re.match('^[\d]{1,12}$', user_id)) else None
    except:
        user_id = None
    return user_id


# Recommender system
def pearson_similarity(person1, person2, data):
    '''Pearson correlation coefficient calculation'''
    # [TODO] Reimplement the PCC calculation algorithm
    common_ranked_items = [
        itm for itm in data[person1] if itm in data[person2]]
    n = len(common_ranked_items)

    s1 = sum([
        data[person1][item] for item in common_ranked_items])
    s2 = sum([
        data[person2][item] for item in common_ranked_items])

    ss1 = sum([
        pow(data[person1][item], 2) for item in common_ranked_items])
    ss2 = sum([
        pow(data[person2][item], 2) for item in common_ranked_items])

    ps = sum([
        data[person1][item] * data[person2][item]
        for item in common_ranked_items])

    num = n * ps - (s1 * s2)
    den = math.sqrt((n * ss1 - math.pow(s1, 2)) * (n * ss2 - math.pow(s2, 2)))

    return (num / den) if den != 0 else 0


def recommend(person, bound, data, similarity=pearson_similarity):
    '''Find the most similarities(most correlated) entry'''
    # [TODO] reconfig the dataset input
    scores = [
        (similarity(person, other, data), other)
        for other in data if other != person]

    scores.sort()
    scores.reverse()
    scores = scores[0:bound]
    recomms = {}

    for sim, other in scores:
        ranked = data[other]

        for itm in ranked:
            if itm not in data[person]:
                weight = sim * ranked[itm]

                if itm in recomms:
                    s, weights = recomms[itm]
                    recomms[itm] = (s + sim, weights + [weight])
                else:
                    recomms[itm] = (sim, [weight])

    for r in recomms:
        sim, item = recomms[r]
        recomms[r] = sum(item) / sim

    return recomms, scores


def get_player_stats_response(player_id):
    '''Get player stats request'''
    try:
        response = requests.get(OPEN_DOTA_PLAYER_HEROES.format(player_id))
        data_json = json.loads(response.content.decode('utf-8'))
    except:
        data_json = None
    return data_json


# Algorithm to compute score
def compute_score(user_hero_stats, player_id):
    try:
        total_scores = 0.0
        hero_data = {}
        total_score = 0.0

        for entry in user_hero_stats:
            if entry['games'] != 0:
                hero_id = entry['hero_id']
                # [TODO] try a new score implementation
                score = entry['win'] * entry['win'] / entry['games']
                total_score += score

                hero_data[hero_id] = score

        # [TODO] try a new score normalization implementation
        for key, value in hero_data.items():
            normalized_score = 100.0 * value / total_score
            hero_data[key] = normalized_score
    except:
        hero_data = None
    return hero_data


def recommend_user(player_id, data, hero_name):
    try:
        user_hero_stats = get_player_stats_response(player_id)
        hero_data = compute_score(user_hero_stats, player_id)
        data[str(player_id)] = hero_data

        results, scores = recommend(str(player_id), 10, data)
        sorted_hero_data = sorted(
            hero_data.items(),
            key=operator.itemgetter(1),
            reverse=True)[0:3]

        # [TODO] move the message config to html
        message = '''
            Your best heroes are:
                <a href="https://www.opendota.com/players/
                    {0}/matches?hero_id={1}">{2}
                </a>,
                <a href="https://www.opendota.com/players/
                    {0}/matches?hero_id={3}">{4}
                </a>,
                <a href="https://www.opendota.com/players/
                    {0}/matches?hero_id={5}">{6}
                </a> <br><br>
            Your play style is similar to: <br>
                <a href="https://dotabuff.com/players/{7}">
                    https://www.dotabuff.com/players/{7}
                </a> <br>
                <a href="https://dotabuff.com/players/{8}">
                    https://www.dotabuff.com/players/{8}
                </a> <br>
                <a href="https://dotabuff.com/players/{9}">
                    https://www.dotabuff.com/players/{9}
                </a> <br><br>
            We recommend you to practice:
            '''.format(
                str(player_id),
                str(sorted_hero_data[0][0]),
                hero_name[str(sorted_hero_data[0][0])],
                str(sorted_hero_data[1][0]),
                hero_name[str(sorted_hero_data[1][0])],
                str(sorted_hero_data[2][0]),
                hero_name[str(sorted_hero_data[2][0])],
                scores[0][1],
                scores[1][1],
                scores[2][1]
                )

        for rec_hero_id in list(results)[0:3]:
            message += (
                '<a href="https://www.opendota.com/heroes/{}">{}</a>, '
                .format(rec_hero_id, str(hero_name[rec_hero_id])))
        message += '\n'
    except:
        message = "Player not found !!!"

    return message
