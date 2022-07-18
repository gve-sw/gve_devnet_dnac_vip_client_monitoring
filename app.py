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
from dnacentersdk import DNACenterAPI
from dotenv import load_dotenv
import os
import smtplib
from email.message import EmailMessage

from config import USERS, HEALTH_LOW, SNR

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

## Helper Functions
def send_email(USER, body):
    message = EmailMessage()
    message.set_content(body)

    message['Subject'] = f"DNAC VIP Client Monitoring alert for user {USER}"
    message['From'] = "GVE DevNet DNAC VIP Client Monitoring"
    message['To'] = RECIPIENT_EMAIL

    server = smtplib.SMTP_SSL(SMTP_SERVER_URL, SMTP_SERVER_PORT)
    server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    server.send_message(message)
    server.quit()

    print(f"---Email has been sent to {RECIPIENT_EMAIL}---")

def send_email(USER, body):
    message = EmailMessage()
    message.set_content(body)

    message['Subject'] = f"DNAC VIP Client Monitoring alert for user {USER}"
    message['From'] = "GVE DevNet DNAC VIP Client Monitoring" # Change this if needed
    message['To'] = RECIPIENT_EMAIL

    server = smtplib.SMTP_SSL(SMTP_SERVER_URL, SMTP_SERVER_PORT)
    server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    server.send_message(message)
    server.quit()

    print(f"---Email has been sent to {RECIPIENT_EMAIL}---")


def get_all_health_scores_from_user(user_details):
    print("We are getting all health scores from users")
    health_scores = []
    for user_detail in user_details:
        health_scores_dict = {}
        user_detail = user_detail["userDetails"]
        for health_score in user_detail["healthScore"]:
            if health_score["healthType"] == "OVERALL":
                overall_health_score = health_score["score"]
        
        health_scores_dict["score"] = overall_health_score
        health_scores_dict["hostname"] = user_detail["hostName"]
        health_scores_dict["id"] = user_detail["id"]
        health_scores.append(health_scores_dict)
        return health_scores
        
def convert_all_health_scores_dict_to_message(all_health_scores):
    all_health_scores_message = ""
    for health_score in all_health_scores:
        all_health_scores_message += f"- {health_score['hostname']}\n"
        all_health_scores_message += f"    * ID: {health_score['id']}\n"
        all_health_scores_message += f"    * score: {health_score['score']}\n"
    return all_health_scores_message


def check_health_from_user_detail(user_detail, user_details):
    alert = False
    alert_reason_message = ""
    user_detail = user_detail["userDetails"]
    try:
        # print(json.dumps(user_detail, indent=2))
        for health_score in user_detail["healthScore"]:
            if health_score["healthType"] == "OVERALL":
                overall_health_score = health_score["score"]

        issue_count = user_detail["issueCount"]
        rssi = float(user_detail["rssi"])
        snr = float(user_detail["snr"])
    except Exception as e:
        print("An exception has occurred")
        print(e)
        return 

    print("Checking the thresholds")
    # check the thresholds
    if overall_health_score <= HEALTH_LOW:
        alert = True
        alert_reason_message += f"- The overall health score is {overall_health_score}, which is below {HEALTH_LOW}\n"
    if snr <= SNR:
        alert = True
        alert_reason_message += f"- The snr is {snr}, which is below {SNR}\n"
    if float(user_detail["txLinkError"]) > 0:
        alert = True
        alert_reason_message += f"- There are {user_detail['txLinkError']} txLinkErrors"
    if float(user_detail["rxLinkError"]) > 0:
        alert = True
        alert_reason_message += f"- There are {user_detail['rxLinkError']} rxLinkErrors"
    
    if alert:
        print("**sending email**")

        # Retrieve health scores from other clients of users
        all_health_scores = get_all_health_scores_from_user(user_details)

        # Turn all_health_scores into message
        all_health_scores_message = convert_all_health_scores_dict_to_message(all_health_scores)

        message = f"""
DNA Center VIP Client Alert:
Please review the information for the Client-{user_detail['hostMac']}, which belongs to user {user_detail['userId']}:
Connection Status: {user_detail['connectionStatus']}
Location: {user_detail['location']}
Health: {overall_health_score}
RSSI: {rssi}
Issue Count: {issue_count}
SNR: {user_detail['snr']}
txRate: {user_detail['txRate']}
rxRate: {user_detail['rxRate']}

Onboarding:
- Average Run Duration: {user_detail['onboarding']['averageRunDuration']}
- Max Run Duration: {user_detail['onboarding']['maxRunDuration']}
- Average Assocation Duration: {user_detail['onboarding']['averageAssocDuration']}
- Max Assocation Duration: {user_detail['onboarding']['maxAssocDuration']}
- Average Authentication Duration: {user_detail['onboarding']['averageAuthDuration']}
- Max DHCP Duration: {user_detail['onboarding']['maxDhcpDuration']}
- Latest Root Cause List: {user_detail["onboarding"]['latestRootCauseList']}

Health scores of other clients of user {user_detail['userId']}:
{all_health_scores_message}

The reason for the alert:\n{alert_reason_message}
"""

        send_email(user_detail['userId'], message)
        

# Main function
def main():
    global alert_count
    print('**DNA Center users to be monitored: **', USERS)

    # alerts will be sent until the alert counter reaches the max alert count
    alert_count = 0

    dna_center = DNACenterAPI(username=DNAC_USERNAME, password=DNAC_PASSWORD, base_url=DNAC_BASE_URL, verify=False)
    print("**Successfuly connected to DNAC**")

    for USER in USERS:
        try:
            user_details = dna_center.users.get_user_enrichment_details(headers={'entity_type': 'network_user_id', 'entity_value': USER})
            for user_detail in user_details:
                # Check the health
                check_health_from_user_detail(user_detail, user_details)
        except Exception as e:
            print("An exception has occurred:")
            print(e)

if __name__ == '__main__':
    main()