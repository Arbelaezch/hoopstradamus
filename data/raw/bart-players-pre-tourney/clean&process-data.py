import re
import pandas as pd

def parse_player_info(player_row):
    parts = player_row.split('\t')
    if len(parts) < 3:
        return None, None, None
    
    year = parts[0].strip()
    height = parts[1].strip()
    name = parts[2].strip()
    
    return year, height, name

def parse_shot_stats(made_attempted, percentage):
    if not made_attempted or not percentage:
        return None, None, None
    
    try:
        made, attempted = map(int, made_attempted.split('-'))
        pct = float(percentage.strip('.'))  # Remove the leading dot
        return made, attempted, pct/1000    # Convert from .620 format to 0.620
    except (ValueError, AttributeError):
        return None, None, None

def convert_table_to_csv(input_file, output_file):
    with open(input_file, 'r') as f:
        lines = f.readlines()
    
    data = []
    for line in lines[1:]:  # Skip header
        cols = line.strip().split('\t')
        if len(cols) < 15:
            continue
            
        # Parse player information
        player_cols = cols[:4]
        remaining_cols = cols[4:]
        
        year, height, name = parse_player_info('\t'.join(player_cols[1:]))
        
        # The shooting stats are in fixed positions from the end
        # remaining_cols[-5] = "77-184"
        # remaining_cols[-4] = ".418"
        # remaining_cols[-3] = "7.4"
        # remaining_cols[-2] = "40-130"
        # remaining_cols[-1] = ".308"
        
        twop_made_attempted = remaining_cols[-5]
        twop_pct = remaining_cols[-4]
        threep_per_100 = remaining_cols[-3]
        threep_made_attempted = remaining_cols[-2]
        threep_pct = remaining_cols[-1]
        
        # Parse shooting stats
        twop_made, twop_attempted, twop_percentage = parse_shot_stats(twop_made_attempted, twop_pct)
        threep_made, threep_attempted, threep_percentage = parse_shot_stats(threep_made_attempted, threep_pct)
        
        row = {
            'Rank': player_cols[0],
            'Year': year,
            'Height': height,
            'Player': name,
            'Team': remaining_cols[0],
            'Conf': remaining_cols[1],
            'Min%': remaining_cols[2],
            'PRPG': remaining_cols[3],
            'BPM': remaining_cols[4],
            'ORtg': remaining_cols[5],
            'Usg': remaining_cols[6],
            'eFG': remaining_cols[7],
            'TS': remaining_cols[8],
            'OR': remaining_cols[9],
            'DR': remaining_cols[10],
            'Ast': remaining_cols[11],
            'TO': remaining_cols[12],
            'Blk': remaining_cols[13],
            'Stl': remaining_cols[14],
            'FTR': remaining_cols[15],
            '2P_Made': twop_made,
            '2P_Attempted': twop_attempted,
            '2P%': twop_percentage,
            '3P/100': threep_per_100,
            '3P_Made': threep_made,
            '3P_Attempted': threep_attempted,
            '3P%': threep_percentage
        }
        data.append(row)
    
    df = pd.DataFrame(data)
    df.to_csv(output_file, index=False)

# Usage example
for year in range(2014, 2025):
    input_file = f"{year}.txt"
    output_file = f"{year}_processed.csv"
    try:
        convert_table_to_csv(input_file, output_file)
        print(f"Successfully processed {input_file}")
    except Exception as e:
        print(f"Error processing {input_file}: {str(e)}")