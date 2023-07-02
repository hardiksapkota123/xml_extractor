import requests
from bs4 import BeautifulSoup
import re
import streamlit as st
import base64
from urllib.parse import urlparse

def extract_xml_content(url):
    # Fetch the XML content from the website
    response = requests.get(url)
    xml_content = response.content

    # Create a BeautifulSoup object to parse the XML
    soup = BeautifulSoup(xml_content, "xml")

    # Extract the information from the XML
    items = soup.find_all("item")

    extracted_data = []
    for item in items:
        title = item.find("title").get_text(strip=True)

        # Some websites use "dc:creator" and others use "creator" tag
        creator_tag = item.find("dc:creator")
        if creator_tag:
            creator = creator_tag.get_text(strip=True)
        else:
            creator = item.find("creator").get_text(strip=True)

        pub_date = item.find("pubDate").get_text(strip=True)

        # Extract content and remove HTML tags
        content = item.find("content:encoded").get_text(strip=True)
        content = re.sub("<.*?>", "", content)

        # Remove unwanted text
        content = re.sub(r"\[CDATA\[(.*?)\]\]", "", content)
        content = re.sub(r"\[.*?\]", "", content)
        content = re.sub(r"\nThe post .* appeared first on .*.", "", content)

        extracted_data.append({
            "Title": title,
            "Creator": creator,
            "Published Date": pub_date,
            "Content": content.strip()
        })

    return extracted_data


def get_filename(url):
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    return f"{domain}.txt"


@st.cache_data
def download_file(url, item):
    output_text = ""
    output_text += f"Title: {item['Title']}\n"
    output_text += f"Creator: {item['Creator']}\n"
    output_text += f"Published Date: {item['Published Date']}\n"
    output_text += f"Content: {item['Content']}\n\n"

    return output_text


# Streamlit web app
def main():
    st.title("XML Content Extractor")
    st.write("Enter the URLs of the XML feeds:")

    url_input = st.text_area("URLs", height=50)

    if st.button("Extract"):
        urls = url_input.split("\n")
        extracted_data = []

        for url in urls:
            extracted_data.extend(extract_xml_content(url.strip()))

        st.success("Extraction completed.")

        # Use a counter to keep track of the current item index
        counter = 0
        for url in urls:
            # Get the number of items for this URL
            num_items = len(extract_xml_content(url.strip()))
            # Loop over the items that belong to this URL
            for i in range(num_items):
                # Get the item from the extracted data using the counter
                item = extracted_data[counter]
                output_text = download_file(url, item)
                st.text(output_text)
                href = f'<a href="data:file/txt;base64,{base64.b64encode(output_text.encode()).decode()}" download="{get_filename(url)}">Download {get_filename(url)}</a>'
                st.markdown(href, unsafe_allow_html=True)
                # Increment the counter by one
                counter += 1

    st.markdown("---")
    st.write("Made with ❤️ by Hardik")


if __name__ == "__main__":
    main()
