from flask import jsonify
import pandas as pd
from sklearn.preprocessing import LabelEncoder



def load_flight_data(file_path):
    df = pd.read_csv(file_path, low_memory=False)
    return df


def preprocess_flight_data(df):

    columns_to_drop = ['FlightDate']
    df.drop(columns=columns_to_drop, inplace=True)

    df['DepartureDelayGroups'] = df['DepartureDelayGroups'].astype(float)
    df['ArrivalDelayGroups'] = df['ArrivalDelayGroups'].astype(float)
    df['Month'] = df['Month'].astype(int)
    df['DayofMonth'] = df['DayofMonth'].astype(int)

    categorical_columns = ['Marketing_Airline_Network', 'Origin', 'Dest'] 
    label_encoders = {}

    for col in categorical_columns:
        label_encoders[col] = LabelEncoder()
        df[col + '_encoded'] = label_encoders[col].fit_transform(df[col])

    return df

def geo_data(df):

    total_delay_per_state = df.groupby('OriginState')['DepDelayMinutes'].sum().reset_index()
    total_arrival_per_state = df.groupby('OriginState')['ArrDelayMinutes'].sum().reset_index()

    return total_delay_per_state, total_arrival_per_state
