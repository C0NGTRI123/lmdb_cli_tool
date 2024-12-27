import multiprocessing as mp
from multiprocessing import Queue
import traceback
from typing import List


def multiprocess_exec(func, args: List, num_processes: int) -> List:
    """
    Execute a function in parallel using multiple processes.
    
    Args:
        func: Function to execute in parallel
        args: List of arguments to process
        num_processes: Number of parallel processes to use
    
    Returns:
        List of results from all processes
    """
    # Create result queue
    result_queue = Queue()
    
    # Calculate chunk size for splitting work
    chunk_size = len(args) // num_processes + (1 if len(args) % num_processes else 0)
    
    # Split args into chunks
    arg_chunks = [args[i:i + chunk_size] for i in range(0, len(args), chunk_size)]
    
    def worker(chunk, queue):
        """Worker function that processes a chunk of arguments"""
        try:
            results = [func(arg) for arg in chunk]
            queue.put(results)
        except Exception as e:
            queue.put((e, traceback.format_exc()))
    
    # Create and start processes
    processes = []
    for chunk in arg_chunks:
        p = mp.Process(target=worker, args=(chunk, result_queue))
        p.start()
        processes.append(p)
    
    # Wait for all processes to complete
    for p in processes:
        p.join()
    
    # Collect results
    results = []
    for _ in range(len(arg_chunks)):
        chunk_result = result_queue.get()
        if isinstance(chunk_result, tuple) and isinstance(chunk_result[0], Exception):
            raise chunk_result[0]
        results.extend(chunk_result)
    
    return results
    