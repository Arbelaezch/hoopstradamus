import csv
import re

def clean_team_name(team):
    # Remove seed numbers (digits) from the end of team names
    return re.sub(r'\s+\d+$', '', team)

def parse_input_file(filename):
    # Read the input file
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    # Remove empty lines and strip whitespace
    lines = [line.strip() for line in lines if line.strip()]
    
    # Find the data rows (those starting with a number followed by a team name)
    data_rows = []
    for line in lines:
        if re.match(r'^\d+\s+\S+', line):  # Matches lines starting with number followed by text
            data_rows.append(line)
    
    # Process each data row
    processed_data = []
    shot_types = ['Dunks', 'Close_Twos', 'Farther_Twos', 'Threes']
    sides = ['Offense', 'Defense']
    
    for row in data_rows:
        try:
            # Split the row while preserving spaces in team names
            parts = re.split(r'\s+', row.strip())
            
            # First element is always rank number
            rank = parts[0]
            
            # Find the numerical data - they always come in pairs
            # Work backwards from the end since we know the pattern of numbers
            numbers = []
            current_pos = len(parts) - 1
            
            # We expect 16 numbers (8 pairs for 4 shot types × 2 sides)
            while len(numbers) < 16 and current_pos >= 0:
                if re.match(r'^-?\d+\.?\d*$', parts[current_pos]):
                    numbers.insert(0, parts[current_pos])
                current_pos -= 1
            
            # The conference will be right before the numbers
            conference = parts[current_pos]
            
            # Everything between rank and conference is the team name
            team = ' '.join(parts[1:current_pos])
            # Clean the team name to remove seed numbers
            team = clean_team_name(team)
            
            # Verify we have the right number of data points
            if len(numbers) != 16:
                print(f"Warning: Row for {team} has {len(numbers)} values instead of 16")
                continue
                
            # Create rows for each shot type and side
            idx = 0
            for shot_type in shot_types:
                for side in sides:
                    try:
                        fg_pct = float(numbers[idx])
                        share = float(numbers[idx + 1])
                        processed_data.append([
                            team.strip(),
                            conference.strip(),
                            shot_type,
                            side,
                            fg_pct,
                            share
                        ])
                        idx += 2
                    except ValueError:
                        print(f"Warning: Invalid number format in row for {team}")
                        continue
                        
        except Exception as e:
            print(f"Error processing row: {row}")
            print(f"Error details: {str(e)}")
            continue
    
    return processed_data

def write_csv(data, output_filename):
    with open(output_filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        # Write header
        writer.writerow(['Team', 'Conference', 'Shot_Type', 'Side', 'FG_Percentage', 'Share'])
        # Write data
        writer.writerows(data)

def main():
    # Process all text files from 2014 to 2024
    for year in range(2014, 2025):
        input_filename = f"{year}.txt"
        output_filename = f"{year}_processed.csv"
        
        try:
            print(f"Processing {input_filename}...")
            data = parse_input_file(input_filename)
            if data:
                write_csv(data, output_filename)
                print(f"Successfully processed {input_filename} to {output_filename}")
                print(f"Processed {len(data)} rows of data")
            else:
                print(f"No valid data found in {input_filename}")
        except FileNotFoundError:
            print(f"Warning: {input_filename} not found")
        except Exception as e:
            print(f"Error processing {input_filename}: {str(e)}")

if __name__ == "__main__":
    main()