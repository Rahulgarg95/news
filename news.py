import feedparser
from flask import Flask
from flask import render_template
from flask import request
import json
import urllib
import urllib2

app = Flask(__name__)

RSS_FEEDS = {'bbc': 'http://feeds.bbci.co.uk/news/rss.xml',
             'cnn': 'http://rss.cnn.com/rss/edition.rss',
             'fox': 'http://feeds.foxnews.com/foxnews/latest',
             'iol': 'http://www.iol.co.za/cmlink/1.640',
             'ht': 'https://www.hindustantimes.com/rss/topnews/rssfeed.xml',
             'toi': 'https://timesofindia.indiatimes.com/rssfeedstopstories.cms'}

WEATHER_URL = "http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&APPID=e3bc88eb0649abdb0577c04ce4d878e2"
CURRENCY_URL = "https://openexchangerates.org//api/latest.json?app_id=6a0f7b96a90f4ed98578d79648afd01a"

DEFAULTS = {'publication': 'bbc',
            'city': 'London,UK',
            'currency_from': 'GBP',
            'currency_to': 'USD'
            }


@app.route("/")
def home():
    # get customised headlines, based on user input or default
    publication = request.args.get('query')
    if not publication:
        publication = DEFAULTS['publication']
    articles = get_news(publication)
    # get customised weather based on user input or default
    city = request.args.get('city')
    if not city:
        city = DEFAULTS['city']
    weather = get_weather(city)
    # get customised currency based on user input or default
    currency_from = request.args.get("currency_from")
    if not currency_from:
        currency_from = DEFAULTS['currency_from']
    currency_to = request.args.get("currency_to")
    if not currency_to:
        currency_to = DEFAULTS['currency_to']
    rate, currencies = get_rate(currency_from, currency_to)
    return render_template("home.html", articles=articles, weather=weather,
                           currency_from=currency_from, currency_to=currency_to, rate=rate,
                           currencies=sorted(currencies))


def get_rate(frm, to):
    all_currency = urllib2.urlopen(CURRENCY_URL).read()
    parsed = json.loads(all_currency).get('rates')
    frm_rate = parsed.get(frm.upper())
    to_rate = parsed.get(to.upper())
    return (to_rate / frm_rate, parsed.keys())


def get_news(publication):
    feed = feedparser.parse(RSS_FEEDS[publication])
    return feed['entries']


def get_weather(query):
    query = urllib.quote(query)
    url = WEATHER_URL.format(query)
    data = urllib2.urlopen(url).read()
    parsed = json.loads(data)
    weather = None
    if parsed.get('weather'):
        weather = {'description': parsed['weather'][0]['description'],
                   'temperature': parsed['main']['temp'],
                   'city': parsed['name'],
                   'country': parsed['sys']['country']
                   }
    return weather

if __name__ == "__main__":
    app.run(port=5000, debug=True)