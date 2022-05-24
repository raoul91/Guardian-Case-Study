import pandas as pd
import requests
from datetime import datetime
from dataframe_processor import DataFrameProcessor


class GuardianSearch:
    def __init__(self, search_term, from_date, to_date):
        self.search_term = search_term
        self.from_date = from_date
        self.to_date = to_date

    def get_response(self, page=1):
        search_url = "https://content.guardianapis.com/search"
        params = {
            "q": self.search_term,
            "page": page,
            "from-date": self.from_date,
            "to-date": self.to_date,
            "api-key": "test",
        }
        r = requests.get(url=search_url, params=params)
        json = r.json()
        return json.get("response")

    def count_pages(self):
        response = self.get_response()
        return response.get("pages")

    def date_section_dict(self):
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
                    post_date = result.get("webPublicationDate").split("T")[0]
                    if date_section_dict.get((post_date, section)):
                        date_section_dict[(post_date, section)] += 1
                    else:
                        date_section_dict[(post_date, section)] = 1

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
        date_section_dict, sections = self.date_section_dict()
        df = self.initialize_zero_df(sections)

        for (date, section), count in date_section_dict.items():
            df.at[date, section] = count

        return df


def main():
    search_term = "trudeau"
    from_date = "2018-01-01"
    to_date = datetime.now().date().strftime("%Y-%m-%d")
    title = "Articles about '{search_term}' from {from_date} to {to_date}".format(
        search_term=search_term,
        from_date=from_date,
        to_date=to_date,
    )

    # Initialize search
    gs = GuardianSearch(
        search_term=[search_term],
        from_date=from_date,
        to_date=to_date
    )

    # Get dataframe with articles per date (rows) and section (columns)
    df = gs.get_article_section_df()

    # Initialize processor to create plots, statistics, etc.
    dfProcessor = DataFrameProcessor(df)

    # Total number of articles, average, and standard deviation
    print("Total number of articles: {0}".format(dfProcessor.total_number()))
    print("Averge number of articles: {0}".format(dfProcessor.mean()))
    print("Stardard deviation: {0}".format(dfProcessor.std()))

    # Articles by section
    print("Articles by Section:")
    for section, number in dfProcessor.articles_by_section_dict().items():
        print("{section}: {number}".format(section=section, number=number))

    # Pie chart
    dfProcessor.section_pie_chart(title)

    # Generate CSV with number of artibles per date
    dfProcessor.generate_csv()

    # Generate histogram
    dfProcessor.histogram(title)

    # Generate autocorrelation plot
    dfProcessor.autocorrelation(title)

    # Generate evolution plot
    dfProcessor.evolution_plot(title)

    # Get CSV with usual dates
    dfProcessor.generate_unusual_events_csv()

    # Zip all the files
    dfProcessor.zip("guardian_search_{0}.zip".format(to_date))


if __name__ == "__main__":
    main()
