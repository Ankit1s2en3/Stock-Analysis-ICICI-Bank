import csv
from dateutil.parser import parse
from sqlalchemy import Column, Date, Float, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import tkinter  as tk 
from tkinter import * 
from tkinter import ttk


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


class Window(tk.Tk):
    def __init__(self,root,content):


        self.frame = ttk.Frame(content,borderwidth=5,relief='ridge',width=200,height=100)
        self.namelbl = ttk.Label(content,text='Remarks')
        self.remark = ttk.Entry(content,state='disabled')
        self.var = IntVar()
        self.var.set(2)
        buySignal = ttk.Radiobutton(content,text='buy', variable=self.var,value=1,command = self.addRecords)
        sellSignal = ttk.Radiobutton(content,text='sell',variable=self.var,value=-1,command = self.addRecords)
        AllData = ttk.Radiobutton(content,text='All',variable=self.var,value=2,command = self.addRecords)
        self.ok = ttk.Button(content,text='Okay',state= DISABLED,command=self.addRemark)
        cancel = ttk.Button(content, text='Cancel')
        self.tree = ttk.Treeview(self.frame)
        self.vsb = ttk.Scrollbar(self.frame,orient='vertical')

        content.grid(column=0, row=0, sticky = (N,S,E,W))
        self.frame.grid(column=0, row=0, columnspan=3, rowspan=2, sticky=(N,S,E,W))
        self.namelbl.grid(column=3, row=0, columnspan=2,sticky=(N,W),padx=5)
        self.remark.grid(column=3, row=1, columnspan=4,sticky=(N,E,W),padx=5,pady=5)
        AllData.grid(column=0, row=3)
        sellSignal.grid(column=1, row=3)
        buySignal.grid(column=2, row=3)
        self.ok.grid(column=3, row=3)
        cancel.grid(column=4, row=3)

        #configure is used to add weights to rows and columns
        #it also heps to set resizing
        root.columnconfigure(0,weight=1)
        root.rowconfigure(0,weight=1)

        content.columnconfigure(0,weight=3)
        content.columnconfigure(1,weight=3)
        content.columnconfigure(2,weight=3)
        content.columnconfigure(3,weight=1)
        content.columnconfigure(4,weight=1)

        content.rowconfigure(1,weight=1)

        self.frame.columnconfigure(0,weight=1)
        self.frame.rowconfigure(0,weight=1)

        
        #removing first empty column
        self.tree['show'] = 'headings'
        #adding theme
        sty = ttk.Style(root)
        sty.theme_use('clam')
        #adding font for all child 
        sty.configure('.',font=('Helvetica',11))
        sty.configure('Treeview.Heading',foreground='black',font=('Helvetica',11,'bold'))

        self.tree['columns'] = ('id','date','close_price','rolling_avg_10_days','rolling_avg_20_days','position','remarks') #Stocks.__table__.columns.keys()

        #assigning the width,minwidth and anchor to the respective columns
        self.tree.column('id',width=50,minwidth=50,anchor=tk.CENTER)
        self.tree.column('date',width=100,minwidth=100,anchor=tk.CENTER)
        self.tree.column('close_price',width=100,minwidth=100,anchor=tk.CENTER)
        self.tree.column('rolling_avg_10_days',width=150,minwidth=150,anchor=tk.CENTER)
        self.tree.column('rolling_avg_20_days',width=150,minwidth=150,anchor=tk.CENTER)
        self.tree.column('position',width=150,minwidth=150,anchor=tk.CENTER)
        self.tree.column('remarks',width=100,minwidth=100,anchor=tk.CENTER)

        #assign the heading names to the respective columns
        self.tree.heading('id',text='ID',anchor=tk.CENTER)
        self.tree.heading('date',text='Date',anchor=tk.CENTER)
        self.tree.heading('close_price',text='Close Price',anchor=tk.CENTER)
        self.tree.heading('rolling_avg_10_days',text='Average 10 Days',anchor=tk.CENTER)
        self.tree.heading('rolling_avg_20_days',text='Average 20 Days',anchor=tk.CENTER)
        self.tree.heading('position',text='Buy/Sell Signal',anchor=tk.CENTER)
        self.tree.heading('remarks',text='Remarks',anchor=tk.CENTER)


        self.vsb.configure(command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.vsb.set)

        self.vsb.grid(row=0,column=0,sticky=NE+SE)
        self.addRecords()
        self.tree.grid(row=0,column=0,sticky=(N+S+E+W))
        self.tree.bind('<Double-1>',self.selectedItem)
        root.mainloop()

    def addRemark(self):
        newRemark = self.remark.get()
        session = Session()
        session.query(Stocks).filter(Stocks.id == self.id).update({'remarks': newRemark})
        session.commit()
        self.ok.config(state='disabled')
        self.remark.config(state='disabled')
        self.addRecords()

    def selectedItem(self,e):
        item = self.tree.selection()[0]
        self.id = self.tree.item(item)['values'][0]
        signal = self.tree.item(item)['values'][5]
        if signal =='buy' or signal == 'sell':
            self.remark.config(state='enable')
            self.ok.config(state='enable')
        else:
            self.remark.config(state='disabled')
            self.ok.config(state='disabled')
    def addRecords(self):
        i=0
        #seeing data using SQL Alchemy
        session = Session()
        signal = self.var.get()
        if signal == -1 or signal ==1:
            data_session = session.query(Stocks).filter(Stocks.position == signal).all()
        else:
            print('get all data')
            data_session = session.query(Stocks).all()
        #session.commit()
        for record in self.tree.get_children():
            self.tree.delete(record)

        for s in data_session:
            att = s.__dict__
            signal = ''
            if att['position'] == 1:
                signal = 'buy'
            elif att['position'] == -1:
                signal = 'sell'
            else:
                signal = '---'

            self.tree.insert('',i,text='',values=(att['id'],att['Date'],att['Close'],att['rolling_avg_10_days'],att['rolling_avg_20_days'],signal,att['remarks']) )

            i = i +1
        
        print('records added!!')
        session.commit()
       


root = Tk()
root.geometry('800x600')
root.title("Stocks details")
root.geometry("800x600")
content = ttk.Frame(root)

w = Window(root,content)

