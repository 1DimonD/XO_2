import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.legend_handler import HandlerTuple
from windrose import WindroseAxes
import matplotlib.patches as mpatches
import numpy as np


def make_standings_table_image(df, image_size=(10, 6)):
    # Calculate column widths based on the length of team names
    max_team_name_length = df['Team'].apply(len).max()
    team_column_width = max_team_name_length * 0.15

    points = df['Points'].astype(float)
    norm = plt.Normalize(points.min(), points.max())
    cmap = LinearSegmentedColormap.from_list("RdYlGn_custom", ["red", "yellow", "green"])
    colors = cmap(norm(points))
    cell_colors = [[tuple(color)] * len(df.columns) for color in colors]

    # Create the table plot
    fig, ax = plt.subplots(figsize=image_size)
    ax.axis('tight')
    ax.axis('off')
    table = ax.table(cellText=df.values, colLabels=df.columns, loc='center', cellLoc='center')
    for i in range(len(df)):
        for j in range(len(df.columns)):
            cell_color = colors[i]
            table.get_celld()[(i+1, j)].set_facecolor(cell_color)
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.auto_set_column_width(col=list(range(len(df.columns))))
    table.scale(1, 1.5)

    # Save the plot as a JPG image
    file_path = "images/league_standings.jpg"
    plt.savefig(file_path, bbox_inches='tight', pad_inches=0.1)

    # Close the plot to free up resources
    plt.close(fig)

    return file_path


def create_players_table(df):
    # Define colors for player positions
    position_colors = {
        'Goalkeeper': '#CD853F',  # Light brown
        'Defender': '#90EE90',  # Light green
        'Midfielder': '#FFFFE0',  # Light yellow
        'Attacker': '#F08080'  # Light red
    }

    # Create a figure and axis
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.axis('off')  # Hide axes

    # Create the table plot
    table = ax.table(cellText=df.values,
                     colLabels=df.columns,
                     cellLoc='center',
                     loc='center')

    # Color cells based on player position
    for (i, j), cell in table.get_celld().items():
        if i == 0:
            cell.set_facecolor('lightgrey')  # Color header cells grey
        else:
            if df.columns[j] == 'position':
                position = cell.get_text().get_text()
                cell.set_facecolor(position_colors.get(position, 'white'))

    # Adjust layout
    plt.tight_layout()

    # Save the plot as an image
    file_path = 'images/team_players.jpg'
    plt.savefig(file_path, bbox_inches='tight')

    # Close the plot to free up resources
    plt.close(fig)

    return file_path


def create_result_table(df):
    # Define colors for each result
    result_colors = {
        'W': '#90EE90',  # Light green for wins
        'D': '#FFFFE0',  # Light yellow for draws
        'L': '#F08080'  # Light red for losses
    }

    # Create a figure and axis
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.axis('off')  # Hide axes

    # Create the table plot
    table = ax.table(cellText=df.values,
                     colLabels=df.columns,
                     cellLoc='center',
                     loc='center')

    # Color rows based on result
    for (i, j), cell in table.get_celld().items():
        if i == 0:
            cell.set_facecolor('lightgrey')  # Color header row grey
        else:
            result = df.iloc[i - 1]['W/D/L']
            cell.set_facecolor(result_colors.get(result, 'white'))

    # Adjust layout
    plt.tight_layout()

    # Save the plot as an image
    file_path = 'images/team_result.jpg'
    plt.savefig(file_path, bbox_inches='tight')

    # Close the plot to free up resources
    plt.close(fig)

    return file_path

def create_wind_rose_by_predictions(df):
    # Extract column names (directions)
    directions = df.index.tolist()
    num_directions = len(directions)

    # Extract home and away team predictions
    home_predictions = df[df.columns[0]].tolist()
    away_predictions = df[df.columns[1]].tolist()

    # Create wind rose plot
    fig, ax = plt.subplots(subplot_kw={'projection': 'windrose'})

    # Define colormaps
    cmap_home = cm.get_cmap('cool')
    cmap_away = cm.get_cmap('autumn')

    # Plot home team predictions
    ax.plot(np.radians(range(0, 360, int(360 / num_directions))), home_predictions, color=cmap_home(0.7))
    ax.fill(np.radians(range(0, 360, int(360 / num_directions))), home_predictions, color=cmap_home(0.7), alpha=0.3)

    # Plot away team predictions
    ax.plot(np.radians(range(0, 360, int(360 / num_directions))), away_predictions, color=cmap_away(0.7))
    ax.fill(np.radians(range(0, 360, int(360 / num_directions))), away_predictions, color=cmap_away(0.7), alpha=0.3)

    # Set direction labels on the edges
    ax.set_thetagrids(range(0, 360, int(360 / num_directions)), directions)

    # Connect first and last dots
    home_first_point = (np.radians(0), home_predictions[0])
    home_last_point = (np.radians(360-int(360/num_directions)), home_predictions[-1])
    ax.plot([home_first_point[0], home_last_point[0]], [home_first_point[1], home_last_point[1]], color=cmap_home(0.7))

    away_first_point = (np.radians(0), away_predictions[0])
    away_last_point = (np.radians(360-int(360/num_directions)), away_predictions[-1])
    ax.plot([away_first_point[0], away_last_point[0]], [away_first_point[1], away_last_point[1]], color=cmap_away(0.7))

    # Save the plot as an image
    file_path = 'images/predictions.jpg'
    plt.savefig(file_path, bbox_inches='tight')

    plt.close(fig)

    return file_path, f"{df.columns[0]} - blue\n{df.columns[1]} - orange"
