from flask import Flask, render_template, request, jsonify
import requests
import os
import logging
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

API_KEY = os.getenv('ALPHAVANTAGE_API_KEY')


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/pobierz-dane-akcji', methods=['POST'])
def pobierz_dane_akcji():
    try:
        data = request.get_json()
        logging.info(f'Otrzymane dane: {data}')

        symbol = data.get('symbol')
        start_date = data.get('startDate')
        end_date = data.get('endDate')

        if not symbol or not start_date or not end_date:
            logging.error('Brak wymaganych danych')
            return jsonify({'error': 'Brak wymaganych danych'}), 400

        url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={API_KEY}&outputsize=full'
        response = requests.get(url)
        json_data = response.json()
        logging.info(f'Odpowiedź API: {json_data}')

        if response.status_code == 200 and 'Time Series (Daily)' in json_data:
            time_series = json_data['Time Series (Daily)']
            filtered_data = {date: val for date, val in time_series.items() if start_date <= date <= end_date}

            chart_data = {
                "labels": list(filtered_data.keys()),
                "datasets": [
                    {
                        "label": "Open",
                        "data": [float(val["1. open"]) for val in filtered_data.values()],
                        "borderColor": "rgba(75, 192, 192, 1)",
                        "backgroundColor": "rgba(75, 192, 192, 0.2)"
                    },
                    {
                        "label": "High",
                        "data": [float(val["2. high"]) for val in filtered_data.values()],
                        "borderColor": "rgba(153, 102, 255, 1)",
                        "backgroundColor": "rgba(153, 102, 255, 0.2)"
                    },
                    {
                        "label": "Low",
                        "data": [float(val["3. low"]) for val in filtered_data.values()],
                        "borderColor": "rgba(255, 159, 64, 1)",
                        "backgroundColor": "rgba(255, 159, 64, 0.2)"
                    },
                    {
                        "label": "Close",
                        "data": [float(val["4. close"]) for val in filtered_data.values()],
                        "borderColor": "rgba(54, 162, 235, 1)",
                        "backgroundColor": "rgba(54, 162, 235, 0.2)"
                    }
                ]
            }
            return jsonify(chart_data)
        elif 'Error Message' in json_data:
            logging.error(f'Błąd API: {json_data["Error Message"]}')
            return jsonify({'error': json_data['Error Message']}), 400
        else:
            logging.error('Nie udało się pobrać danych z API')
            return jsonify({'error': 'Nie udało się pobrać danych'}), 400
    except Exception as e:
        logging.error(f'Error fetching stock data: {e}')
        return jsonify({'error': 'Wystąpił błąd podczas przetwarzania żądania'}), 500


@app.route('/search-stocks', methods=['GET'])
def search_stocks():
    query = request.args.get('query')
    if not query:
        return jsonify({'error': 'Brak wymaganego parametru query'}), 400

    url = f'https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords={query}&apikey={API_KEY}'
    response = requests.get(url)
    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({'error': 'Nie udało się pobrać danych'}), 400


if __name__ == '__main__':
    app.run(debug=True)
