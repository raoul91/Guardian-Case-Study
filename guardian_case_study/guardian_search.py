import os
import pandas as pd
import requests
from urllib import response
from datetime import datetime, timedelta
from pathlib import Path
import matplotlib.pyplot as plt
import statistics


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = os.path.join(BASE_DIR, "data")


def get_guardian_respose(search_term, from_date, page=1):
    url = "https://content.guardianapis.com/search?page={page}&q={search_term}&from-date={from_date}&api-key=test".format(
        search_term=search_term,
        from_date=from_date,
        page=page,
    )
    r = requests.get(url, auth=('user', 'pass'))
    json = r.json()
    return json.get("response")


def main():
    search_term = "trudeau"

    from_date_str = '2018-01-01'
    from_date = datetime.strptime(from_date_str, '%Y-%m-%d').date()
    today = datetime.now().date()  # TODO: define this globally
    today_str = today.strftime("%Y-%m-%d")

    # initialize zero data frame
    idx = pd.date_range(start=from_date, end=today, freq="D")
    df = pd.DataFrame({'occurrences': [0]*len(idx)}, index=idx)
    df.index.name = 'date'
    response = get_guardian_respose(search_term, from_date, page=1)

    # Count number of pages
    pages_count = response.get("pages")

    for page in range(1, pages_count+1):
        response = get_guardian_respose(search_term, from_date, page=page)
        if response.get("status") == "ok":
            results = response.get("results")
            for result in results:
                webPublicationDate = result.get("webPublicationDate")
                webPublicationDay = webPublicationDate.split("T")[0]
                df.at[webPublicationDay, 'occurrences'] += 1

    # write df to csv
    csv_output_path = os.path.join(DATA_DIR, "output.csv")
    df.to_csv(csv_output_path)

    # calculate mean value of articles
    print(statistics.mean(df['occurrences']))

    # plot and show and save
    """
    plt.plot(df.index, df['occurrences'], lw=1, color='red')
    plt.xlabel("date")
    plt.ylabel("number of articles")
    plt.xticks(rotation=45)
    fig = plt.gcf()
    fig.set_size_inches(10, 10)
    plot_output_path = os.path.join(DATA_DIR, "number_of_articles.png")
    fig.savefig(plot_output_path, dpi=100)
    plt.show()
    """


if __name__ == "__main__":
    main()
