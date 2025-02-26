##################################################
# Board Game Recommender v1.2
##################################################
import os
import random
import re

from flask import Flask, make_response, render_template, request
from flask_mail import Mail, Message
from flask_wtf.csrf import CSRFProtect
from flask_caching import Cache

# environmental variables
from dotenv import load_dotenv

# DB
import psycopg2

################################################
load_dotenv()  # Load environment variables from .env file
################################################

# Variables for all templates

personal_recs = ['Dominant Species', 'Planet Steam', 'Cascadia', 'The Castles of Burgundy (84876)', 'Gloomhaven',
                 'Ticket to Ride: Europe', 'Battlestar Galactica: The Board Game', 'Terraforming Mars']
two_player_recs = ['Battle Line', 'Android: Netrunner', 'Twilight Struggle', '7 Wonders Duel']
party_recs = ['Skull', 'No Thanks!', 'Codenames', 'Crokinole']

character_map = {' ': '_', '!': '_', '*': '_', '^': '_', '%': '_', '$': '_', '&': 'and',
                 ':': '_', '#': '_', "'": '_', '(': '_', ')': '_', '/': '_',
                 '.': '_', ',': '_', '-': '_', '?': '_', '`': '_', '+': '_', '"': '_', '[': '_',
                 ']': '_', '=': '_', '@': '_', ';': '_', '<': '_', '>': '_', '}': '_', '{': '_',
                 '~': '_', '|': '_', '\\': '_'}

################################################

# Start of app
# cache configuration
config = {
    "DEBUG": True,          # some Flask specific configs
    "CACHE_TYPE": "SimpleCache",  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 7200
}
app = Flask(__name__, static_folder='static')
# tell Flask to use the above defined config
app.config.from_mapping(config)
# Initialize Flask-Cache
cache = Cache(app)

# If RUNNING_IN_PRODUCTION is defined as an environment variable, then we're running on Azure
if not 'RUNNING_IN_PRODUCTION' in os.environ:
    # Local development, where we'll use environment variables.
    print("Loading config.development and environment variables from .env file.")
    app.config.from_object('azureproject.development')

else:
    # Production, we don't load environment variables from .env file but add them as environment variables in Azure.
    print("Loading config.production.")
    app.config.from_object('azureproject.production')

with app.app_context():
    # Establish a connection to the PostgreSQL database

    if not 'USE_REMOTE_POSTGRESQL' in os.environ:
        # Connection to local SQL db
        conn = psycopg2.connect(
            host=app.config['DB_HOST'],
            port=app.config['DB_PORT'],
            user=app.config['DB_USER'],
            password=app.config['DB_PASSWORD'],
            database=app.config['DB_NAME']
        )
    else:
        # Connection to Azure SQL db
        connection_params = {
            'host': app.config['DB_HOST'],
            'port': app.config['DB_PORT'],
            'dbname': app.config['DB_NAME'],
            'user': app.config['DB_USER'],
            'password': app.config['DB_PASSWORD'],
            'sslmode': app.config['DB_SSL']
        }

        # Establish a connection to the PostgreSQL database
        conn = psycopg2.connect(**connection_params)

    # Establish connection to mail server
    app.config['MAIL_SERVER'] = app.config['MAIL_SERVER']
    app.config['MAIL_PORT'] = app.config['MAIL_PORT']
    app.config['MAIL_USE_TLS'] = app.config['MAIL_USE_TLS']
    app.config['MAIL_USERNAME'] = app.config['MAIL_USERNAME']
    app.config['MAIL_PASSWORD'] = app.config['MAIL_PASSWORD']

mail = Mail(app)


################################################
# Functions for all templates

# Get index for game title
def rec_value_getter(names):
    cursor = conn.cursor()

    # Create a comma-separated string of placeholders for the game names
    placeholders = ','.join(['%s'] * len(names))

    # Execute a SELECT query to fetch the table
    query = "SELECT tgi.name, tgi.image, tgi.year_pub, tgi.play_time, tgi.min_players, tgi.max_players, tgi.avg_rating, CONCAT('https://boardgamegeek.com/boardgame/',gidb.bggid) " \
            "FROM table_game_info tgi, game_info_db gidb WHERE tgi.name = gidb.name and tgi.name IN ({}) ORDER BY year_pub DESC".format(placeholders)
    cursor.execute(query, names)
    matching_games = cursor.fetchall()

    cursor.close()
    return matching_games


################################################
# Variables for app
top_suggest = rec_value_getter(personal_recs)
two_player_suggest = rec_value_getter(two_player_recs)
party_suggest = rec_value_getter(party_recs)

# Get game names for autofill
cursor = conn.cursor()
cursor.execute("SELECT name from table_game_info ORDER BY year_pub DESC")
results = cursor.fetchall()
name_list = [row[0] for row in results]
cursor.close()


################################################
# print(game_names)
@app.route('/')
@cache.cached()
# index folder MUST be named "templates"
def index():
    ################################################
    # OUTPUT VARIABLES:
    # index_2.html - the html template to render
    # top_suggest - list of top game suggestions
    # two_player_suggest - list of two player game suggestions
    # party_suggest - list of party game suggestions
    # min_players - min number of players used in filtering (slider bar)
    # max_players - max number of players used in filtering (slider bar)
    # min_year - min year used in filtering (slider bar)
    # max_year - max year used in filtering (slider bar)
    # game_name - list of games names for Autofill
    ################################################
    min_players, max_players = map(float, [1, 10])
    min_year, max_year = map(float, [1950, 2021])
    return render_template('index_2.html', top_suggest=top_suggest, selected_option='option1',
                           two_player_suggest=two_player_suggest,
                           party_suggest=party_suggest,
                           min_players=min_players, max_players=max_players,
                           min_year=min_year, max_year=max_year,
                           game_name=name_list
                           )


@app.route('/recommend_games', methods=['GET', 'POST'])
def game_recommender():
    ################################################
    # INPUT VARIABLES:
    # dropdown - dropdown form indicating what type of filtering to use
    # user_input - the game name (hopefully) being searched for by user in search bar (string)
    # player_num - the min/max values of slider bar for players wanted (will use default values if GET method used)
    # year_num - the min/max values of slider bar for years wanted (will use default values if GET method used)
    ################################################
    # OUTPUT VARIABLES:
    # index_2.html - the html template to render
    # selected_option - the option chosen in the dropdown form (string)
    # top_suggest - list of top game suggestions
    # two_player_suggest - list of two player game suggestions
    # party_suggest - list of party game suggestions
    # min_players - min number of players used in filtering (slider bar)
    # max_players - max number of players used in filtering (slider bar)
    # min_year - min year used in filtering (slider bar)
    # max_year - max year used in filtering (slider bar)
    # game_name - list of games names for Autofill
    # data_list (optional) - nested list of game information from SQL db
    # rec_name (optional) - name of recommender filter chosen (string)
    # search_name (optional) - the game name (hopefully) being searched for by user in search bar (string)
    # feedback (optional) - message reporting that game cannot be found (string)
    # error_message (optional) - message reporting that somebody broke something... (string)
    ################################################

    # Get values from forms
    dropdown_value = request.form.get('dropdown')
    table_name = request.form.get('user_input')

    # Send to vanilla index if routed directly to /recommend_games (no_inputs)
    if table_name is None:

        min_players, max_players = map(float, [1, 10])
        min_year, max_year = map(float, [1950, 2021])
        return render_template('index_2.html', top_suggest=top_suggest, selected_option='option1',
                               two_player_suggest=two_player_suggest,
                               party_suggest=party_suggest,
                               min_players=min_players, max_players=max_players,
                               min_year=min_year, max_year=max_year,
                               game_name=name_list
                               )
    else:
        # making a copy to report back as we will modify the input
        search_name = table_name
        # get min/max player slider bar values
        min_players, max_players = map(float, request.form.get('player_num').split(','))
        # get min/max year slider bar values
        try:
            min_year, max_year = map(float, request.form.get('year_num').split(','))
        except:
            min_year, max_year = map(str, request.form.get('year_num').split(','))
            if max_year == 'Older than 1985':
                max_year = 1984
            else:
                max_year = float(max_year)
            if min_year == 'Older than 1985':
                min_year = -10000
            else:
                min_year = float(min_year)

        # Set suggestion number
        suggestions = 20

        # For anti-recommender. Scores lower than this may not have good feature data.
        threshold = .01
        # higher number of results for anti-recommender as we will randomize results (many very close together)
        num_results = 500

        # Determine similarity matrix based on user selection
        if dropdown_value == 'option1':
            search_type = 'combined'
            rec_name = 'THEME AND MECHANICS'
        elif dropdown_value == 'option2':
            search_type = 'mech'
            rec_name = 'MECHANICS ONLY'
        elif dropdown_value == 'option3':
            search_type = 'theme'
            rec_name = 'THEME ONLY'
        elif dropdown_value == 'option4':
            # we will use the reverse of the combined features
            search_type = 'combined'
            rec_name = 'ANTI-RECOMMENDER'

        else:
            # similarity_matrix = similarity_all
            search_type = 'combined'
        # Use Anti-Recommend or not
        if dropdown_value == 'option4':
            order = "ASC"
        else:
            order = "DESC"

        # Get index for game title
        # Convert special characters from games names typically in games to '_'
        for char, replacement in character_map.items():
            table_name = table_name.replace(char, replacement)

        # Escape any remaining special characters in the table name and make lowercase
        esc_table_name = re.escape(table_name.lower())
        esc_table_name = str('table_' + esc_table_name)
        # Execute a SELECT query to fetch the table
        cursor = conn.cursor()
        query_exact = "SELECT table_name FROM information_schema.tables WHERE table_name = %s"
        # Execute the query with the table name as a parameter
        cursor.execute(query_exact, (esc_table_name,))
        matching_table = cursor.fetchall()
        try:
            # print(matching_table)
            # check for exact matches and use first if exists
            if len(matching_table) == 0:
                match_check = False
            elif len(matching_table) == 1:
                matched_table = matching_table[0][0]
                # print(matched_table)
                match_check = True
            elif len(matching_table > 1):
                matched_table = matching_table[0][0]
                match_check = True

            if not match_check:
                # check for partial or non-exact matches
                query_partial = "SELECT table_name FROM information_schema.tables WHERE table_name ~ %s"
                # Execute the query with the table name as a parameter
                cursor.execute(query_partial, (esc_table_name,))
                alt_matching_tables = cursor.fetchall()
                if len(alt_matching_tables) == 0:
                    alt_match_check = False
                elif len(alt_matching_tables) >= 1:
                    alt_match_check = True
                    alt_table = alt_matching_tables[0][0]
                    # print(alt_table)
            if match_check or alt_match_check:

                # Use exact matches if possible
                if match_check:
                    # print(match_check)
                    query_table = f"SELECT g.name, g.image, g.year_pub, g.play_time, g.min_players, g.max_players, g.avg_rating, CONCAT('https://boardgamegeek.com/boardgame/',k.bggid) " \
                                  f"FROM {matched_table} m " \
                                  f"JOIN table_game_info g ON m.id = g.id JOIN game_info_db k on g.name = k.name " \
                                  f"WHERE {search_type} >= %s AND g.max_players <= %s AND g.min_players >= %s " \
                                  f"AND g.year_pub::numeric >= %s AND g.year_pub::numeric <= %s " \
                                  f"ORDER BY {search_type} {order} " \
                                  f"LIMIT %s"
                                  
                    #print(query_table)
                    # Execute the query with the table name as a parameter
                    # Execute the query with the parameter values
                    if dropdown_value == 'option4':
                        cursor.execute(query_table,
                                       (threshold, max_players, min_players, min_year, max_year, num_results))
                        data_list = cursor.fetchall()
                        cursor.close()
                        random.shuffle(data_list)
                        data_list = data_list[:20]
                    else:
                        cursor.execute(query_table,
                                       (threshold, max_players, min_players, min_year, max_year, suggestions))
                        data_list = cursor.fetchall()
                        cursor.close()
                    # column_names = [desc[0] for desc in cursor.description]


                # Otherwise, use first partial match
                else:
                    # print(match_check)
                    query_table = f"SELECT g.name, g.image, g.year_pub, g.play_time, g.min_players, g.max_players, g.avg_rating, CONCAT('https://boardgamegeek.com/boardgame/',k.bggid) " \
                                  f"FROM {alt_table} m " \
                                  f"JOIN table_game_info g ON m.id = g.id JOIN game_info_db k on g.name = k.name " \
                                  f"WHERE {search_type} >= %s AND g.max_players <= %s AND g.min_players >= %s " \
                                  f"AND g.year_pub::numeric >= %s AND g.year_pub::numeric <= %s " \
                                  f"ORDER BY {search_type} {order} " \
                                  f"LIMIT %s"
                    # Execute the query with the table name as a parameter
                    # Use unique settings for anti-rec
                    if dropdown_value == 'option4':
                        cursor.execute(query_table,
                                       (threshold, max_players, min_players, min_year, max_year, num_results))
                        data_list = cursor.fetchall()
                        cursor.close()
                        random.shuffle(data_list)
                        data_list = data_list[:16]

                    else:
                        cursor.execute(query_table,
                                       (threshold, max_players, min_players, min_year, max_year, suggestions))
                        data_list = cursor.fetchall()
                        cursor.close()
                        # column_names = [desc[0] for desc in cursor.description]

                return render_template('index_2.html', search_name=search_name, selected_option=dropdown_value,
                                       top_suggest=top_suggest, two_player_suggest=two_player_suggest,
                                       party_suggest=party_suggest, min_players=min_players,
                                       max_players=max_players,
                                       min_year=min_year, max_year=max_year,
                                       rec_name=rec_name, data=data_list,
                                       game_name=name_list
                                       )

            else:
                # If no exact or partial matches, return feedback to user
                no_game = [1]
                return render_template('index_2.html', search_name=search_name, feedback=no_game,
                                       top_suggest=top_suggest,
                                       two_player_suggest=two_player_suggest,
                                       party_suggest=party_suggest,
                                       min_players=min_players, max_players=max_players,
                                       min_year=min_year, max_year=max_year,
                                       game_name=name_list
                                       )
            cursor.close()

        except psycopg2.Error as e:
            error_message = str(e)
            return render_template('index_2.html', error_message=error_message, top_suggest=top_suggest,
                                   two_player_suggest=two_player_suggest,
                                   party_suggest=party_suggest,
                                   min_players=min_players, max_players=max_players,
                                   min_year=min_year, max_year=max_year,
                                   game_name=name_list
                                   )


@app.route('/send-email', methods=['post'])
def send_email():
    ################################################
    # INPUT VARIABLES:
    # Name - Name field from contact section
    # Email - Email field from contact section
    # Message - Message field from contact section

    # OUTPUT VARIABLES:
    # msg - the email being sent using Flask Mail
    ################################################
    name_value = request.form.get('Name')
    # print(name_value)
    email_value = request.form.get('Email')
    message_value = request.form.get('Message')
    msg = Message('Thanks for the message, ' + name_value + '!', sender='reply.wswp@gmail.com',
                  recipients=['reply.wswp@gmail.com',
                              email_value])
    msg.body = 'This is a copy of your message: "' + message_value + '"'
    mail.send(msg)
    return 'Email sent!'


if __name__ == '__main__':
    app.run(debug=True)
