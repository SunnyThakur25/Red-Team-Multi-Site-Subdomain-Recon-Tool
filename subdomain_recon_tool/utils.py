# utils.py
import os

# Loading keywords from file
def load_keywords(keyword_file):
    try:
        with open(keyword_file, 'r') as f:
            lines = [line.strip() for line in f if line.strip()]
        keywords = {}
        current_category = 'other'
        for line in lines:
            if line.startswith('#'):
                current_category = line[1:].strip()
                keywords[current_category] = []
            else:
                keywords[current_category].append(line)
        return keywords
    except FileNotFoundError:
        return {'other': []}

# Classifying pages
def classify_page(url, content, keywords):
    for category, keyword_list in keywords.items():
        if any(keyword in url.lower() for keyword in keyword_list):
            return category
    return 'other'

# Loading logo
def load_logo(logo_path):
    if os.path.exists(logo_path):
        return logo_path
    else:
        print("Logo not found, using placeholder")
        return "https://via.placeholder.com/150?text=Red+Team+Logo"

