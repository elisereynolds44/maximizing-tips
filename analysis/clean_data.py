import pandas as pd


def load_and_clean_data(filepath="data/tipsdataset.csv"):
    df = pd.read_csv(filepath)

    # Basic cleaning
    df.dropna(inplace=True)  # Remove missing values if any
    df['tip_percent'] = (df['tip'] / df['total_bill']) * 100  # Add tip % column
    return df