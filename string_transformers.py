def create_current_matches_string(df):

    # Initialize an empty string to store the matches
    matches_string = ""

    # Iterate over rows in the DataFrame
    for index, row in df.iterrows():
        # Extract data from the row
        match_id = row['id']
        teams = row['teams']
        current_result = row['current_result']
        half = row['half']
        time = row['time (in minutes)']

        # Construct the match string and append it to the matches string
        match_string = f"{match_id} - {teams} {current_result} ({half} - {time}m)"
        matches_string += match_string + "\n"

    return matches_string

