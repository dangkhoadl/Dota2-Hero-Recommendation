import sys
sys.path.insert(0, './leaderboard')
sys.path.insert(0, './recommender_system')

from flask import Flask, render_template, request
from multiprocessing import Pool
import json

from process_id import clean_input, get_player
from create_schema import Database

from recommender import clean_player_id, recommend_user

# App and database
app = Flask(__name__)
db = Database()

# Dataset for recommender system
with open('.//recommender_system//cleaned_data.json') as json_data:
    dataset = json.load(json_data)
with open('.//recommender_system//hero_name.json') as json_data:
    hero_name = json.load(json_data)


# Home page
@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


# API 1 - Leaderboard
@app.route('/result', methods=['POST'])
def result():
    if request.method == 'POST':
        # Get and clean input
        id_list = request.form["id_name"]
        print(id_list)
        id_list = clean_input(id_list)

        # Insert Entry if not in database
        for player_id in id_list:
            if db.has_player_id(player_id) != 1:
                # Implement thread pool to handle multiple requests
                # [TODO] improve the request handling speed
                with Pool(16) as p:
                    player_info = get_player(player_id)

                if player_info is None:
                    continue

                db.insert(
                    player_id=player_info['player_id'],
                    player_name=player_info['player_name'],
                    week_wr=player_info['week_wr'],
                    month_wr=player_info['month_wr'],
                    year_wr=player_info['year_wr'])

        # Query leader board
        leader_board = db.query_list(id_list)
        if leader_board is None:
            return render_template("result.html", text='Players not found !!!')

        # Present the results to the frontend
        # [TODO] Move message configuration to index.html
        message = '''
            Player Leaderboard <br><br>'''

        for i, player in enumerate(leader_board):
            message = message + '''
                <b>Rank</b>: {0}<br>
                <b>Player id</b>: {1}<br>
                <b>Player name</b>: {2}<br>
                <b>Dotabuff profile</b>:
                    <a href="https://dotabuff.com/players/{1}">
                        dotabuff.com/players/{1}
                    </a><br>
                <b>Last week win rate</b>: {3}<br>
                <b>Last month win rate</b>: {4}<br>
                <b>Last year win rate</b>: {5}<br><br>
                '''.format(
                    str(i + 1),
                    player['player_id'],
                    player['player_name'],
                    str(player['week_wr']) + ' %'
                    if player['week_wr'] != -1.00
                    else 'Not played since last week',
                    str(player['month_wr']) + ' %'
                    if player['month_wr'] != -1.00
                    else 'Not played since last month',
                    str(player['year_wr']) + ' %'
                    if player['year_wr'] != -1.00
                    else 'Not played since last year')

        return render_template("result.html", text=message)
    return render_template("index.html", text='Players not found !!!')


# API 2 - Recommender system
@app.route('/heroes_recommend', methods=['POST'])
def heroes_recommend():
    if request.method == 'POST':
        # Get and clean input
        user_id = request.form["player_id"]
        user_id = clean_player_id(user_id)

        if user_id is None:
            return render_template(
                "heroes_recommend.html",
                text='Players not found !!!')

        # [TODO] Implement a database for the recommender system
        message = recommend_user(user_id, dataset, hero_name)

        return render_template("heroes_recommend.html", text=message)
    return render_template("index.html", text='Players not found !!!')


if __name__ == '__main__':
    app.debug = True
    app.run()
