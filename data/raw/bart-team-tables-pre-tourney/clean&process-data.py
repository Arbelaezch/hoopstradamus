import os
import pandas as pd

def convert_table_to_csv(input_file, output_file):
    # Read the table file
    df = pd.read_csv(input_file, sep='\t', skipinitialspace=True)
    
    # Drop the first unnamed index column (row numbers)
    df = df.drop(df.columns[0], axis=1)
    
    # Drop the duplicate Team column at the end
    df = df.drop(df.columns[-1], axis=1)
    
    # Drop the Record column
    df = df.drop('Record', axis=1)
    
    # Calculate Losses from Games and Wins
    df['Losses'] = df['Games'] - df['Wins']
    
    # Clean up any extra whitespace in column names
    df.columns = df.columns.str.strip()
    
    # Save to CSV
    df.to_csv(output_file, index=False)

def process_all_files(input_dir='.'):
    # Process all txt files from 2014 to 2024
    for year in range(2014, 2025):
        input_file = f"{year}.txt"
        output_file = f"{year}.csv"
        
        # Check if input file exists
        if os.path.exists(input_file):
            try:
                convert_table_to_csv(input_file, output_file)
                print(f"Successfully converted {input_file} to {output_file}")
            except Exception as e:
                print(f"Error processing {input_file}: {str(e)}")
        else:
            print(f"File not found: {input_file}")

if __name__ == "__main__":
    process_all_files()