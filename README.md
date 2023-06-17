# Board_Game_Recommender_v1.1
Board game recommender using collaborative filtering
# ###################################################
About

Why make something like this?

I think that there's a perfect board game waiting to be discovered by everyone, regardless of whether you're new to the hobby or a grizzled gamer. 
That's why I created a powerful tool that empowers you to explore and find board games that you'll truly enjoy, using a variety of methods.

I designed the system to give you control and customization over the recommendations you receive.
You can choose which features and aspects of board games are emphasized, enabling you to explore tailored recommendations that align with your specific interests and gameplay preferences.
By providing you these choices, my aim is to help you uncover hidden gems, explore different themes and mechanics, and find board games that resonate with your gaming style.

Alongside creating a tool that I feel would be helpful in discovering board games for everyone to enjoy, this was a learning opportunity for me to create a site and filtering system from the ground up.
I still have more I want to add to this site, and have enjoyed having a project that has helped me grow in different skills.

To see the Jupyter notebooks for the creation of the similarity scores, visit this repository: https://github.com/klaustd/Board_Game_Recommender_Jupyter.
# #################################################

Main App Variables
# ###############################################
INPUT VARIABLES:
* dropdown - dropdown form indicating what type of filtering to use
* user_input - the game name (hopefully) being searched for by user in search bar (string)
* player_num - the min/max values of slider bar for players wanted (will use default values if GET method used)
* year_num - the min/max values of slider bar for years wanted (will use default values if GET method used)
* Name - Name field from contact section
* Email - Email field from contact section
* Message - Message field from contact section
# ###############################################
OUTPUT VARIABLES:
* index_2.html - the html template to render
* selected_option - the option chosen in the dropdown form (string)
* top_suggest - list of top game suggestions
* two_player_suggest - list of two player game suggestions
* party_suggest - list of party game suggestions
* min_players - min number of players used in filtering (slider bar)
* max_players - max number of players used in filtering (slider bar)
* min_year - min year used in filtering (slider bar)
* max_year - max year used in filtering (slider bar)
* game_name - list of games names for Autofill
* data_list (optional) - nested list of game information from SQL db
* rec_name (optional) - name of recommender filter chosen (string)
* search_name (optional) - the game name (hopefully) being searched for by user in search bar (string)
* feedback (optional) - message reporting that game cannot be found (string)
* error_message (optional) - message reporting that somebody broke something... (string)
* msg - the email being sent using Flask Mail
# ###############################################
Development vs Production

environmental variables are accessed with development.py when in dev mode, otherwise production.py is used 
# ###############################################
Various Input Files

* df_games_app.pkl and df_index.pkl are used to provide game names for autofill and initial features
* Dockerfile and requirements.txt used for CI/CD
