# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (c) 2022 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at
               https://developer.cisco.com/docs/licenses
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
"""

__author__ = "Simon Fang <sifang@cisco.com>"
__copyright__ = "Copyright (c) 2022 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.1"

# Import section
import time

from dnacentersdk import DNACenterAPI

from dotenv import load_dotenv
import os
import smtplib
from email.message import EmailMessage
import json

from config import USERS, MAC_CLIENTS, HEALTH_LOW, SNR, BW_LOW

# Load environment variables
load_dotenv()

# Global variables
DNAC_USERNAME = os.getenv("DNAC_USERNAME")
DNAC_PASSWORD = os.getenv("DNAC_PASSWORD")
DNAC_BASE_URL = os.getenv("DNAC_BASE_URL")

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")
SMTP_SERVER_URL = os.getenv("SMTP_SERVER_URL")
SMTP_SERVER_PORT = int(os.getenv("SMTP_SERVER_PORT"))

MAX_ALERT = 1

alert_count = 0 

## Helper Functions
def send_email(MAC_CLIENT, body):
    message = EmailMessage()
    message.set_content(body)

    message['Subject'] = f"DNAC VIP Client Monitoring alert for client {MAC_CLIENT}"
    message['From'] = "GVE DevNet DNAC VIP Client Monitoring"
    message['To'] = RECIPIENT_EMAIL

    server = smtplib.SMTP_SSL(SMTP_SERVER_URL, SMTP_SERVER_PORT)
    server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    server.send_message(message)
    server.quit()

    print(f"---Email has been sent to {RECIPIENT_EMAIL}---")


def client_health_check(alert, client_health):
    """
    This function will check if the client health score {client_health} is above the predefined threshold
    :param alert: parameter for alert to check if alert needs to be sent or not
    :param client_health: client health score
    :return: alert
    """
    if client_health <= HEALTH_LOW:
        alert = True
        print(f"**client Health too low: {client_health}, send email alert**")
    return alert

def check_general_health(dna_center_api, MAC_CLIENT, user_detail=None):
    global alert_count
    alert = False
    
    client_info = dna_center_api.clients.get_client_detail(mac_address=MAC_CLIENT)
    print(json.dumps(client_info, indent=2))

    # parse the client health score, ap name, snr, location
    try:
        health_score = client_info['detail']['healthScore']
        for score in health_score:
            if score['healthType'] == 'OVERALL':
                client_health = score['score']
        ap_name = client_info['detail']['clientConnection']
        snr = float(client_info['detail']['snr'])
        location = client_info['detail']['location']
    except Exception as e:
        print('**An exception has occurred**')
        print(e)

    alert = client_health_check(alert, client_health)

    # Generic values for PoV
    total_data_transfer = 101 

    if snr <= SNR:
        alert = True
    if total_data_transfer <= BW_LOW:
        alert = True

    if alert:
        print("**sending email**")

        message = f"DNA Center VIP Client Alert:\n" \
                f" Please review the information for the VIP Client-{MAC_CLIENT}:\n" \
                f"Location: {location}\n" \
                f"AP: {ap_name}\n" \
                f"Health: {client_health}\n" \
                f"SNR: {snr}\n\n" \
                f"Client info JSON:\n"

        message += json.dumps(client_info, indent=4)

        if user_detail:
            message += json.dumps(user_detail, indent=4)
        
        # send message from slack bot to the specified space: #bot-project
        send_email(MAC_CLIENT, message)

        alert_count += 1
        time.sleep(5)

# Main function
def main():
    global alert_count
    print('**DNA Center users to be monitored: **', USERS)

    # alerts will be sent until the alert counter reaches the max alert count
    alert_count = 0

    dna_center = DNACenterAPI(username=DNAC_USERNAME, password=DNAC_PASSWORD, base_url=DNAC_BASE_URL, verify=False)
    print("**Successfuly connected to DNAC**")

    user_details = []
    for USER in USERS:
        try:
            user_detail = dna_center.users.get_user_enrichtment_details(headers={'entity_type': 'network_user_id', 'entity_value': USER})
            user_details.append(user_detail)
        except Exception as e:
            print(e)
            print(f"No user data for user: {USER}")

    while alert_count < MAX_ALERT: # Can also be changed to: while True
        if user_details: # If user_details non-empty, then populate MAC_CLIENTS with mac_clients in user_details
            for user_detail in user_details:
                # get mac_client from each user_detail
                connected_devices = user_detail[0]["connectedDevice"]
                mac_addresses_connected_devices = []
                for dev in connected_devices:
                    mac_addresses_connected_devices.append(dev["deviceDetails"]["macAddress"])

                # check health score of each client in user_detail
                for mac_address in mac_addresses_connected_devices:
                    check_general_health(dna_center, mac_address, user_detail)

        else: 
            print('**DNA Center clients to be monitored: **', MAC_CLIENTS)
            for MAC_CLIENT in MAC_CLIENTS:
                check_general_health(dna_center, MAC_CLIENT)

if __name__ == '__main__':
    main()