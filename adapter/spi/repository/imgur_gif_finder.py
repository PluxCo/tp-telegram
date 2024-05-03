import random

import requests

from port.spi.gif_finder_port import GifFinderPort


class ImgurGifFinder(GifFinderPort):
    def __init__(self, client_id: str):
        self.client_id = client_id

    def find_gif(self, mood: str) -> str:
        page = 1

        resp = requests.get(f"https://api.imgur.com/3/gallery/search/top/all/{page}/?q={mood}&q_type=anigif",
                            headers={"Authorization": f"Client-ID {self.client_id}"})

        images = [i for i in resp.json()["data"] if "mp4" in i]

        print(len(images), len(resp.json()["data"]))

        selected_image = random.choice(images)

        return selected_image["mp4"]
