import numpy as np
from dateutil.parser import parse
# from scipy.stats import zscore
from datetime import datetime
import pandas as pd
# from calendar import monthrange

class DynamicDataCleaner:
    def __init__(self, z_threshold=3):
        self.z_threshold = z_threshold

    def from_dataframe(self, df: pd.DataFrame):
        self.df = df.copy()
        return self

    def clean_column_names(self):
        self.df.columns = [col.strip().lower().replace(" ", "_") for col in self.df.columns]
        return self

    def drop_duplicates(self):
        self.df = self.df.drop_duplicates()
        return self

    def trim_strings(self):
        # for col in self.df.select_dtypes(include='object').columns:
        #     self.df[col] = self.df[col].str.strip()
        return self

    def handle_missing(self):
        for col in self.df.columns:
            if self.df[col].dtype == 'object':
                self.df[col] = self.df[col].str.strip()
                self.df[col].fillna('Unknown')
            elif self.df[col].dtype in ['int64', 'float64']:
                self.df[col].fillna(self.df[col].median())
        return self

    def convert_dates(self,datecolumns):
        for col in self.df.columns:
            converted = None
            print(col,self.df[col].dtype,self.df[col].dtype.name)
            # Object or string columns
            if self.df[col].dtype == 'object' or self.df[col].dtype.name == 'string':     
                converted = self.df[col].apply(convert_date)
                # converted = pd.to_datetime(self.df[col],  format='%b %d, %Y', errors='coerce')
                
                # print(converted)
            # Numeric types — only convert if likely YYYYMMDD
            elif self.df[col].dtype in ['int64', 'float64']:
                # Check if >50% of the values are in valid date range
                valid_mask = self.df[col].between(19000101, 21001231)
                if valid_mask.mean() > 0.5:
                    converted = pd.to_datetime(self.df[col].astype(str), format='%Y%m%d', errors='coerce')
            
            # Replace column only if majority values were converted successfully
            if converted is not None and converted.notna().mean() > 0.5:
                self.df[col] = converted
        return self

    def remove_outliers(self):
        # numeric_cols = self.df.select_dtypes(include=['float64', 'int64']).columns
        # z_scores = np.abs(zscore(self.df[numeric_cols]))
        # self.df = self.df[(z_scores < self.z_threshold).all(axis=1)]
        return self

    def get_cleaned_data(self):
        return self.df
    
def convert_date(input_date):
    try:
        return parse(input_date).strftime('%Y-%m-%d')
    except:
        return None  # or x if you want to keep the original

    # input_date = str(input_date)

    # date_formats_1 = ["%d/%m/%Y", "%d/%m/%y", "%d-%m-%Y", "%d-%m-%y", "%d %m %Y", "%d %b %Y", "%d %B %Y", "%b %d, %Y"]
    # date_formats_2 = ["%m-%Y", "%m/%Y", "%b-%Y", "%b/%Y", "%B-%Y", "%B/%Y"]

    # for date_format in date_formats_1:
    #     try:
    #         return datetime.strptime(input_date, date_format).strftime("%Y-%m-%d")
    #     except ValueError:
    #         pass

    # for date_format in date_formats_2:
    #     try:
    #         date_object = datetime.strptime(input_date, date_format)
    #         last_day_of_month = monthrange(date_object.year, date_object.month)[1]
    #         new_date = date_object.replace(day=last_day_of_month)
    #         return new_date.strftime("%Y-%m-%d")
    #     except ValueError:
    #         pass

    # return input_date
