
# sourcery skip: dict-literal, merge-dict-assign
# import random
# import time
from pythonosc import udp_client


class OSC():
    def __init__(self, config) -> None:
        self.client = udp_client.SimpleUDPClient(config['ip'], config['port'])

    def send(self, part, value):
        """sends an OSC message to the server.

        Args:
            part (str): the body-part. 
            value (float): the screen coordinate of the part [0,1]
        """        
        self.client.send_message(f"/{part}", value)
        # time.sleep(1)