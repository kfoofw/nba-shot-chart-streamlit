# from nba_api.stats.endpoints import shotchartdetail
import requests
import json
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from matplotlib.patches import Circle, Rectangle, Arc

import streamlit as st

# Set up player dict
player_dict = {}
player_dict["James Harden"] = 201935
player_dict["Lebron James"] = 2544
player_dict["Trae Young"] = 1629027
player_dict["Steph Curry"] = 201939
player_dict["Kawhi Leonard"] = 202695

# URL for requests
headers = {
		'Host': 'stats.nba.com',
		'Connection': 'keep-alive',
		'Accept': 'application/json, text/plain, */*',
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
		'Referer': 'https://stats.nba.com/',
		"x-nba-stats-origin": "stats",
		"x-nba-stats-token": "true",
		'Accept-Encoding': 'gzip, deflate, br',
		'Accept-Language': 'en-US,en;q=0.9',
	}

url_base = 'https://stats.nba.com/stats/shotchartdetail'

# Set cache for data pull
@st.cache 
def pull_data(player_id, season_type):
	parameters = {
		'ContextMeasure': 'FGA',
		'LastNGames': 0,
		'LeagueID': '00',
		'Month': 0,
		'OpponentTeamID': 0,
		'Period': 0,
		'PlayerID': player_id,
		'SeasonType': season_type,
		'TeamID': 0,
		'VsDivision': '',
		'VsConference': '',
		'SeasonSegment': '',
		'Season': '2018-19',
		'RookieYear': '',
		'PlayerPosition': '',
		'Outcome': '',
		'Location': '',
		'GameSegment': '',
		'GameId': '',
		'DateTo': '',
		'DateFrom': ''
	}
	
	response = requests.get(url_base, params=parameters, headers=headers)

	return response


# Default to James Harden
player_id = 201935
season_type = "Regular Season"

# Player Radio Button
player_name = st.radio(
	"Whose shot chart do you want to see?",
	('James Harden', 'Lebron James', 'Trae Young', "Steph Curry", "Kawhi Leonard"))
player_id = player_dict[player_name]

# Season Radio Button
season_selection = st.radio(
	"Which season type do you prefer",
	('Regular Season', 'Playoffs'))

if season_selection == "Regular Season":
	season_type = "Regular Season"
else:
	season_type = "Playoffs"

response = pull_data(player_id, season_type)

# Get json
content = json.loads(response.content)

# Obtain relevant data
headers = content["resultSets"][0]["headers"]
shots = content["resultSets"][0]["rowSet"]

# Create dataframe
shot_df = pd.DataFrame(shots, columns = headers)

#########################################
def draw_court(ax=None, color='black', lw=2, outer_lines=False):
    # If an axes object isn't provided to plot onto, just get current one
    if ax is None:
        ax = plt.gca()

    # Create the various parts of an NBA basketball court

    # Create the basketball hoop
    # Diameter of a hoop is 18" so it has a radius of 9", which is a value
    # 7.5 in our coordinate system
    hoop = Circle((0, 0), radius=7.5, linewidth=lw, color=color, fill=False)

    # Create backboard
    backboard = Rectangle((-30, -7.5), 60, -1, linewidth=lw, color=color)

    # The paint
    # Create the outer box 0f the paint, width=16ft, height=19ft
    outer_box = Rectangle((-80, -47.5), 160, 190, linewidth=lw, color=color,
                          fill=False)
    # Create the inner box of the paint, widt=12ft, height=19ft
    inner_box = Rectangle((-60, -47.5), 120, 190, linewidth=lw, color=color,
                          fill=False)

    # Create free throw top arc
    top_free_throw = Arc((0, 142.5), 120, 120, theta1=0, theta2=180,
                         linewidth=lw, color=color, fill=False)
    # Create free throw bottom arc
    bottom_free_throw = Arc((0, 142.5), 120, 120, theta1=180, theta2=0,
                            linewidth=lw, color=color, linestyle='dashed')
    # Restricted Zone, it is an arc with 4ft radius from center of the hoop
    restricted = Arc((0, 0), 80, 80, theta1=0, theta2=180, linewidth=lw,
                     color=color)

    # Three point line
    # Create the side 3pt lines, they are 14ft long before they begin to arc
    corner_three_a = Rectangle((-220, -47.5), 0, 140, linewidth=lw,
                               color=color)
    corner_three_b = Rectangle((220, -47.5), 0, 140, linewidth=lw, color=color)
    # 3pt arc - center of arc will be the hoop, arc is 23'9" away from hoop
    # I just played around with the theta values until they lined up with the 
    # threes
    three_arc = Arc((0, 0), 475, 475, theta1=22, theta2=158, linewidth=lw,
                    color=color)

    # Center Court
    center_outer_arc = Arc((0, 422.5), 120, 120, theta1=180, theta2=0,
                           linewidth=lw, color=color)
    center_inner_arc = Arc((0, 422.5), 40, 40, theta1=180, theta2=0,
                           linewidth=lw, color=color)

    # List of the court elements to be plotted onto the axes
    court_elements = [hoop, backboard, outer_box, inner_box, top_free_throw,
                      bottom_free_throw, restricted, corner_three_a,
                      corner_three_b, three_arc, center_outer_arc,
                      center_inner_arc]

    if outer_lines:
        # Draw the half court line, baseline and side out bound lines
        outer_lines = Rectangle((-250, -47.5), 500, 470, linewidth=lw,
                                color=color, fill=False)
        court_elements.append(outer_lines)

    # Add the court elements onto the axes
    for element in court_elements:
        ax.add_patch(element)

    return ax

# create our jointplot
cmap=plt.cm.gist_heat_r
joint_shot_chart = sns.jointplot(shot_df.LOC_X, shot_df.LOC_Y, stat_func=None,
                                 kind='scatter', space=0, alpha=0.5, color=cmap(.2))

joint_shot_chart.fig.set_size_inches(12,11)

# A joint plot has 3 Axes, the first one called ax_joint 
# is the one we want to draw our court onto and adjust some other settings
ax = joint_shot_chart.ax_joint
draw_court(ax)

# Adjust the axis limits and orientation of the plot in order
# to plot half court, with the hoop by the top of the plot
ax.set_xlim(-250,250)
ax.set_ylim(422.5, -47.5)

# Get rid of axis labels and tick marks
ax.set_xlabel('')
ax.set_ylabel('')
ax.tick_params(labelbottom='off', labelleft='off')


st.subheader('NBA Shot Chart for ' + player_name + " in 2018-19 " + season_selection)

st.pyplot()

st.write("Special credit to Savvas Tjortjoglou for the charts.")
st.write("Check out his awesome blog post here: http://savvastjortjoglou.com/nba-shot-sharts.html")
