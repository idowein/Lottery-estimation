import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq

def analyze_lottery_periodicity(file_path, sheet_name=0, column_name='ball 1'):
    # Load specific sheet from Excel file
    try:
        # Using sheet_name to target the correct tab in Excel
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        
        # Ensure the column exists in the selected sheet
        if column_name not in df.columns:
            print(f"Column '{column_name}' not found in sheet '{sheet_name}'")
            print(f"Available columns: {df.columns.tolist()}")
            return
            
        signal = df[column_name].values
    except Exception as e:
        print(f"Error loading file or sheet: {e}")
        return

    # Subtract mean to remove DC component (frequency 0 spike)
    signal_centered = signal - np.mean(signal)
    
    n = len(signal_centered)
    # Compute Fast Fourier Transform
    yf = fft(signal_centered)
    # Generate frequency axis (1 sample per draw)
    xf = fftfreq(n, 1) 

    # Filter for positive frequencies only
    pos_mask = xf > 0
    frequencies = xf[pos_mask]
    magnitudes = np.abs(yf[pos_mask])
    
    # Convert frequency (1/draws) to period (draws per cycle)
    periods = 1 / frequencies

    # Visualization
    plt.figure(figsize=(14, 6))
    
    # Plot Frequency Domain
    plt.subplot(1, 2, 1)
    plt.plot(frequencies, magnitudes)
    plt.title(f'Frequency Domain (Sheet: {sheet_name})')
    plt.xlabel('Frequency (Cycles per Draw)')
    plt.ylabel('Magnitude')
    plt.grid(True, alpha=0.3)

    # Plot Periodicity (Focusing on cycles between 2 and 100 draws)
    plt.subplot(1, 2, 2)
    plt.plot(periods, magnitudes)
    plt.title('Periodicity Analysis (Time Domain Interpretation)')
    plt.xlabel('Period (Every X Draws)')
    plt.ylabel('Magnitude')
    plt.xlim(2, 100) 
    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()

    # Identify and print top 5 periodicities
    top_indices = np.argsort(magnitudes)[-5:][::-1]
    print(f"Top Periodicities Identified in '{sheet_name}':")
    print("-" * 40)
    for idx in top_indices:
        print(f"Cycle detected every {periods[idx]:.2f} draws (Strength: {magnitudes[idx]:.2f})")

# Example Usage:
analyze_lottery_periodicity('C:\\Users\\idowe\\Downloads\\Lotto.xlsx', sheet_name='Time domain 1-6 numbers', column_name='ball 36')