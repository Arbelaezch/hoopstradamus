import pandas as pd
import sys

def clean_csv(input_file, output_file):
    """
    Clean a CSV file by removing repeated headers and standardizing formatting.
    Also renames offensive and defensive stat columns with appropriate prefixes.
    
    Args:
        input_file (str): Path to input CSV file
        output_file (str): Path to output CSV file
    """
    # Read the file as text first to identify the true header row
    with open(input_file, 'r') as f:
        lines = f.readlines()
    
    # Find all header rows (they start with "#\tRk\tDate")
    header_indices = [i for i, line in enumerate(lines) 
                     if line.startswith('#\tRk\tDate') or line.startswith('Offense\tDefense')]
    
    # Get the first real header (skip "Offense Defense" line)
    if lines[header_indices[0]].startswith('Offense\tDefense'):
        header_row = header_indices[0] + 1
    else:
        header_row = header_indices[0]
    
    # Get the header line and split it into columns
    header_line = lines[header_row].strip()
    original_columns = header_line.split('\t')
    
    # Create the new column names
    stat_columns = ['EFF', 'eFG%', 'TO%', 'Reb%', 'FTR']
    new_columns = []
    
    # Find the first occurrence of 'EFF'
    first_eff_index = original_columns.index('EFF')
    
    for i, col in enumerate(original_columns):
        if col in stat_columns:
            if i >= first_eff_index and i < first_eff_index + 5:  # First group (offensive)
                new_columns.append(f'O.{col}')
            elif i >= first_eff_index + 5 and i < first_eff_index + 10:  # Second group (defensive)
                new_columns.append(f'D.{col}')
            else:
                new_columns.append(col)
        else:
            new_columns.append(col)
    
    # Create a list of non-header row indices
    data_rows = [i for i in range(len(lines)) 
                if i not in header_indices and i != header_row]
    
    # Read only the data rows with the new column names
    df = pd.read_csv(input_file, 
                     sep='\t',
                     skiprows=lambda x: x in header_indices or x == header_row,
                     names=new_columns)
    
    # Write to new CSV file
    df.to_csv(output_file, index=False)
    
    print(f"Successfully cleaned {input_file} and saved to {output_file}")
    print("Renamed columns with 'O.' and 'D.' prefixes for offensive and defensive stats")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python clean_csv.py input_file.csv output_file.csv")
        sys.exit(1)
        
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    clean_csv(input_file, output_file)