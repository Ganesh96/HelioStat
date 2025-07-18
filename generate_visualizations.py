"""
generate_visualizations.py

This script performs a data visualization for solar panel tilt analysis to determine
the optimal tilt strategies for maximizing Global Horizontal Irradiance (GHI)
based on hourly solar data.

Author: Santhanam, Ganesan
Date: June 28, 2025 - July 18, 2025
Affiliation: University Of Florida
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from main_solar_analysis import SolarAnalysis # Import the class from the other file

def get_monthly_ghi_data(analyzer: SolarAnalysis, sky_condition: str) -> pd.DataFrame:
    """
    Calculates the GHI for every month for each of the 6 arrangements.

    Args:
        analyzer: An instantiated SolarAnalysis object.
        sky_condition: 'cloudy' or 'clear'.

    Returns:
        A DataFrame with months as rows and arrangements as columns.
    """
    
    # --- Tilts for each arrangement ---
    # Arr 4: Find optimal tilt for each month
    monthly_tilts_arr4 = [analyzer.find_optimal_tilt([m], sky_condition)[0] for m in range(1, 13)]
    
    # Arr 5: Find one optimal tilt for summer and one for winter
    opt_tilt_summer, _ = analyzer.find_optimal_tilt(analyzer.SUMMER_MONTHS, sky_condition)
    opt_tilt_winter, _ = analyzer.find_optimal_tilt(analyzer.WINTER_MONTHS, sky_condition)
    monthly_tilts_arr5 = [opt_tilt_summer if m in analyzer.SUMMER_MONTHS else opt_tilt_winter for m in range(1, 13)]

    # Arr 6: Find one optimal tilt for the whole year
    opt_tilt_annual, _ = analyzer.find_optimal_tilt(list(range(1, 13)), sky_condition)

    # --- Collect monthly GHI data ---
    data = {}
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    for i, month_name in enumerate(month_names):
        month_num = i + 1
        
        # Calculate GHI for this month using the tilt defined by each arrangement
        adjustment = analyzer.EARTH_AXIAL_TILT / 2
        
        data.setdefault("Month", []).append(month_name)
        data.setdefault("Arr 1: 0° Fixed", []).append(analyzer.calculate_ghi_for_tilt(0, [month_num], sky_condition))
        data.setdefault("Arr 2: 29° Fixed", []).append(analyzer.calculate_ghi_for_tilt(analyzer.LATITUDE_DEGREES, [month_num], sky_condition))
        
        # Arr 3 uses different tilts for summer/winter
        tilt_arr3 = (analyzer.LATITUDE_DEGREES - adjustment) if month_num in analyzer.SUMMER_MONTHS else (analyzer.LATITUDE_DEGREES + adjustment)
        data.setdefault("Arr 3: Two-Season Fixed", []).append(analyzer.calculate_ghi_for_tilt(tilt_arr3, [month_num], sky_condition))

        data.setdefault("Arr 4: Monthly Optimal", []).append(analyzer.calculate_ghi_for_tilt(monthly_tilts_arr4[i], [month_num], sky_condition))
        data.setdefault("Arr 5: Two-Season Optimal", []).append(analyzer.calculate_ghi_for_tilt(monthly_tilts_arr5[i], [month_num], sky_condition))
        data.setdefault("Arr 6: Annual Optimal", []).append(analyzer.calculate_ghi_for_tilt(opt_tilt_annual, [month_num], sky_condition))

    return pd.DataFrame(data).set_index("Month")

def plot_monthly_comparison(monthly_df: pd.DataFrame, arr1_name: str, arr2_name: str, sky_condition: str, year: int):
    """Generates a grouped bar chart comparing the monthly GHI of two arrangements."""
    
    df_to_plot = monthly_df[[arr1_name, arr2_name]]
    
    df_to_plot.plot(kind='bar', figsize=(12, 7), width=0.8)
    
    plt.title(f'Monthly GHI Comparison: {arr1_name} vs. {arr2_name} ({year}, {sky_condition.capitalize()} Sky)', fontsize=16)
    plt.ylabel('GHI Output (Wh/m²)', fontsize=12)
    plt.xlabel('Month', fontsize=12)
    plt.xticks(rotation=0)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.legend(title='Arrangement')
    plt.tight_layout()
    plt.show()

def plot_tilt_strategies(analyzer: SolarAnalysis, sky_condition: str, year: int):
    """Plots the tilt angles used by each arrangement over the year."""
    
    plt.figure(figsize=(14, 8))
    months = list(range(1, 13))
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    
    # --- Get tilts for each strategy ---
    tilts = {}
    tilts['Arr 1: 0° Fixed'] = [0] * 12
    tilts['Arr 2: 29° Fixed'] = [analyzer.LATITUDE_DEGREES] * 12
    
    adjustment = analyzer.EARTH_AXIAL_TILT / 2
    tilts['Arr 3: Two-Season Fixed'] = [(analyzer.LATITUDE_DEGREES - adjustment) if m in analyzer.SUMMER_MONTHS else (analyzer.LATITUDE_DEGREES + adjustment) for m in months]

    tilts['Arr 4: Monthly Optimal'] = [analyzer.find_optimal_tilt([m], sky_condition)[0] for m in months]
    
    opt_tilt_summer, _ = analyzer.find_optimal_tilt(analyzer.SUMMER_MONTHS, sky_condition)
    opt_tilt_winter, _ = analyzer.find_optimal_tilt(analyzer.WINTER_MONTHS, sky_condition)
    tilts['Arr 5: Two-Season Optimal'] = [opt_tilt_summer if m in analyzer.SUMMER_MONTHS else opt_tilt_winter for m in months]
    
    opt_tilt_annual, _ = analyzer.find_optimal_tilt(months, sky_condition)
    tilts['Arr 6: Annual Optimal'] = [opt_tilt_annual] * 12

    # --- Plotting ---
    for name, tilt_values in tilts.items():
        # Use drawstyle='steps-post' for step-like functions
        drawstyle = 'steps-post' if name in ['Arr 3: Two-Season Fixed', 'Arr 5: Two-Season Optimal'] else 'default'
        plt.plot(months, tilt_values, marker='o', linestyle='--', label=name, drawstyle=drawstyle)

    plt.title(f'Comparison of Tilt Angle Strategies ({year}, {sky_condition.capitalize()} Sky)', fontsize=16)
    plt.xlabel('Month', fontsize=12)
    plt.ylabel('Panel Tilt Angle (Degrees)', fontsize=12)
    plt.xticks(months, month_names)
    plt.yticks(np.arange(0, 51, 5))
    plt.legend(title='Arrangement', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()

def plot_cumulative_gain(monthly_df: pd.DataFrame, base_arr: str, optimized_arr: str, sky_condition: str, year: int):
    """Plots the cumulative GHI gain of an optimized strategy over a base strategy."""
    
    gain = (monthly_df[optimized_arr] - monthly_df[base_arr]).cumsum()
    
    plt.figure(figsize=(12, 7))
    gain.plot(kind='line', marker='o', legend=False)
    
    plt.title(f'Cumulative GHI Gain: {optimized_arr} vs. {base_arr} ({year}, {sky_condition.capitalize()} Sky)', fontsize=16)
    plt.ylabel('Cumulative GHI Gain (Wh/m²)', fontsize=12)
    plt.xlabel('Month', fontsize=12)
    plt.xticks(rotation=0)
    plt.grid(True, linestyle='--', alpha=0.7)
    # Add a horizontal line at y=0 for reference
    plt.axhline(0, color='black', linewidth=0.8, linestyle='--')
    plt.tight_layout()
    plt.show()

# --- Main Execution Block ---

if __name__ == "__main__":
    YEAR = 2023
    SKY_CONDITION = 'cloudy'  # Can be 'cloudy' or 'clear'
    FILE_PATH = f'{YEAR}_with_declination.csv'
    
    print(f"--- Generating Visualization Suite for {YEAR} ({SKY_CONDITION.capitalize()} Sky) ---")
    
    main_analyzer = SolarAnalysis(FILE_PATH)
    
    if main_analyzer.data is not None:
        # 1. Get the foundational monthly GHI data
        monthly_ghi_df = get_monthly_ghi_data(main_analyzer, SKY_CONDITION)
        
        # 2. Generate the requested comparison charts
        print("\nGenerating monthly comparison charts...")
        plot_monthly_comparison(monthly_ghi_df, "Arr 1: 0° Fixed", "Arr 2: 29° Fixed", SKY_CONDITION, YEAR)
        plot_monthly_comparison(monthly_ghi_df, "Arr 4: Monthly Optimal", "Arr 3: Two-Season Fixed", SKY_CONDITION, YEAR)
        plot_monthly_comparison(monthly_ghi_df, "Arr 6: Annual Optimal", "Arr 5: Two-Season Optimal", SKY_CONDITION, YEAR)
        
        # 3. Generate the tilt strategy timeline
        print("Generating tilt strategy timeline chart...")
        plot_tilt_strategies(main_analyzer, SKY_CONDITION, YEAR)
        
        # 4. Generate the cumulative gain chart
        print("Generating cumulative gain chart...")
        plot_cumulative_gain(monthly_ghi_df, "Arr 6: Annual Optimal", "Arr 4: Monthly Optimal", SKY_CONDITION, YEAR)
        
        print("\n--- All visualizations have been generated. ---")
    else:
        print("Could not generate visualizations due to data loading error.")