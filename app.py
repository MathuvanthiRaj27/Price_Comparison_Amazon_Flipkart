from flask import Flask, render_template, request, make_response, jsonify
import pickle
import io
import csv
from io import StringIO
import pandas as pd
import numpy as np
import requests
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import re

from pandas import DataFrame

app = Flask(__name__)

HEADERS = ({'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Genvcko), Chrome/44.0.2403.157 Safari/537.36','Accept-Language': 'en-US, en;q=0.5'})
@app.route('/', methods=['GET'])
def Home():
    return render_template('index.html')

@app.route('/index1', methods=['GET'])
def index1():
    return render_template('index1.html')

@app.route('/index', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/layout', methods=['GET'])
def layout():
    return render_template('layout.html')


main_list = []
main_list_f = []

@app.route('/amazon', methods=["POST"])

def amazon():
    product_name = request.form['product']
    for i in range(1, 10):
        get_data(i,product_name)

    df: DataFrame = pd.DataFrame(main_list)
    main_list.clear()
    df.columns = ["Mobile_Name", "Color", "RAM (GB)", "Storage (GB)", "Amazon_Price"]
    df['Amazon_Price'] = df['Amazon_Price'].apply(lambda x: x.replace(',', "")).astype(int)
    df.drop_duplicates(inplace=True)
    a_df: DataFrame= df
    print(a_df)
    del df
    return render_template('index.html', column_names=a_df.columns.values, res_amazon=list(a_df.values.tolist()), zip=zip)

@app.route('/flipkart', methods=["POST"])
def flipkart():
    product_name = request.form['flipkart']
    for i in range(1, 10):
        get_data_flip(i,product_name)
    df1 = pd.DataFrame(main_list_f)
    main_list_f.clear()
    df1.columns = ["Mobile_Name", "Color", "RAM (GB)", "Storage (GB)", "Flipkart_Price"]
    df1['Flipkart_Price'] = df1['Flipkart_Price'].apply(lambda x: x.replace(',', "")).astype(int)
    df1.drop_duplicates(inplace=True)
    return render_template('index.html', column_names=df1.columns.values, res_flipkart=list(df1.values.tolist()), zip=zip)


def get_data_flip(pageNo,f_name):
    #url = "https://www.flipkart.com/search?q=" + f_name + "&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=on&as=off&sort=popularity&page="
    url = "https://www.flipkart.com/search?q=samsung&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=on&as=off"
    req = requests.get(f'{url}{str(pageNo)}')
    soup = BeautifulSoup(req.content, 'lxml')
    for main in soup.find_all("div", {"class": "_3pLy-c row"}):
        sub = main.find("div", {"class": "_4rR01T"})
        f_list = []
        try:
            if f_name.lower() not in sub.text.lower():
                continue
            m_name = sub.text.split("(")[0].strip()
            m_color = sub.text.split("(")[1].split(",")[0].strip()
            m_storage = re.search(r'\d+', (sub.text.split("(")[1].split(",")[1].split("GB")[0].strip())).group()
            for i in main.find_all("li", {"class": "rgWa7D"}):
                if "RAM" in i.text:
                    ram = re.search(r'\d+', (i.text.split("RAM")[0].split("GB")[0].strip())).group()
                    # m_storage = i.split("|")[1].strip()
            m_price = main.find("div", {"class": "_30jeq3 _1_WHN1"}).text.split("₹")[1].strip()
            # print(m_name, m_color,m_storage,ram, m_price)
            f_list.append(m_name.upper())
            f_list.append(m_color.upper())
            f_list.append(ram)
            f_list.append(m_storage)
            f_list.append(m_price)
            main_list_f.append(f_list)
            # print(main_list_f)
        except:
            continue

    return main_list_f


def get_data(pageNo,product_name):
    url = "https://www.amazon.in/s?k=" + product_name + "&page=" + str(pageNo)
    req = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(req.content, 'lxml')

    for main in soup.find_all("div", {"class": "sg-col sg-col-4-of-12 sg-col-8-of-16 sg-col-12-of-20"}):
        list1 = []
        m_name = main.find("span", {"class": "a-size-medium a-color-base a-text-normal"}).text.split("(")[0].strip()
        if product_name.upper() not in m_name.upper():
            continue

            # print(m_name)
        sub = main.find("span", {"class": "a-size-medium a-color-base a-text-normal"}).text.replace("(",
                                                                                                        "|").replace(
                ")", "").split("|")
            # print(sub)
        try:
            if "RAM" not in main.find("span", {"class": "a-size-medium a-color-base a-text-normal"}).text:
                continue
            else:
                m_color = sub[1].split(",")[0]
                m_ram = re.search(r'\d+', (sub[1].split(",")[1].split("GB")[0])).group()
                #print(m_ram)
                m_storage = re.search(r'\d+', (sub[1].split(",")[2].split("GB")[0])).group()
                #print(m_storage)
                    # print(m_color,m_ram,m_storage)
            m_price = main.find("span", {"class": "a-offscreen"}).text.split("₹")[1].strip()

            list1.append(m_name.upper())
            list1.append(m_color.upper())
            list1.append(m_ram)
            list1.append(m_storage)
            list1.append(m_price)
            main_list.append(list1)
                # print(main_list)
        except:
            continue
    return main_list


@app.route('/compare', methods=["POST"])

def compare_price():
    product = request.form['product_name']
    for i in range(1, 5):
        get_data(i,product)
    df: DataFrame = pd.DataFrame(main_list)
    main_list.clear()
    df.columns = ["Mobile_Name", "Color", "RAM (GB)", "Storage (GB)", "Amazon_Price"]
    df['Amazon_Price'] = df['Amazon_Price'].apply(lambda x: x.replace(',', "")).astype(int)
    df.drop_duplicates(inplace=True)
    print(df)
    for i in range(1, 10):
        get_data_flip(i, product)
    df1 = pd.DataFrame(main_list_f)
    main_list_f.clear()
    df1.columns = ["Mobile_Name", "Color", "RAM (GB)", "Storage (GB)", "Flipkart_Price"]
    df1['Flipkart_Price'] = df1['Flipkart_Price'].apply(lambda x: x.replace(',', "")).astype(int)
    df1.drop_duplicates(inplace=True)
    print(df1)
    try:
        mergedStuff = pd.merge(df, df1, how='inner')
        mergedStuff['Difference_Amount'] = abs(mergedStuff['Amazon_Price'] - mergedStuff['Flipkart_Price'])
    except:
        mergedStuff=""
    return render_template('index1.html', column_names=mergedStuff.columns.values, res_compare=list(mergedStuff.values.tolist()), zip=zip)

@app.route('/single', methods=["POST"])

def single():
    price = amazon_price()
    f_price = flipkart_price()
    try:
        if int(price)< int(f_price):
            message = "You can prefer Amazon"
        elif int(price)== int(f_price):
            message = "Both have the same price"
        else:
            message = "You can prefer Flipkart"
    except:
        message="Give a correct value"
    return render_template('layout.html',  Predict = "The Price in Amazon is : "+ price, Predicted ="The Price in Flipkart is : "+f_price, Prediction = message)

def flipkart_price():
    mobile = request.form['mobile']
    color = request.form['color']
    ram = request.form['ram']
    storage = request.form['storage']
    for i in range(1, 10):
        get_data_flip(i, mobile)
    df1 = pd.DataFrame(main_list_f)
    df1.columns = ["Mobile_Name", "Color", "RAM (GB)", "Storage (GB)", "Flipkart_Price"]
    df1['Flipkart_Price'] = df1['Flipkart_Price'].apply(lambda x: x.replace(',', "")).astype(int)
    df1.drop_duplicates(inplace=True)
    df2 = df1[(df1['Mobile_Name'] == mobile.upper()) & (df1['Color'] == color.upper()) & (df1['RAM (GB)'] == ram) & (df1['Storage (GB)'] == storage)]
    res_pric = df2['Flipkart_Price'].to_string(index=False)
    print(res_pric)
    return res_pric



def amazon_price():
    mobile = request.form['mobile']
    color = request.form['color']
    ram = request.form['ram']
    storage = request.form['storage']
    for i in range(1, 5):
        get_data(i,mobile)
    df: DataFrame = pd.DataFrame(main_list)
    df.columns = ["Mobile_Name", "Color", "RAM (GB)", "Storage (GB)", "Amazon_Price"]
    df['Amazon_Price'] = df['Amazon_Price'].apply(lambda x: x.replace(',', "")).astype(int)
    df.drop_duplicates(inplace=True)
    df1 = df[(df['Mobile_Name'] ==mobile.upper()) & (df['Color']==color.upper()) & (df['RAM (GB)']==ram) & (df['Storage (GB)']==storage)]
    res_price = df1['Amazon_Price'].to_string(index=False)
    print(res_price)
    return res_price

if __name__ == "__main__":
    app.run(debug=True)
