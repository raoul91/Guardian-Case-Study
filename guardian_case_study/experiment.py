import os
from re import A
from turtle import st
from numpy import zeros
import pandas as pd
import requests
from urllib import response
from datetime import datetime, timedelta
from pathlib import Path
import matplotlib.pyplot as plt
import statistics
import numpy as np


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


def generate_unusual_events_csv(df, mean, std):
    df_new = df.copy()
    df_new["total"] = df_new.sum(axis=1)
    df_new = df_new[abs(df_new["total"]-mean) >= 3*std]
    # TODO: sort by number of events
    path = os.path.join(DATA_DIR, "unusual.csv")
    df_new.to_csv(path, sep=";")


def generate_evolution_series(df):
    df_new = df.copy()
    df_new["total"] = df_new.sum(axis=1)
    plt.plot(df_new.index, df_new['total'], lw=1, color='red')
    plt.xlabel("date")
    plt.ylabel("number of articles")
    plt.xticks(rotation=45)
    fig = plt.gcf()
    fig.set_size_inches(10, 10)
    plot_output_path = os.path.join(DATA_DIR, "number_of_articles.png")
    fig.savefig(plot_output_path, dpi=100)
    plt.clf()


def articles_by_section_dict(df):
    df_new = df.copy()
    df_new = df_new.sum(axis=0)
    dict = df_new.to_dict()
    return dict


def section_pie_chart(df):
    # TODO: need to make this differently
    df_new = df.copy()
    df_new = df_new.sum(axis=0)

    """
    title = "Articles Trudeau per Section"
    df_newer = pd.DataFrame({"section": df_new.index, title: df_new.values})
    pie = df_newer.groupby(['section']).sum().plot(kind='pie', y=title)
    fig = pie.get_figure()
    path = os.path.join(DATA_DIR, "sections_pie_chart.pdf")
    fig.savefig(path)    
    """

    df = pd.DataFrame({'mass': [0.330, 4.87, 5.97], 'radius': [
                      2439.7, 6051.8, 6378.1]}, index=['Mercury', 'Venus', 'Earth'])
    plot = df.plot.pie(y='mass', figsize=(5, 5))
    path = os.path.join(DATA_DIR, "pie_chart.pdf")
    plt.savefig(path)
    plt.clf()


def hist(df):
    df_new = df.copy()
    s = df_new.sum(axis=1)
    plt.hist(s.values)
    path = os.path.join(DATA_DIR, "histogram.pdf")
    plt.savefig(path)
    plt.clf()


def autocorrelation(df):
    df_new = df.copy()
    s = df_new.sum(axis=1)
    x = pd.plotting.autocorrelation_plot(s)
    path = os.path.join(DATA_DIR, "autocorrelation.pdf")
    plt.savefig(path)
    plt.clf()


def main():
    today = datetime.now().date()
    today_str = today.strftime("%Y-%m-%d")

    # generate dataframe with number of articles per section and date
    guardian_search = GuardianSearch(["trudeau"], "2022-01-20", today_str)
    df = guardian_search.get_article_section_df()

    print("Sum = {0}".format(total_number(df)))
    print(mean(df))
    print(std(df))

    # hist(df)
    section_pie_chart(df)
    generate_evolution_series(df)
    hist(df)
    autocorrelation(df)


if __name__ == "__main__":
    main()
