from dataclasses import dataclass


@dataclass
class Config:
    """Configuration class for the S2ST system."""
    # Audio settings
    sample_rate: int = 44100
    chunk_duration: float = 15.0  # seconds
    silence_threshold: float = 2.0

    # Performance settings
    max_queue_size: int = 20
    processing_timeout: float = 10.0
    
    # Languages
    source_language: str = "en"
    target_language: str = "pt"

 