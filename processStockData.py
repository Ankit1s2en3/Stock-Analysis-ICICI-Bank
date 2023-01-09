from nsepy import get_history
from datetime import date
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import csv
from dateutil.parser import parse
from sqlalchemy import Column, Date, Float, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

engine = create_engine('sqlite:///stocksData.sqlite3', echo=True)
Base = declarative_base()

class Stocks(Base):
    __tablename__ = 'ICICIBANK'
    id = Column(Integer, primary_key=True)
    Date = Column(String(200))
    Close = Column(Float)
    rolling_avg_10_days = Column(Float)
    rolling_avg_20_days = Column(Float)
    position = Column(Integer)
    remarks = Column(String)

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

try:
    data = get_history(symbol='ICICIBANK', start=date(2021,1,1),end=date(2022,9,2))
    data = data[['Close']]
    #getting rolling averages
    data['rolling_avg_10_days'] =  data['Close'].rolling(10).mean()
    data['rolling_avg_20_days'] =  data['Close'].rolling(20).mean()
    #calculating change in rolling avg 10,10 and finding signals
    data['Signal'] = 0.0
    data['Signal'] = np.where(data['rolling_avg_10_days'] > data['rolling_avg_20_days'] ,1.0,0.0)
    data['position'] = data['Signal'].diff()
    #making columns for signals to buy or sell
    buy = data[(data['position']==1)][['Close']]
    sell = data[(data['position']==-1)][['Close']]
    #converting date index into column **
    data = data.reset_index()

    #first indexes of buy and sell, considering buy signal first **
    f_idx_s = data[data['position']==-1].index[0]
    f_idx_b = data[data['position']==1].index[0]
    if f_idx_s < f_idx_b:
        sell = data[data.index > f_idx_s ]
        sell = sell[sell['position']==-1][['Date','Close']]
    else:
        sell = data[(data['position']==-1)][['Date','Close']]
    buy = data[(data['position']==1)][['Date','Close']]

    pairs_sell_buy = pd.DataFrame()

    if len(buy) != len(sell):
        pnl = sell['Close'].values - buy['Close'].values[:-1] #removing last row if it has unpacked buy
        pairs_sell_buy['buy date'] = buy.iloc[:-1, :]['Date']
        pairs_sell_buy['buy price'] = buy.iloc[:-1, :]['Close'].values #removing last row if it has unpacked buy
    else:
        pnl = sell['Close'].values - buy['Close'].values
        pairs_sell_buy['buy date'] = buy['Date'].values
        pairs_sell_buy['buy price'] = buy['Close'].values

    #print(type(buy.index))
    pairs_sell_buy['sell date'] = sell['Date'].values
    pairs_sell_buy['sell price'] = sell['Close'].values
    pairs_sell_buy['profit and loss'] = pnl
    pairs_sell_buy.to_csv('pnlData.csv')

    print('total profit/loss booked : ',sum(pnl))
    unbooked_pnl = sum(pnl) - buy['Close'].values[-1]
    print('total profit/loss unbooked : ',unbooked_pnl)

    data.dropna(inplace=True)
    print(data)
    data.index.names = ['id']
    data = data.drop(['Signal'],axis=1)
    data.to_csv('addToDatabase.csv')
except Exception as e:
    print('error occured while importing stock data from nsepy ')
    print(e)



def prepare_listing(row):
  #  row["Date"] = parse_none(row["Date"])
    return Stocks(**row)

try:

    with open('addToDatabase.csv', encoding='utf-8', newline='') as csv_file:
        csvreader = csv.DictReader(csv_file, quotechar='"')
        listings = [prepare_listing(row) for row in csvreader]
        session = Session()
        session.add_all(listings)
        session.commit()
    os.remove("addToDatabase.csv")
except Exception as e:
    print('error')
    print(e)