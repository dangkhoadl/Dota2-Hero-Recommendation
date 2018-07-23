from flask import Flask
import psycopg2

# config db localhost
# CREDENTIAL = '''
#     dbname='dota'
#     user='postgres'
#     password='dangkhoa'
#     host='localhost'
#     port='5432'
# '''

# config db heroku
CREDENTIAL = '''
    dbname='d45n2vli6dp5b6'
    user='zqgiibubodoqgg'
    password='df796d8c90b9f9248406ebe8fb5eb1989dc1ff365c1b33b46009c754a66b2978'
    host='ec2-23-23-247-222.compute-1.amazonaws.com'
    port='5432'
'''


class Database:
    def creat_table(
            self,
            database=CREDENTIAL):
        '''Create table'''
        # [TODO] resuse connection
        conn = psycopg2.connect(database)
        cur = conn.cursor()

        cur.execute('''
            CREATE TABLE IF NOT EXISTS api (
                id SERIAL PRIMARY KEY,
                player_id_ INTEGER NOT NULL UNIQUE,
                player_name_ TEXT,
                week_wr_ FLOAT,
                month_wr_ FLOAT,
                year_wr_ FLOAT);
            ''')

        conn.commit()
        conn.close()

    def insert(
            self,
            player_id, player_name,
            week_wr, month_wr, year_wr,
            database=CREDENTIAL):
        '''Insert item'''
        # [TODO] resuse connection
        conn = psycopg2.connect(database)
        cur = conn.cursor()

        cur.execute('''
            INSERT INTO api(
                player_id_, player_name_,
                week_wr_, month_wr_, year_wr_)
            VALUES ('{}', '{}', '{}', '{}', '{}');
            '''.format(
                str(player_id), str(player_name),
                str(week_wr), str(month_wr), str(year_wr)))

        conn.commit()
        conn.close()

    def has_player_id(
            self,
            player_id,
            database=CREDENTIAL):
        try:
            # [TODO] resuse connection
            conn = psycopg2.connect(database)
            cur = conn.cursor()

            cur.execute('''
                SELECT 1
                FROM api
                WHERE player_id_ = {};
                '''.format(str(player_id)))
            result = cur.fetchall()
            if result != []:
                (value,) = result[0]
            else:
                value = 0

            conn.commit()
            conn.close()
        except:
            value = None
        return value

    def query_list(
            self,
            id_list,
            database=CREDENTIAL):
        try:
            # [TODO] resuse connection
            conn = psycopg2.connect(database)
            cur = conn.cursor()

            cur.execute('''
                SELECT player_id_, player_name_, week_wr_, month_wr_, year_wr_
                FROM api
                WHERE player_id_ IN ({})
                ORDER BY week_wr_ DESC, month_wr_ DESC, year_wr_ DESC;
                '''.format(' ,'.join([str(e) for e in id_list])))
            results = cur.fetchall()

            leader_board = None
            if results != []:
                leader_board = []
                for entry in results:
                    leader_board.append({
                        'player_id': entry[0],
                        'player_name': entry[1],
                        'week_wr': entry[2],
                        'month_wr': entry[3],
                        'year_wr': entry[4]})

            conn.commit()
            conn.close()
        except:
            leader_board = None
        return leader_board


if __name__ == '__main__':
    # Create db schema
    db = Database()
    db.creat_table()
