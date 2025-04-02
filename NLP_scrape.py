

import os
import requests
from bs4 import BeautifulSoup
import PyPDF2
from io import BytesIO
import cloudscraper

# Create folder
output_folder = "speech_transcripts"
os.makedirs(output_folder, exist_ok=True)

def save_transcript(text, filename):
    with open(os.path.join(output_folder, filename), "w", encoding="utf-8") as f:
        f.write(text)

def extract_text_from_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    return ' '.join([p.get_text(strip=True) for p in soup.find_all('p')])

def extract_text_from_pdf(pdf_content):
    with BytesIO(pdf_content) as f:
        reader = PyPDF2.PdfReader(f)
        return ''.join(p.extract_text() for p in reader.pages)

def scrape_bc(html):
    soup = BeautifulSoup(html, 'html.parser')
    content = soup.find("div", class_="content-body") or soup
    return ' '.join(p.get_text(strip=True) for p in content.find_all('p'))

def scrape_uk(html):
    soup = BeautifulSoup(html, 'html.parser')
    content = soup.find("div", class_="govspeak") or soup
    return ' '.join(p.get_text(strip=True) for p in content.find_all('p'))


def fetch_and_save(url, filename, special=None, is_pdf=False):
    try:
        if is_pdf:
            r = requests.get(url)
            r.raise_for_status()
            transcript = extract_text_from_pdf(r.content)
        elif special:
            r = requests.get(url)
            r.raise_for_status()
            transcript = special(r.content) if callable(special) else special(url)
        else:
            r = requests.get(url)
            r.raise_for_status()
            transcript = extract_text_from_html(r.content)
        save_transcript(transcript, filename)
        print(f"✅ Saved: {filename}")
    except Exception as e:
        print(f"❌ Failed: {filename} — {e}")
        
        


# List of speeches
speeches = [
    # Working general scrapers
    ("https://www.presidency.ucsb.edu/documents/address-before-joint-session-the-congress-4", "usa_congress.txt"),
    ("https://presidentofindia.nic.in/speeches/address-honble-president-india-smt-droupadi-murmu-parliament-1", "india_president.txt"),
    ("https://www.scoop.co.nz/stories/PA2501/S00058/pms-speech-state-of-the-nation-2025.htm", "new_zealand_speech.txt"),
    ("https://www.stateofthenation.gov.za/assets/downloads/SONA_2025_Speech.pdf", "south_africa_sona_2025.txt", None, True),
    ("https://www.fiannafail.ie/news/speech-by-taoiseach-micheál-martin-on-the-announcement-of-members-of-government", "ireland_taoiseach.txt"),
    ("https://opm.gov.bs/prime-minister-davis-national-address-building-more-affordable-bahamas/", "bahamas_national_address.txt"),

    # Specialized
    ("https://lims.leg.bc.ca/pdms/file/ldp/43rd1st/43rd1st-throne-speech.pdf", "canada_bc.txt", None, True),
    ("https://www.gov.uk/government/speeches/the-kings-speech-2024", "uk_kings_speech.txt", scrape_uk)
]

for s in speeches:
    url = s[0]
    filename = s[1]
    special = s[2] if len(s) > 2 else None
    is_pdf = s[3] if len(s) > 3 else False
    fetch_and_save(url, filename, special, is_pdf)
