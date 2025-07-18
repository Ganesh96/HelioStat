# HelioStat

==================================================
The Importance of the Hourly Declination Angle
==================================================
The sun's declination angle—its angle north or south of the celestial equator—is not constant;
it changes continuously throughout the day and year. Early simulation models might simplify this
by using a single average declination angle for an entire day. However, this program improves
upon that by using a precise, hourly declination angle.

This higher resolution is critical for accuracy. The core of the GHI calculation depends on the
angle of incidence (theta), which is a function of latitude, panel tilt, and the declination angle.
By updating the declination for each hour, the simulation accurately captures the sun's changing
path across the sky. This directly impacts the calculated contribution of Direct Normal Irradiance (DNI)
to the panel's surface, leading to a more realistic and reliable estimation of the total energy
output for any given tilt.
==================================================

### Starting Full Solar Analysis for 2023

---

### Annual GHI Output Table by Arrangement (2023)

| Arrangement | Cloudy Sky GHI | Clear Sky GHI |
| :--- | :---: | :---: |
| **Arr. 1:** 0° Fixed | 2,215,915 | 2,931,221 |
| **Arr. 2:** 29° Fixed (Lat) | 2,446,077 | 3,281,576 |
| **Arr. 3:** Two Fixed (Lat±11.7°) | 2,501,214 | 3,371,934 |
| **Arr. 4:** Monthly Optimal | 2,517,552 | 3,398,906 |
| **Arr. 5:** Summer/Winter Optimal | 2,502,981 | 3,375,555 |
| **Arr. 6:** Annual Optimal | 2,446,111 | 3,281,849 |

### 3-Month Sliding Window Analysis Table (2023)

---

| Window | Optimal Tilt (Cloudy) |
| :--- | :---: |
| Jan-Mar | 41 |
| Feb-Apr | 32 |
| Mar-May | 22 |
| Apr-Jun | 13 |
| May-Jul | 9 |
| Jun-Aug | 10 |
| Jul-Sep | 17 |
| Aug-Oct | 28 |
| Sep-Nov | 38 |
| Oct-Dec | 46 |
| Nov-Jan | 50 |
| Dec-Feb | 48 |


# Algorithm of Solar Analysis: A Step-by-Step Guide

The primary purpose of this program is to identify the optimal solar panel tilt strategy to maximize energy capture by comparing six different approaches, or "Arrangements."

---

## Step 1: Setup and Preparation

* **Start**: The program begins execution.
* **Define Constants**: It establishes unchangeable key values such as Gainesville's latitude (29.65°), the Earth's tilt (23.45°), and the months designated as summer or winter.
* **Load Data**: The program reads solar energy data from a `.csv` file for a specified year, like 2023. This file provides hourly details on sunlight (DHI and DNI) and the sun's declination angle.

---

## Step 2: Core Calculation Logic

This section serves as the program's engine and is utilized in all subsequent steps.

### Create a Calculation Function (Calculate Energy for a Tilt)

This function requires a **tilt angle**, a **list of months**, and the **sky condition** ('cloudy' or 'clear') as inputs. It then calculates the total solar energy (GHI) that a panel would receive at that specific tilt angle for every hour within the given months. The formula used accounts for the panel's tilt, the location's latitude, and the sun's hourly declination angle. The function returns the total energy for the entire period by summing the energy from all hours.

### Create an Optimization Function (Find Best Tilt)

This function takes a **list of months** and the **sky condition** as inputs. It evaluates every possible whole-number tilt angle from 0° to 90°, using the `Calculate Energy for a Tilt` function to determine the energy generated at each angle. The function identifies the tilt angle that yields the most energy and returns the **best tilt angle** along with the **maximum energy** value.

---

## Step 3: Analyze the Six Arrangements

The program assesses six strategies to determine the total energy each would generate over a full year.

* **Arrangement 1 (0° Fixed)**: The `Calculate Energy for a Tilt` function is used with the angle set to 0° for all 12 months.
* **Arrangement 2 (29° Fixed)**: The `Calculate Energy for a Tilt` function is used with the angle set to 29° (the latitude) for all 12 months.
* **Arrangement 3 (Two-Season Fixed)**: A "summer tilt" (29° - 11.7°) and a "winter tilt" (29° + 11.7°) are calculated. The energy for the summer and winter months is calculated using their respective tilts, and the results are added together for a yearly total.
* **Arrangement 4 (Monthly Optimal)**: The `Find Best Tilt` function is used for each month from January to December to find the best angle for each month. The maximum energy from all 12 months is then summed for a yearly total.
* **Arrangement 5 (Two-Season Optimal)**: The `Find Best Tilt` function is used once for all summer months combined and once for all winter months combined to find the single best tilt for each season. The two maximum energy results are then added together for a yearly total.
* **Arrangement 6 (Annual Optimal)**: The `Find Best Tilt` function is used for all 12 months at once to determine the single best tilt for the entire year.

---

## Step 4: Final Output and Visualization

* **Create Summary Table**: The program organizes the total yearly energy from all six arrangements into a table for comparison.
* **Generate Charts**: Graphs are created to visualize the results, including a bar chart comparing the total annual energy from each arrangement, a line chart showing the panel tilt angle for each strategy over the year, and monthly bar charts comparing specific pairs of arrangements.
* **End**: The program concludes after displaying the tables and charts.