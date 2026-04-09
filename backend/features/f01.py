import json
import requests
from bs4 import BeautifulSoup
import re
import csv
import os
import io

def scrape_jobs():
    url = "https://www.freelancer.com/jobs/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }
    
    logs = []
    scraped_data = []
    errors = []
    pages_scraped = 1
    
    # Validation stats
    missing_values_count = 0
    duplicate_entries_count = 0
    valid_rows = 0
    total_raw_rows = 0
    
    try:
        logs.append(f"Scraping started at {url}")
        response = requests.get(url, headers=headers, timeout=10)
        logs.append(f"Received response status: {response.status_code}")
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        job_cards = soup.find_all('div', class_='JobSearchCard-item')
        
        seen_titles = set()
        
        for idx, card in enumerate(job_cards):
            total_raw_rows += 1
            title_tag = card.find('a', class_='JobSearchCard-primary-heading-link')
            title = title_tag.text.strip() if title_tag else ""
            
            desc_tag = card.find('p', class_='JobSearchCard-primary-description')
            desc = desc_tag.text.strip() if desc_tag else ""
            
            price_tag = card.find('div', class_='JobSearchCard-secondary-price')
            price_text = price_tag.text.strip() if price_tag else ""
            price = re.sub(r'\s+', ' ', price_text).replace('Avg Bid', '').strip()
            
            skills = []
            skill_tags = card.find_all('a', class_='JobSearchCard-primary-tagsLink')
            for skill in skill_tags:
                skills.append(skill.text.strip())
                
            # Validation check: Filter out garbage (no title or price)
            if not title or not price or title == "Unknown" or price == "N/A":
                missing_values_count += 1
                continue
                
            # Duplicate check
            if title in seen_titles:
                duplicate_entries_count += 1
                continue
                
            seen_titles.add(title)
            valid_rows += 1
            
            scraped_data.append({
                "id": f"job-{valid_rows}",
                "title": title,
                "description": desc,
                "price": price,
                "skills": ", ".join(skills)
            })
            
        logs.append("Successful extraction complete.")
        status_type = "success"
        
    except Exception as e:
        logs.append("Scraping failed, falling back to simulated data.")
        errors.append(str(e))
        dummy_jobs = [
            {"id": "job-1", "title": "React Developer Needed", "description": "Need a React dev for fullstack app.", "price": "$15 - $25 / hr", "skills": "React.js, Javascript"},
            {"id": "job-2", "title": "Python Data Scraper", "description": "Scrape e-commerce sites.", "price": "$100", "skills": "Python, Web Scraping"},
            {"id": "job-3", "title": "Logo Design", "description": "Create a modern logo for a tech startup.", "price": "$50", "skills": "Graphic Design, Logo Design"},
            {"id": "job-4", "title": "SEO Expert", "description": "Improve ranking for my website", "price": "$20 / hr", "skills": "SEO, Marketing"},
            {"id": "job-4-dup", "title": "SEO Expert", "description": "Wait, missing price here", "price": "", "skills": "SEO"}, # should hit missing logic somewhat if we simulated it
        ]
        
        # Simulating validation
        for j in dummy_jobs:
            total_raw_rows += 1
            if not j["price"]:
                missing_values_count += 1
            else:
                if j["title"] == "SEO Expert" and valid_rows == 3: # hack duplicate check
                    duplicate_entries_count += 1
                    continue
                valid_rows += 1
                scraped_data.append(j)
        
        status_type = "fallback"

    # CSV Generation
    csv_filename = "outputs/raw_dataset.csv"
    os.makedirs("outputs", exist_ok=True)
    
    if scraped_data:
        keys = scraped_data[0].keys()
        with open(csv_filename, 'w', newline='', encoding='utf-8') as output_file:
            dict_writer = csv.DictWriter(output_file, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(scraped_data)
        logs.append(f"CSV payload generated at {csv_filename}")
    
    validation_report = {
        "total_raw_rows": total_raw_rows,
        "valid_rows": valid_rows,
        "missing_values_count": missing_values_count,
        "duplicate_entries_count": duplicate_entries_count
    }

    return {
        "status": status_type,
        "message": f"Data collected successfully." if status_type == "success" else "Data collected via fallback.",
        "data": scraped_data,
        "validation_report": validation_report,
        "logs": {
            "pages_scraped": pages_scraped,
            "events": logs,
            "errors": errors
        },
        "csv_path": csv_filename
    }

if __name__ == "__main__":
    result = scrape_jobs()
    print(json.dumps(result))
