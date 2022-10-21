import json
import requests
from random import randint
import os.path

import modules.scripts as scripts
import gradio as gr

from modules import sd_samplers, shared
from modules.processing import Processed, process_images


class Script(scripts.Script):
    def title(self):
        return "Lexica2Prompt"

    def ui(self, is_img2img):
        with gr.Row():
            search = gr.Textbox(label='Lexica.art Search Term:')
        return [search]

    def run(self, p, search):
        images = []
        search_string = search.replace(" ","+")
        url = "https://lexica.art/api/v1/search?q=" + search_string
        resp = requests.get(url=url)
        data = resp.json() # Check the JSON Response Content documentation below
        prompts = data["images"]
        random_index = randint(0, len(prompts)-1)

        p.prompt = prompts[random_index]["prompt"]
        proc = process_images(p)
        images += proc.images

        return Processed(p, images, p.seed, proc.info)