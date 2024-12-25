@staticmethod       
def get_currency(country_id: int, countries):
    for country in countries:
        if country.id == int(country_id):
            return country.currency