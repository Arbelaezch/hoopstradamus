# College Basketball Game Statistics (2013-2024)

## Dataset Description
This dataset contains detailed game-by-game statistics for NCAA Division I men's basketball games from the 2013-14 season through the 2023-24 season (excluding 2019-20). The data was sourced from [barttorvik.com](https://barttorvik.com/gamestat.php).

Data uploaded to Kaggle in CSV format.
[NCAAM Basketball Game Schedules 2014-2024](https://www.kaggle.com/datasets/arbelaezch/ncaam-basketball-game-schedules-2014-2024)


## Temporal Coverage
- Start: 2013-14 season
- End: 2023-24 season
- Note: 2019-20 season is excluded due to the COVID-19 pandemic's impact on that season

## Column Descriptions

### Game Information
- **Date**: Game date in YYYY-MM-DD format
- **Type**: Type of game
  - N: Non-conference regular season game
  - C: Conference regular season game
  - CT: Conference Tournament game
  - P: NIT Tournament game
  - T: NCAA Tournament game
- **Team**: Name of the team
- **Conf.**: Conference affiliation of the team
- **Opp.**: Opponent team name
- **Venue**: Game location (Home/Away/Neutral)

### Game Outcomes
- **Win**: Binary indicator of game result (1 = Win, 0 = Loss)
- **Points_For**: Points scored by the team
- **Points_Against**: Points scored by the opponent
- **Point_Differential**: Point difference (Points_For minus Points_Against)

### Team Performance Metrics
- **Adj. O**: Adjusted offensive efficiency
- **Adj. D**: Adjusted defensive efficiency
- **T**: Game tempo (possessions per 40 minutes)

### Offensive Statistics (prefixed with O.)
- **O.EFF**: Offensive efficiency (points per 100 possessions)
- **O.eFG%**: Effective field goal percentage
- **O.TO%**: Turnover percentage
- **O.Reb%**: Offensive rebounding percentage
- **O.FTR**: Free throw rate

### Defensive Statistics (prefixed with D.)
- **D.EFF**: Defensive efficiency (points allowed per 100 possessions)
- **D.eFG%**: Opponent's effective field goal percentage
- **D.TO%**: Forced turnover percentage
- **D.Reb%**: Defensive rebounding percentage
- **D.FTR**: Opponent's free throw rate

### Performance Metrics
- **G-Sc**: Game Score (a measure of game performance)
- **+/-**: Plus/minus score differential

## Usage Notes
- All efficiency metrics are tempo-adjusted
- Conference affiliations reflect the team's conference for that specific season
- Neutral site games include both tournament and non-tournament games
- The dataset includes regular season and postseason games