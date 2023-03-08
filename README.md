Final-year project for polytechnic Early Admission Exercise

# What is this?
A simple portfolio website that I've created by following the following guide: https://youtu.be/dam0GPOAvVI

It also has some basic capabilities to communicate with the EVE Online API service (EVE Swagger Interface - ESI)

## Current capabilities:
- Displaying character and corporation wallet

## TODO
- Implement a mechanic to present transactional data as graphs and charts
- Add another page to see corporation and personal contracts


## How to run the project locally?

1. Clone the repository on your system
```shell
git clone https://github.com/Kyria/flask-esipy-example.git
```

2. Install requirements on your system
```shell
pip install -r requirements.txt
```

## Create your app in https://developers.eveonline.com

1. Go to https://developers.eveonline.com
2. Login and go to `manage applications`
3. Create a new application
4. Fill all the fields

3. Open up `config.json` and edit the keys inside
```json
{
    "application": {
        "app_key": "YOUR_SECRET_KEY",
        "client_id": "YOUR_CLIENT_ID",
        "callback": "YOUR_CALLBACK_URL",
        "headers": {"User-Agent": "YOUR_HEADER"}
    }
}

4. Run the following command in the command prompt
```shell
python main.py
```