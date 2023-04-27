# CS50-Finance
My implementation of the CS50 Finance web app from week 9 of the course
In order to initialize the flask server we must run the command "export API_KEY=value", the value of which can be found in finance/api_key.txt
The main part of the work can be found inside finance/app.py where all of the routes are implemented through flask.
You will see frequent calls to the "lookup" function, which can be found in finance/helpers.py, as it is the way we fetch data from our API.
The templates folder (finance/templates) contains all of the html pages that are being rendered through the routes.


