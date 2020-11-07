import os
import sys
import csv
import time
from re import search, split
from datetime import datetime
from psaw import PushshiftAPI

print("Please enter the date range you'd like to scrape. The dates should be in the MM/DD/YYYY format.")

before = split("-|/| ", input("Scrape subreddit before: "))
after = split("-|/| ", input("Scrape subreddit after: "))
if len(before) == 1: before = [1, 2, 2020]
if len(after) == 1: after = [1, 1, 2020]

api = PushshiftAPI()

class Subreddit:
    def __init__(self, sub):
        self.sub = sub
        if not os.path.exists('output'):
            os.makedirs('output')
        
    def get_row(self, row, row_fields):
                cols = []
                formatText = ["title", "selftext", "body"]
                for field in row_fields:
                    try:
                        if field == "created":
                            date = datetime.fromtimestamp(row.d_[field])
                            cols.append(date.ctime())
                        else:
                            field_data = row.d_[field]
                            if field in formatText:
                                cols.append(field_data.replace('\r', ' ').replace(
                                    '\n', ' '))
                            else:
                                cols.append(field_data)
                    except:
                        cols.append("")
                return cols

    def scrape(self):
        subreddit = self.sub
        m_after = int(after[0])
        d_after = int(after[1])
        y_after = int(after[2])
        m_before = int(before[0])
        d_before = int(before[1])
        y_before = int(before[2])
        
        with open("output/reddit_" + str(before[2]) + "_" + subreddit + ".csv", 'wt', newline='', encoding='utf-8') as output_file:
                fields = ("subreddit", "created", "created_utc", "title", "img")
                output = csv.writer(output_file)
                output.writerow([*fields, "text", "url", "type"])
                afterDate = int(datetime(y_after, m_after, d_after).timestamp())
                beforeDate = int(datetime(y_before, m_before, d_before).timestamp())
                posts = []
                posts_fields = [*fields, "selftext", "url"]
                
                try:
                    submission_gen = api.search_submissions(
                        after=afterDate,
                        before=beforeDate,
                        subreddit=subreddit,
                        filter=posts_fields
                    )
                    
                    for g in submission_gen:
                        posts.append([*self.get_row(g, posts_fields), "submission"])
                    for post in posts:
                        output.writerow(post)
                        
                except Exception as err: 
                    print(err)

if not sys.argv:
    print("Please enter which subreddits you'd like scraped")
    subs = split(",|, |;| ",input("Scrape subreddit after: "))
else: subs = sys.argv

i = 1
while i < len(subs):
    print("Scraping r/" + subs[i])
    S = Subreddit(subs[i])
    S.scrape()
    i += 1
