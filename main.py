import json

import requests
from bs4 import BeautifulSoup


def format_author_name(author_name):
    # Replace spaces with hyphens
    formatted_name = author_name.replace(" ", "-")
    # Replace single quotes with nothing
    formatted_name = formatted_name.replace("'", "")
    # Replace periods with hyphens (except if it's at the end of the name)
    if formatted_name.endswith("."):
        formatted_name = formatted_name[:-1]  # Remove the dot
    else:
        formatted_name = formatted_name.replace(".", "-")

    return formatted_name


# Function to scrape quotes and authors from the website
def scrape_quotes_and_authors():
    url = "http://quotes.toscrape.com"
    quotes = []
    authors = []

    page = 1
    while True:
        # Send a GET request to the current page
        response = requests.get(f"{url}/page/{page}")
        # Parse the HTML content
        soup = BeautifulSoup(response.content, "html.parser")

        # Find all quote containers
        quote_containers = soup.find_all("div", class_="quote")

        # Iterate over each quote container
        for container in quote_containers:
            quote_text = container.find("span", class_="text").text
            author_name = container.find("small", class_="author").text
            tags = [tag.text for tag in container.find_all("a", class_="tag")]

            # Add quote to the list of quotes
            quotes.append({"quote": quote_text, "author": author_name, "tags": tags})

            # Check if author already exists
            if author_name not in [author["fullname"] for author in authors]:
                # If not, scrape author details
                author_url = f"{url}/author/{format_author_name(author_name)}"
                author_response = requests.get(author_url)
                author_soup = BeautifulSoup(author_response.content, "html.parser")

                # Extract author details
                born_date = author_soup.find("span", class_="author-born-date").text
                born_location = author_soup.find(
                    "span", class_="author-born-location"
                ).text
                description = author_soup.find(
                    "div", class_="author-description"
                ).text.strip()

                # Add author to the list of authors
                authors.append(
                    {
                        "fullname": author_name,
                        "born_date": born_date,
                        "born_location": born_location,
                        "description": description,
                    }
                )

        # Check if there's a next page
        next_page = soup.find("li", class_="next")
        if next_page is None:
            break  # Exit loop if there's no next page
        else:
            page += 1  # Move to the next page

    return quotes, authors


# Function to save data into JSON files
def save_data_to_json(quotes, authors):
    with open("quotes.json", "w") as quotes_file:
        json.dump(quotes, quotes_file, indent=4)

    with open("authors.json", "w") as authors_file:
        json.dump(authors, authors_file, indent=4)


# Main function to execute scraping and saving
def main():
    quotes, authors = scrape_quotes_and_authors()
    save_data_to_json(quotes, authors)


if __name__ == "__main__":
    main()
