import json
import requests
from random import randint
import os.path
from pathlib import Path
import modules.scripts as scripts
import gradio as gr

from modules import sd_samplers, shared
from modules.processing import Processed, process_images
from modules.shared import opts

LEXIKREA_VER = "1"

base_dir = Path(scripts.basedir())
LEXIKREA_DIR = getattr(opts, "lexikrea_dir", base_dir / "scripts/saved_prompts")

def change_output_folder(path):
    #alp = setattr(opts,"lexikrea_dir", path)
    opts.data["lexikrea_dir"] = path
    opts.save(shared.config_filename)
    global LEXIKREA_DIR
    LEXIKREA_DIR = path
    print(f"Prompts will now be saved to {path}")


def get_prompt_data(site, search_string):
    if site == "Krea.ai":
        url = "https://devapi.krea.ai/prompts/?format=json&search=" + search_string
        resp = requests.get(url=url)
        data = resp.json()
        prompts = data["results"]
    else:
        url = "https://lexica.art/api/v1/search?q=" + search_string
        resp = requests.get(url=url)
        data = resp.json()
        prompts = data["images"]

    return prompts


def create_txt(search, site):
    search_string = search.replace(" ","+")
    prompts = get_prompt_data(site, search)
    if site == "Krea.ai":
        out_path = f"{LEXIKREA_DIR}/krea"
    else:
        out_path = f"{LEXIKREA_DIR}/lex"


    txt_string = search.replace(" ","_")
    Path(out_path).mkdir(parents=True, exist_ok=True)
    txt_filename = f"{out_path}/{txt_string}.txt"
    for i in range(0, 50):
        prompt = prompts[i]["prompt"]
        if not os.path.isfile(txt_filename):
            with open(txt_filename, "w", encoding="utf8") as myfile:
                myfile.write(f"{prompt}\n")
        else:
            with open(txt_filename, "a", encoding="utf8") as myfile:
                myfile.write(f"{prompt}\n")
    print(f"Created {txt_filename}")


def show_results(site, search):
    prompts_dict = {}
    prompts = get_prompt_data(site, search)
    prompts_dict[int(0)] = "Random"
    for i in range(0,50):
        prompts_dict[int(i + 1)] = prompts[i]["prompt"]
    
    return gr.Dropdown.update(choices=[v for k, v in prompts_dict.items()])

def generate_one(prompt):
    images = []
    p.prompt = prompt
    proc = process_images(p)
    images += proc.images


class Script(scripts.Script):
    def title(self):
        return f"LexiKrea v{LEXIKREA_VER}"

    def ui(self, is_img2img):
        with gr.Row():
            search = gr.Textbox(label='Prompt Search Term:')
        with gr.Row(equal_height=True):
            site = gr.Radio(label='Site to search', choices=["Krea.ai","Lexica.art"], value="Krea.ai", type="value")
            #match_seed = gr.Checkbox(label='Use seed', value=False)
            #match_size = gr.Checkbox(label='Use size', value=False)
            #match_cfg = gr.Checkbox(label='Use CFG Scale', value=False)
            generate_all = gr.Checkbox(label='Generate all 50 results', value=False)
        with gr.Row():
            display_prompts = gr.Dropdown(label='Pulled Prompts')
        with gr.Row():
            fetch_prompts = gr.Button('List Prompts')
        with gr.Row():
            output_folder = gr.Textbox(label='Output DIR', value=LEXIKREA_DIR)
        with gr.Row():
            change_output = gr.Button('Update output folder')
            output_to_txt = gr.Button('Output to text', show_progress=True)

        fetch_prompts.click(
            fn=show_results,
            inputs=[
                site,
                search,
            ],
            outputs=[
                display_prompts,
            ]
            )
        change_output.click(
            fn=change_output_folder,
            inputs=[
                output_folder,
            ],
            outputs=[]
            )
        output_to_txt.click(
            fn=create_txt,
            inputs=[
                search,
                site,
            ],
            outputs=[]
        )

        return [search, generate_all, output_to_txt, output_folder, change_output, site, fetch_prompts, display_prompts]

    def run(self, p, search, generate_all, output_to_txt, output_folder, change_output, site, fetch_prompts, display_prompts):
        images = []
        search_string = search.replace(" ","+")
        prompts = get_prompt_data(site, search_string)
        if site == "Krea.ai":
            if generate_all:
                print("Generating all 50 results from Krea.ai")
                for i in range(0, 50):
                    p.prompt = prompts[i]["prompt"] 

#                    if match_size:
#                        p.width = prompts[i]["model_parameters"]["width"]
#                        p.height = prompts[i]["model_parameters"]["height"]
#                    if match_seed:
#                        if "seed" in prompts[i]["generations"][0]["raw_data"]["raw_discord_data"]:
#                            p.seed = prompts[i]["generations"][0]["raw_data"]["raw_discord_data"]["seed"]
#                    if match_cfg:
#                        p.cfg_scale = prompts[i]["model_parameters"]["cfg_scale"]

                    proc = process_images(p)
                    images += proc.images

            else:
                if not display_prompts or display_prompts == "Random":

                    random_index = randint(0, 50)
                    p.prompt = prompts[random_index]["prompt"]
#                    if match_size:
#                        p.width = prompts[random_index]["model_parameters"]["width"]
#                        p.height = prompts[random_index]["model_parameters"]["height"]
#                    if match_seed:
#                        if "seed" in prompts[random_index]["generations"][0]["raw_data"]["raw_discord_data"]:
#                            p.seed = prompts[random_index]["generations"][0]["raw_data"]["raw_discord_data"]["seed"]
#                    if match_cfg:
#                        p.cfg_scale = prompts[random_index]["model_parameters"]["cfg_scale"]
                else:
                    p.prompt = display_prompts
                proc = process_images(p)
                images += proc.images

        else:
            random_index = randint(0, 50)
            if generate_all:
                print("Generating all 50 results")
                for i in range(0, 50):
                    p.prompt = prompts[i]["prompt"]
#                    if match_size:
#                        p.width = prompts[i]["width"]
#                        p.height = prompts[i]["height"]
#                    if match_seed:
#                        p.seed = prompts[i]["seed"]
#                    if match_cfg:
#                        p.cfg_scale = prompts[i]["guidance"]
                    proc = process_images(p)
                    images += proc.images
            else:
                if not display_prompts or display_prompts == "Random":
                    random_index = randint(0, 50)
                    p.prompt = prompts[random_index]["prompt"]
#                    if match_size:
#                        p.width = prompts[random_index]["width"]
#                        p.height = prompts[random_index]["height"]
#                    if match_seed:
#                        p.seed = prompts[random_index]["seed"]
#                    if match_cfg:
#                        p.cfg_scale = prompts[random_index]["guidance"]
                else:
                    p.prompt = display_prompts
                proc = process_images(p)
                images += proc.images

        return Processed(p, images, p.seed, proc.info)
