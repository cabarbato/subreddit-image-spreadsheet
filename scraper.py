import os
import sys
import time
import requests
from re import search, split
from datetime import datetime
import xlsxwriter
from PIL import Image
from psaw import PushshiftAPI

print("Please enter the date range you'd like to scrape. The dates should be in the MM/DD/YYYY format.")

before = split("-|/| ", input("Scrape subreddit before: "))
after = split("-|/| ", input("Scrape subreddit after: "))
if len(before) != 3:
    before = [1, 2, 2020]
if len(after) != 3:
    after = [1, 1, 2020]

api = PushshiftAPI()

root_urls = ("i.redd.it/", "imgur.com/")
file_formats = (".jpg", ".jpeg", ".png")

class Subreddit:
    def __init__(self, sub):
        self.sub = sub
        self.data = []
        self.fields = ("subreddit", "created", "created_utc",
                       "title", "url", "image")
        self.output_dir = sub + "/"
        self.images_dir = self.output_dir + "images"
        if not os.path.exists(self.images_dir):
            os.makedirs(self.images_dir)
        self.image_files = os.listdir(self.images_dir)
        self.workbook = xlsxwriter.Workbook(self.output_dir + 'data.xlsx')
        self.worksheet = self.workbook.add_worksheet()
        self.worksheet.set_default_row(75)
        self.worksheet.set_default_row(300)

    def addRow(self, data, url):
        # Collect post data and image for each row to write to spreadsheet
        cols = []
        for field in self.fields:
            try:
                if field == "created":
                    date = datetime.fromtimestamp(data.d_[field])
                    cols.append(date.ctime())
                elif field == "image":
                    cols.append(self.downloadImage(url))
                else:
                    cols.append(data.d_[field])
            except:
                cols.append("")
        self.writeToXlsx(cols)

    def downloadImage(self, url):
        for root_url in root_urls:
            file = url.replace(root_url, '')
        try:
            image = requests.get(file, allow_redirects=False)
            if(image.status_code == 200):
                try:
                    output_filehandle = open(
                        self.images_dir + file, mode='bx')
                    output_filehandle.write(image.content)
                    self.resizeImage(file)
                except:
                    print('downloading ' + file + ' failed!')
                    pass
        except: print('Could not reach url')

    def getImgPost(self, row):
        # Only get rows with a url that's an image.
        this_url = row.d_["url"]
        for root_url in root_urls:
            if root_url in this_url:
                if root_url == "imgur.com/":
                    this_url == this_url + ".jpeg"
                for file_format in file_formats:
                    if this_url.endswith(file_format):
                        self.addRow(row, this_url)
                        break

    def resizeImage(self, file):
        # Resize the image using Pillow, a fork of the Python Imaging Libary.
        basewidth = 400
        try:
            img = Image.open(self.images_dir + file)
            wpercent = (basewidth/float(img.size[0]))
            hsize = int((float(img.size[1])*float(wpercent)))
            img = img.resize((basewidth, hsize), Image.ANTIALIAS)
            img.save(self.images_dir + file)
        except Exception as err:
            print(err)

    def scrape(self):
        # Use psaw, a wrapper for the pushshift.io API (which makes it much easier to choose a date range for reddit scrapes), to scrape reddit with the submitted parameters.
        afterDate = int(datetime(
            int(after[2]),
            int(after[0]),
            int(after[1]))
            .timestamp())
        beforeDate = int(datetime(
            int(before[2]),
            int(before[0]),
            int(before[1]))
            .timestamp())

        try:
            submission_gen = api.search_submissions(
                after=afterDate,
                before=beforeDate,
                subreddit=self.sub,
                filter=self.fields
            )

            for g in submission_gen:
                self.getImgPost(g)

        except Exception as err:
            print(err)
            
    def writeToXlsx(self, columns):
        # This is the method that actually writes everything to an .xlsx file
        return


if not sys.argv:
    print("Please enter which subreddits you'd like scraped")
    subs = split(",|, |;| ", input("Scrape subreddit after: "))
    i = 0
else:
    subs = sys.argv
    i = 1

while i < len(subs):
    print("Scraping r/" + subs[i])
    S = Subreddit(subs[i])
    S.scrape()
    i += 1
