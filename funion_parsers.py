from bs4 import BeautifulSoup
import PyPDF2
from io import BytesIO

def extract_text_from_pdf(pdf_content):
    """ Extract text from PDF """
    with BytesIO(pdf_content) as f:
        reader = PyPDF2.PdfReader(f)
        return ''.join(p.extract_text() for p in reader.pages)

def scrape_uk(html):
    """ Special scraper for UK speeches """
    soup = BeautifulSoup(html, 'html.parser')
    content = soup.find("div", class_="govspeak") or soup
    return ' '.join(p.get_text(strip=True) for p in content.find_all('p'))
