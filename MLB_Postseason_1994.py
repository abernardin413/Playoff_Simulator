import random

# ==== RATING CALCULATION ====

def compute_rating(wins, losses, runs_scored, runs_allowed, on_base, slugging):
    games = wins + losses
    # Handle case where games is 0 to prevent ZeroDivisionError
    if games == 0:
        return 0.0
    win_pct = wins / games
    run_diff_per_game = (runs_scored - runs_allowed) / games
    run_diff_norm = (run_diff_per_game + 3) / 6  # Normalize to [0, 1]
    pythag_winloss = (runs_scored ** 1.83) / ((runs_scored ** 1.83) + (runs_allowed ** 1.83))
    # Use ** for exponentiation, not ^
    return (pythag_winloss * 0.35) + (win_pct * 0.1) + (run_diff_norm * 0.3) + (on_base * 0.1) + (slugging * 0.15)


# ==== GAME & SERIES SIMULATION ====

def game_win_prob(team_rating, opp_rating, home_field_advantage=0):
    # Handle case where both ratings are 0 to prevent ZeroDivisionError
    if (team_rating + home_field_advantage + opp_rating) == 0:
        return 0.5 # Default to 50/50 if no rating information
    return (team_rating + home_field_advantage) / (team_rating + home_field_advantage + opp_rating)

def simulate_game_100_times(team_rating, opp_rating, is_home, hfa=0.05):
    team_wins = 0
    opp_wins = 0
    for _ in range(100): # Simulate each game 100 times
        prob = game_win_prob(team_rating, opp_rating, hfa if is_home else 0)
        if random.random() < prob:
            team_wins += 1
        else:
            opp_wins += 1
    return team_wins > opp_wins # Return True if team wins more simulations, False otherwise

def get_home_games(round_name, home_team_is_A):
    formats = {
        "divisional":     [True, True, False, False, True],
        "lcs":            [True, True, False, False, False, True, True],
        "world_series":   [True, True, False, False, False, True, True],
    }
    base = formats[round_name]
    return base if home_team_is_A else [not g for g in base]

def simulate_series(team_A, team_B, round_name):
    series_format = {
        "divisional":   (3, 5),
        "lcs":          (4, 7),
        "world_series": (4, 7)
    }[round_name]

    wins_needed, max_games = series_format

    # HOME FIELD LOGIC
    if round_name == "world_series":
        # For World Series, the home field advantage is determined by the team with the better regular season record.
        # If records are tied, then by seed.
        if team_A["wins"] != team_B["wins"]:
            home_team_is_A = team_A["wins"] > team_B["wins"]
        else:
            home_team_is_A = team_A["seed"] < team_B["seed"]
    else:
        home_team_is_A = team_A["seed"] < team_B["seed"]

    home_games = get_home_games(round_name, home_team_is_A)
    home_team_in_series = team_A if home_team_is_A else team_B
    away_team_in_series = team_B if home_team_is_A else team_A


    team_A_wins = 0
    team_B_wins = 0

    print(f"\n🎯 {round_name.upper()} SERIES: {team_A['name']} (Seed {team_A['seed']}) vs {team_B['name']} (Seed {team_B['seed']})")
    print(f"🏟 Home field advantage: {home_team_in_series['name']}")

    for i in range(max_games):
        # Ensure 'i' is within the bounds of 'home_games' list
        if i >= len(home_games):
            break

        is_home_for_A = home_games[i]
        
        # Determine which team is home for this specific game
        current_home_team = team_A if is_home_for_A else team_B

        winner_A = simulate_game_100_times(team_A['rating'], team_B['rating'], is_home_for_A)

        if winner_A:
            team_A_wins += 1
            print(f"Game {i+1} (Home: {current_home_team['name']}): {team_A['name']} win.")
        else:
            team_B_wins += 1
            print(f"Game {i+1} (Home: {current_home_team['name']}): {team_B['name']} win.")

        if team_A_wins == wins_needed:
            print(f"🏆 {team_A['name']} win the {round_name} series {team_A_wins}-{team_B_wins}")
            return team_A
        elif team_B_wins == wins_needed:
            print(f"🏆 {team_B['name']} win the {round_name} series {team_B_wins}-{team_A_wins}")
            return team_B


# ==== POSTSEASON BRACKET SIMULATION ====

def simulate_postseason(teams_AL, teams_NL):
    print("\n⚾ SIMULATING MLB POSTSEASON BRACKET\n")

    # Division Series
    ALDS1 = simulate_series(teams_AL[1], teams_AL[4], "divisional")
    ALDS2 = simulate_series(teams_AL[2], teams_AL[3], "divisional")
    NLDS1 = simulate_series(teams_NL[1], teams_NL[4], "divisional")
    NLDS2 = simulate_series(teams_NL[2], teams_NL[3], "divisional")

    # League Championship
    ALCS = simulate_series(ALDS1, ALDS2, "lcs")
    NLCS = simulate_series(NLDS1, NLDS2, "lcs")

    # World Series
    WS_winner = simulate_series(ALCS, NLCS, "world_series")
    print(f"\n🏁 WORLD SERIES CHAMPION: {WS_winner['name']} 🏆\n")


# ==== TEAM DATA ====

def create_team(name, wins, losses, runs_scored, runs_allowed, on_base, slugging, seed):
    return {
        "name": name,
        "wins": wins,
        "losses": losses,
        "runs_scored": runs_scored,
        "runs_allowed": runs_allowed,
        "on_base": on_base,
        "slugging": slugging,
        "seed": seed,
        "rating": compute_rating(wins, losses, runs_scored, runs_allowed, on_base, slugging)
    }

teams_AL = [
    None, # 0 index is unused, keeping for 1-based seed indexing
    create_team("New York Yankees", 70, 43, 670, 534, 0.374, 0.462, 1),
    create_team("Chicago White Sox", 67, 46, 633, 498, 0.366, 0.444, 2),
    create_team("Texas Rangers", 52, 62, 613, 697, 0.353, 0.436, 3),
    create_team("Cleveland Indians", 66, 47, 679, 562, 0.351, 0.484, 4),
]

teams_NL = [
    None, # 0 index is unused, keeping for 1-based seed indexing
    create_team("Montreal Expos", 74, 40, 585, 454, 0.343, 0.435, 1),
    create_team("Cincinnati Reds", 66, 48, 609, 490, 0.350, 0.449, 2),
    create_team("Los Angeles Dodgers", 58, 56, 532, 509, 0.333, 0.414, 3),
    create_team("Atlanta Braves", 68, 46, 542, 448, 0.333, 0.434, 4),
]

simulate_postseason(teams_AL, teams_NL)