import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq
import os

def analyze_all_columns(file_path, sheet_name, columns_to_analyze, output_folder):
    """
    Iterates through specified columns, performs spectral analysis, 
    saves plots as PNG files, and exports data to a new Excel sheet.
    """
    all_results = []
    
    # Ensure the output directory exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"Created directory: {output_folder}")

    # 1. Load the data
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
    except Exception as e:
        print(f"Error loading file: {e}")
        return

    # 2. Process each column
    for col in columns_to_analyze:
        if col not in df.columns:
            print(f"Column {col} missing. Skipping...")
            continue

        # --- Signal Processing ---
        signal = df[col].values
        # Drop NaN values (empty cells) to prevent FFT failure
        signal = signal[~np.isnan(signal)]
        
        if len(signal) == 0:
            continue

        signal_centered = signal - np.mean(signal)
        n = len(signal_centered)
        
        # FFT Calculations
        yf = fft(signal_centered)
        xf = fftfreq(n, 1)
        
        pos_mask = xf > 0
        frequencies = xf[pos_mask]
        magnitudes = np.abs(yf[pos_mask])
        
        # --- Thresholding ---
        mags_no_dc = magnitudes[1:]
        mean_noise = np.mean(mags_no_dc)
        std_noise = np.std(mags_no_dc)
        
        sigma_threshold = mean_noise + 3 * std_noise
        snr_threshold_val = mean_noise * (10**(3/10))
        
        # --- Visualization and Saving ---
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        fig.suptitle(f"Spectral Analysis - Column: {col}", fontsize=16)
        
        # Plot 1: Time Domain
        ax1.plot(signal_centered, color='gray', alpha=0.6)
        ax1.axhline(0, color='black', linestyle='--')
        ax1.set_title("Time Domain (Centered Signal)")
        ax1.set_xlabel("Draw Number")
        ax1.set_ylabel("Amplitude")
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Frequency Domain
        ax2.plot(frequencies[1:], magnitudes[1:], color='blue', label='Spectrum')
        ax2.axhline(y=sigma_threshold, color='red', linestyle='--', label='3-Sigma Threshold')
        ax2.axhline(y=snr_threshold_val, color='green', linestyle=':', label='3dB SNR Threshold')
        ax2.set_title("Frequency Domain (FFT)")
        ax2.set_xlabel("Frequency (Cycles/Draw)")
        ax2.set_ylabel("Magnitude")
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        
        # Save the figure to the specified path
        file_name = f"Analysis_Column_{col}.png"
        save_path = os.path.join(output_folder, file_name)
        plt.savefig(save_path)
        print(f"Saved plot: {save_path}")
        
        # Close plot to free up memory
        plt.close(fig)

        # --- Data Collection ---
        sig_idx = np.where((magnitudes > sigma_threshold) | (magnitudes > snr_threshold_val))[0]
        
        for idx in sig_idx:
            freq = frequencies[idx]
            mag = magnitudes[idx]
            all_results.append({
                'Column': col,
                'Frequency': freq,
                'Period (Draws)': 1/freq,
                'Magnitude': mag,
                'SNR_dB': 10 * np.log10(mag / mean_noise),
                'Passed_3_Sigma': mag > sigma_threshold
            })

    # 3. Export all statistical data to a new Excel sheet
    if all_results:
        try:
            results_df = pd.DataFrame(all_results)
            with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                results_df.to_excel(writer, sheet_name='Analysis_Results', index=False)
            print(f"\nAnalysis complete! Excel data updated in sheet 'Analysis_Results'.")
        except Exception as e:
            print(f"Error saving to Excel: {e}. (Ensure the file is closed!)")
    else:
        print("\nNo significant patterns found.")

# --- Settings ---
excel_path = r'C:\\Users\\idowe\\MyProjects\\Lottery-estimation\\Lotto.xlsx'
sheet = 'Time domain - special number'
columns = [1, 2, 3, 4, 5, 6, 7]
graphs_path = r'C:\\Users\\idowe\\MyProjects\\Lottery-estimation\\Graphs\\the strong number - time and frequency analysis'

# --- Run ---
analyze_all_columns(excel_path, sheet, columns, graphs_path)