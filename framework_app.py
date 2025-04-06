from funion_class import Funion
import funion_parsers as fp
import pprint as pp

def main():
    fun = Funion()

    # Scrape and save speech transcripts
    fun.load_text("https://www.presidency.ucsb.edu/documents/address-before-joint-session-the-congress-4",
                  "usa_congress.txt", label="USA Congress")

    fun.load_text("https://presidentofindia.nic.in/speeches/address-honble-president-india-smt-droupadi-murmu-parliament-1",
                  "india_president.txt", label="India President")

    fun.load_text("https://www.scoop.co.nz/stories/PA2501/S00058/pms-speech-state-of-the-nation-2025.htm",
                  "new_zealand_speech.txt", label="New Zealand PM")

    fun.load_text("https://www.stateofthenation.gov.za/assets/downloads/SONA_2025_Speech.pdf",
                  "south_africa_sona_2025.txt", label="South Africa SONA", parser=fp.extract_text_from_pdf)

    fun.load_text("https://www.fiannafail.ie/news/speech-by-taoiseach-micheál-martin-on-the-announcement-of-members-of-government",
                  "ireland_taoiseach.txt", label="Ireland Taoiseach")

    fun.load_text("https://opm.gov.bs/prime-minister-davis-national-address-building-more-affordable-bahamas/",
                  "bahamas_national_address.txt", label="Bahamas National Address")

    fun.load_text("https://lims.leg.bc.ca/pdms/file/ldp/43rd1st/43rd1st-throne-speech.pdf",
                  "canada_bc.txt", label="Canada BC Throne Speech", parser=fp.extract_text_from_pdf)

    fun.load_text("https://www.gov.uk/government/speeches/the-kings-speech-2024",
                  "uk_kings_speech.txt", label="UK King's Speech", parser=fp.scrape_uk)

    # Optional: print collected data
    pp.pprint(fun.data)

    # Generate comparative visualization
    fun.plot_summary()

if __name__ == "__main__":
    main()
