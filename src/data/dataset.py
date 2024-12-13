import os
import json
from typing import List, Tuple, Dict, Any

from loguru import logger
from PIL import Image

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from utils.constant import IMAGE_SUFFIX


class SceneText(object):
    def __init__(self, image_dir_path: str, json_dir_path: str):
        if not os.path.exists(image_dir_path):
            raise FileNotFoundError(f"Image directory not found: {image_dir_path}")
        if not os.path.exists(json_dir_path):
            raise FileNotFoundError(f"JSON directory not found: {json_dir_path}")

        self.image_list_path: List[str] = []
        self.json_list_path: List[str] = []

        images = sorted([f for f in os.listdir(image_dir_path) if any(f.endswith(suffix) for suffix in IMAGE_SUFFIX)])
        jsons = [os.path.splitext(f)[0] + ".json" for f in images]
        
        self.image_path_list = [os.path.join(image_dir_path, img) for img in images]
        self.json_path_list = [os.path.join(json_dir_path, js) for js in jsons]

    def __len__(self):
        return len(self.image_path_list)
    
    def __getitem__(self, idx):
        image_path, json_path = self.image_path_list[idx], self.json_path_list[idx]
        with open(json_path, "r") as f:
            label = json.load(f)
        label_text = ""  
        if label:  # Ensure label is not empty
            label_text = " ".join([text["text"] for text in label])
        return image_path, label_text


class LayoutLLM(object):
    def __init__(self, image_dir_path: str, json_dir_path: str):
        if not os.path.exists(image_dir_path):
            raise FileNotFoundError(f"Image directory not found: {image_dir_path}")
        if not os.path.exists(json_dir_path):
            raise FileNotFoundError(f"JSON directory not found: {json_dir_path}")

        self.image_list_path: List[str] = []
        self.json_list_path: List[str] = []

        images = sorted([f for f in os.listdir(image_dir_path) if any(f.endswith(suffix) for suffix in IMAGE_SUFFIX)])
        jsons = [f + ".json" for f in images]
        
        self.image_path_list = [os.path.join(image_dir_path, img) for img in images]
        self.json_path_list = [os.path.join(json_dir_path, js) for js in jsons]

    def __len__(self):
        return len(self.image_path_list)
    
    def __getitem__(self, idx):
        image_path, json_path = self.image_path_list[idx], self.json_path_list[idx]
        label_text = ""
        try:
            with open(json_path, "r") as f:
                label = json.load(f)
            if label:  # Ensure label is not empty
                label_text = " ".join([text["text"] for text in label])
        except FileNotFoundError:
            logger.error(f"JSON file not found: {json_path}")
        except json.JSONDecodeError:
            logger.error(f"Failed to decode JSON file: {json_path}")
        except Exception as e:
            logger.error(f"Unexpected error reading JSON file {json_path}: {e}")
        
        return image_path, label_text