import os
from google.genai import types
from config import TRUNCATED_FILE_LENGTH

def get_file_content(working_directory, file_path):
    try:
        working_directory = os.path.realpath(working_directory)
        path = os.path.realpath(os.path.join(working_directory, file_path))
        if not os.path.exists(path) or os.path.commonprefix([path, working_directory]) != working_directory:
            return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'
        if not os.path.isfile(path):
            return f'Error: File not found or is not a regular file: "{file_path}"'
        with open(path) as f:
            res = f.read()
            if len(res) > TRUNCATED_FILE_LENGTH:
                res = f'{res[:TRUNCATED_FILE_LENGTH]} ...File "{file_path}" truncated at {TRUNCATED_FILE_LENGTH}'
            return res
    except Exception as e:
        return f"Error:{e}"
    
schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Reads the content of the specified file",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the file to read from, relative to the working directory.",
            ),
        },
    ),
)