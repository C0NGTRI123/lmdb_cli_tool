from dataclasses import dataclass, field
from typing import Literal, Optional, Union, List


@dataclass
class ReadArguments:
    r"""
    Dataclass for read arguments
    """
    
    lmdb_dir_path: Optional[Union[str, List[str]]] = field(
        default=None,
        metadata={"help": "Path to the directory containing images"},
    )
    
    do_visualize: Optional[bool] = field(
        default=False,
        metadata={"help": "Whether to visualize the images"},
    )
