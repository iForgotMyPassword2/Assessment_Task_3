#!/usr/bin/env python3
import pandas as pd
import os
import sys
import re


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



    if __name__ == "__main__":
        main()
        


def victoria():

    CSV_PATH = os.path.join(os.path.dirname(__file__), "Victoria_Train_patronage_per_station.csv")
    PROCESSED_OUT = os.path.join(os.path.dirname(__file__), "vic_processed_patronage_dec24.csv")


    # ---------- Helpers ----------
    def _snake(s: str) -> str:
        """Normalize a column name to lower snake_case."""
        s = re.sub(r"\s+", "_", str(s).strip())
        s = s.replace("-", "_").replace("/", "_")
        s = re.sub(r"_+", "_", s)
        return s.lower()


    def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
        """Return a copy with normalized snake_case columns."""
        d = df.copy()
        d.columns = [_snake(c) for c in d.columns]
        return d


    def find_column(d: pd.DataFrame, candidates) -> str:
        """
        Given a normalized DataFrame and a list of candidate column names (lower snake),
        return the first existing one or raise a helpful error.
        """
        for name in candidates:
            if name in d.columns:
                return name
        raise KeyError(
            "Could not find a required column. Looked for any of: "
            + ", ".join(candidates)
            + f". Columns present: {list(d.columns)}"
        )


    def normalise_entry_exit(val: str) -> str:
        """Map variations to 'Entry' or 'Exit'."""
        if val is None:
            return None
        s = str(val).strip().lower()
        if s in {"entry", "entries", "in"}:
            return "Entry"
        if s in {"exit", "exits", "out"}:
            return "Exit"
        # fallback: try to guess
        if "ent" in s or s.startswith("in"):
            return "Entry"
        if "ex" in s or s.startswith("out"):
            return "Exit"
        return str(val)  # leave as-is; will become its own column if pivoted


    def clean_trip_value(x):
        """
        Convert Trip string values to numeric.
        Handles:
        - 'Less than 50', 'less than 50', '<50', '< 50', etc. → midpoint of last number (50→25)
        - '12,345' and other thousand separators
        - blanks → 0
        """
        if pd.isna(x):
            return 0
        s = str(x).strip().replace(",", "").replace(" ", "")
        sl = s.lower()

        # Detect 'less than' or '<' patterns
        if "lessthan" in sl or sl.startswith("<"):
            # extract the last number
            nums = re.findall(r"\d+", s)
            if nums:
                n = int(nums[-1])
                return max(0, n // 2)  # midpoint heuristic
            return 25  # sensible default

        # General numeric extraction
        nums = re.findall(r"[-+]?\d+", s)
        if nums:
            try:
                return int(nums[-1])
            except Exception:
                pass

        # Last resort
        try:
            return int(float(s))
        except Exception:
            return 0


    def detect_schema(df: pd.DataFrame):
        """
        Detect key columns from a variety of plausible names.
        Returns a dict with keys: month, station, entry_exit, trip (normalized names).
        """
        d = normalize_columns(df)

        month_col = find_column(d, ["monthyear", "month", "period"])
        station_col = find_column(d, ["station", "stop", "stop_name"])
        # Direction / Entry_Exit column might be missing if already wide format
        entry_exit_col = None
        for c in ["entry_exit", "entry_or_exit", "direction", "in_out", "entryexit", "entry__exit"]:
            if c in d.columns:
                entry_exit_col = c
                break

        trip_col = None
        for c in ["trip", "trips", "patronage", "count", "volume"]:
            if c in d.columns:
                trip_col = c
                break

        # Check for already wide format (Entry / Exit columns present)
        wide_entry = "entry" in d.columns
        wide_exit = "exit" in d.columns

        if not (trip_col or (wide_entry and wide_exit)):
            raise KeyError(
                "Could not find a trips/patronage column or separate Entry/Exit columns. "
                "Expected one of: trip, trips, patronage, count, volume OR both 'Entry' and 'Exit' columns."
            )

        return {
            "month": month_col,
            "station": station_col,
            "entry_exit": entry_exit_col,  # may be None if wide
            "trip": trip_col,              # may be None if wide
            "is_wide": (wide_entry and wide_exit),
        }


    # ---------- Core processing ----------
    def process_patronage(df: pd.DataFrame, month="Dec-24", min_total=200, ascending=False) -> pd.DataFrame:
        """
        Processing pipeline:
        - filter to month
        - compute Entry, Exit, Total per Station (from long or wide formats)
        - filter stations with Total >= min_total
        - sort by Total
        Returns columns: Station, Entry, Exit, Total
        """
        if df.empty:
            raise ValueError("Input dataframe is empty.")

        d = normalize_columns(df)
        schema = detect_schema(df)

        month_col = schema["month"]
        station_col = schema["station"]
        entry_exit_col = schema["entry_exit"]
        trip_col = schema["trip"]
        is_wide = schema["is_wide"]

        # Filter by month
        d = d[d[month_col] == month].copy()
        if d.empty:
            raise ValueError(f"No rows found for month '{month}'. Check the exact month codes in your CSV.")

        # Build Entry/Exit/Total
        if is_wide:
            # Expect 'entry' and 'exit' columns already numeric
            for col in ["entry", "exit"]:
                if col in d.columns:
                    d[col] = pd.to_numeric(d[col], errors="coerce").fillna(0).astype(int)
                else:
                    d[col] = 0
            g = d.groupby(station_col, as_index=False).agg(Entry=("entry", "sum"),
                                                        Exit=("exit", "sum"))
            g["Total"] = g["Entry"] + g["Exit"]
        else:
            # Long format with entry_exit + trip
            d["trip_num"] = d[trip_col].apply(clean_trip_value).astype(int)
            d["ee_norm"] = d[entry_exit_col].apply(normalise_entry_exit)
            pivot = d.pivot_table(index=station_col,
                                columns="ee_norm",
                                values="trip_num",
                                aggfunc="sum",
                                fill_value=0)
            # Ensure both columns exist
            entry_vals = pivot["Entry"] if "Entry" in pivot.columns else 0
            exit_vals  = pivot["Exit"]  if "Exit"  in pivot.columns else 0

            g = pd.DataFrame({
                "Station": pivot.index,
                "Entry": entry_vals,
                "Exit": exit_vals
            })
            g["Total"] = g["Entry"] + g["Exit"]

        # Ensure station column named 'Station'
        if "Station" not in g.columns:
            g = g.rename(columns={station_col: "Station"})

        # Filter by min_total, sort
        g = g[g["Total"] >= int(min_total)].copy()
        g = g.sort_values("Total", ascending=ascending, kind="mergesort").reset_index(drop=True)

        # Only requested columns in final output
        return g[["Station", "Entry", "Exit", "Total"]]


    def list_outliers(df: pd.DataFrame):
        """
        Identify outliers using mean ± 2*std (same as previous).
        Returns (low_outliers, high_outliers).
        """
        if df.empty:
            return df.copy(), df.copy()
        mean = df["Total"].mean()
        std = df["Total"].std()
        hi = df[df["Total"] > mean + 2 * std]
        lo = df[df["Total"] < max(0, mean - 2 * std)]
        return lo, hi


    # ---------- CLI ----------
    def main():
        if not os.path.exists(CSV_PATH):
            print("CSV file not found at", CSV_PATH)
            sys.exit(1)

        try:
            df = pd.read_csv(CSV_PATH)
        except Exception as e:
            print("Failed to read CSV:", e)
            sys.exit(1)

        sort_desc = True
        month = "Dec-24"
        min_total = 200

        # First process
        try:
            processed = process_patronage(df, month=month, min_total=min_total, ascending=not sort_desc)
        except Exception as e:
            print("\nError during initial processing:", e)
            # Try to be helpful: show the unique month values to guide the user
            try:
                d = normalize_columns(df)
                month_col = find_column(d, ["monthyear", "month", "period"])
                uniq = sorted(map(str, d[month_col].dropna().unique()))
                print("Available month values in your file:", ", ".join(uniq[:50]), "..." if len(uniq) > 50 else "")
            except Exception:
                pass
            sys.exit(1)

        while True:
            print("\n=== Victoria Patronage CLI ===")
            print("1) Show top 10 stations")
            print("2) Show bottom 10 stations")
            print(f"3) Toggle sort order (currently {'descending' if sort_desc else 'ascending'})")
            print("4) List outliers (very high / very low)")
            print("5) Add a row of data (Entry or Exit record)")
            print("6) Ask a prompt question (e.g., busiest station)")
            print(f"7) Save processed CSV to {PROCESSED_OUT}")
            print(f"8) Change month (currently {month})")
            print(f"9) Change minimum total filter (currently {min_total})")
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
                low, high = list_outliers(processed)
                print("\nHigh outliers (very busy):")
                print(high.sort_values("Total", ascending=False).to_string(index=False))
                print("\nLow outliers (unusually quiet):")
                print(low.sort_values("Total").to_string(index=False))
            elif choice == "5":
                # Add one new row interactively; we append using the most general long format
                station = input("Station name: ").strip()
                month_in = input(f"Month (e.g., {month}): ").strip() or month
                ee = input("Entry or Exit (Entry/Exit): ").strip().title()
                trip = input("Trip value (number, '<50', or 'Less than 50'): ").strip()

                # Build a best-effort row that matches the CSV's schema
                dnorm = normalize_columns(df)
                # Try to detect columns again to know names
                try:
                    schema = detect_schema(df)
                    month_col = schema["month"]
                    station_col = schema["station"]
                    entry_exit_col = schema["entry_exit"] or "entry_exit"
                    trip_col = schema["trip"] or "trip"
                except Exception:
                    # Fall back to generic names
                    month_col = "monthyear"
                    station_col = "station"
                    entry_exit_col = "entry_exit"
                    trip_col = "trip"

                # Create a dict with all existing columns, default None
                new = {col: None for col in dnorm.columns}
                # Put values into the normalised keys if present; otherwise add them
                if month_col in dnorm.columns:
                    new[month_col] = month_in
                else:
                    new[month_col] = month_in
                if station_col in dnorm.columns:
                    new[station_col] = station
                else:
                    new[station_col] = station
                if entry_exit_col in dnorm.columns:
                    new[entry_exit_col] = ee
                else:
                    new[entry_exit_col] = ee
                if trip_col in dnorm.columns:
                    new[trip_col] = trip
                else:
                    new[trip_col] = trip

                # Map back to original case-sensitive columns of df
                # Build mapping from normalized -> original
                norm_to_orig = {_snake(c): c for c in df.columns}
                new_orig = {}
                for k_norm, v in new.items():
                    k_orig = norm_to_orig.get(k_norm, k_norm)
                    new_orig[k_orig] = v

                df = pd.concat([df, pd.DataFrame([new_orig])], ignore_index=True)
                processed = process_patronage(df, month=month, min_total=min_total, ascending=not sort_desc)
                print("Row added. Station totals updated.")
            elif choice == "6":
                q = input("Ask a short prompt (e.g., 'what was the busiest station?'): ").strip().lower()
                if "busiest" in q:
                    top = processed.sort_values("Total", ascending=False).head(1)
                    if not top.empty:
                        print("Busiest station:", top.iloc[0]["Station"], "with total", int(top.iloc[0]["Total"]))
                    else:
                        print("No data available.")
                elif "how many stations" in q:
                    print("Number of stations:", len(processed))
                else:
                    print("Sorry, prompt not recognised. Try: 'what was the busiest station?', 'how many stations'")
            elif choice == "7":
                processed.to_csv(PROCESSED_OUT, index=False)
                print("Saved processed CSV to", PROCESSED_OUT)
            elif choice == "8":
                new_month = input("Enter month label exactly as in CSV (e.g., Dec-24): ").strip()
                if new_month:
                    month = new_month
                    try:
                        processed = process_patronage(df, month=month, min_total=min_total, ascending=not sort_desc)
                        print("Month changed to", month)
                    except Exception as e:
                        print("Error after changing month:", e)
            elif choice == "9":
                try:
                    new_min = int(input("Enter new minimum Total (integer): ").strip())
                    min_total = new_min
                    processed = process_patronage(df, month=month, min_total=min_total, ascending=not sort_desc)
                    print("Minimum total filter changed to", min_total)
                except Exception as e:
                    print("Invalid number or error:", e)
            elif choice == "0":
                print("Goodbye.")
                break
            else:
                print("Invalid option. Try again.")


    if __name__ == "__main__":
        main()



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
            victoria()
            break
        elif data_choice == '3':
            print('You are now looking at city of sydney car ownership')
            csv_path = os.path.join(os.path.dirname(__file__), "CarOwnership_AllTimePeriod_Datatype_EN_For_10_20.csv")
            if os.path.exists(csv_path):
                df = pd.read_csv(csv_path)
                print("\nFirst 5 rows of the car ownership dataset:")
                print(df.head().to_string(index=False))
            else:
                print("Car ownership CSV file not found at", csv_path)
            back_home = input('Press 1 to go back to home')
            if back_home == '1':
                dataset_home()
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

dataset_home()

