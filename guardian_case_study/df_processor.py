import os
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
from zipfile import ZipFile

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = os.path.join(BASE_DIR, "data")


class DataFrameProcessor:
    def __init__(self, df):
        self.df = df
        self.files = []

    def generate_articles_csv(self):
        df_new = self.df.copy()
        s = df_new.sum(axis=1)
        total_df = pd.DataFrame(
            {"Total No. of Articles": s.values}, index=s.index)
        total_df.index.name = "date"
        path = os.path.join(DATA_DIR, "number_of_articles.csv")
        total_df.to_csv(path, sep=";")
        self.files.append(path)

    def total_number(self):
        df_new = self.df.copy()
        s = df_new.sum(axis=1)
        return s.sum()

    def mean(self):
        df_new = self.df.copy()
        s = df_new.sum(axis=1)
        return s.mean()

    def std(self):
        df_new = self.df.copy()
        s = df_new.sum(axis=1)
        return s.std()

    def generate_csv(self):
        df_new = self.df.copy()
        s = df_new.sum(axis=1)
        total_df = pd.DataFrame(
            {"Total No. Articles": s.values}, index=s.index)
        path = os.path.join(DATA_DIR, "number_of_articles.csv")
        total_df.to_csv(path, sep=";")
        self.files.append(path)

    def generate_unusual_events_csv(self):
        df_new = self.df.copy()
        df_new["total"] = df_new.sum(axis=1)
        m = self.mean()
        sd = self.std()
        df_new = df_new[abs(df_new["total"]-m) >= 3*sd]
        # TODO: sort by number of events
        path = os.path.join(DATA_DIR, "unusual_events.csv")
        df_new.to_csv(path, sep=";")
        self.files.append(path)

    def generate_evolution_series(self, title):
        df_new = self.df.copy()
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
        self.files.append(path)

    def articles_by_section_dict(self):
        df_new = self.df.copy()
        df_new = df_new.sum(axis=0)
        dict = df_new.to_dict()
        # return sorted dictionary
        return {k: v for k, v in sorted(dict.items(), key=lambda item: item[1], reverse=True)}

    def section_pie_chart(self, title):
        df_new = self.df.copy()
        s = df_new.sum(axis=0)
        articles_per_section = pd.DataFrame(
            {'articles': s.values}, index=s.index)
        articles_per_section.plot.pie(y='articles', textprops={
            'fontsize': 5}, figsize=(15, 15))
        path = os.path.join(DATA_DIR, "pie_chart.pdf")
        plt.title(title)
        plt.savefig(path)
        plt.clf()
        self.files.append(path)

    def histogram(self, title):
        df_new = self.df.copy()
        s = df_new.sum(axis=1)
        plt.hist(s.values)
        path = os.path.join(DATA_DIR, "histogram.pdf")
        plt.title(title)
        plt.savefig(path)
        plt.clf()
        self.files.append(path)

    def autocorrelation(self, title):
        df_new = self.df.copy()
        s = df_new.sum(axis=1)
        pd.plotting.autocorrelation_plot(s)
        path = os.path.join(DATA_DIR, "autocorrelation.pdf")
        plt.title(title)
        plt.savefig(path)
        plt.clf()
        self.files.append(path)

    def zip(self, file_name):
        zip_path = os.path.join(DATA_DIR, file_name)
        zip = ZipFile(zip_path, 'w')
        for file_path in self.files:
            zip.write(file_path, os.path.basename(file_path))

        zip.close()
