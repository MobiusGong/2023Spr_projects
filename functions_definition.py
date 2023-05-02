import matplotlib.pyplot as plt
import os
import pandas as pd


def download_large_flights_file(url: str = "https://data.transportation.gov/api/views/xgub-n9bw/rows.csv?accessType=DOWNLOAD",
                                filename: str = "International_Report_Passengers.csv") -> pd.DataFrame:
    """
    One of the files needed for this project is over 25M which can not be uploaded to Github.
    This function will download the file from the website and return the dataframe.
    If the file is already in the directory, it will read the file directly and return the dataframe.
    :param url: url of the file from U.S. Department of Transportation
    :param filename: name of the file to be saved or loaded from the local directory
    :return: dataframe
    """
    column_names = ['data_dte', 'Year', 'Month', 'usg_apt_id', 'usg_apt', 'usg_wac', 'fg_apt_id', 'fg_apt', 'fg_wac',
                    'airlineid', 'carrier', 'carriergroup', 'type', 'Scheduled', 'Charter', 'Total']

    if os.path.exists(filename):
        df_IRP = pd.read_csv(filename, parse_dates=['data_dte'], names=column_names, header=0)
    else:
        df_IRP = pd.read_csv(url, parse_dates=['data_dte'], names=column_names, header=0)
        df_IRP.to_csv(filename, index=False)

    return df_IRP


def read_and_combine_FDI_data(file1: str, file2: str, col1: str = 'CN to US in billion U.S. dollars', col2: str = 'US to CN in billion U.S. dollars') -> pd.DataFrame:
    """
    This function will read two csv files and combine them into one dataframe.
    One file is the Foreign direct investment (FDI) from China to US
    Another is FDI from US to China.
    :param file1:  FDI from China to US. Source: https://www.statista.com/statistics/188935/foreign-direct-investment-from-china-in-the-united-states/?locale=en
    :param file2: FDI from US to China. Source: https://www.statista.com/statistics/188629/united-states-direct-investments-in-china-since-2000/?locale=en
    :param col1: CN to US in billion U.S. dollars
    :param col2: US to CN in billion U.S. dollars
    :return: dataframe
    """
    df1 = pd.read_csv(file1, header=None, names=['Year', col1], dtype={'Year': int, 'Value': float})
    df2 = pd.read_csv(file2, header=None, names=['Year', col2], dtype={'Year': int, 'Value': float})
    df_combined = df1.merge(df2, on='Year')
    return df_combined


def plot_FDI_data(df: pd.DataFrame, col1: str = "CN to US in billion U.S. dollars", col2: str = "US to CN in billion U.S. dollars") -> None:
    """
    This function will plot the FDI data from China to US and US to China.
    :param df: combined dataframe from read_and_combine_FDI_data()
    :param col1: CN to US in billion U.S. dollars
    :param col2: US to CN in billion U.S. dollars
    :return: None
    """
    plt.figure(figsize=(18, 6))
    plt.plot(df['Year'], df[col1], label=col1)
    plt.plot(df['Year'], df[col2], label=col2)

    plt.xlabel('Year')
    plt.ylabel('Value in billion U.S. dollars')
    plt.title('FDI Flows: China to US vs. US to China')
    plt.xticks(df['Year'], rotation=45)  # You can adjust the rotation of the labels if needed
    plt.legend()
    plt.grid()
    plt.show()


def read_CN_US_airports_IATA(filename : str = "airports from Open data.csv")-> pd.DataFrame:
    """
    This function will read the airports data so that we can get the IATA code for each airport
    from US and CN.
    :param filename: "airports from Open data.csv". Source: https://ourairports.com/data/
    :return: dataframe
    """
    df_airports = pd.read_csv(filename)
    df_airports = df_airports[df_airports['iata_code'].notna()]
    df_airports = df_airports[(df_airports['iso_country'] == 'CN') | (df_airports['iso_country'] == 'US')]
    df_airports = df_airports[['name', 'iata_code', 'iso_country']]
    return df_airports


def filter_flights_with_CN(df_IRP : pd.DataFrame, df_airports_CN_US: pd.DataFrame) -> pd.DataFrame:
    """
    This function will filter the flights that are to or from China. All irrelevant data will be removed.
    :param df_IRP:
    :param df_airports_CN_US:
    :return: dataframe
    """
    # Get the unique IATA codes from df_CN_airpots
    cn_iata_codes = df_airports_CN_US['iata_code'].unique()

    # Filter df_IRP based on whether 'fg_apt' is in the cn_iata_codes
    df_filtered = df_IRP[df_IRP['fg_apt'].isin(cn_iata_codes)]

    return df_filtered


def plot_total_flights_by_year_continuously(df_IRP : pd.DataFrame) -> None:
    """
    This function will plot the total number of flights by year continuously.
    :param df_IRP:
    :return:
    """
    df_IRP_by_year = df_IRP.groupby(['Year']).size().reset_index(name='Number of flights')
    plt.figure(figsize=(18, 6))
    plt.plot(df_IRP_by_year['Year'], df_IRP_by_year['Number of flights'])
    plt.xlabel('Year')
    plt.ylabel('Number of flights')
    plt.title('Total number of flights by year')
    plt.xticks(df_IRP_by_year['Year'], rotation=45)  # You can adjust the rotation of the labels if needed
    plt.grid()
    plt.show()


def plot_total_flights_by_year(df_IRP: pd.DataFrame, start_year: int = 1999, end_year: int = 2022) -> None:
    """
    This function will plot the total number of flights by year. Different years will be shown in different colors.
    :param df_IRP:
    :return:
    """
    df_IRP_with_time_range = df_IRP[(df_IRP['Year'] <= end_year) & (df_IRP['Year'] >= start_year)]
    df_IRP_by_year_month = df_IRP_with_time_range.groupby(['Year', 'Month']).size().reset_index(name='Number of flights')
    years = df_IRP_by_year_month['Year'].unique()

    plt.figure(figsize=(18, 6))

    for year in years:
        df_year = df_IRP_by_year_month[df_IRP_by_year_month['Year'] == year]
        plt.plot(df_year['Month'], df_year['Number of flights'], label=str(year))

    plt.xlabel('Month')
    plt.ylabel('Total number of flights')
    plt.title('Total number of flights by year (after 1999)')
    plt.legend(title='Year')
    plt.grid()
    plt.show()


def calculate_correlation(df_IRP: pd.DataFrame, df_FDI: pd.DataFrame, US_to_CN: bool = True, correlation_between_two_FDI: bool = False) -> float:
    """
    This function will calculate the correlation between the yearly flights and the FDI.
    :param df_IRP: DataFrame containing the flight data
    :param df_FDI: DataFrame containing the FDI data
    :param US_to_CN: if True, use FDI from US to CN, otherwise use FDI from CN to US.
    :return: correlation
    """
    df_IRP_by_year = df_IRP.groupby(['Year']).size().reset_index(name='Number of flights')
    df_combined = df_IRP_by_year.merge(df_FDI, on='Year')

    if correlation_between_two_FDI:
        correlation = df_combined['US to CN in billion U.S. dollars'].corr(
            df_combined['CN to US in billion U.S. dollars'])
    elif US_to_CN:
        correlation = df_combined['Number of flights'].corr(df_combined['US to CN in billion U.S. dollars'])
    else:
        correlation = df_combined['Number of flights'].corr(df_combined['CN to US in billion U.S. dollars'])

    return correlation


def seasonal_fluctuations_in_US_China_flights(df_IRP: pd.DataFrame, start_year: int = 1999, end_year: int = 2022) -> None:
    """
    This function will plot the total number of flights by month.
    it will also print out a table with the first column being the mouth and the second column being the total number of flights in that month from 2000 to 2021
    :param df_IRP: the dataframe containing the flight data
    :param start_year: the start year of the data
    :param end_year: the end year of the data
    :return:
    """
    df_IRP = df_IRP[(df_IRP['Year'] <= end_year) & (df_IRP['Year'] >= start_year)]
    df_IRP_by_year_month = df_IRP.groupby(['Year', 'Month']).size().reset_index(name='Number of flights')
    df_IRP_by_month = df_IRP_by_year_month.groupby(['Month']).sum().reset_index()
    df_IRP_by_month = df_IRP_by_month.drop(columns=['Year'])
    df_IRP_by_month = df_IRP_by_month.sort_values(by=['Number of flights'], ascending=False).reset_index(drop=True)
    print(df_IRP_by_month)

    plt.figure(figsize=(18, 6))
    plt.bar(df_IRP_by_month['Month'], df_IRP_by_month['Number of flights'])
    plt.xlabel('Month')
    plt.ylabel('Number of flights')
    plt.title('Total number of flights by month')
    plt.grid()
    plt.show()


def add_airport_name(df_IRP : pd.DataFrame, df_CN_US_airports_IATA: pd.DataFrame, inspect : bool = False, add_missing_airport_name: bool = False,
                     add_names: list[str] = None, add_iata_codes: list[str] = None, add_iso_country: list[str] = None) -> pd.DataFrame:
    """
    This function will add the full airport name to the IRP data frame.
    The full airport name will be added as the fg_apt_name and usg_apt_name columns.
    :param df_IRP: the data frame containing the IRP data
    :param df_CN_US_airports_IATA: the data frame containing the airport name, IATA code, and ISO country code
    :param inspect: if True, print out the missing fg_apt and usg_apt values compared to the df_CN_US_airports_IATA
    :param add_missing_airport_name: if True, add the missing airport information to the df_IRP
    :param add_names: a list of airport names to be added to the df_IRP
    :param add_iata_codes: a list of IATA codes to be added to the df_IRP
    :param add_iso_country: a list of ISO country codes to be added to the df_IRP
    :return: the df_IRP with the fg_apt_name and usg_apt_name columns added
    """
    if inspect:
        # Find missing fg_apt values
        missing_fg_apt = set(df_IRP['fg_apt']).difference(df_CN_US_airports_IATA['iata_code'])
        if missing_fg_apt:
            print(f"Missing 'fg_apt' values:{missing_fg_apt}")
            print(df_IRP[df_IRP['fg_apt'].isin(missing_fg_apt)])

        # Find missing usg_apt values
        missing_usg_apt = set(df_IRP['usg_apt']).difference(df_CN_US_airports_IATA['iata_code'])
        if missing_usg_apt:
            print(f"Missing 'usg_apt' values:{missing_usg_apt}")
            print(df_IRP[df_IRP['usg_apt'].isin(missing_usg_apt)])

    if add_missing_airport_name:
        # Add airport name to df_CN_US_airports_IATA ['name', 'iata_code', 'iso_country']
        new_airports_df = pd.DataFrame({
            'name': add_names,
            'iata_code': add_iata_codes,
            'iso_country': add_iso_country})

        df_CN_US_airports_IATA = pd.concat([df_CN_US_airports_IATA, new_airports_df], ignore_index=True)

    df_IRP_with_airport_name = df_IRP.merge(df_CN_US_airports_IATA, left_on='fg_apt', right_on='iata_code', suffixes=('', '_fg'))
    df_IRP_with_airport_name = df_IRP_with_airport_name.rename(columns={'name': 'fg_apt_name'})
    df_IRP_with_airport_name = df_IRP_with_airport_name.drop(columns=['iata_code'])

    df_IRP_with_airport_name = df_IRP_with_airport_name.merge(df_CN_US_airports_IATA, left_on='usg_apt', right_on='iata_code', suffixes=('', '_usg'))
    df_IRP_with_airport_name = df_IRP_with_airport_name.rename(columns={'name': 'usg_apt_name'})
    df_IRP_with_airport_name = df_IRP_with_airport_name.drop(columns=['iata_code'])

    return df_IRP_with_airport_name


def most_popular_routes_between_US_and_China(df_IRP_with_airport_name: pd.DataFrame, topn: int = 10) -> None:
    """
    This function will print out the top n most popular routes between US and China
    :param df_IRP_with_airport_name:
    :param topn:
    :return:
    """
    df_IRP_by_airline = df_IRP_with_airport_name.groupby(['fg_apt_name', 'usg_apt_name']).size().reset_index(name='Number of flights')
    df_IRP_by_airline = df_IRP_by_airline.sort_values(by=['Number of flights'], ascending=False).reset_index(drop=True)
    print(df_IRP_by_airline.head(topn))



