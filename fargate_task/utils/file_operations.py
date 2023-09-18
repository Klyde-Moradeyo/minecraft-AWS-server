import hcl
import tempfile
from logger import setup_logging

# Setting up logging
logger = setup_logging()

def convert_bytes(byte_value):
    # Conversion factors
    KB = 1024
    MB = KB ** 2
    GB = KB ** 3
    
    # Calculate sizes
    size_kb = byte_value / KB
    size_mb = byte_value / MB
    size_gb = byte_value / GB
    
    return {
        "size_bytes": byte_value,
        "size_kb": size_kb,
        "size_mb": size_mb,
        "size_gb": size_gb
    }

def read_from_tf_vars(var, file_path):
    try:
        with open(file_path, 'r') as f:
            obj = hcl.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Cannot open {file_path}")
    except Exception as e:
        raise ValueError(f"Error parsing HCL: {e}")
        
    if var not in obj['variable']:
        raise ValueError(f"Cannot find {var} in {file_path}")

    return obj['variable'][var]["default"]

def write_to_tmp_file(content):
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
        temp_file.write(content)
        temp_file.flush() # Ensure any buffered data is written to the file
        dir = temp_file.name
    return dir

def check_mc_bundle_size(file_size, api_url):
    try:
        MAX_BUNDLE_SIZE_MB = 1600
        BUFFER = 0.15 
        BUNDLE_SIZE_LIMIT = MAX_BUNDLE_SIZE_MB - (MAX_BUNDLE_SIZE_MB * BUFFER) # Safe Guard of 15% of the size limit

        logger.info(f"Minecraft Bundle size: {convert_bytes(file_size)['size_gb']} GB")

        if convert_bytes(file_size)["size_mb"] > BUNDLE_SIZE_LIMIT:
            data = {"command": "mc_world_archive"}
            response = send_to_api(data, api_url)
            return response
        else:
            logger.info(f"Minecraft Bundle size within permissible limit.")
            
    except Exception as e:
        logger.error(f"An error occurred while checking Minecraft bundle size: {str(e)}")
        raise

