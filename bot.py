import requests
import json

# Base URL for API
base_url = "https://www.freelancer.com/api/projects/0.1/projects/"

# Query parameters for fetching active projects
params = {
    "compact": "",
    "limit": 5,
    "languages[]": ["en", "fr"],
    "jobs[]": [9, 36, 39, 77, 95, 115, 121, 199, 245, 292, 334, 335, 420, 472, 717, 761, 977, 995, 1039, 1075, 1077, 1383, 1402, 1420, 1421, 1601, 2280, 2320, 2533, 2719, 2761, 2836, 2889, 2890, 2891, 2907, 2911, 2917, 2918, 2919, 2926, 2931, 2937, 2944, 2946, 2948, 2959, 2961, 2963, 2966, 2977, 2985, 2986, 3001],
}

# Authorization header
headers = {
    "freelancer-oauth-v1": "<oauth_access_token>",  # Replace with your OAuth token
}

# Telegram bot details
telegram_bot_token = "7978640691:AAGetaNtpElql0zP1XaAcs5Z7CQVdzgB4kw"  # Replace with your Telegram bot token
telegram_chat_ids = ["1691991490", "1156227602"]  # Replace with your Telegram chat IDs

# Fetch active projects
def fetch_active_projects():
    response = requests.get(base_url + "active/", headers=headers, params=params)
    if response.status_code == 200:
        return response.json().get("result", {}).get("projects", [])
    else:
        print(f"Error fetching active projects: {response.text}")
        return []

# Fetch project details by ID
def fetch_project_details(project_id):
    response = requests.get(base_url + f"{project_id}/", headers=headers, params={"full_description": True, "user_country_details": True})
    if response.status_code == 200:
        return response.json().get("result", {})
    else:
        print(f"Error fetching project {project_id}: {response.text}")
        return {}

# Extract important details from project data
def extract_project_info(project):
    return {
        "title": project.get("title"),
        "full_description": project.get("description"),
        "skills_required": [skill.get("name") for skill in (project.get("jobs") or []) if skill],
        "number_of_bids": project.get("bid_stats", {}).get("bid_count"),
        "min_price": project.get("budget", {}).get("minimum"),
        "max_price": project.get("budget", {}).get("maximum"),
        "currency": project.get("currency", {}).get("code"),
        "user_country_details": project.get("user_country_details", {}),
        "link": f"https://www.freelancer.com/projects/{project.get('id')}"  # Construct the project link
    }

# Send Telegram message
def send_telegram_message(message):
    for chat_id in telegram_chat_ids:
        url = f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage"
        payload = {"chat_id": chat_id, "text": message}
        response = requests.post(url, data=payload)
        if response.status_code != 200:
            print(f"Failed to send message to Telegram chat {chat_id}: {response.text}")

# Main workflow
if __name__ == "__main__":
    projects = fetch_active_projects()
    detailed_projects = []

    for project in projects:
        project_id = project.get("id")
        if project_id:
            detailed_project = fetch_project_details(project_id)
            project_info = extract_project_info(detailed_project)
            detailed_projects.append(project_info)

            # Prepare Telegram message
            message = (
                f"New Project Alert!\n\n"
                f"Title: {project_info['title']}\n"
                f"Description: {project_info['full_description']}\n"
                f"Skills Required: {', '.join(project_info['skills_required'])}\n"
                f"Number of Bids: {project_info['number_of_bids']}\n"
                f"Budget: {project_info['min_price']} - {project_info['max_price']} {project_info['currency']}\n"
                f"Country Details: {project_info['user_country_details']}\n"
                f"Link: {project_info['link']}\n"
            )
            send_telegram_message(message)

    # Print extracted project details
    print(json.dumps({"status": "success", "projects": detailed_projects}, indent=2))
