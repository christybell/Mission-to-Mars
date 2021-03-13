# Import Splinter, BeautifulSoup, and Pandas
from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd
import datetime as dt
import random
import time

def scrape_all():
    # Initiate headless driver for deployment
    executable_path = {'executable_path': r'C:\Users\bellc\Downloads\chromedriver.exe'}
    browser = Browser('chrome', **executable_path, headless=True)

    news_title, news_paragraph = mars_news(browser)
    hemisphere_image_urls = mars_hemispheres(browser)

    # Run all scraping functions and store results in a dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now(),
        "hemispheres": hemisphere_image_urls
    }

    # Stop webdriver and return data
    browser.quit()
    return data

def mars_news(browser):

    # Scrape Mars News
    # Visit the mars nasa news site
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=2)

    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one("ul.item_list li.slide")
        # Use the parent element to find the first 'a' tag and save it as 'news_title'
        news_title = slide_elem.find("div", class_="content_title").get_text()
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find("div", class_="article_teaser_body").get_text()

    except AttributeError:
        return None, None

    return news_title, news_p

# ## JPL Space Images Featured Image

def featured_image(browser):
    # Visit URL
    url = 'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/index.html'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')

    except AttributeError:
        return None

    # Use the base url to create an absolute url
    img_url = f'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/{img_url_rel}'

    return img_url

# ## Mars Facts

def mars_facts():

    # Add try/except for error handling
    try:
        # Use 'read_html' to scrape the facts table into a dataframe
        df = pd.read_html('http://space-facts.com/mars/')[0]

    except BaseException:
        return None

    # Assign columns and set index of dataframe
    df.columns=['Description', 'Mars']
    df.set_index('Description', inplace=True)

    # Convert dataframe into HTML format, add bootstrap
    return df.to_html(classes="table table-striped")

def mars_hemispheres(browser):
    # Visit URL 
    url = 'https://data-class-mars-hemispheres.s3.amazonaws.com/Mars_Hemispheres/index.html'
    browser.visit(url)
    
    # Parse HTML with soup
    html_hemispheres = browser.html
    hemisphere_soup = soup(html_hemispheres, 'html.parser')

    # Scrape items that contain mars hemisphere info
    hemispheres = hemisphere_soup.find_all('div', class_='item')

    # Create a list to hold hemisphere images and titles.
    hemisphere_image_urls = []

    # Store main URL
    hemispheres_url = 'https://data-class-mars-hemispheres.s3.amazonaws.com/Mars_Hemispheres/'

    # Loop through list of all hemisphere info to retrieve image urls and titles
    for x in hemispheres:
        # Add wait time to avoid time out or website access restrictions
        rand_num = random.randint(3,8)
        time.sleep(rand_num)

        # Store title
        title = x.find('h3').text
    
        # Store link that takes you to full image jpg
        ending_img_url = x.find('a', class_='itemLink product-item')['href']
    
        # Visit website link for full image
        browser.visit(hemispheres_url + ending_img_url)
    
        # Parse HTML with soup
        img_html = browser.html
        img_soup = soup(img_html, 'html.parser')
    
        # Create full image URL
        img_url = hemispheres_url + img_soup.find('img', class_='wide-image')['src']
    
        # Append retrieved info to a list of dictionaries
        hemisphere_image_urls.append({'img_url' : img_url, 'title' : title})

    # Stop webdriver and return data
    browser.quit()
    return hemisphere_image_urls

if __name__ == "__main__":

    # If running as script, print scraped data
    print(scrape_all())