from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
from sqlalchemy import create_engine

app = Flask(__name__)

engine = create_engine('sqlite:///ohlc.db')
engine1 = create_engine('sqlite:///ohlc1.db')
engine2 = create_engine('sqlite:///ohlc2.db')
@app.route('/', methods=['GET', 'POST'])
def index():
    sql = '''SELECT * FROM websitedata'''
    df = pd.read_sql_table(table_name='websitedata', con=engine)
    return render_template('index.html', tables=[df.to_html(classes='data')])

@app.route('/4hour/', methods=['GET', 'POST'])
def about():
    sql1 = '''SELECT * FROM websitedata'''
    df1 = pd.read_sql_table(table_name='websitedata', con=engine1)
    return render_template('about.html', tables1=[df1.to_html(classes='data')])

@app.route('/5min/')
def lowtimeframe():
    sql2 = '''SELECT * FROM websitedata'''
    df2 = pd.read_sql_table(table_name='websitedata', con=engine2)
    return render_template('lowtimeframe.html', tables2=[df2.to_html(classes='data')])

if __name__ == '__main__':
    app.run(host = '0.0.0.0')