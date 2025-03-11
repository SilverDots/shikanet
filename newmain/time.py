from data_loader.loader import discord_loader, krishna_loader
import pandas as pd

db = discord_loader()
# db = krishna_loader()

# print(db.data[db.date_field].head())

# Convert dates to datetime format


# Convert to the desired format
# db.data[db.date_field] = db.data[db.date_field].dt.strftime('%Y-%m-%d %H:%M:%S')



# print where 2025-01-01 00:00:00 <= date <= 2025-01-05 00:00:00
# db_dates_where = db.data[(db.data[db.date_field] >= '2025-01-01 00:00:00') & (db.data[db.date_field] <= '2025-01-05 00:00:00')]
# print(db.data[db.date_field].dt.date)

def get_messages_from_time_range(start_time, end_time):
    '''
    Get messages from a time range

    Parameters:
    start_time: str - start time in the format 'YYYY-MM-DD HH:MM:SS'
    end_time: str - end time in the format 'YYYY-MM-DD HH:MM:SS'
    '''
    # db.data[db.date_field] = pd.to_datetime(db.data[db.date_field], errors='coerce', utc=True)

    # # Drop rows with invalid dates
    # db.data.dropna(subset=[db.date_field], inplace=True)
    start_time = pd.to_datetime(start_time, errors='coerce', utc=True)
    end_time = pd.to_datetime(end_time, errors='coerce', utc=True)
    
    return db.data[(db.data["datetime_formatted"] >= start_time) & (db.data["datetime_formatted"] <= end_time)]

start_time = '2024-01-01 00:00:00'
end_time = '2024-01-05 00:00:00'
messages = get_messages_from_time_range(start_time, end_time)
print(len(messages[db.date_field]))