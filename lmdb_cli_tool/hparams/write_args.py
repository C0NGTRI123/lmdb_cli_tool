from dataclasses import dataclass, field
from typing import Literal, Optional


@dataclass
class WriteArguments:
    r"""
    Dataclass for write arguments
    """
    
    image_dir_path: Optional[str] = field(
        default=None,
        metadata={"help": "Path to the directory containing images"},
    )
    json_dir_path: Optional[str] = field(
        default=None,
        metadata={"help": "Path to the directory containing JSON files"},
    )
    output_dir: Optional[str] = field(
        default=None,
        metadata={"help": "Path to the output directory"},
    )
    json_format: Optional[Literal["scene_text", "layoutllm"]] = field(
        default=None,
        metadata={"help": "The format of the JSON files"},
    )
