import os
import queue
import multiprocessing as mp
from multiprocessing import Queue
import traceback
from typing import List, Tuple, Dict, Any, Union

import lmdb
from PIL import Image
import psutil
from loguru import logger

from utils.utils import bytes2str, pil2bytes, str2bytes, bytes2pil
from base.lmdb_base import LMDBBaseReader, LMDBBaseWriter, LMDBBaseRecovery


class LMDBWriter(LMDBBaseWriter):
    def __init__(self, output_path: str, map_size: int = 1099511627776, num_workers: int = None, resume=False):
        """
        Initialize LMDB Writer
        
        :param output_path: Path for storing LMDB database
        :param map_size: Maximum size of LMDB environment (defaults to 10% of available memory)
        :param num_workers: Number of processing workers
        :param resume: Resume writing from existing counter
        """
        self.output_path = output_path

        # Dynamically set map_size based on available system memory
        if map_size is None:
            total_memory = psutil.virtual_memory().total
            map_size = int(total_memory * 0.1)
        self.map_size = map_size

        self.num_workers = num_workers or max(1, mp.cpu_count() - 1)
        os.makedirs(output_path, exist_ok=True)

        if not resume and os.path.exists(os.path.join(output_path, "data.mdb")):
            logger.info("Clearing existing database...")
            os.remove(os.path.join(output_path, "data.mdb"))
            os.remove(os.path.join(output_path, "lock.mdb"))
            os.remove(os.path.join(output_path, "lmdb.lst"))
        
        # Initialize LMDB environment
        self.env = lmdb.open(
            output_path,
            map_size=self.map_size,
            metasync=False,
            sync=False
        )
        
        with self.env.begin(write=True) as txn:
            if resume:
                # Load existing counter and metadata
                self.counter = int(txn.get(b"__counter__", b"0"))
                logger.info(f"Resuming from counter {self.counter}")
            else:
                # Initialize new database
                self.counter = 0
                # Set initial metadata
                txn.put(b"__counter__", b"0")

        self.file_list_path = os.path.join(output_path, "lmdb.lst")

    def create_dataset(self, datasets: List[Tuple[str, str, str]], batch_size: int = 1000):
        """
        Create LMDB dataset using multiprocessing
        
        :param datasets: List of (image_path, label, type) tuples
        :param batch_size: Number of images to process in each batch
        """
        # Create queues
        input_queue = Queue()
        output_queue = Queue()
        
        # Populate input queue
        for dataset in datasets:
            input_queue.put(dataset)
        
        # Add termination signals
        for _ in range(self.num_workers):
            input_queue.put(None)
        
        def worker(input_q, output_q):
            while True:
                try:
                    item = input_q.get(timeout=1)
                    if item is None:
                        break
                    
                    try:
                        # Process the image
                        with Image.open(item[0]) as img:
                            image_bin = pil2bytes(img)
                        
                        # Prepare processed data
                        processed = {
                            'image_bin': image_bin,
                            'image_path': os.path.basename(item[0]),
                            'label': item[1],
                        }
                        output_q.put(processed)
                    
                    except Exception as e:
                        logger.error(f"Processing error for {item[0]}: {e}")
                        traceback.print_exc()
                
                except queue.Empty:
                    break
        
        # Start workers
        processes = []
        for _ in range(self.num_workers):
            p = mp.Process(target=worker, args=(input_queue, output_queue))
            p.start()
            processes.append(p)
        
        # Collect and write results
        try:
            processed_count = 0
            cache = {}
            
            while processes:
                try:
                    processed_image = output_queue.get(timeout=1)
                    
                    # Write processed image to cache
                    cache[f"image-{self.counter:09d}".encode()] = processed_image['image_bin']
                    cache[f"label-{self.counter:09d}".encode()] = str2bytes(processed_image['label'])

                    with open(self.file_list_path, "a") as f:
                        f.write("{}\n".format(processed_image['image_path']))

                    self.counter += 1
                    processed_count += 1
                    
                    # Write cache if it grows too large
                    if len(cache) >= batch_size:
                        self._write_cache(cache)
                        cache = {}
                    
                    # Log progress
                    if processed_count % 1000 == 0:
                        logger.info(f"Processed {processed_count} images")
                
                except queue.Empty:
                    if not any(p.is_alive() for p in processes):
                        break
                
                processes = [p for p in processes if p.is_alive()]
        
        finally:
            # Terminate processes
            for p in processes:
                p.terminate()
                p.join()
            
            # Write remaining cache
            if cache:
                self._write_cache(cache)
            
            self.close()
        
        logger.info(f"Total images processed: {processed_count}")
        

    def _write_cache(self, cache: Dict[bytes, bytes]):
        """Write cache to LMDB with metadata"""
        try:
            with self.env.begin(write=True) as txn:
                for k, v in cache.items():
                    txn.put(k, v)
                # Update metadata
                txn.put(b"__counter__", str(self.counter).encode())
        except Exception as e:
            logger.error(f"Error writing cache: {e}")
            raise

    def close(self):
        """Close LMDB environment"""
        try:
            self.env.close()
        except Exception as e:
            logger.error(f"Error closing environment: {e}")


class LMDBReader(LMDBBaseReader):
    def __init__(self, lmdb_paths: Union[str, List[str]], readonly: bool = True):
        """
        Initialize LMDB reader for single or multiple LMDB paths
        
        Args:
            lmdb_paths: Single path string or list of paths to LMDB directories
            readonly: Whether to open LMDB in readonly mode (default: True)
        """
        self.paths = [lmdb_paths] if isinstance(lmdb_paths, str) else lmdb_paths
        self.envs = []
        self.lengths = []
        
        try:
            # Open all environments
            for path in self.paths:
                if not os.path.exists(path):
                    raise FileNotFoundError(f"LMDB path not found: {path}")
                env = lmdb.open(path, readonly=readonly)
                self.envs.append(env)
                
                with env.begin(write=False) as txn:
                    length = int(txn.get(b"__counter__", b"0"))
                    self.lengths.append(length)
            
            self.total_length = sum(self.lengths)
            
            # Only calculate cumulative lengths for multiple DBs
            if len(self.paths) > 1:
                self.cumulative_lengths = [sum(self.lengths[:i]) for i in range(len(self.lengths) + 1)]
            
        except Exception as e:
            # Clean up on initialization failure
            self.close()
            raise e

    def __len__(self):
        return self.total_length

    def __getitem__(self, idx):
        if idx < 0 or idx >= self.total_length:
            raise IndexError(f"Index {idx} out of range for total length {self.total_length}")

        if len(self.envs) == 1:
            env = self.envs[0]
            local_idx = idx
        else:
            lmdb_index = next(i for i in range(len(self.cumulative_lengths) - 1)
                            if self.cumulative_lengths[i] <= idx < self.cumulative_lengths[i + 1])
            env = self.envs[lmdb_index]
            local_idx = idx - self.cumulative_lengths[lmdb_index]

        with env.begin(write=False) as txn:
            image_key = f"image-{local_idx:09d}".encode()
            label_key = f"label-{local_idx:09d}".encode()
            
            image_bin = txn.get(image_key)
            label_bin = txn.get(label_key)
            
            if image_bin is None:
                raise KeyError(f"Image not found for index {idx}")

            return (
                bytes2pil(image_bin),
                bytes2str(label_bin),
            )

    def close(self):
        """Close all LMDB environments"""
        for env in self.envs:
            try:
                env.close()
            except Exception as e:
                logger.error(f"Error closing LMDB environment: {e}")
        self.envs = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class LMDBRecovery(LMDBBaseRecovery):
    def __init__(self, lmdb_path: str, readonly: bool = True):
        """
        Initialize LMDB reader for single or multiple LMDB paths
        
        Args:
            lmdb_paths: Single path string or list of paths to LMDB directories
            readonly: Whether to open LMDB in readonly mode (default: True)

        Output:
            Data recovery from LMDB database (image)
        """
        self.output_path = os.path.basename(lmdb_path).replace("_lmdb", "_recovered")
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path, exist_ok=True)
        if not os.path.exists(lmdb_path):
            raise FileNotFoundError(f"LMDB path not found: {lmdb_path}")
        self.env = lmdb.open(lmdb_path, readonly=True)
        with self.env.begin(write=False) as txn:
            self.counter = int(txn.get(b"__counter__", b"0"))
        self.list_file_path = os.path.join(lmdb_path, "lmdb.lst")
        self.file_list = self._load_list_file()

    def _load_list_file(self):
        """Load list file for image paths"""
        with open(self.list_file_path, "r") as f:
            file_list = f.read().splitlines()
        return file_list

    def recover_images(self):
        """Recover images from LMDB database base on self.file_list"""
        for idx, image_path in enumerate(self.file_list):
            with self.env.begin(write=False) as txn:
                image_key = f"image-{idx:09d}".encode()
                image_bin = txn.get(image_key)
                if image_bin is None:
                    logger.error(f"Image not found for index {idx}")
                    continue
                with open(os.path.join(self.output_path, image_path), "wb") as f:
                    f.write(image_bin)
            logger.info(f"Recovered image {idx}/{self.counter}")
        logger.info(f"Total images recovered: {len(self.file_list)}")
        