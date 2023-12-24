import time
import schedule
import requests
from mastodon import Mastodon

# Replace 'YOUR_NWS_API_ENDPOINT', 'YOUR_NWS_API_TOKEN', 'YOUR_MASTODON_ACCESS_TOKEN', and 'MASTODON_INSTANCE_URL'
NWS_API_ENDPOINT = 'YOUR_NWS_API_ENDPOINT'
NWS_API_TOKEN = 'YOUR_NWS_API_TOKEN'
MASTODON_ACCESS_TOKEN = 'YOUR_MASTODON_ACCESS_TOKEN'
MASTODON_INSTANCE_URL = 'MASTODON_INSTANCE_URL'

# Specify the zone
nws_zone = 'ALERT_ZONE_FROM_NWS'

# Load previously posted alerts from a file
try:
    with open('posted_alerts.txt', 'r') as file:
        posted_alerts = set(file.read().splitlines())
except FileNotFoundError:
    posted_alerts = set()

# Define the function to fetch and post alerts
def fetch_and_post_alerts():
    try:
        # Make a request to the NWS API to get alerts for the specified location
        nws_alerts_url = f'{NWS_API_ENDPOINT}/alerts/active/zone/{nws_zone}'
        response = requests.get(nws_alerts_url)

        if response.status_code == 200:
            # Parse the JSON response
            alerts_data = response.json()

            # Check if there are any active alerts
            if alerts_data['features']:
                # Extract alert information (replace these keys with your actual data keys)
                alert_title = alerts_data['features'][0]['properties']['headline']
                alert_description = alerts_data['features'][0]['properties']['description']
                alert_id = alerts_data['features'][0]['properties']['id']

                # Create a unique identifier for the alert
                alert_id = f'{alert_id}'

                # Check if the alert has already been posted
                if alert_id not in posted_alerts:
                    # Prepare the status message
                    status_message = f'{alert_title}\n\n{alert_description}'

                    # Post to Mastodon
                    mastodon = Mastodon(
                        access_token=MASTODON_ACCESS_TOKEN,
                        api_base_url=MASTODON_INSTANCE_URL
                    )
                    mastodon.status_post(status_message)

                    # Update the list of posted alerts
                    posted_alerts.add(alert_id)

                    print(f'Successfully posted to Mastodon: {status_message}')

                else:
                    print('Alert already posted.')

            else:
                print('No active weather alerts.')

        else:
            print(f'Error: {response.status_code} - Unable to fetch weather alerts from NWS API')

    except Exception as e:
        print(f'Error: {str(e)}')

# Schedule the function to run every 5 minutes
schedule.every(5).minutes.do(fetch_and_post_alerts)

# Run the scheduler continuously
while True:
    schedule.run_pending()
    time.sleep(1)
