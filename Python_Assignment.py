#!/usr/bin/env python
# coding: utf-8

# In[1]:


# Import the required libraries
import pandas as pd            # For data manipulation
from bs4 import BeautifulSoup  # For web scraping
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

# Set the path to the ChromeDriver executable
driver_path = 'E:\chromedriver_win32\chromedriver'

# Create a Service object
chrome_service = Service(executable_path=driver_path)

# Initialize the Chrome web driver with the Service object
driver = webdriver.Chrome(service=chrome_service)

# Create empty lists to store the data for this page
Product_URL, Product_Name, Product_Price, Rating, Number_of_Reviews = [],[],[],[],[]

# The output file after extraction
output_file = 'Products_details.csv'

base_url="https://www.amazon.in/s?k=bags&crid=2M096C61O4MLT&qid=1690105337&sprefix=ba%2Caps%2C283&ref=sr_pg_"

def getsubstring(text, specific_character):
    # Split the text at the specific character
    parts = text.split(specific_character)
    # Get the first part (substring) before the specific character
    substring = parts[0]
    return (substring)

def getLastSubstrings(text, from_stings):
    # Find the index of the specific character
    index = text.index(from_stings)
    # Get the substring from the specific character to the end of the string
    substring = text[index + 1:]
    return(substring)

def getUrl(base_url, page_number):
    url1 = getsubstring(base_url, 'crid')
    url2 = getLastSubstrings(base_url, "&crid")
    final_url = url1 + "page=" + str(page_number) + "&" + url2 + str(page_number)
    return final_url

# Function to scrape page data and save it to a CSV file
def scrape_page(url):
    # Open the URL in Chrome browser
    driver.get(url)
    # Get the page source
    html_content = driver.page_source

    # Create a BeautifulSoup object from the response text using the html.parser
    soup = BeautifulSoup(html_content, 'html.parser')

    # Extract data from the page using BeautifulSoup selectors or regular expressions
    for Soup in soup.find_all('div', class_='a-section a-spacing-small a-spacing-top-small'):
        
        #Extract Product URL
        url = Soup.find('a', class_='a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal')
        if url:
            url = url['href']
            link = url.split("?")[0]
            pro_link = "https://www.amazon.in/" + link
            Product_URL.append(pro_link)
        else:
            Product_URL.append("N/A")

        # Extract product name
        product_name = Soup.find('span', class_='a-size-medium a-color-base a-text-normal')
        if product_name is not None:
            Product_Name.append(product_name.text)
        else:
            product_name = Soup.find('a', class_='a-size-medium a-color-base a-text-normal') #span
            if product_name is not None:
                Product_Name.append(product_name.text)
            else:
                Product_Name.append("N/A")

        # Extract product price
        price = Soup.find('span', class_='a-offscreen')
        if price is not None:
            Product_Price.append(price.text)
        else:
            Product_Price.append("N/A")

        # Extract product rating
        rating = Soup.find('span', class_='a-icon-alt') 
        if rating is not None:
            rating=(rating.text).split(' ')[0]
            Rating.append(rating)
        else:
            Rating.append("N/A")

        # Extract total number of ratings for the product
        No_of_reviews = Soup.find('span', class_='a-size-base s-underline-text')  
        if No_of_reviews is not None:
            t_clean=((No_of_reviews.text).split(" "))[0]
            t_clean = t_clean.replace('(', '').replace(')', '')  # Remove parentheses
            Number_of_Reviews.append(t_clean)
        else:
            Number_of_Reviews.append("N/A")
            
    # Create a Pandas DataFrame with the lists and append it to the output file
    df = pd.DataFrame({'Product URL': Product_URL, 'Product Name': Product_Name, 'Product Price': Product_Price, "Ratings": Rating, "Number_of_Reviews": Number_of_Reviews})
    df.to_csv(output_file, index=False, encoding='utf-8')

max_pages=20

# Scrape each page in the range of page numbers
for n in range(1, max_pages + 1):
    url = getUrl(base_url, page_number=n)   
    print(url)
    # Save the data to a CSV file
    scrape_page(url)
print("Data has been successfully saved to", output_file)


# In[2]:


# Load the csv file into a pandas DataFrame
df = pd.read_csv(output_file)

# Extract the URL column into a list
url_list = df["Product URL"].tolist()

# Assuming url_list contains the list of URLs with 'nan' and 'https://www.amazon.in//sspa/click' links
url_list = [link for link in url_list if pd.notna(link) and link != 'https://www.amazon.in//sspa/click']

# Create an empty list to store the results for each product
results = []

# Iterate through each URL in the list and scrape product details
for url in url_list:
    # Check if the URL is NaN (missing)
    if pd.isnull(url):
        continue
    # Initialize the Chrome web driver with the Service object
    driver = webdriver.Chrome(service=chrome_service)
    print(url)
    # Open the URL in Chrome browser
    driver.get(url)

    # Get the page source
    html_content = driver.page_source

    # Create a BeautifulSoup object from the response text using the html.parser
    soup = BeautifulSoup(html_content, 'html.parser')

    # Extract the Product Description
    description_element = soup.find('div', class_='a-section launchpad-text-left-justify')
    if description_element:
        description = description_element.find('p')
        if description:
            description = description.get_text(strip=True)
        else:
            description = "N/A"
    else:
        description_element2 = soup.find('div', {'id': 'productDescription'})
        if description_element2:
            description = description_element2.get_text(strip=True)
        else:
            td_elements = soup.find_all('td', class_='apm-top')
            if td_elements:
                description_list = []
                for td in td_elements:
                    div_content = td.find('div', class_='apm-eventhirdcol apm-floatleft')
                    if div_content:
                        h4_tag = div_content.find('h4', class_='a-spacing-mini')
                        heading = h4_tag.get_text(strip=True) if h4_tag else "N/A"

                        p_tag = div_content.find('p')
                        paragraph = p_tag.get_text(strip=True) if p_tag else "N/A"

                        description_list.append(f"{heading}: {paragraph}")

                if description_list:
                    description = '  \n  '.join(description_list)
                else:
                    description = "N/A"
            else:
                description = "N/A"

    # Find the ASIN information by extracting it from the URL
    asin = url.split('/')[-2]

    # Extract product Description from the page
    product_description = soup.find('div', {'id': 'feature-bullets'})
    # Check if the product_description is found before processing
    if product_description is None:
        # If the element is not found, set Product_description to "N/A" and continue to the next URL
        Product_description = "N/A"
    else:
        # Extract and concatenate the product details from the list items
        product_details = []
        for li_tag in product_description.find_all('li'):
            product_detail = li_tag.get_text(strip=True)
            product_details.append(product_detail)
        Product_description = '  \n '.join(product_details)

    # Find the Manufacturer information
    product_details = soup.find('div', {'id': 'detailBullets_feature_div'})
    if product_details is None:
        product_details2 = soup.find('div', {'class': 'a-section table-padding'})
        if product_details2:
            for li_tag in product_details2.find_all('tr'):
                if "Manufacturer" in li_tag.get_text():
                    manufacturer = li_tag.find('th', class_='a-color-secondary a-size-base prodDetSectionEntry').find_next('td').get_text(strip=True)
                    break
                else:
                    # If the element is not found, set manufacturer to "N/A" and continue to the next URL
                    manufacturer = "N/A"
        else:
            manufacturer = "N/A"
    else:
        manufacturer = None
        for li_tag in product_details.find_all('li'):
            if "Manufacturer" in li_tag.get_text():
                manufacturer = li_tag.find('span', class_='a-text-bold').find_next('span').get_text(strip=True)
                break

    # Close the Chrome browser
    driver.quit()

    # Append the results for each iteration to the list
    results.append([description, asin, Product_description, manufacturer])

# Save the results list to a CSV file
output_csv_file = 'product_details_output.csv'
df_result = pd.DataFrame(results, columns=['Description', 'ASIN', 'Product Description', 'Manufacturer'])
df_result.to_csv(output_csv_file, index=False)

print("Data has been successfully saved to", output_csv_file)


# In[3]:


# Read the CSV file
df = pd.read_csv(output_csv_file)
# Set the display option to show the full link
pd.set_option('display.max_colwidth', None)
df

