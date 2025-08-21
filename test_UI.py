#!/usr/bin/env python3
import pandas as pd
import os
import sys


# NSW_train_patronage = pd.read_csv('NSW_Train_patronage_per_station.csv')
# VIC_train_patronage = pd.read_csv('Victoria_Train_patronage_per_station.csv')

# Modified_NSW_train_patronage = NSW_train_patronage.str.strip('_id')

#!/usr/bin/env python3
"""
NSW Train Patronage CLI
-----------------------
Interactive text-based UI to process and explore NSW Train patronage data.

Features:
- Clean and process data (Trip → numeric, pivot Entry/Exit, sum totals).
- Filter by month (default: Dec-24).
- Drop stations under a chosen patronage threshold (default: 200).
- Sort stations (busiest → quietest by default, toggleable).
- Options to view top/bottom stations, outliers, busiest station, etc.
- Add new rows of data via prompts (column by column).
- Save the processed dataset to CSV.
"""

import pandas as pd
import os
import sys

# File paths (adjust if needed)
CSV_PATH = os.path.join(os.path.dirname(__file__), "NSW_Train_patronage_per_station.csv")
PROCESSED_OUT = os.path.join(os.path.dirname(__file__), "processed_patronage_dec24.csv")

def what():
    def clean_trip_value(x):
        """Convert Trip string values to numeric. Treat 'Less than 50' as 25."""
        s = str(x).strip().replace(",", "")
        if s.lower().startswith("less than"):
            # e.g. 'Less than 50' → midpoint = 25
            for p in s.split()[::-1]:
                if p.isdigit():
                    return int(int(p) // 2)
            return 25
        try:
            return int(float(s))
        except:
            return 0


    def process_patronage(df, month="Dec-24", min_total=200, ascending=False):
        """
        Process the raw dataframe:
        - keep only rows for the requested month
        - convert Trip to numeric
        - pivot Entry/Exit into columns then sum totals per Station
        - drop stations with Total < min_total
        - return dataframe sorted by Total
        """
        d = df.copy()
        month_col = "MonthYear" if "MonthYear" in d.columns else "Month"
        d = d[d[month_col] == month].copy()

        if d.empty:
            raise ValueError(f"No rows found for month '{month}'.")

        d["Trip_num"] = d["Trip"].apply(clean_trip_value).astype("Int64")

        if "Entry_Exit" in d.columns:
            pivot = d.pivot_table(
                index="Station",
                columns="Entry_Exit",
                values="Trip_num",
                aggfunc="sum",
                fill_value=0,
            )
            for c in ["Entry", "Exit"]:
                if c not in pivot.columns:
                    pivot[c] = 0
            pivot = pivot.reset_index().rename_axis(None, axis=1)
            pivot["Total"] = pivot["Entry"] + pivot["Exit"]
        else:
            pivot = d.groupby("Station", as_index=False).agg(Total=("Trip_num", "sum"))
            pivot["Entry"] = pd.NA
            pivot["Exit"] = pd.NA

        pivot = pivot[pivot["Total"] >= min_total].copy()
        pivot.sort_values("Total", ascending=ascending, inplace=True)
        pivot.reset_index(drop=True, inplace=True)
        return pivot


    def list_outliers(df):
        """Find outliers using mean ± 2*std."""
        mean = df["Total"].mean()
        std = df["Total"].std()
        high = df[df["Total"] > mean + 2 * std]
        low = df[df["Total"] < max(0, mean - 2 * std)]
        return low, high


    def main():
        if not os.path.exists(CSV_PATH):
            print("CSV file not found at", CSV_PATH)
            sys.exit(1)

        df = pd.read_csv(CSV_PATH)

        sort_desc = True
        month = "Dec-24"
        min_total = 200
        processed = process_patronage(df, month=month, min_total=min_total, ascending=not sort_desc)

        while True:
            print("\n=== NSW Patronage CLI ===")
            print("1) Show top 10 stations")
            print("2) Show bottom 10 stations")
            print(f"3) Toggle sort order (currently {'descending' if sort_desc else 'ascending'})")
            print("4) Add a row of data (Entry or Exit record)")
            print(f"5) Save processed CSV to {PROCESSED_OUT}")
            print("0) Exit")

            choice = input("Choose an option: ").strip()

            if choice == "1":
                print(processed.head(10).to_string(index=False))
            elif choice == "2":
                print(processed.tail(10).to_string(index=False))
            elif choice == "3":
                sort_desc = not sort_desc
                processed = process_patronage(df, month=month, min_total=min_total, ascending=not sort_desc)
                print("Sort order now", "descending" if sort_desc else "ascending")
        
            elif choice == "4":
                # Add one new row interactively
                station = input("Station name: ").strip()
                month_in = input("MonthYear (e.g., Dec-24): ").strip() or month
                ee = input("Entry or Exit (Entry/Exit): ").strip().title()
                trip = input("Trip value (number or 'Less than 50'): ").strip()

                new = {
                    "MonthYear": month_in,
                    "Station": station,
                    "Entry_Exit": ee,
                    "Trip": trip,
                }
                # Fill missing original columns if needed
                for c in df.columns:
                    if c not in new:
                        new[c] = None
                df = pd.concat([df, pd.DataFrame([new])], ignore_index=True)
                processed = process_patronage(df, month=month, min_total=min_total, ascending=not sort_desc)
                print("Row added. Station totals updated.")
        
            elif choice == "5":
                processed.to_csv(PROCESSED_OUT, index=False)
                print("Saved processed CSV to", PROCESSED_OUT)
            elif choice == "0":
                print("going back to home...")
                dataset_home()
            else:
                print("Invalid option. Try again.")

def dataset_home():
    print('\n === This is the dataset homepage: ===')
    print('\n Here, you can use and manipulate the listed datasets')
    print('\n1. train patronage in NSW suburbs and their densities')
    print('2. train patronage in VIC suburbs and their densities')
    print('3. Car ownership in the city of sydney')
    print('4. Exit the program :(')
    while True:
        data_choice = input('Choose between 1 and 2 to choose dataset')
        if data_choice == '1':
            print('You are viewing NSW train patronage')
            what()
            break
        elif data_choice == '2':
            print('You are viewing VIC patronage')
            break
        elif data_choice == '3':
            print('You are now looking at city of sydney car ownership')
            break
        elif data_choice == '4':
            exit()
        else:
            print('error, press either one, two or three')


def thesis_question():
    print('\n === Main Thesis question: ===')
    print('"How does population density affect public transport usage and car ownership in Australian suburbs?"')
    print('\n This thesis statement shows...')
    while True:
        choice = input('press 1 to move onto dataset list and press 2 to exit')
        if choice == '1':
            print('going to dataset list...')
            dataset_home
            break
        elif choice == '2':
            Title_Screen()
            break
        else:
            print('error, press either one or 2')
        


def Title_Screen():
    print('\n === Main Menu === ')
    print('1. View thesis question')
    print('2. View dataset list')
    print('3. Exit')

    choice = input('Choose between 1, 2 and 3 to choose next destination')
    if choice == '1':
        thesis_question()
    elif choice == '2':
        dataset_home()
    else:
        print('error')



if __name__ == "__main__":
    main()
    