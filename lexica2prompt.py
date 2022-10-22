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
        with gr.Row():
            match_seed = gr.Checkbox(label='Use seed', value=False)
            match_size = gr.Checkbox(label='Use size', value=False)
            match_cfg = gr.Checkbox(label='Use CFG Scale', value=False)
            match_sampler = gr.Checkbox(label='Use PLMS and 50 steps (Lexica default)', value=False)
            generate_all = gr.Checkbox(label='Generate all 50 results', value=False)
        return [search, generate_all, match_seed, match_size, match_sampler, match_cfg]

    def run(self, p, search, generate_all, match_seed, match_size, match_sampler, match_cfg):
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
                if match_size:
                    p.width = prompts[random_index]["width"]
                    p.height = prompts[random_index]["height"]
                if match_seed:
                    p.seed = prompts[random_index]["seed"]
                if match_cfg:
                    p.cfg_scale = prompts[random_index]["guidance"]
                proc = process_images(p)
                images += proc.images
        else:
            p.prompt = prompts[random_index]["prompt"]
            if match_size:
                p.width = prompts[random_index]["width"]
                p.height = prompts[random_index]["height"]
            if match_seed:
                p.seed = prompts[random_index]["seed"]
            if match_cfg:
                p.cfg_scale = prompts[random_index]["guidance"]
            proc = process_images(p)
            images += proc.images

        return Processed(p, images, p.seed, proc.info)
