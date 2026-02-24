import os
import time
import json
import logging
import argparse
from pathlib import Path

def setup_gc_logger(log_dir: str) -> logging.Logger:
    """Configures a dedicated, file-only logger for artifact management."""
    os.makedirs(log_dir, exist_ok=True)
    logger = logging.getLogger("ArtifactManager")
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        formatter = logging.Formatter('%(asctime)s | %(levelname)-8s | ArtifactManager | %(message)s')
        file_handler = logging.FileHandler(os.path.join(log_dir, 'execution.log'))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    return logger

def get_directory_size(target_dir: Path) -> float:
    """Computes the total recursive size of a directory in Megabytes."""
    total_size = sum(f.stat().st_size for f in target_dir.glob('**/*') if f.is_file())
    return total_size / (1024 * 1024)

def execute_garbage_collection(target_dir_str: str, max_mb: float, target_mb: float, logger: logging.Logger):
    """
    Executes Least Recently Used (LRU) purge against the target directory.
    Outputs telemetrics as strictly formatted JSON to stdout.
    """
    t_start = time.perf_counter()
    target_dir = Path(target_dir_str)
    
    payload = {
        "status": "Unknown",
        "directory": target_dir_str,
        "files_purged": 0,
        "size_before_mb": 0.0,
        "size_after_mb": 0.0,
        "quota_limit_mb": max_mb,
        "execution_time_ms": 0.0
    }

    if not target_dir.exists():
        logger.error(f"Target directory {target_dir_str} does not exist.")
        payload["status"] = "Error"
        payload["description"] = "Target directory not found."
        print(json.dumps(payload))
        return

    current_mb = get_directory_size(target_dir)
    payload["size_before_mb"] = round(current_mb, 2)
    payload["size_after_mb"] = round(current_mb, 2)
    
    # Storage is within nominal operational bounds
    if current_mb <= max_mb:
        logger.info(f"Storage nominal. Current: {current_mb:.2f} MB / Limit: {max_mb:.2f} MB.")
        payload["status"] = "Nominal"
        payload["execution_time_ms"] = round((time.perf_counter() - t_start) * 1000, 2)
        print(json.dumps(payload))
        return

    # Quota exceeded. Initiate LRU Purge.
    logger.info(f"Storage quota exceeded ({current_mb:.2f} MB > {max_mb:.2f} MB). Initiating purge.")
    payload["status"] = "Purged"
    
    files = [(f, f.stat().st_mtime) for f in target_dir.glob('**/*') if f.is_file()]
    files.sort(key=lambda x: x[1]) # Sort ascending by modified time (oldest first)
    
    bytes_to_recover = (current_mb - target_mb) * 1024 * 1024
    bytes_recovered = 0
    files_deleted = 0

    for file_path, _ in files:
        if bytes_recovered >= bytes_to_recover:
            break
            
        try:
            file_size = file_path.stat().st_size
            file_path.unlink()
            bytes_recovered += file_size
            files_deleted += 1
        except Exception as e:
            logger.error(f"Failed to delete {file_path.name}: {str(e)}")

    new_mb = get_directory_size(target_dir)
    
    payload["files_purged"] = files_deleted
    payload["size_after_mb"] = round(new_mb, 2)
    payload["execution_time_ms"] = round((time.perf_counter() - t_start) * 1000, 2)

    logger.info(f"GC Complete. Purged {files_deleted} files. New size: {new_mb:.2f} MB.")
    print(json.dumps(payload))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Artifact Garbage Collection")
    parser.add_argument("--dir", "-d", type=str, default="./output/images", help="Target directory for GC.")
    parser.add_argument("--limit", "-l", type=float, default=500.0, help="Maximum storage threshold in MB.")
    parser.add_argument("--target", "-t", type=float, default=450.0, help="Target storage size in MB after purge.")
    
    args = parser.parse_args()
    
    log_directory = "./logs"
    gc_logger = setup_gc_logger(log_directory)
    
    execute_garbage_collection(args.dir, args.limit, args.target, gc_logger)