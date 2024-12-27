import os
import json
from typing import List

from loguru import logger

from lmdb_cli_tool.utils.constant import IMAGE_SUFFIX


class SceneText:
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


class LayoutLLM:
    def __init__(self, image_dir_path: str, json_dir_path: str):
        if not os.path.exists(image_dir_path):
            raise FileNotFoundError(f"Image directory not found: {image_dir_path}")
        if not os.path.exists(json_dir_path):
            raise FileNotFoundError(f"JSON directory not found: {json_dir_path}")
        
        json_dir_basename_path = os.path.basename(json_dir_path)
        
        self.image_list_path: List[str] = []
        self.json_list_path: List[str] = []
        
        images = sorted([f for f in os.listdir(image_dir_path) if any(f.endswith(suffix) for suffix in IMAGE_SUFFIX)])
        jsons = []
        
        if json_dir_basename_path == "DOCILE":
            json_pattern = "IE-docile-images-"
            jsons = [json_pattern + f + ".json" for f in images]
        elif json_dir_basename_path == "RVL_CDIP":
            json_pattern = "classification-RVL_CDIP-archive-specification-img-"
            jsons = [json_pattern + f + ".json" for f in images]
        elif json_dir_basename_path == "PubLayNet":
            json_files = sorted([f for f in os.listdir(json_dir_path) if f.endswith(".json")])
            json_map = self._map_publaynet_jsons(images, json_files)
            for image in images:
                if image in json_map:
                    self.image_list_path.append(os.path.join(image_dir_path, image))
                    self.json_list_path.append(os.path.join(json_dir_path, json_map[image]))
        else:
            jsons = [os.path.splitext(f)[0] + ".json" for f in images]
        
        if json_dir_basename_path != "PubLayNet":
            self.image_list_path = [os.path.join(image_dir_path, img) for img in images]
            self.json_list_path = [os.path.join(json_dir_path, js) for js in jsons]
    
    @staticmethod
    def _map_publaynet_jsons(images: List[str], json_files: List[str]) -> dict:
        """
        Map image filenames to their corresponding JSON filenames in PubLayNet.
        """
        json_map = {}
        for image in images:
            # Extract the unique identifier from the image filename (e.g., "PMC6093876_00001" from "train_PMC6093876_00001.jpg")
            image_id = "_".join(image.split("_")[1:])
            for json_file in json_files:
                # Match JSON filenames that include the identifier
                if image_id in json_file:
                    json_map[image] = json_file
                    break
        return json_map
    
    def __len__(self):
        return len(self.image_list_path)
    
    def __getitem__(self, idx):
        image_path, json_path = self.image_list_path[idx], self.json_list_path[idx]
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


class AWSExtractText:
    def __init__(self, image_dir_path: str, json_dir_path: str):
        if not os.path.exists(image_dir_path):
            raise FileNotFoundError(f"Image directory not found: {image_dir_path}")
        if not os.path.exists(json_dir_path):
            raise FileNotFoundError(f"JSON directory not found: {json_dir_path}")
        
        self.image_list_path: List[str] = []
        self.json_list_path: List[str] = []
        
        images = sorted([f for f in os.listdir(image_dir_path) if any(f.endswith(suffix) for suffix in IMAGE_SUFFIX)])
        jsons = [os.path.splitext(f)[0] + ".json" for f in images]
        
        self.image_list_path = [os.path.join(image_dir_path, img) for img in images]
        self.json_list_path = [os.path.join(json_dir_path, js) for js in jsons]
    
    def __len__(self):
        return len(self.image_list_path)
    
    def __getitem__(self, idx):
        image_path, json_path = self.image_list_path[idx], self.json_list_path[idx]
        label_text = ""
        try:
            with open(json_path, "r") as f:
                label = json.load(f)
            if label:
                label = label["LINE"]
                label_text = " ".join([line["Text"] for line in label])
        except FileNotFoundError:
            logger.error(f"JSON file not found: {json_path}")
        except json.JSONDecodeError:
            logger.error(f"Failed to decode JSON file: {json_path}")
        except Exception as e:
            logger.error(f"Unexpected error reading JSON file {json_path}: {e}")
        
        return image_path, label_text


class AzureExtractText:
    def __init__(self, image_dir_path: str, json_dir_path: str):
        if not os.path.exists(image_dir_path):
            raise FileNotFoundError(f"Image directory not found: {image_dir_path}")
        if not os.path.exists(json_dir_path):
            raise FileNotFoundError(f"JSON directory not found: {json_dir_path}")
        
        self.image_list_path: List[str] = []
        self.json_list_path: List[str] = []
        
        images = sorted([f for f in os.listdir(image_dir_path) if any(f.endswith(suffix) for suffix in IMAGE_SUFFIX)])
        jsons = [os.path.splitext(f)[0] + ".json" for f in images]
        
        self.image_list_path = [os.path.join(image_dir_path, img) for img in images]
        self.json_list_path = [os.path.join(json_dir_path, js) for js in jsons]
    
    def __len__(self):
        return len(self.image_list_path)
    
    def __getitem__(self, idx):
        image_path, json_path = self.image_list_path[idx], self.json_list_path[idx]
        label_text = ""
        try:
            with open(json_path, "r") as f:
                label = json.load(f)
            if label:  # Ensure label is not empty
                label = label["recognitionResults"][0]
                label_text = " ".join([line["text"] for line in label["lines"]])
        except FileNotFoundError:
            logger.error(f"JSON file not found: {json_path}")
        except json.JSONDecodeError:
            logger.error(f"Failed to decode JSON file: {json_path}")
        except Exception as e:
            logger.error(f"Unexpected error reading JSON file {json_path}: {e}")
        
        return image_path, label_text


if __name__ == "__main__":
    json_path = "/home/rb074/Downloads/data/docvqa/ocr/ffbf0023_p5.json"
    with open(json_path, "r") as f:
        label = json.load(f)
        label = label["LINE"]
        label_text = " ".join([line["Text"] for line in label])
        import pdb; pdb.set_trace()
