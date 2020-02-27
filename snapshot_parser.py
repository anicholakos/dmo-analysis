import scrapy
import os
import re
import json
import html2text
import lxml.etree
import lxml.html

from scrapy.linkextractors import LinkExtractor

# scrapy runspider dictionary_parser.py
# Global variable that stores all info in a nested dictionary for our JSON file
websites = { }

# Change the path to wherever the snapshots are located

# Windows Paths
# path = 'C:/Users/user/Documents/Projects/dmo-analysis/snapshots'
# allowed_domains = ["file:///C:/Users/user/Documents/Projects/dmo-analysis/snapshots"]
# start_urls.append('file:///' + os.path.join(subdir, file))
class ArchiveSpider(scrapy.Spider):
    path = '/home/snichola/Documents/projects/dmo-analysis/'
    name = "archive"
    allowed_domains = ["file:///home/snichola/Documents/projects/dmo-analysis/snapshots"]
    start_urls = []

    # Create a list of urls(or files in this case) to scrape
    for subdir, dirs, files in os.walk(path):
        for file in files:
            start_urls.append('file://home' + os.path.join(subdir, file))

    # Start parsing the start_urls
    # Regex to get current domain
    # Extract internal links first by only allowing the urls from domain
    # We make the assumption that DMOs won't link to each other
    # strip .html from certain snapshots to get the date
    def parse(self, response):
        date = response.url.replace('.html','').replace('.xml','')
        date = (date[len(date)-23:-15])
        year = date[:-4]
        month = date[4:-2]
        domain = (re.search("(?P<url>www[^%]+)", response.url).group("url"))

        internal = []
        extractor = LinkExtractor(allow_domains=domain[4:])
        links = extractor.extract_links(response)
        for link in links:
            internal.append(link.url)

        # Get external links next by denying the urls from domain
        external = []
        extractor = LinkExtractor(deny_domains=domain[4:])
        links = extractor.extract_links(response)
        for link in links:
            if "file://" not in link.url:
                external.append(link.url)

        # Get keywords from meta tags
        if response.xpath("//meta[@name='keywords']/@content"):
            keywords = response.xpath("//meta[@name='keywords']/@content")[0].extract()
        else:
            keywords = ''

         # Get description from meta tags
        if response.xpath("//meta[@name='description']/@content"):
            description = response.xpath("//meta[@name='description']/@content")[0].extract()
        else:
            description = ''

        # Get all the image names
        if response.xpath("//img/@src"):
            images = response.xpath("//img/@src").extract()
        else:
            images = []
        
        # Get the raw text and clean it
        root = lxml.html.fromstring(response.body)
        lxml.etree.strip_elements(root, lxml.etree.Comment, "script", "head")
        text = lxml.html.tostring(root, method="text", encoding="unicode").replace('\u00a0','').replace('\r','').replace('\n','').replace('\t','').replace('\u00bb','')
        state = state_of_site(domain)

        # Update key values in dictionary
        if year not in websites:
            websites[year] = {month: {domain: {'state': state, 'internal': internal, 'external': external, 'text': text, 'keywords': keywords, 'description': description, 'images': images}}} 
        else:
            if month not in websites[year]:
                websites[year].update({month: {domain: {'state': state, 'internal': internal, 'external': external, 'text': text, 'keywords': keywords, 'description': description, 'images': images}}})
            else:
                websites[year][month].update({domain: {'state': state, 'internal': internal, 'external': external, 'text': text, 'keywords': keywords, 'description': description, 'images': images}})

    # Dump dictionary to JSON file when spider is done running
    def closed( self, reason ):
        data = json.dumps(websites, indent=4, sort_keys=True)
        with open("websites.json","w") as f:
            f.write(data)      

# Determine the state from domain
def state_of_site(domain):
    if "state.al.us" in domain or "alabama" in domain:
        return "Alabama"
    elif "alaska" in domain:
        return "Alaska"
    elif "arizona" in domain:
        return "Arizona"
    elif "arkansas" in domain:
        return "Arkansas"
    elif "calif" in domain:
        return "California"
    elif "colorado" in domain:
        return "Colorado"
    elif ".ct" in domain:
        return "Connecticut"
    elif "state.de.us" in domain or "delaware" in domain:
        return "Delaware"
    elif "washington.org" in domain:
        return "District of Columbia"
    elif "flausa" in domain or "florida" in domain:
        return "Florida"
    elif "georgia" in domain:
        return "Georgia"
    elif "hawaii" in domain:
        return "Hawaii"
    elif "visitid.org" in domain or "idaho" in domain:
        return "Idaho"
    elif "illinois" in domain:
        return "Illinois"
    elif "state.in.us" in domain or "indiana" in domain:
        return "Indiana"
    elif "state.ia.us" in domain or "iowa" in domain:
        return "Iowa"
    elif "travelks" in domain or "kansas" in domain:
        return "Kansas"
    elif "state.ky" in domain or "kentucky" in domain:
        return "Kentucky"
    elif "louisiana" in domain:
        return "Louisiana"
    elif "maine" in domain:
        return "Maine"
    elif "mdisfun" in domain or "maryland" in domain:
        return "Maryland"
    elif "mass" in domain:
        return "Massachusetts"
    elif "michigan" in domain:
        return "Michigan"
    elif "minnesota" in domain:
        return "Minnesota"
    elif "decd.state.ms" in domain or "mississippi" in domain:
        return "Mississippi"
    elif "ecodev" in domain or "missouri" in domain or "visitmo" in domain:
        return "Missouri"
    elif "mt." in domain:
        return "Montana"
    elif ".ne." in domain or "nebraska" in domain:
        return "Nebraska"
    elif "nevada" in domain:
        return "Nevada"
    elif "nh" in domain:
        return "New Hampshire"
    elif "nj." in domain:
        return "New Jersey"
    elif "newmexico" in domain:
        return "New Mexico"
    elif "ny" in domain:
        return "New York"
    elif "visitnc" in domain:
        return "North Carolina"
    elif "ndtourism" in domain:
        return "North Dakota"
    elif ".oh" in domain or "ohio" in domain:
        return "Ohio"
    elif "travelok" in domain:
        return "Oklahoma"
    elif "oregon" in domain:
        return "Oregon"
    elif "pa." in domain:
        return "Pennsylvania"
    elif "rhodeisland" in domain:
        return "Rhode Island"
    elif "travelsc" in domain or "southcarolina" in domain:
        return "South Carolina"
    elif "sd" in domain or "southdakota" in domain:
        return "South Dakota"
    elif ".tn" in domain:
        return "Tennessee"
    elif "tex" in domain:
        return "Texas"
    elif "utah" in domain:
        return "Utah"
    elif "vermont" in domain:
        return "Vermont"
    elif "virginia" in domain:
        return "Virginia"
    elif "tourism.wa.gov" in domain or "experiencewashington" in domain or "experiencewa" in domain:
        return "Washington"
    elif "wv" in domain:
        return "West Virginia"
    elif "wi" in domain:
        return "Wisconsin"
    elif "wyoming" in domain:
        return "Wyoming"
    else:
        return "Not Found"


    
        
    

    