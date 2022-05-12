# GVE DevNet DNAC VIP Client Monitoring
The app will monitor VIP clients, e.g. executives or important guests, that are connected to the DNA Center. In case there are any issues, then an alert will be sent to proactively take action. 


## Contacts
* Simon Fang (sifang@cisco.com)

## Solution Components
* Python 3
* DNA Center


## Installation/Configuration
The following commands are executed in the terminal.

1. Create and activate a virtual environment for the project:
   
        #WINDOWS:
        $ py -3 -m venv [add_name_of_virtual_environment_here] 
        $ [add_name_of_virtual_environment_here]/Scripts/activate.bat 
        #MAC:
        $ python3 -m venv [add_name_of_virtual_environment_here] 
        $ source [add_name_of_virtual_environment_here]/bin/activate
        

> For more information about virtual environments, please click [here](https://docs.python.org/3/tutorial/venv.html)

2. Access the created virtual environment folder

        $ cd [add_name_of_virtual_environment_here] 

3. Clone this repository

        $ git clone [add_link_to_repository_here]

4. Access the folder `gve_devnet_dnac_vip_client_monitoring`

        $ cd gve_devnet_dnac_vip_client_monitoring

5. Install the dependencies:

        $ pip install -r requirements.txt

6. Open the `.env` file and add the DNAC and email credentials:

    ```python
    DNAC_USERNAME = "<insert_dnac_username>"
    DNAC_PASSWORD = "<insert_dnac_password>"
    DNAC_BASE_URL = "<insert_dnac_base_url>"

    EMAIL_ADDRESS = "<insert_email_address>" # Add the email address of the smtp server
    EMAIL_PASSWORD = "<insert_email_password>"
    RECIPIENT_EMAIL = "<insert_recipient_email>" # Add the email address of the recipient
    SMTP_SERVER_URL = "<insert_smtp_server_url>"
    SMTP_SERVER_PORT = 465 # change to the correct port
    ``` 

7. Open the `config.py` file and add the general configurations, thresholds and the clients or users to be monitored:

    ```python
    USERS = ['<insert_user_id>', '<insert_user_id>'] # Add a list of users, which can be email address
    MAC_CLIENTS = ['<insert_mac_address>', '<insert_mac_address>'] # Or add a list of mac clients
    HEALTH_LOW = 90 # arbitrary number as example, but health is between 0 and 10
    SNR = 100 # arbitrary number as example
    BW_LOW = 100 # arbitrary number as example
    ```

## Usage
Now it is time to launch the application! Simply type in the following command in your terminal:

    $ python app.py


# Screenshots

![IMAGES/0image.png](IMAGES/0image.png)

### LICENSE

Provided under Cisco Sample Code License, for details see [LICENSE](LICENSE.md)

### CODE_OF_CONDUCT

Our code of conduct is available [here](CODE_OF_CONDUCT.md)

### CONTRIBUTING

See our contributing guidelines [here](CONTRIBUTING.md)

#### DISCLAIMER:
<b>Please note:</b> This script is meant for demo purposes only. All tools/ scripts in this repo are released for use "AS IS" without any warranties of any kind, including, but not limited to their installation, use, or performance. Any use of these scripts and tools is at your own risk. There is no guarantee that they have been through thorough testing in a comparable environment and we are not responsible for any damage or data loss incurred with their use.
You are responsible for reviewing and testing any scripts you run thoroughly before use in any non-testing environment.