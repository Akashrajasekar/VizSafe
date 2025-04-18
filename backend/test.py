import tempfile

# Get the path to the system's temporary directory
temp_dir = tempfile.gettempdir()
print(f"Temporary directory path: {temp_dir}")
