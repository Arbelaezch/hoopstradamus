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

    def load_multiple_seasons(self, years: List[int]) -> pd.DataFrame:
        """Load and combine multiple seasons of data"""
        all_seasons = []
        for year in years:
            try:
                season_df = self.load_season_data(year)
                all_seasons.append(season_df)
            except Exception as e:
                logger.warning(f"Couldn't load {year} season: {str(e)}")
                continue
        
        if not all_seasons:
            raise ValueError("No seasons could be loaded")
        
        return pd.concat(all_seasons, ignore_index=True)

    def create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create features for model training"""
        try:
            logger.info(f"Input DataFrame columns: {df.columns.tolist()}")
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
            
            logger.info(f"Output DataFrame columns: {feature_df.columns.tolist()}")
            logger.info(f"Number of records: {len(feature_df)}")
            
            return feature_df
            
        except Exception as e:
            logger.error(f"Error creating features: {str(e)}")
            raise

    def prepare_matchup_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare data for matchup prediction between tournament teams only"""
        try:
            seasons = sorted(df['Season'].unique())
            logger.info(f"Processing tournament matchups for seasons: {seasons}")
            
            all_matchups = []
            
            # Process each season separately
            for season in seasons:
                logger.info(f"Generating tournament matchups for season {season}")
                
                # Filter data for current season
                season_df = df[df['Season'] == season]
                
                # Get ONLY tournament teams for this season
                tourney_df = season_df[season_df['IsTourney']]
                tourney_teams = tourney_df['TeamName'].unique()
                logger.info(f"Found {len(tourney_teams)} tournament teams for season {season}")
                
                if len(tourney_teams) == 0:
                    logger.warning(f"No tournament teams found for season {season}")
                    continue
                    
                # Generate matchups only between tournament teams
                season_matchups = []
                for team1 in tourney_teams:
                    for team2 in tourney_teams:
                        if team1 != team2:
                            season_matchups.append({
                                'Team1': team1,
                                'Team2': team2,
                                'Season': int(season)
                            })
                
                all_matchups.extend(season_matchups)
                logger.info(f"Generated {len(season_matchups)} tournament matchups for season {season}")
            
            if not all_matchups:
                raise ValueError("No tournament matchups were generated")
                
            # Convert to DataFrame
            matchups_df = pd.DataFrame(all_matchups)
            logger.info(f"Total tournament matchups generated: {len(matchups_df)}")
            logger.info(f"Matchups by season:\n{matchups_df['Season'].value_counts().sort_index()}")
            
            # Add team features for both teams
            team1_cols = ['TeamName', 'AdjOE', 'AdjDE', 'AdjTempo', 'EfficiencyDiff', 
                        'TempoAdjOffEff', 'TempoAdjDefEff', 'OverallRankScore', 'seed', 'Season']
            
            # First merge for Team1
            logger.info("Adding Team1 features...")
            matchups_df = matchups_df.merge(
                df[df['IsTourney']][team1_cols],  # Only use tournament teams for merging
                left_on=['Team1', 'Season'],
                right_on=['TeamName', 'Season'],
                validate='m:1'
            ).drop(columns=['TeamName'])
            
            # Second merge for Team2
            logger.info("Adding Team2 features...")
            matchups_df = matchups_df.merge(
                df[df['IsTourney']][team1_cols],  # Only use tournament teams for merging
                left_on=['Team2', 'Season'],
                right_on=['TeamName', 'Season'],
                suffixes=('_1', '_2'),
                validate='m:1'
            ).drop(columns=['TeamName'])
            
            # Create matchup-specific features
            matchups_df['SeedDiff'] = matchups_df['seed_1'] - matchups_df['seed_2']
            matchups_df['EfficiencyDiffDelta'] = matchups_df['EfficiencyDiff_1'] - matchups_df['EfficiencyDiff_2']
            matchups_df['TempoRatio'] = matchups_df['AdjTempo_1'] / matchups_df['AdjTempo_2']
            
            # Final verification
            logger.info(f"Final tournament matchups shape: {matchups_df.shape}")
            logger.info(f"Final seasons in matchups:\n{matchups_df['Season'].value_counts().sort_index()}")
            
            return matchups_df
            
        except Exception as e:
            logger.error(f"Error preparing matchup data: {str(e)}")
            raise

    def process_seasons(self, years: List[int]) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Process specified seasons of data and create features"""
        try:
            # Load and combine season data
            df = self.load_multiple_seasons(years)
            
            # Create features
            feature_df = self.create_features(df)
            
            # Prepare matchup data
            matchup_df = self.prepare_matchup_data(feature_df)
            
            # Save processed data
            years_str = f"{min(years)}-{max(years)}"
            feature_df.to_csv(self.processed_data_path / f'features_{years_str}.csv', index=False)
            matchup_df.to_csv(self.processed_data_path / f'matchups_{years_str}.csv', index=False)
            
            logger.info(f"Processed data saved for years {years_str}")
            
            return feature_df, matchup_df
            
        except Exception as e:
            logger.error(f"Error processing seasons: {str(e)}")
            raise

if __name__ == "__main__":
    # Example usage
    processor = MarchMadnessDataProcessor()
    
    # Define years to process (2014-2024 excluding 2020)
    years_to_process = list(range(2014, 2020)) + list(range(2021, 2025))
    
    # Process all seasons
    features_df, matchups_df = processor.process_seasons(years_to_process)
    
    print("\nFeature DataFrame Info:")
    print(features_df.info())
    
    print("\nSeasons in features dataset:")
    print(features_df['Season'].value_counts().sort_index())
    
    print("\nSeasons in matchups dataset:")
    print(matchups_df['Season'].value_counts().sort_index())
    
    print("\nSample features for most recent season:")
    print(features_df[features_df['Season'] == max(years_to_process)].head(1))
    
    print("\nMatchup DataFrame Info:")
    print(matchups_df.info())
    print("\nSample matchup from most recent season:")
    print(matchups_df[matchups_df['Season'] == max(years_to_process)].head(1))
    
    # Print some summary statistics
    print("\nNumber of teams per season:")
    print(features_df.groupby('Season')['TeamName'].count())
    
    print("\nNumber of tournament teams per season:")
    print(features_df[features_df['IsTourney']].groupby('Season')['TeamName'].count())