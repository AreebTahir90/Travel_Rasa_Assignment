# Eco Travel Assistant

## Overview

The Eco Travel Assistant is a student prototype developed using Rasa Open Source,
Python and Streamlit.

The purpose of the chatbot is to support users who want to make more sustainable
travel decisions.

The chatbot can provide information about accommodation, public transport,
cultural attractions, weather, currency conversion and travel-related carbon
emissions.

It also supports multi-turn trip planning by collecting:

- destination
- travel dates
- budget
- sustainability preference

The collected information is stored using Rasa slots and is used to provide a
simple weighted transport recommendation.

---

## Main Features

The prototype includes:

- Rasa NLU and dialogue management
- DIETClassifier
- multi-turn Rasa forms
- destination, date, budget and sustainability slots
- hotel search using OpenStreetMap / Overpass
- public transport information using OpenStreetMap / Overpass
- cultural attraction search
- weather information using Open-Meteo
- currency conversion
- carbon estimates using Climatiq
- local carbon factors as an API fallback
- weighted transport recommendations
- dynamic quick reply buttons
- two-stage fallback handling
- human advisor handover
- conversation context packaging
- green, amber and red carbon indicators
- Streamlit user interface

---

## Technologies

Python 3.10

Rasa 3.6.21

Rasa SDK 3.6.2

Streamlit

Requests

OpenStreetMap / Overpass API

Open-Meteo API

Climatiq API

---

## Project Structure

```text
eco_travel_rasa_student_project/

actions/
    actions.py

    helpers/
        geocode_place.py
        find_hotels.py
        find_transport.py
        find_attractions.py
        weather_forecast.py
        currency_exchange.py
        carbon_estimate.py

data/
    nlu.yml
    rules.yml
    stories.yml

tests/
    test_stories.yml

config.yml
domain.yml
endpoints.yml
endpoints.docker.yml
credentials.yml

streamlit_app.py
requirements.txt

Dockerfile
docker-compose.yml
.env.example
README.md