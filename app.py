# Importing essential libraries and modules

from flask import Flask, render_template, request, Markup
import numpy as np
import pandas as pd

from utils.fertilizer import fertilizer_dic
import requests
import pickle
import io


# ==============================================================================================

# -------------------------LOADING THE TRAINED MODELS -----------------------------------------------


# Loading crop recommendation model

crop_recommendation_model_path = 'models/RandomForest.pkl'
crop_recommendation_model = pickle.load(
    open(crop_recommendation_model_path, 'rb'))


# =========================================================================================

# Custom functions for calculations


def weather_fetch(city_name):
    """
    Fetch and returns the temperature and humidity of a city
    :params: city_name
    :return: temperature, humidity
    """
    api_key = "38f3813fc3e7fac2bfe53ac6229d7f39"
    base_url = "http://api.openweathermap.org/data/2.5/weather?"

    complete_url = base_url + "appid=" + api_key + "&q=" + city_name
    response = requests.get(complete_url)
    x = response.json()

    if x["cod"] != "404":
        y = x["main"]

        temperature = round((y["temp"] - 273.15), 2)
        humidity = y["humidity"]
        return temperature, humidity
    else:
        return None


# ===============================================================================================
# ------------------------------------ FLASK APP -------------------------------------------------


app = Flask(__name__)


# render home page


@app.route('/')
def home():
    title = 'AGRIFRIEND-HOME'
    return render_template('index.html', title=title, url='/static/h1.jpg')


# render crop recommendation form page


@app.route('/crop-recommend')
def crop_recommend():
    title = 'AGRIFRIEND-CROP RECOMMENDATIONS '
    return render_template('crop.html', title=title)


# render fertilizer recommendation form page


@app.route('/fertilizer')
def fertilizer_recommendation():
    title = 'AGRIFRIEND-FERTILIZER SUGGESTIONS'

    return render_template('fertilizer.html', title=title)


@app.route('/video', methods=['GET', 'POST'])
def video_recommend():
    title = "AGRIFRIEND-VIDEO RECOMMENDATIONS"
    return render_template('videos.html', title=title)


@app.route('/MSPcrop', methods=['GET', 'POST'])
def mymsp():
    title = "AGRIFRIEND-MSP SUGGESTION"
    return render_template('msp.html', title=title)

# ===============================================================================================

# RENDER PREDICTION PAGES

# render crop recommendation result page


@app.route('/crop-predict', methods=['POST'])
def crop_prediction():
    title = 'AGRIFRIEND-A ROBOUST CROP RECOMMENDATIONS'

    if request.method == 'POST':
        N = int(request.form['nitrogen'])
        P = int(request.form['phosphorous'])
        K = int(request.form['pottasium'])
        ph = float(request.form['ph'])
        rainfall = float(request.form['rainfall'])

        # state = request.form.get("stt")
        city = request.form.get("city")

        if weather_fetch(city) != None:
            temperature, humidity = weather_fetch(city)
            data = np.array([[N, P, K, temperature, humidity, ph, rainfall]])
            my_prediction = crop_recommendation_model.predict(data)
            final_prediction = my_prediction[0]

            return render_template('crop-result.html', prediction=final_prediction, title=title,temp=temperature,hum=humidity)

        else:

            return render_template('try_again.html', title=title)


# render fertilizer recommendation result page


@app.route('/fertilizer-predict', methods=['POST'])
def fert_recommend():
    title = 'AGRIFRIEND-FERTILIZER SUGGESTIONS'

    crop_name = str(request.form['cropname'])
    N = int(request.form['nitrogen'])
    P = int(request.form['phosphorous'])
    K = int(request.form['pottasium'])
    # ph = float(request.form['ph'])

    df = pd.read_csv('Data/fertilizer.csv')

    nr = df[df['Crop'] == crop_name]['N'].iloc[0]
    pr = df[df['Crop'] == crop_name]['P'].iloc[0]
    kr = df[df['Crop'] == crop_name]['K'].iloc[0]

    n = nr - N
    p = pr - P
    k = kr - K
    temp = {abs(n): "N", abs(p): "P", abs(k): "K"}
    max_value = temp[max(temp.keys())]
    if max_value == "N":
        if n < 0:
            key = 'NHigh'
        else:
            key = "Nlow"
    elif max_value == "P":
        if p < 0:
            key = 'PHigh'
        else:
            key = "Plow"
    else:
        if k < 0:
            key = 'KHigh'
        else:
            key = "Klow"

    response = Markup(str(fertilizer_dic[key]))

    return render_template('fertilizer-result.html', recommendation=response, title=title)





# render data based on crop msp
@app.route('/IndiaMsp', methods=['POST'])
def cropmsp():
    title = 'AGRIFRIEND-MSP SUGGESTION'
    final = []

    crop_msp = str(request.form['mspprice'])
    df = pd.read_csv('Data/msp.csv')
    price = df[df['State'] == crop_msp].iloc[:].values
    for x in price:
        final.append(x)
    mydata = pd.DataFrame(final)
    mydata.columns = ['State', 'District', 'Market Name',
                      'Arrival(QTL)', 'Variety', 'MODAL Price (RS/QTL)', 'MIN Price (RS/QTL)',
                      'MAX Price (RS/QTL)', 'CropName']


    return render_template('mspresults.html', tables=[mydata.to_html(classes='data', header="true")],
                           titles=mydata.columns.values, title=title)


#render faq
@app.route('/faq')
def faq():
    return render_template('faq.html')
@app.route('/weather')
def weather():
    return render_template('weatherdashboard.html')
# ===============================================================================================
if __name__ == '__main__':
    app.run(debug=True)
