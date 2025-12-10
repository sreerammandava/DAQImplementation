import re
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

INPUT_FILENAME = 'Data.txt'
OUTPUT_IMAGE = 'heatmap_normalized.png'

def parse_log_file(filename):
    """
    Parses the log file to extract (x, y) coordinates and Vpp values.
    Returns a list of dictionaries.
    """
    # Regex patterns
    coord_pattern = re.compile(r"Move to X:\s*([\d\.]+)\s*cm,\s*Y:\s*([\d\.]+)\s*cm")
    vpp_pattern = re.compile(r"-> Recorded Vpp:\s*([\d\.]+)\s*V")

    data_map = {} 
    current_x = None
    current_y = None

    try:
        with open(filename, 'r') as f:
            for line in f:
                # Check for coordinates
                coord_match = coord_pattern.search(line)
                if coord_match:
                    current_x = float(coord_match.group(1))
                    current_y = float(coord_match.group(2))
                    continue

                # Check for Voltage
                vpp_match = vpp_pattern.search(line)
                if vpp_match and current_x is not None and current_y is not None:
                    vpp = float(vpp_match.group(1))
                    data_map[(current_x, current_y)] = vpp
                    current_x = None 
                    current_y = None
                    
    except FileNotFoundError:
        print(f"Error: Could not find file '{filename}'.")
        return []

    clean_data = []
    for (x, y), vpp in data_map.items():
        clean_data.append({'x': x, 'y': y, 'vpp': vpp})
        
    return clean_data

def generate_heatmap(data):
    if not data:
        print("No data found.")
        return

    # 1. Create DataFrame
    df = pd.DataFrame(data)

    # 2. Calculate Raw Power (Vpp^2)
    df['power'] = df['vpp'] ** 2

    # 3. NORMALIZE the Power
    # Find the maximum power peak in the dataset
    max_power = df['power'].max()
    
    # Divide all points by the max power (Result is 0.0 to 1.0)
    df['normalized_power'] = df['power'] / max_power

    # 4. Pivot for Heatmap
    heatmap_data = df.pivot(index='y', columns='x', values='normalized_power')
    
    # Sort index so Y=0 is at the bottom (physically accurate)
    heatmap_data = heatmap_data.sort_index(ascending=True)

    # 5. Plotting
    plt.figure(figsize=(10, 8))
    
    ax = sns.heatmap(heatmap_data, 
                     cmap='viridis', 
                     annot=False, 
                     fmt=".2f",
                     square=True,
                     vmin=0.0, # Force scale min to 0
                     vmax=1.0, # Force scale max to 1
                     cbar_kws={'label': 'Normalized Power ($P / P_{max}$)'})

    # Invert Y axis to put (0,0) at bottom-left
    ax.invert_yaxis()

    plt.title('Normalized Ultrasonic Field Distribution')
    plt.xlabel('X Position (cm)')
    plt.ylabel('Y Position (cm)')
    
    plt.tight_layout()
    plt.savefig(OUTPUT_IMAGE, dpi=300)
    print(f"Heatmap saved to {OUTPUT_IMAGE}")
    plt.show()

if __name__ == "__main__":
    data = parse_log_file(INPUT_FILENAME)
    generate_heatmap(data)
