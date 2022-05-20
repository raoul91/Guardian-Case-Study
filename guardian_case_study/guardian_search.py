import os
from re import A
from numpy import zeros
import pandas as pd
import requests
from urllib import response
from datetime import datetime, timedelta
from pathlib import Path
import matplotlib.pyplot as plt
import statistics


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = os.path.join(BASE_DIR, "data")


class GuardianSearch:
    def __init__(self, search_terms, from_date, to_date):
        self.search_terms = search_terms
        self.from_date = from_date
        self.to_date = to_date

    def get_search_url(self, page=1):
        search_terms_concatenated = " AND ".join(self.search_terms)
        return "https://content.guardianapis.com/search?page={page}&q={search_terms}&from-date={from_date}&to-date={to_date}&api-key=test".format(
            page=page,
            search_terms=search_terms_concatenated,
            from_date=self.from_date,
            to_date=self.to_date
        )

    def get_response(self, page=1):
        url = self.get_search_url(page)
        r = requests.get(url, auth=('user', 'pass'))
        json = r.json()
        return json.get("response")

    def count_pages(self):
        response = self.get_response()
        return response.get("pages")

    def get_date_section_dict(self):
        date_section_dict = {}
        sections = set()
        pages = self.count_pages()

        for page in range(1, pages+1):
            response = self.get_response(page=page)
            if response.get("status") == "ok":
                results = response.get("results")
                for result in results:
                    section = result.get("sectionName")
                    sections.add(section)
                    post_date = result.get("webPublicationDate")
                    post_day = post_date.split("T")[0]
                    if date_section_dict.get((post_day, section)):
                        date_section_dict[(post_day, section)] += 1
                    else:
                        date_section_dict[(post_day, section)] = 1

        return date_section_dict, list(sections)

    def initialize_zero_df(self, sections):
        idx = pd.date_range(start=self.from_date, end=self.to_date, freq="D")
        zero_content = {}

        for section in sections:
            zero_content[section] = [0]*len(idx)

        df = pd.DataFrame(zero_content, index=idx)
        df.index.name = 'date'
        return df

    def get_article_section_df(self):
        date_section_dict, sections = self.get_date_section_dict()
        df = self.initialize_zero_df(sections)

        for (date, section), count in date_section_dict.items():
            df.at[date, section] = count

        return df


def main():
    today = datetime.now().date()
    today_str = today.strftime("%Y-%m-%d")
    guardian_search = GuardianSearch(["trudeau"], "2018-01-01", today_str)

    df = guardian_search.get_article_section_df()
    output_path = os.path.join(DATA_DIR, "output.csv")

    df["total"] = df.sum(axis=1)
    df.to_csv(output_path, sep=";")

    # calculate mean, variance, standard deviation
    mean = df["total"].mean()
    print("Average no. of articles over all days = {0}".format(mean))

    var = df["total"].var()
    print("Variance of no. of articles = {0}".format(var))

    std = df["total"].std()
    print("Standard deviation of no. of articles = {0}".format(std))

    """
    # max section and number of articles per section
    s = df.sum(axis=0)
    s_dict = s.to_dict()
    s_dict.pop("total")

    print("Number of articles per section:")
    for section, number in s_dict.items():
        print("{section}: {number}".format(
            section=section, number=number))
    max_section = max(s_dict, key=s_dict.get)
    print("Section with the most articles = {0}".format(max_section))

    # articles per section
    art_per_section = pd.DataFrame(
        {'No. of articles per section': s.values}, index=s.index)
    art_per_section.index.name = "Section"
    articles_per_section_path = os.path.join(
        DATA_DIR, "articles_per_section.csv")

    # plot article

    plt.plot(df.index, df['total'], lw=1, color='red')
    plt.xlabel("date")
    plt.ylabel("number of articles")
    plt.xticks(rotation=45)
    fig = plt.gcf()
    fig.set_size_inches(10, 10)
    plot_output_path = os.path.join(DATA_DIR, "number_of_articles.png")
    fig.savefig(plot_output_path, dpi=100)
    plt.show()


    # all data points will be within +/- 3 std
    special_dates_df = df[[abs(df["total"]-mean) > 3*std]]
    print("special events")
    print(special_dates_df)

    # autocorrelation plot to detect seasonality
    print(df.sum(axis=1))
    x = pd.plotting.autocorrelation_plot(df.sum(axis=1))
    plt.show()
    x.plot()
    """

    # special dates (dates for which ...)
    special_dates = df[abs(df["total"] - mean) > 3*std]
    special_dates_path = os.path.join(DATA_DIR, "special_dates.csv")
    special_dates.to_csv(special_dates_path, sep=";")


if __name__ == "__main__":
    main()
