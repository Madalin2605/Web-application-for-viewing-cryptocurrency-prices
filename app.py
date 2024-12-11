import base64
import json

import numpy as np
import pandas as pd
from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from wtforms import SelectField
import requests
import matplotlib.pyplot as plt
from io import BytesIO
from datetime import datetime, timedelta
import mpld3

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'


def get_coins():
    url = "https://coinranking1.p.rapidapi.com/coins"
    headers = {
        "X-RapidAPI-Key": "82849bd050msh252549694dfdf02p12635ajsne577ad4dce21",
        "X-RapidAPI-Host": "coinranking1.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Ridică o excepție pentru erori HTTP

        data = response.json()
        coins = [coin['name'] for coin in data['data']['coins']]
        id = [coin['uuid'] for coin in data['data']['coins']]
        # coins = [{"name": coin['name'], "id": coin['uuid']} for coin in data['data']['coins']]
        return coins, id

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None


def get_coin(coin_id):
    url = f"https://coinranking1.p.rapidapi.com/coin/{coin_id}"

    headers = {
        "X-RapidAPI-Key": "82849bd050msh252549694dfdf02p12635ajsne577ad4dce21",
        "X-RapidAPI-Host": "coinranking1.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Ridică o excepție pentru erori HTTP

        data = response.json()
        coin_info = {
            "symbol": data["data"]["coin"]["symbol"],
            "name": data["data"]["coin"]["name"],
            "price": data["data"]["coin"]["price"]
        }
        return coin_info

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None


def get_price_history(coin_id, interval):
    url = f"https://coinranking1.p.rapidapi.com/coin/{coin_id}/history"

    querystring = {"timePeriod": interval}

    headers = {
        "X-RapidAPI-Key": "82849bd050msh252549694dfdf02p12635ajsne577ad4dce21",
        "X-RapidAPI-Host": "coinranking1.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()  # Ridică o excepție pentru erori HTTP

        data = response.json()
        prices = [float(price['price']) for price in data['data']['history']]
        timestamps = [datetime.utcfromtimestamp(entry['timestamp']) for entry in data['data']['history']]
        history = [{"price": price['price'], "timestamp": price['timestamp']} for price in data['data']['history']]
        return timestamps, prices

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None


# # history = get_price_history('Qwsogvtv82FCd', "1y")
# timestamps, prices = get_price_history('Qwsogvtv82FCd', "1y")
# # timestamps = [datetime.utcfromtimestamp(entry['timestamp']) for entry in history]
# # prices = [float(entry['price']) for entry in history]
# print(timestamps)
# print(prices)
# df = pd.DataFrame({'Timestamp': timestamps, 'Price': prices})
# df = df.sort_values(by='Timestamp')
#
# plt.figure(figsize=(10, 6))
# plt.plot(df['Timestamp'], df['Price'], marker='o', linestyle='-', color='b')
#
# plt.title('Evolutia Pretului')
# plt.xlabel('Timp')
# plt.ylabel('Pret')
#
# plt.xticks(rotation=45)
#
# plt.tight_layout()
# plt.show()

@app.route('/', methods=['GET', 'POST'])
def index():
    coins, coins_id = get_coins()
    if request.method == 'POST':
        name = request.form['name']
        interval = request.form['interval']
        id = coins_id[coins.index(name)]
        info = get_coin(id)
        timestamps, prices = get_price_history(id, interval)

        # Generare grafic cu matplotlib
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(timestamps, prices, label='Evolutia Pretului ' + name + ' in ultimele ' + interval, color='green')
        ax.set_xlabel('Data', fontsize=16, fontweight='bold')
        ax.set_ylabel('Pret', fontsize=16, fontweight='bold')
        ax.legend(fontsize=12)
        ax.grid(False)

        # Conversie in format HTML utilizand mpld3
        html_fig = mpld3.fig_to_html(fig)
        html_fig2 = mpld3.fig_to_html(fig)

        return render_template('index.html', coins=coins, info=info, name=name, html_fig=html_fig, html_fig2=html_fig2, prices=prices)

    return render_template('index.html', coins=coins, info=None, name=None, html_fig=None, html_fig2=None, prices=None)


if __name__ == '__main__':
    app.run(debug=True)
