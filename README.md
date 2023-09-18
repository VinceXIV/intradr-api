# intradr-api

This api provides functionality including
1. Fetching relevant stock data using APIs such as yfinance
2. Doing the calculations created by the user from the front end. It receives a JSON data corresponding to an array of mathematical expressions used to define new variables (e.g all calculations involved in creating the Sharpe Ratio)
3. It uses tools such as symbolab to aid in parsing the mathematical expressions, does the calculations and returns the results

## Setting it up

### Prerequisites
You are working with Ubuntu 20~. If working with any other case, the directives provided below are not guaranteed to work

### Steps
1. Have venv and python3 installed in your system
2. clone the repository using the command `git clone https://github.com/VinceXIV/intradr-api`
3. Navigate to the relevant directory (In this case intradr-api) using `cd intradr-api`
4. Create a virtual environment using the command `python3 -m venv dev-env`
5. Activate the virtual environment `source dev-env/bin/activate`
6. Install the requirements provided in the requirements.txt using `pip install -r requirements.txt`
7. Run the app; `flask --app intradr-api run`
