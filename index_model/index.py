import csv
import datetime as dt
import pathlib

import pandas as pd

class IndexModel:
    def __init__(self) -> None:
        #start of index
        self.level = 100
        self.start_day = None
        self.end_day = None
        self.composition = []
        self.portfolio_weight = []
        self.index_level_dict = {}
        path = pathlib.Path('data_sources/stock_prices.csv')
        self.stocks = pd.read_csv(path)

    def is_start_of_month(self, index: int, column: int) -> bool:
        return self.stocks.iloc[index, column].strftime("%m") != self.stocks.iloc[index - 1, column].strftime("%m")

    def calculate_composition(self, index: int):
        composition = []
        for df_index, stock_price in enumerate(self.stocks.iloc[index - 1, 1:11]):
            composition.append([stock_price, df_index])
        composition.sort(reverse=True)
        return [composition[0][1], composition[1][1], composition[2][1]]

    def determine_portfolio_allocation(self, index: int):
        stock_volume_one = None
        stock_volume_two = None
        stock_volume_three = None
        highest_market_cap = 0.5 * self.level
        second_to_third_cap = 0.25 * self.level
        for i, column in enumerate(self.composition):
            # selecting the proper columns of the dataframe; column 'Date' is not yet accounted for
            column = column + 1
            if i == 0:
                stock_volume_one = highest_market_cap / self.stocks.iloc[index, column]
            if i == 1:
                stock_volume_two = second_to_third_cap / self.stocks.iloc[index, column]
            if i == 2:
                stock_volume_three = second_to_third_cap / self.stocks.iloc[index, column]
        return [stock_volume_one, stock_volume_two, stock_volume_three]

    def calc_index_level(self, start_date: dt.date, end_date: dt.date) -> None:
        self.stocks['Date'] = pd.to_datetime(self.stocks['Date'], format=(
            '%d/%m/%Y'))  # converts the date from string format to datetime format.
        self.start_date = start_date.strftime('%d/%m/%Y')
        self.end_date = end_date.strftime('%d/%m/%Y')
        for index in self.stocks.index:
            index_calc_value = 0
            date = self.stocks.at[index, 'Date'].strftime('%d/%m/%Y')
            # select column of 'Date'. In this program at Pos. 1, therefore 0.
            if self.is_start_of_month(index, 0) and len(self.composition) > 0:
                for list_pos, volume in enumerate(self.portfolio_weight):
                    index_calc_value += volume * self.stocks.iloc[index, self.composition[list_pos] + 1]
                self.composition = self.calculate_composition(index)
                self.portfolio_weight = self.determine_portfolio_allocation(index)
                self.level = index_calc_value
                self.index_level_dict[date] = self.level

            if self.is_start_of_month(index, 0):
                 self.composition = self.calculate_composition(index)
                 self.portfolio_weight = self.determine_portfolio_allocation(index)

            if len(self.composition) < 1:
                continue
            for list_pos, volume in enumerate(self.portfolio_weight):
                index_calc_value += volume * self.stocks.iloc[index, self.composition[list_pos] + 1]
            self.level = index_calc_value
            if self.index_level_dict.get(date) != None:
                continue
            self.index_level_dict[date] = self.level

    def export_values(self, file_name: str):
        with open(file_name, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Date', 'index_level'])
            found_start_date = False
            for date, index_level in self.index_level_dict.items():
                if date == self.start_date:
                    found_start_date = True
                if found_start_date:
                    writer.writerow([date, index_level])
                if date == self.end_date:
                    break