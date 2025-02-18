# Hoopstradamus

A machine learning model for predicting NCAA March Madness tournament outcomes. Hoopstradamus analyzes historical tournament data, team statistics, and performance metrics to forecast game results and generate bracket predictions. Perfect for data scientists and basketball enthusiasts looking to gain an edge in their bracket challenges.

## Data Used

The Hoopstradamus model uses a combination of historical data, team statistics, and performance metrics to make predictions. The following datasets are used:

- 2013-2025 NCAAM Basketball Full Season Schedules. I have uploaded this data to Kaggle: https://www.kaggle.com/datasets/arbelaezch/ncaam-basketball-game-schedules-2014-2024. This data was sourced from https://barttorvik.com/gamestat.php and cleaned using the `data/raw/bart-full-season-schedules/clean_data.py` script.

- Top 1600 Players in D1 NCAAM Basketball for ever season from 2013 - 2025. This data was also sourced from [Barttorvik] (https://barttorvik.com/playerstat.php) and cleaned using the `data/raw/bart-players-pre-tourney/clean&process-data.py` script.

- Team Shooting Splits for every team from every season from 2013 - 2025. This data was sourced from [Barttorvik] (https://barttorvik.com/teamstats.php) and cleaned using the `data/raw/TeamShootingSplits/clean&process-data.py` script.

- Team Tables for every team from every season from 2013 - 2025. This data is similar to Kenpom's team summary data. It contains ADJ OE and other team mean stats from over the course of the season. This data was sourced from [Barttorvik] (https://barttorvik.com/team-tables_each.php) and cleaned using the `data/raw/bart-team-tables-pre-tourney/clean&process-data.py` script.

- I did also source Kenpom Team Summary Data for each season from 2013 - 2025, though I did not use it. This data can be found at [Kenpom's website](https://kenpom.com/).

Barttorvik is happy to share their data for public use.

## Data Merging

After cleaning and processing the data, I merged it into a single dataset for each season. This was done using the `src/data/merge_datasets.py` script. I then had to again clean this merged dataset to remove any duplicates and handle any missing values. This was done using the `merged_data/clean_merged_data.py` script.

## Model Training

