from mcp.server.fastmcp import FastMCP
import os
import re
import glob

mcp = FastMCP("log-reader")

def _get_files_in_rotation(base_path: str):
    """
    Finds all rotated files for a given base path.
    Assumes standard rotation: file.log, file.log.1, file.log.2, etc.
    """
    files = []
    if os.path.exists(base_path):
        files.append(base_path)
    
    # Simple check for .1, .2, etc. and other common patterns could be added here
    # For now, we look for base_path.* and filter
    # This might catch unrelated files if naming is tricky, but standard logrotate is predictable.
    directory = os.path.dirname(base_path) or "."
    basename = os.path.basename(base_path)
    
    # We want to catch file.log.1, file.log.2
    # We shouldn't catch file.log.gz for this simple version unless we add support
    candidates = glob.glob(f"{base_path}.*")
    
    rotated = []
    for cand in candidates:
        # Check if suffix is integer
        suffix = cand.replace(base_path + ".", "")
        if suffix.isdigit():
            rotated.append((int(suffix), cand))
    
    # Sort by index (1 is newest rotated, 2 is older)
    rotated.sort(key=lambda x: x[0])
    
    # Result list: [main_file, .1, .2, ...]
    # But wait, read_log typically wants newest lines.
    # Newest data is in base_path, then .1 is older, .2 is older.
    # So the order for reading "last N lines" should be Main -> .1 -> .2
    return files + [x[1] for x in rotated]

@mcp.tool()
def read_log(path: str, lines: int = 100) -> str:
    """
    Reads the last N lines of a log file, including rotated files if necessary.
    
    Args:
        path: Absolute path to the log file
        lines: Number of lines to read from the end (default: 100)
    """
    files = _get_files_in_rotation(path)
    if not files:
        return f"Error: File not found at {path}"
    
    collected_lines = []
    lines_needed = lines
    
    # We traverse files from newest (main) to oldest (.1, .2)
    # until we have enough lines.
    for file_path in files:
        if lines_needed <= 0:
            break
            
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                # Read all lines is safest for simple logic, though inefficient for massive files
                # Optimization: use seek/tail logic if needed, but keeping it simple for now
                file_lines = f.readlines()
                
                # We want the *end* of the newest file, and then the *end* of the older file (which comes before structurally)
                # Actually, logically:
                # Log Stream: [Oldest File Data] ... [Newest File Data]
                # We want the TAIL of the Stream.
                
                # If we take lines from Newest, we take from the bottom.
                # If we still need lines, we go to Previous (.1) and take from bottom there too?
                # Yes, because .1 was the main file previously.
                
                part = file_lines[-lines_needed:]
                # We prepend because we are going backwards in time (Main -> .1 -> .2)
                collected_lines = part + collected_lines
                lines_needed -= len(part)
        except Exception as e:
            # If we fail to read a rotated file, we just skip it or stop?
            # Let's note it but continue
            pass

    return "".join(collected_lines)

@mcp.tool()
def read_log_chunk(path: str, offset: int, max_bytes: int = 4096) -> str:
    """
    Reads a chunk of the log file starting from a specific byte offset.
    Useful for tailing a file.
    
    Args:
        path: Absolute path to the log file
        offset: Byte offset to start reading from
        max_bytes: Maximum number of bytes to read (default: 4096)
        
    Returns:
        JSON string containing "content" and "next_offset".
        Format: {"content": "...", "next_offset": 12345}
    """
    if not os.path.exists(path):
        return f"Error: File not found at {path}"
        
    try:
        with open(path, 'rb') as f: # Read binary to handle offsets accurately
            f.seek(offset)
            data = f.read(max_bytes)
            new_offset = f.tell()
            
            # Decode carefully, might cut a char in half?
            # 'replace' strategy is safest for logs
            text = data.decode('utf-8', errors='replace')
            
            import json
            return json.dumps({
                "content": text,
                "next_offset": new_offset
            })
    except Exception as e:
        return f"Error reading log chunk: {str(e)}"

@mcp.tool()
def search_log(path: str, pattern: str, is_regex: bool = False) -> str:
    """
    Searches for a pattern in a log file.
    
    Args:
        path: Absolute path to the log file
        pattern: String pattern to search for
        is_regex: If True, treats pattern as a regular expression.
    """
    if not os.path.exists(path):
        return f"Error: File not found at {path}"
    
    matches = []
    try:
        # Pre-compile regex if needed
        regex = None
        if is_regex:
            try:
                regex = re.compile(pattern)
            except re.error as e:
                return f"Error: Invalid regex pattern: {str(e)}"

        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            for line in f:
                if is_regex:
                    if regex.search(line):
                        matches.append(line)
                else:
                    if pattern in line:
                        matches.append(line)
        
        if not matches:
            return "No matches found."
            
        return "".join(matches)
    except Exception as e:
        return f"Error searching log file: {str(e)}"

if __name__ == "__main__":
    mcp.run()
