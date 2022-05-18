from urllib import response
import requests
from datetime import datetime, timedelta
import pandas as pd
from pathlib import Path
import os


def get_respose(search_term, from_date, page=1):
    url = "https://content.guardianapis.com/search?page={page}&q={search_term}&from-date={from_date}&api-key=test".format(
        search_term=search_term, from_date=from_date, page=page)

    r = requests.get(url, auth=('user', 'pass'))
    json = r.json()
    return json.get("response")


def say_hello():
    print("Hello....")


def main():
    search_term = "trudeau"

    from_date_str = '2018-01-01'
    from_date = datetime.strptime(from_date_str, '%Y-%m-%d').date()
    today = datetime.now().date()  # TODO: define this globally
    today_str = today.strftime("%Y-%m-%d")

    # initialize zero data frame
    idx = pd.date_range(start=from_date, end=today, freq="D")
    df = pd.DataFrame({'Occurrences': [0]*len(idx)}, index=idx)
    df.index.name = "Date"
    print(df.at["2018-01-03", "Occurrences"])

    response = get_respose(search_term, from_date, page=1)

    # counting number of pages
    pages_count = response.get("pages")
    print(pages_count)

    for page in range(1, pages_count+1):
        response = get_respose(search_term, from_date, page=page)
        if response.get("status") == "ok":
            results = response.get("results")
            for result in results:
                webPublicationDate = result.get("webPublicationDate")
                webPublicationDay = webPublicationDate.split("T")[0]
                df.at[webPublicationDay, "Occurrences"] += 1

    # write df to csv
    BASE_DIR = Path(__file__).resolve().parent.parent
    DATA_DIR = os.path.join(BASE_DIR, "data")
    output_path = os.path.join(DATA_DIR, "output.csv")
    df.to_csv(output_path)


if __name__ == "__main__":
    main()
