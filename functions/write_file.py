import os
from google.genai import types

def write_file(working_directory, file_path, content):
    try:
        working_directory = os.path.realpath(working_directory)
        path = os.path.realpath(os.path.join(working_directory, file_path))
        if os.path.commonprefix([path, working_directory]) != working_directory:
            return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'
        with open(path, "w") as f:
            f.write(content)
            return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
    except Exception as e:
        return f"Error:{e}"
    
schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Writes the specified content to the file at the specified file path, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "content": types.Schema(
                type=types.Type.STRING,
                description="The content to write to the file",
            ),
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the file to write to, relative to the working directory.",
            ),
        },
    ),
)