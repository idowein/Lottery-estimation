import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq

def analyze_lottery_periodicity(file_path, sheet_name='Time domain 1-6 numbers', column_name='ball 36'):
    # Load specific sheet from Excel file
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        
        if column_name not in df.columns:
            print(f"Column '{column_name}' not found in sheet '{sheet_name}'")
            print(f"Available columns: {df.columns.tolist()}")
            return
            
        signal = df[column_name].values
    except Exception as e:
        print(f"Error loading file or sheet: {e}")
        return

    # 1. Time Domain Prep
    signal_centered = signal - np.mean(signal)
    n = len(signal_centered)
    t = np.arange(n) 

    # 2. Frequency Domain Prep
    yf = fft(signal_centered)
    xf = fftfreq(n, 1) 

    pos_mask = xf > 0
    frequencies = xf[pos_mask]
    magnitudes = np.abs(yf[pos_mask])
    
    # --- Visualization ---
    plt.figure(figsize=(14, 5))
    
    # Plot 1: Time Domain (Left)
    plt.subplot(1, 2, 1)
    plt.plot(t, signal_centered, color='gray', alpha=0.6)
    plt.axhline(0, color='black', lw=1, ls='--')
    plt.title(f'Time Domain\nSheet: {sheet_name} | Column: {column_name}')
    plt.xlabel('Draw Number (n)')
    plt.ylabel('Amplitude (Centered)')
    plt.grid(True, alpha=0.3)

    # Plot 2: Frequency Domain (Right)
    plt.subplot(1, 2, 2)
    # Ignore the zero freqs
    plt.plot(frequencies[1:], magnitudes[1:], color='blue')
    plt.title('Frequency Domain (k/N)')
    plt.xlabel('Frequency (Cycles per Draw)')
    plt.ylabel('Magnitude')
    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()

    # Identify and print top 5 periodicities
    top_indices = np.argsort(magnitudes)[-5:][::-1]
    print(f"\nTop Frequencies Identified in '{sheet_name}' for '{column_name}':")
    print("-" * 55)
    for idx in top_indices:
        period = 1 / frequencies[idx]
        print(f"Freq: {frequencies[idx]:.4f} | Every {period:.2f} draws | Strength: {magnitudes[idx]:.2f}")

analyze_lottery_periodicity('C:\\Users\\idowe\\MyProjects\\Lottery-estimation\\Lotto.xlsx', 
                            sheet_name='Time domain - the strong number', 
                            column_name='ball 6')