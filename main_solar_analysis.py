"""
main_solar_analysis.py

This script performs a comprehensive solar panel tilt analysis to determine
the optimal tilt strategies for maximizing Global Horizontal Irradiance (GHI)
based on hourly solar data.

Author: Santhanam, Ganesan
Date: May 2, 2025 - June 28, 2025
Affiliation: University Of Florida
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

class SolarAnalysis:
    """
    A class to perform comprehensive solar panel tilt analysis based on GHI data.
    """
    # --- Constants for the analysis ---
    LATITUDE_DEGREES = 29.651949  # Gainesville, FL
    LATITUDE_RADIANS = np.radians(LATITUDE_DEGREES)
    EARTH_AXIAL_TILT = 23.45

    WINTER_MONTHS = [10, 11, 12, 1, 2, 3]
    SUMMER_MONTHS = [4, 5, 6, 7, 8, 9]

    def __init__(self, csv_file_path: str):
        """
        Initializes the SolarAnalysis class by loading and preparing the dataset.

        Args:
            csv_file_path (str): The path to the input CSV file.
        """
        self.csv_file_path = csv_file_path
        self.data = self._load_and_prepare_data()

    def _load_and_prepare_data(self):
        """
        Loads the CSV file into a pandas DataFrame and performs initial cleaning.

        Returns:
            pd.DataFrame: A prepared DataFrame or None if loading fails.
        """
        try:
            df = pd.read_csv(self.csv_file_path)
            # Ensure essential columns are numeric
            numeric_cols = ['DHI', 'DNI', 'Clearsky DHI', 'Clearsky DNI', 'Declination Angle', 'Month']
            for col in numeric_cols:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            df.dropna(subset=numeric_cols, inplace=True)
            # Pre-calculate declination in radians
            df['Declination Angle Rad'] = np.radians(df['Declination Angle'])
            return df
        except FileNotFoundError:
            print(f"Error: The file '{self.csv_file_path}' was not found.")
            return None
        except Exception as e:
            print(f"An error occurred while loading the data: {e}")
            return None

    def calculate_ghi_for_tilt(self, tilt_degrees: float, months: list, sky_condition: str) -> float:
        """
        Calculates the total GHI for a given set of months and a fixed tilt angle.

        Args:
            tilt_degrees (float): The panel tilt angle in degrees.
            months (list): A list of month numbers to include in the calculation.
            sky_condition (str): 'cloudy' or 'clear'.

        Returns:
            float: The sum of GHI for the period.
        """
        if self.data is None:
            return 0.0

        dhi_col = 'DHI' if sky_condition == 'cloudy' else 'Clearsky DHI'
        dni_col = 'DNI' if sky_condition == 'cloudy' else 'Clearsky DNI'

        df_period = self.data[self.data['Month'].isin(months)].copy()
        
        # Filter out night hours or zero-radiation hours to speed up calculation
        df_period = df_period[~((df_period[dhi_col] == 0) & (df_period[dni_col] == 0))]

        if df_period.empty:
            return 0.0

        panel_tilt_rad = np.radians(tilt_degrees)

        # Vectorized calculation for efficiency
        declination_rad = df_period['Declination Angle Rad'].values
        dhi = df_period[dhi_col].values
        dni = df_period[dni_col].values

        theta_angle_rad = self.LATITUDE_RADIANS - panel_tilt_rad - declination_rad
        cos_theta = np.cos(theta_angle_rad)

        # Only consider positive contributions from DNI (when the sun is in front of the panel)
        dni_contribution = np.where(cos_theta > 0, cos_theta * dni, 0)
        
        ghi_output = dhi + dni_contribution
        return np.sum(ghi_output)

    def find_optimal_tilt(self, months: list, sky_condition: str) -> tuple:
        """
        Finds the single optimal tilt that maximizes GHI for a given period.

        Args:
            months (list): A list of month numbers for the optimization period.
            sky_condition (str): 'cloudy' or 'clear'.

        Returns:
            tuple: (best_tilt, max_ghi)
        """
        max_ghi = -1
        best_tilt = -1

        for tilt in range(0, 91):  # Iterate from 0 to 90 degrees
            ghi = self.calculate_ghi_for_tilt(tilt, months, sky_condition)
            if ghi > max_ghi:
                max_ghi = ghi
                best_tilt = tilt
        
        return best_tilt, max_ghi

    # --- Arrangement Analyses ---

    def analyze_arrangement_1(self, sky_condition: str) -> float:
        """Arrangement 1: Fixed 0 degrees all year."""
        return self.calculate_ghi_for_tilt(0, list(range(1, 13)), sky_condition)

    def analyze_arrangement_2(self, sky_condition: str) -> float:
        """Arrangement 2: Fixed at latitude (29 degrees) all year."""
        return self.calculate_ghi_for_tilt(self.LATITUDE_DEGREES, list(range(1, 13)), sky_condition)

    def analyze_arrangement_3(self, sky_condition: str) -> float:
        """Arrangement 3: Two fixed tilts based on latitude +/- half of Earth's axial tilt."""
        adjustment = self.EARTH_AXIAL_TILT / 2
        summer_tilt = self.LATITUDE_DEGREES - adjustment
        winter_tilt = self.LATITUDE_DEGREES + adjustment

        ghi_summer = self.calculate_ghi_for_tilt(summer_tilt, self.SUMMER_MONTHS, sky_condition)
        ghi_winter = self.calculate_ghi_for_tilt(winter_tilt, self.WINTER_MONTHS, sky_condition)
        
        return ghi_summer + ghi_winter

    def analyze_arrangement_4(self, sky_condition: str) -> float:
        """Arrangement 4: Monthly optimal tilts."""
        total_ghi = 0
        for month in range(1, 13):
            _, max_ghi = self.find_optimal_tilt([month], sky_condition)
            total_ghi += max_ghi
        return total_ghi
        
    def analyze_arrangement_5(self, sky_condition: str) -> float:
        """Arrangement 5: Optimized tilt for summer and winter periods."""
        _, ghi_summer = self.find_optimal_tilt(self.SUMMER_MONTHS, sky_condition)
        _, ghi_winter = self.find_optimal_tilt(self.WINTER_MONTHS, sky_condition)
        return ghi_summer + ghi_winter

    def analyze_arrangement_6(self, sky_condition: str) -> float:
        """Arrangement 6: Single optimal tilt for the entire year."""
        _, max_ghi = self.find_optimal_tilt(list(range(1, 13)), sky_condition)
        return max_ghi

    # --- Sliding Window Analysis ---
    
    def analyze_sliding_window(self, window_size: int, sky_condition: str) -> pd.DataFrame:
        """
        Performs a sliding window analysis to find optimal tilts for rolling periods.

        Args:
            window_size (int): The number of months in each window.
            sky_condition (str): 'cloudy' or 'clear'.

        Returns:
            pd.DataFrame: A DataFrame containing the results.
        """
        results = []
        month_names = {1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun", 
                       7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"}

        for i in range(1, 13):
            months_in_window = [(m - 1) % 12 + 1 for m in range(i, i + window_size)]
            
            # Create a name for the window (e.g., "Jan-Mar")
            start_month_name = month_names[months_in_window[0]]
            end_month_name = month_names[months_in_window[-1]]
            window_name = f"{start_month_name}-{end_month_name}"

            best_tilt, _ = self.find_optimal_tilt(months_in_window, sky_condition)
            results.append({"Window": window_name, f"Optimal Tilt ({sky_condition.capitalize()})": best_tilt})

        return pd.DataFrame(results)

# --- Plotting and Reporting Functions ---

def plot_arrangement_comparison(results_df: pd.DataFrame, year: int):
    """Plots a bar chart comparing the GHI of all arrangements."""
    results_df.plot(
        kind='bar',
        figsize=(14, 8),
        width=0.8
    )
    plt.title(f'Annual GHI Output Comparison for All Arrangements ({year})', fontsize=16)
    plt.ylabel('Total GHI (Wh/m²)', fontsize=12)
    plt.xlabel('Tilt Arrangement', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()

def plot_sliding_window_analysis(df_2022: pd.DataFrame, df_2023: pd.DataFrame):
    """Plots the sliding window analysis results for two years."""
    plt.figure(figsize=(14, 8))
    plt.plot(df_2022['Window'], df_2022.iloc[:, 1], marker='o', linestyle='-', label='2022 Optimal Tilt')
    plt.plot(df_2023['Window'], df_2023.iloc[:, 1], marker='x', linestyle='--', label='2023 Optimal Tilt')
    
    plt.title('3-Month Sliding Window Optimal Tilt Comparison (Cloudy Sky)', fontsize=16)
    plt.xlabel('3-Month Window', fontsize=12)
    plt.ylabel('Optimal Panel Tilt (Degrees)', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.yticks(np.arange(0, 61, 5))
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()


def print_declination_paragraph():
    """Prints an explanatory paragraph about the declination angle's impact."""
    print("\n" + "="*50)
    print("The Importance of the Hourly Declination Angle")
    print("="*50)
    print(
        "The sun's declination angle—its angle north or south of the celestial equator—is not constant;\n"
        "it changes continuously throughout the day and year. Early simulation models might simplify this\n"
        "by using a single average declination angle for an entire day. However, this program improves\n"
        "upon that by using a precise, hourly declination angle.\n\n"
        "This higher resolution is critical for accuracy. The core of the GHI calculation depends on the\n"
        "angle of incidence (theta), which is a function of latitude, panel tilt, and the declination angle.\n"
        "By updating the declination for each hour, the simulation accurately captures the sun's changing\n"
        "path across the sky. This directly impacts the calculated contribution of Direct Normal Irradiance (DNI)\n"
        "to the panel's surface, leading to a more realistic and reliable estimation of the total energy\n"
        "output for any given tilt."
    )
    print("="*50 + "\n")


# --- Main Execution Block ---

if __name__ == "__main__":
    # ===== RUN ANALYSIS FOR 2023 =====
    YEAR_TO_ANALYZE = 2023
    FILE_PATH = f'{YEAR_TO_ANALYZE}_with_declination.csv'
    
    print(f"--- Starting Full Solar Analysis for {YEAR_TO_ANALYZE} ---")
    
    analyzer_2023 = SolarAnalysis(FILE_PATH)
    
    if analyzer_2023.data is not None:
        # 1. Run all arrangement analyses
        arrangements = {
            "Arr. 1: 0° Fixed": (analyzer_2023.analyze_arrangement_1, {}),
            "Arr. 2: 29° Fixed (Lat)": (analyzer_2023.analyze_arrangement_2, {}),
            "Arr. 3: Two Fixed (Lat±11.7°)": (analyzer_2023.analyze_arrangement_3, {}),
            "Arr. 4: Monthly Optimal": (analyzer_2023.analyze_arrangement_4, {}),
            "Arr. 5: Summer/Winter Optimal": (analyzer_2023.analyze_arrangement_5, {}),
            "Arr. 6: Annual Optimal": (analyzer_2023.analyze_arrangement_6, {}),
        }

        results = {}
        for name, (func, args) in arrangements.items():
            results[name] = {
                'Cloudy Sky GHI': func(sky_condition='cloudy', **args),
                'Clear Sky GHI': func(sky_condition='clear', **args)
            }
        
        results_df_2023 = pd.DataFrame(results).T
        # Format for better readability
        results_df_2023['Cloudy Sky GHI'] = results_df_2023['Cloudy Sky GHI'].map('{:,.0f}'.format)
        results_df_2023['Clear Sky GHI'] = results_df_2023['Clear Sky GHI'].map('{:,.0f}'.format)

        print("\n--- Annual GHI Output Table by Arrangement (2023) ---")
        print(results_df_2023)
        
        # 2. Plot the arrangement comparison
        plot_arrangement_comparison(pd.DataFrame(results).T, YEAR_TO_ANALYZE)
        
        # 3. Sliding Window Analysis for 2023
        print("\n--- 3-Month Sliding Window Analysis Table (2023) ---")
        sliding_window_cloudy_2023 = analyzer_2023.analyze_sliding_window(window_size=3, sky_condition='cloudy')
        print(sliding_window_cloudy_2023.to_string(index=False))

        # ===== RUN ANALYSIS FOR 2022 =====
        YEAR_TO_ANALYZE_2 = 2022
        FILE_PATH_2 = f'{YEAR_TO_ANALYZE_2}_with_declination.csv'
        
        print(f"\n--- Starting Full Solar Analysis for {YEAR_TO_ANALYZE_2} ---")
        
        analyzer_2022 = SolarAnalysis(FILE_PATH_2)
        
        if analyzer_2022.data is not None:
            # We only need the sliding window data for the final graph
            sliding_window_cloudy_2022 = analyzer_2022.analyze_sliding_window(window_size=3, sky_condition='cloudy')
            print(f"\n--- 3-Month Sliding Window Analysis Table (2022) ---")
            print(sliding_window_cloudy_2022.to_string(index=False))

            # 4. Plot sliding window comparison
            plot_sliding_window_analysis(sliding_window_cloudy_2022, sliding_window_cloudy_2023)
        else:
            print(f"\nCould not run analysis for {YEAR_TO_ANALYZE_2}. Check if '{FILE_PATH_2}' exists.")

        # 5. Print the final paragraph
        print_declination_paragraph()

    else:
        print(f"\nCould not run analysis for {YEAR_TO_ANALYZE}. Program will exit.")