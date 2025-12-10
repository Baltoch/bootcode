import os
from google.genai import types

def get_files_info(working_directory, directory="."):
    try:
        res = []
        working_directory = os.path.realpath(working_directory)
        path = os.path.realpath(os.path.join(working_directory, directory))
        if not os.path.exists(path) or os.path.commonprefix([path, working_directory]) != working_directory:
            return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'
        if not os.path.isdir(path):
            return f'Error: "{directory}" is not a directory'
        with os.scandir(path) as it:
            for entry in it:
                if not entry.name.startswith('.') and not entry.name.startswith('__'):
                    res.append(f"- {entry.name}: file_size={os.path.getsize(entry.path)} bytes, is_dir={entry.is_dir()}")
        return "\n".join(res)
    except Exception as e:
        return f"Error:{e}"
    
schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in the specified directory along with their sizes, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="The directory to list files from, relative to the working directory. If not provided, lists files in the working directory itself.",
            ),
        },
    ),
)