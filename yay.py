import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urljoin, urlparse
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.support.ui import WebDriverWait
import requests
from bs4 import BeautifulSoup



import os 
import json

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.binary_location = '/usr/bin/chromium-browser'


# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")

# Set up the Chrome driver using webdriver_manager
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)
wait = WebDriverWait(driver, 100)  # Add explicit wait


def get_character_id(character_name):
    
    try:
        url = f'https://www.personality-database.com/search?keyword={character_name.replace(" ", "%20")}'
        print(url)
        #driver.get(url)
        
        # Use explicit wait instead of implicit wait
        links = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "profile-card-link")))
        print(links)
        if not links:
            print(f"No results found for '{character_name}'")
            return None
            
        target = []
        first_name = character_name.split(" ")[0].lower()
        
        for item in links:
            html_content = item.get_attribute('outerHTML')
            soup = BeautifulSoup(html_content, 'html.parser')
            profile_link = soup.find('a', class_='profile-card-link')['href']
            print(f"Found profile link: {profile_link}")
            
            if first_name in profile_link.lower():
                profile_number = profile_link.split('/')[2]
                target.append(profile_number)
        
        if not target:
            print(f"No matching profiles found for '{character_name}'")
            return None
            
        return target[0]
        
    except Exception as e:
        print(f"Error while searching for '{character_name}': {str(e)}")
        return None

def get_character_info(id, character_name):
    """
    Get detailed character information from personality-database API.
    """
    if id is None:
        print("No valid ID provided")
        return None
        
    try:
        url = f"https://api.personality-database.com/api/v1/profile/{id}"
        response = requests.get(url)
        response.raise_for_status()
        json_data = response.json()
        
        result = {
            "character": json_data.get("mbti_profile"),
            "source": json_data.get("subcategory"),
            "description": json_data.get("wiki_description"),
            "personality summary": json_data.get("personality_type"),
            "watch": json_data.get("watch_count")
        }
        
        ph = {
            "function": json_data.get("functions", []),
            "MBTI": {}
        }
        
        mbti_letter = json_data.get("mbti_letter_stats", [])
        if mbti_letter:
            for letter in mbti_letter[:4]:
                ph["MBTI"][letter["type"]] = letter["PercentageFloat"]
                
        result["personality highlights"] = ph
        
        total = {}
        temp = {}
        result["personality details"] = {}
        
        systems = json_data.get("systems", [])
        for item in systems:
            system_id = item["id"]
            total[system_id] = item["system_vote_count"]
            temp[system_id] = item["system_name"]
        
        breakdown_systems = json_data.get("breakdown_systems", {})
        for system_id in temp:
            if str(system_id) in breakdown_systems:
                personality_counts = {}
                for item in breakdown_systems[str(system_id)]:
                    personality_counts[item["personality_type"]] = item["theCount"]
                result["personality details"][temp[system_id]] = personality_counts
        
        os.makedirs("characters", exist_ok=True)
        
        file_path = f"characters/{character_name.replace(' ', '')}.json"
        with open(file_path, 'w', encoding="utf-8") as json_file:
            json.dump(result, json_file, ensure_ascii=False, indent=4)
        print(f"Character information saved to {file_path}")
        
        return result
        
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {str(e)}")
        return None
    except Exception as e:
        print(f"Error processing character info: {str(e)}")
        return None

if __name__ == "__main__":
    try:
        character_name = "Tony Stark"
        character_id = get_character_id(character_name)
        print(f"Character ID: {character_id}")
        
        # if character_id:
        #     character_info = get_character_info(character_id, character_name)
        #     print(f"Character Info: {character_info}")
            
    except Exception as e:
        print(f"Error in main execution: {str(e)}")
    finally:
        driver.quit()  # Always close the driver when done
