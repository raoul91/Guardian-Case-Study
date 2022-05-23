import os
from turtle import st
import pandas as pd
import requests
from datetime import datetime
from pathlib import Path
import matplotlib.pyplot as plt
from zipfile import ZipFile


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = os.path.join(BASE_DIR, "data")


class GuardianSearch:
    def __init__(self, search_term, from_date, to_date):
        self.search_term = search_term
        self.from_date = from_date
        self.to_date = to_date

    def get_search_url(self, page=1):
        return "https://content.guardianapis.com/search?page={page}&q={search_terms}&from-date={from_date}&to-date={to_date}&api-key=test".format(
            page=page,
            search_terms=self.search_term,
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


def generate_articles_csv(df):
    s = df.sum(axis=1)
    total_df = pd.DataFrame({"Total No. of Articles": s.values}, index=s.index)
    total_df.index.name = "date"
    path = os.path.join(DATA_DIR, "number_of_articles.csv")
    total_df.to_csv(path, sep=";")


def total_number(df):
    df_new = df.copy()
    s = df_new.sum(axis=1)
    return s.sum()


def mean(df):
    df_new = df.copy()
    s = df_new.sum(axis=1)
    return s.mean()


def std(df):
    df_new = df.copy()
    s = df_new.sum(axis=1)
    return s.std()


def generate_csv(df):
    df_new = df.copy()
    s = df_new.sum(axis=1)
    total_df = pd.DataFrame({"Total No. Articles": s.values}, index=s.index)
    path = os.path.join(DATA_DIR, "number_of_articles.csv")
    total_df.to_csv(path, sep=";")


def generate_unusual_events_csv(df):
    df_new = df.copy()
    df_new["total"] = df_new.sum(axis=1)
    m = mean(df)
    sd = std(df)
    df_new = df_new[abs(df_new["total"]-m) >= 3*sd]
    # TODO: sort by number of events
    path = os.path.join(DATA_DIR, "unusual_events.csv")
    df_new.to_csv(path, sep=";")


def generate_evolution_series(df, title):
    df_new = df.copy()
    df_new["total"] = df_new.sum(axis=1)
    plt.plot(df_new.index, df_new['total'], lw=1, color='red')
    plt.title(title)
    plt.xlabel("date")
    plt.ylabel("number of articles")
    plt.xticks(rotation=45)
    fig = plt.gcf()
    fig.set_size_inches(10, 10)
    path = os.path.join(DATA_DIR, "evolution_articles.png")
    fig.savefig(path, dpi=100)
    plt.clf()


def articles_by_section_dict(df):
    df_new = df.copy()
    df_new = df_new.sum(axis=0)
    dict = df_new.to_dict()
    # return sorted dictionary
    return {k: v for k, v in sorted(dict.items(), key=lambda item: item[1], reverse=True)}


def section_pie_chart(df, title):
    df_new = df.copy()
    s = df_new.sum(axis=0)
    articles_per_section = pd.DataFrame({'articles': s.values}, index=s.index)
    articles_per_section.plot.pie(y='articles', textprops={
                                  'fontsize': 5}, figsize=(15, 15))
    path = os.path.join(DATA_DIR, "pie_chart.pdf")
    plt.title(title)
    plt.savefig(path)
    plt.clf()


def histogram(df, title):
    df_new = df.copy()
    s = df_new.sum(axis=1)
    plt.hist(s.values)
    path = os.path.join(DATA_DIR, "histogram.pdf")
    plt.title(title)
    plt.savefig(path)
    plt.clf()


def autocorrelation(df, title):
    df_new = df.copy()
    s = df_new.sum(axis=1)
    pd.plotting.autocorrelation_plot(s)
    path = os.path.join(DATA_DIR, "autocorrelation.pdf")
    plt.title(title)
    plt.savefig(path)
    plt.clf()


def main():
    search_term = "trudeau"
    from_date = "2018-01-01"
    to_date = datetime.now().date().strftime("%Y-%m-%d")
    title = "Articles about '{name}' from {from_date} to {to_date}".format(
        name="Trudeau",
        from_date=from_date,
        to_date=to_date,
    )

    # generate dataframe with number of articles per section and date
    gs = GuardianSearch(search_term, from_date, to_date)
    df = gs.get_article_section_df()

    # Generate csv with number of articles per year
    generate_csv(df)

    # Total number of articles, average, and standard deviation
    print("Total number of articles: {0}".format(total_number(df)))
    print("Averge number of articles: {0}".format(mean(df)))
    print("Stardard deviation: {0}".format(std(df)))

    # Plot histogram
    histogram(df, title)

    # Articles by section
    print("Articles by Section:")
    for section, number in articles_by_section_dict(df).items():
        print("{section}: {number}".format(section=section, number=number))

    # Pie chart articles per section
    section_pie_chart(df, title)

    # Evolution of article count over time
    generate_evolution_series(df, title)

    # Unusual events
    generate_unusual_events_csv(df)

    # Histogram for article count
    histogram(df, title)

    # Autocorrelation diagram to detect seasonality
    autocorrelation(df, title)


if __name__ == "__main__":
    main()
