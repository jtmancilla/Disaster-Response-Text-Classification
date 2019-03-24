import sys
import pandas as pd
from sqlalchemy import create_engine

def load_data(messages_filepath, categories_filepath):
    messages = pd.read_csv(messages_filepath)
    categories = pd.read_csv(categories_filepath)
    categories_split = categories.categories.str.split(';', expand=True)
    # select the first row of the categories dataframe
    row = categories_split.iloc[0]

    # use this row to extract a list of new column names for categories.
    # one way is to apply a lambda function that takes everything 
    # up to the second to last character of each string with slicing
    category_colnames = list(  categories_split.iloc[0].apply(lambda x: str.split(x,'-')[0]) )

    categories_split.columns = category_colnames

    categories = pd.concat( [ categories, categories_split ] , axis = 1)

    # Convert categories indicator columns to numeric
    for column in category_colnames:
        # set each value to be the last character of the string
        categories[column] = categories[column].apply(lambda x: str.split(x,'-')[1])
        
        # convert column from string to numeric
        categories[column] = categories[column].apply(pd.to_numeric)
    
    df = pd.merge(messages, categories, on = 'id')    
    # Drop the categories column

    df = df.drop('categories', axis = 1)
    return df

def clean_data(df):
    return df.drop_duplicates()

def save_data(df, database_filename):
    engine = create_engine('sqlite:///' + database_filename, echo  = True)
    df.to_sql('messages', engine, index=False, if_exists='replace', chunksize=100 )

def main():
    if len(sys.argv) == 4:

        messages_filepath, categories_filepath, database_filepath = sys.argv[1:]

        print('Loading data...\n    MESSAGES: {}\n    CATEGORIES: {}'
              .format(messages_filepath, categories_filepath))
        df = load_data(messages_filepath, categories_filepath)

        print('Cleaning data...')
        df = clean_data(df)
        
        print('Saving data...\n    DATABASE: {}'.format(database_filepath))
        save_data(df, database_filepath)
        
        print('Cleaned data saved to database!')
    
    else:
        print('Please provide the filepaths of the messages and categories '\
              'datasets as the first and second argument respectively, as '\
              'well as the filepath of the database to save the cleaned data '\
              'to as the third argument. \n\nExample: python process_data.py '\
              'disaster_messages.csv disaster_categories.csv '\
              'DisasterResponse.db')


if __name__ == '__main__':
    main()