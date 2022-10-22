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
            match_params = gr.Checkbox(label='Get all generation parameters', value=False)
            generate_all = gr.Checkbox(label='Generate all 50 results', value=False)
        return [search, generate_all, match_params]

    def run(self, p, search, generate_all, match_params):
        images = []
        search_string = search.replace(" ","+")
        url = "https://lexica.art/api/v1/search?q=" + search_string
        resp = requests.get(url=url)
        data = resp.json() # Check the JSON Response Content documentation below
        prompts = data["images"]
        random_index = randint(0, len(prompts)-1)
        if generate_all:
            print("Generating all 50 results")
            for i in range(0, len(prompts)-1):
                p.prompt = prompts[i]["prompt"]
                if match_params:
                    p.width = prompts[random_index]["width"]
                    p.height = prompts[random_index]["height"]
                    p.seed = prompts[random_index]["seed"]
                    p.cfg_scale = prompts[random_index]["guidance"]
                proc = process_images(p)
                images += proc.images
        else:
            p.prompt = prompts[random_index]["prompt"]
            if match_params:
                p.width = prompts[random_index]["width"]
                p.height = prompts[random_index]["height"]
                p.seed = prompts[random_index]["seed"]
                p.cfg_scale = prompts[random_index]["guidance"]
            proc = process_images(p)
            images += proc.images

        return Processed(p, images, p.seed, proc.info)
