import argparse
from pathlib import Path
import sys
from enum import Enum, unique
import time

from loguru import logger

from lmdb_main import LMDBReader, LMDBWriter, LMDBRecovery
from data.dataset import SceneText, LayoutLLM
from utils.constant import VERSION
from utils.config_utils import load_config
from utils.file_utils import json_reader


def process_and_write_lmdb(data_object, output_path: str, resume: bool = False):
    """Process and write dataset to LMDB"""
    datasets = [(data_object[i]) for i in range(len(data_object))]
    writer = LMDBWriter(output_path, resume=resume)
    start_time = time.time()
    writer.create_dataset(datasets)
    end_time = time.time()
    logger.info(f"Dataset writing completed in {end_time - start_time:.2f} seconds")
    

def run_writer():
    parser = argparse.ArgumentParser(description='LMDB Dataset Writer')
    parser.add_argument('--config', type=str, required=True, 
                       help='Path to YAML config file')
    
    args = parser.parse_args()

    # Load and validate config
    if not Path(args.config).exists():
        raise FileNotFoundError(f"Config file not found: {args.config}")
    
    config = load_config(args.config)
    
    dataset = config.get('dataset')
    dataset_lst = [name.strip() for name in dataset.split(',')]
    dataset_info = json_reader(config.get('dataset_info'))
    for name in dataset_lst:
        if name not in dataset_info:
            raise ValueError(f"Dataset name not found in dataset_info.json: {name}")
        image_dir = dataset_info[name].get('image_dir')
        json_dir = dataset_info[name].get('json_dir')
        output = dataset_info[name].get('output_dir')
        json_type = dataset_info[name].get('json_type')

        if not all([image_dir, json_dir, output]):
            raise ValueError("Missing required parameters in config file")
        
        if not Path(image_dir).exists():
            raise FileNotFoundError(f"Image directory not found: {image_dir}")
        
        if not Path(json_dir).exists():
            raise FileNotFoundError(f"JSON directory not found: {json_dir}")

        try:
            # Initialize appropriate dataset object
            if json_type == 'scene_text':
                data_object = SceneText(image_dir, json_dir)
            elif json_type == 'layoutllm':
                data_object = LayoutLLM(image_dir, json_dir)
            else:
                raise ValueError(f"Unsupported dataset type: {json_type}")

            # Process and write
            logger.info(f"Writing dataset to {output}")
            process_and_write_lmdb(data_object, output)
            logger.info("Dataset writing completed successfully")

        except Exception as e:
            logger.error(f"Error writing dataset: {e}")
            raise


def run_reader():
    pass


def run_recovery():
    parser = argparse.ArgumentParser(description='LMDB Dataset Recovery')
    parser.add_argument('--config', type=str, required=True,
                        help='Path to YAML config file')
    args = parser.parse_args()

    # Load and validate config
    if not Path(args.config).exists():
        raise FileNotFoundError(f"Config file not found: {args.config}")
    
    config = load_config(args.config)

    dataset = config.get('dataset')
    dataset_lst = [name.strip() for name in dataset.split(',')]
    dataset_info = json_reader(config.get('dataset_info'))
    for name in dataset_lst:
        if name not in dataset_info:
            raise ValueError(f"Dataset name not found in dataset_info.json: {name}")
        lmdb_dir = dataset_info[name].get('output_dir')
        try:
            # Initialize appropriate dataset object
            recovery = LMDBRecovery(lmdb_dir)
            logger.info(f"Recovering dataset from {lmdb_dir}")
            recovery.recover_images()
            logger.info("Dataset recovery completed successfully")
        except Exception as e:
            logger.error(f"Error recovering dataset: {e}")
            raise

USAGE = (
    "-" * 90
    + "\n"
    + "| Usage:                                                                                 |\n"
    + "|   lmdb-cli write --config <path>    Write data to LMDB database                        |\n"
    + "|   lmdb-cli recovery --config <path> Recover data from LMDB database                    |\n"
    + "|   lmdb-cli version                 Show version information                            |\n"
    + "|   lmdb-cli help                    Show this help message                              |\n"
    + "-" * 90
)

def create_welcome_message(version: str) -> str:
    width = 58
    message = f"Welcome to LMDB DATASET, version {version}"
    padding = (width - len(message) - 2) // 2  # -2 for the border chars
    
    return (
        "-" * width + "\n"
        f"|{' ' * padding}{message}{' ' * (width - padding - len(message) - 2)}|\n"
        + "-" * width
    )

@unique
class Command(str, Enum):
    WRITE = "write"
    READ = "read"
    RECOVERY = "recovery"
    VER = "version"
    HELP = "help"


def main():
    command = sys.argv.pop(1) if len(sys.argv) != 1 else Command.HELP
    if command == Command.WRITE:
        run_writer()
    elif command == Command.READ:
        print("Read command not implemented yet.🙁")
    elif command == Command.RECOVERY:
        run_recovery()
    elif command == Command.VER:
        WELCOME = create_welcome_message(VERSION)
        print(WELCOME)
    elif command == Command.HELP:
        print(USAGE)
    else:
        raise NotImplementedError(f"Unknown command: {command}.")

if __name__ == "__main__":
    main()

