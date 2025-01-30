import pandas as pd
import os
from glob import glob
from datetime import datetime

def convert_date(date_str):
    """Convert date from M/D/YY to YYYY-MM-DD format"""
    try:
        # Parse the date string
        date_obj = datetime.strptime(date_str, '%m/%d/%y')
        # Format as YYYY-MM-DD
        return date_obj.strftime('%Y-%m-%d')
    except Exception as e:
        print(f"Error converting date {date_str}: {str(e)}")
        return date_str

def parse_result(result):
    """Parse result string like 'W, 111-77' into components"""
    try:
        # Remove any quotes from the result string
        result = result.strip('"')
        # Split into win/loss and score
        outcome, score = result.split(', ')
        # Convert W/L to binary
        is_win = 1 if outcome == 'W' else 0
        # Split score into points for and against
        points_for, points_against = map(int, score.split('-'))
        # Calculate point differential
        point_diff = points_for - points_against
        
        return is_win, points_for, points_against, point_diff
    except Exception as e:
        print(f"Error parsing result {result}: {str(e)}")
        return None, None, None, None

def expand_venue(venue):
    """Convert H/A/N to more descriptive values"""
    venue_map = {
        'H': 'Home',
        'A': 'Away',
        'N': 'Neutral'
    }
    return venue_map.get(venue, venue)

def process_csv_files(directory):
    """
    Process all schedule CSV files in the given directory:
    - Drop # and Rk columns
    - Standardize dates
    - Split result into components and drop original Result column
    - Expand venue descriptions
    
    Args:
        directory (str): Path to directory containing CSV files
    """
    # Create pattern to match files like '2013-14_schedule.csv' through '2023-24_schedule.csv'
    pattern = os.path.join(directory, '*_schedule.csv')
    
    # Get list of all matching files
    csv_files = glob(pattern)
    
    for file_path in csv_files:
        # Skip 2019-2020 season
        if '2019-2020_schedule.csv' in file_path:
            print(f"Skipping {file_path} as requested")
            continue
            
        try:
            # Read the CSV file
            df = pd.read_csv(file_path)
            
            # Drop the # and Rk columns
            if '#' in df.columns:
                df = df.drop('#', axis=1)
            if 'Rk' in df.columns:
                df = df.drop('Rk', axis=1)
            
            # Standardize dates
            df['Date'] = df['Date'].apply(convert_date)
            
            # Parse results into separate columns
            result_components = df['Result'].apply(parse_result)
            df['Win'] = result_components.apply(lambda x: x[0])
            df['Points_For'] = result_components.apply(lambda x: x[1])
            df['Points_Against'] = result_components.apply(lambda x: x[2])
            df['Point_Differential'] = result_components.apply(lambda x: x[3])
            
            # Drop the original Result column
            df = df.drop('Result', axis=1)
            
            # Expand venue descriptions
            df['Venue'] = df['Venue'].apply(expand_venue)
            
            # Create output filename
            base_name = os.path.basename(file_path)
            output_path = os.path.join(directory, f"enhanced_{base_name}")
            
            # Save processed file
            df.to_csv(output_path, index=False)
            
            print(f"Successfully processed {file_path}")
            print(f"Saved to {output_path}")
            print(f"Added columns: Win, Points_For, Points_Against, Point_Differential")
            print(f"Dropped columns: #, Rk, Result")
            print(f"Enhanced Date and Venue formats")
            
        except Exception as e:
            print(f"Error processing {file_path}: {str(e)}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python enhance_data.py directory_path")
        sys.exit(1)
    
    directory = sys.argv[1]
    
    if not os.path.isdir(directory):
        print(f"Error: {directory} is not a valid directory")
        sys.exit(1)
    
    process_csv_files(directory)