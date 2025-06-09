from datetime import datetime
from dateutil.rrule import rrule, MONTHLY
from helpers import calc_n_months_between_dates
import requests


class Coinbase:
    def __init__(self, base_url="https://api.coinbase.com", timeout=1):
        self._base_url = base_url
        self._timeout = timeout
        self._base_currencies = {}
        self._crypto_currencies = {}

    def init_base_currencies(self):
        """Initialize currency code:name pairs (i.e. "USD": "United States Dollar")"""

        response = requests.get(
            f"{self._base_url}/v2/currencies", timeout=self._timeout
        )
        json_response = response.json()

        base_currencies = {}
        for base_currency in json_response["data"]:
            base_currencies[base_currency["id"]] = base_currency["name"]

        return base_currencies

    def init_crypto_currencies(self):
        """Initialize crypto currency code:name pairs (i.e. "BTC": "Bitcoin")"""

        response = requests.get(
            f"{self._base_url}/v2/currencies/crypto", timeout=self._timeout
        )

        # If successful
        if response:
            json_response = response.json()

            crypto_currencies = {}
            for crypto_currency in json_response["data"]:
                crypto_currencies[crypto_currency["code"]] = crypto_currency["name"]

            return crypto_currencies
        else:
            raise Exception(f"Error: {response.status_code}")

    def get_crypto_price(self, currency_pair):
        """Get a price of crypto currency."""

        if not self.loaded():
            self.load()

        # If valid base_currency (i.e. "USD")
        # and crypto_currency (i.e. "BTC")
        if (
            currency_pair["base"] in self._base_currencies
            and currency_pair["crypto"] in self._crypto_currencies
        ):
            # Make requests
            response = requests.get(
                # I.e. https://api.coinbase.com/v2/prices/BTC-USD/buy
                f"{self._base_url}/v2/prices/"
                + f"{currency_pair['crypto']}-{currency_pair['base']}/buy",
                timeout=self._timeout,
            )

            # If successful
            if response:
                json_response = response.json()
                return {"amount": float(json_response["data"]["amount"])}
            else:
                raise Exception(f"Error: {response.status_code}")
        else:
            return False

    def get_historic_prices(self, params):
        """Get historic data of crypto currency."""

        # Cap month difference to 25, make sure start <= end
        if calc_n_months_between_dates(
            params["start_date"], params["end_date"]
        ) > 25 or datetime.strptime(
            params["start_date"], "%Y-%m-%d"
        ) > datetime.strptime(params["end_date"], "%Y-%m-%d"):
            return False

        # Unpack
        currency_pair = params["currency_pair"]

        if not self.loaded():
            self.load()

        # If valid base_currency (i.e. "USD")
        # and crypto_currency (i.e. "BTC")
        if (
            currency_pair["base"] in self._base_currencies
            and currency_pair["crypto"] in self._crypto_currencies
        ):
            if params["start_date"] and params["end_date"]:
                try:
                    # Unpack
                    start_date = datetime.strptime(
                        params["start_date"], "%Y-%m-%d"
                    ).date()
                    end_date = datetime.strptime(params["end_date"], "%Y-%m-%d").date()
                except ValueError:
                    return False
            else:
                return False

            # A list to hold dictionaries of historic prices
            historic_prices = []

            # Iterate over the dates
            for d in rrule(MONTHLY, dtstart=start_date, until=end_date):
                response = requests.get(
                    f"{self._base_url}/v2/prices/"
                    + f"{currency_pair['crypto']}-{currency_pair['base']}/buy",
                    params={"date": d.strftime("%Y-%m-%d")},
                    timeout=self._timeout,
                )

                # If successful
                if response:
                    json_response = response.json()

                    # Append a dictionary of historic price
                    historic_prices.append(
                        {
                            "date": d.strftime("%Y-%m-%d"),
                            "amount": float(json_response["data"]["amount"]),
                        }
                    )
                else:
                    raise Exception(response.json()["error"])

            return historic_prices
        else:
            return False

    def loaded(self):
        """Returns True if self._base_currencies and self._crypto_currencies
        are truthy (have value), else False."""
        return True if (self._base_currencies and self._crypto_currencies) else False

    def load(self):
        """Load contents of self._base_currencies and self._crypto_currencies."""
        self._base_currencies = self.init_base_currencies()
        self._crypto_currencies = self.init_crypto_currencies()
