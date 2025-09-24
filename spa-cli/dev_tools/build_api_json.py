from typing import cast
from dotenv import load_dotenv
from utils import get_api_config, get_api_initial_definition
import json

def build_api_json():
    api_definition = get_api_initial_definition()
    _, endpoint_list = get_api_config()

    for ep in endpoint_list:
        cast(dict, api_definition['paths']).update(ep)

    with open("dev_tools/openapi.json", "w+", encoding="utf-8") as f:
        json.dump(api_definition, f, indent=2)

build_api_json()