import pandas as pd
import numpy as np
from typing import Tuple, List, Dict
import logging
from pathlib import Path
import glob

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MarchMadnessDataProcessor:
    def __init__(self, raw_data_path: str = 'data/raw', processed_data_path: str = 'data/processed'):
        self.raw_data_path = Path(raw_data_path)
        self.processed_data_path = Path(processed_data_path)
        self.processed_data_path.mkdir(parents=True, exist_ok=True)

    def load_season_data(self, year: int) -> pd.DataFrame:
        """Load pre-tournament data for a specific season"""
        try:
            filename = f"summary{str(year)[-2:]}_pt.csv"
            df = pd.read_csv(self.raw_data_path / filename)
            df['Season'] = year
            logger.info(f"Loaded {year} season data with shape: {df.shape}")
            return df
        except Exception as e:
            logger.error(f"Error loading {year} season data: {str(e)}")
            raise

    def load_multiple_seasons(self, start_year: int, end_year: int) -> pd.DataFrame:
        """Load and combine multiple seasons of data"""
        all_seasons = []
        for year in range(start_year, end_year + 1):
            try:
                season_df = self.load_season_data(year)
                all_seasons.append(season_df)
            except Exception as e:
                logger.warning(f"Couldn't load {year} season: {str(e)}")
                continue
        
        return pd.concat(all_seasons, ignore_index=True)

    def create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create features for model training"""
        try:
            feature_df = df.copy()
            
            # Create offensive/defensive efficiency difference
            feature_df['EfficiencyDiff'] = feature_df['AdjOE'] - feature_df['AdjDE']
            
            # Create tempo-adjusted efficiency metrics
            feature_df['TempoAdjOffEff'] = feature_df['AdjOE'] * (feature_df['AdjTempo'] / feature_df['AdjTempo'].mean())
            feature_df['TempoAdjDefEff'] = feature_df['AdjDE'] * (feature_df['AdjTempo'] / feature_df['AdjTempo'].mean())
            
            # Create ranking-based features
            feature_df['OverallRankScore'] = (
                feature_df['RankAdjOE'] + 
                feature_df['RankAdjDE'] + 
                feature_df['RankAdjTempo']
            ) / 3
            
            # Convert seeds to numeric, handling empty strings
            feature_df['seed'] = pd.to_numeric(feature_df['seed'], errors='coerce')
            
            # Create seed-based features when seed is available
            feature_df['IsTourney'] = feature_df['seed'].notna()
            
            return feature_df
            
        except Exception as e:
            logger.error(f"Error creating features: {str(e)}")
            raise

    def prepare_matchup_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare data for matchup prediction"""
        try:
            # Create all possible matchup combinations for tournament teams
            tourney_teams = df[df['IsTourney']]['TeamName'].unique()
            matchups = []
            
            for team1 in tourney_teams:
                for team2 in tourney_teams:
                    if team1 != team2:
                        matchups.append({
                            'Team1': team1,
                            'Team2': team2,
                            'Season': df[df['TeamName'] == team1]['Season'].iloc[0]
                        })
            
            matchups_df = pd.DataFrame(matchups)
            
            # Add team features for both teams
            team1_cols = ['TeamName', 'AdjOE', 'AdjDE', 'AdjTempo', 'EfficiencyDiff', 
                         'TempoAdjOffEff', 'TempoAdjDefEff', 'OverallRankScore', 'seed']
            team2_cols = team1_cols.copy()
            
            matchups_df = matchups_df.merge(
                df[team1_cols], 
                left_on=['Team1', 'Season'],
                right_on=['TeamName', 'Season']
            ).drop(columns=['TeamName'])
            
            matchups_df = matchups_df.merge(
                df[team2_cols], 
                left_on=['Team2', 'Season'],
                right_on=['TeamName', 'Season'],
                suffixes=('_1', '_2')
            ).drop(columns=['TeamName'])
            
            # Create matchup-specific features
            matchups_df['SeedDiff'] = matchups_df['seed_1'] - matchups_df['seed_2']
            matchups_df['EfficiencyDiffDelta'] = matchups_df['EfficiencyDiff_1'] - matchups_df['EfficiencyDiff_2']
            matchups_df['TempoRatio'] = matchups_df['AdjTempo_1'] / matchups_df['AdjTempo_2']
            
            return matchups_df
            
        except Exception as e:
            logger.error(f"Error preparing matchup data: {str(e)}")
            raise

    def process_seasons(self, start_year: int, end_year: int) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Process multiple seasons of data and create features"""
        try:
            # Load and combine season data
            df = self.load_multiple_seasons(start_year, end_year)
            
            # Create features
            feature_df = self.create_features(df)
            
            # Prepare matchup data
            matchup_df = self.prepare_matchup_data(feature_df)
            
            # Save processed data
            feature_df.to_csv(self.processed_data_path / f'features_{start_year}_{end_year}.csv', index=False)
            matchup_df.to_csv(self.processed_data_path / f'matchups_{start_year}_{end_year}.csv', index=False)
            
            return feature_df, matchup_df
            
        except Exception as e:
            logger.error(f"Error processing seasons: {str(e)}")
            raise

if __name__ == "__main__":
    # Example usage
    processor = MarchMadnessDataProcessor()
    
    # Process last 5 seasons (2020-2024)
    features_df, matchups_df = processor.process_seasons(2021, 2024)
    
    print("\nFeature DataFrame Info:")
    print(features_df.info())
    print("\nSample features for one team:")
    print(features_df[features_df['Season'] == 2024].head(1))
    
    print("\nMatchup DataFrame Info:")
    print(matchups_df.info())
    print("\nSample matchup:")
    print(matchups_df[matchups_df['Season'] == 2024].head(1))