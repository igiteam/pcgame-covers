import json

JSON_FILE = "pc_games_winejs.json"

def add_cover_url_to_json():
    try:
        # Open and load the JSON file
        with open(JSON_FILE, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        # Add cover_url field to each item if it doesn't exist
        for item in data:
            if "cover_url" not in item:
                item["cover_url"] = "https://cdn.gitgpt.chat/rtx/images/pc-no-cover.png"
        
        # Save the updated JSON back to the file
        with open(JSON_FILE, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=2, ensure_ascii=False)
        
        print(f"Successfully added 'cover_url' field to {len(data)} items in {JSON_FILE}")
        
    except FileNotFoundError:
        print(f"Error: {JSON_FILE} not found in the current directory")
    except json.JSONDecodeError:
        print(f"Error: {JSON_FILE} contains invalid JSON")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    add_cover_url_to_json()