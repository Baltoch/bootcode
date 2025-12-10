import os
import subprocess
from google.genai import types

def run_python_file(working_directory, file_path, args=[]):
    try:
        working_directory = os.path.realpath(working_directory)
        path = os.path.realpath(os.path.join(working_directory, file_path))
        if os.path.commonprefix([path, working_directory]) != working_directory:
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
        if not os.path.exists(path):
            return f'Error: File "{file_path}" not found.'
        if not path.endswith(".py"):
            return f'Error: "{file_path}" is not a Python file.'
        out = subprocess.run(args=["uv", "run", path, *args], timeout=30, capture_output=True, cwd=working_directory, text=True)
        if out: return f"STDOUT: {out.stdout}\n\nSTDERR: {out.stderr}{'\n\n' + 'Process exited with code ' + str(out.returncode) if out.returncode != 0 else ''}"
        return "No output produced"
    except Exception as e:
        return f"Error: executing Python file: {e}"
    
schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Run the specified Python file, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the Python file to run, relative to the working directory.",
            ),
        },
    ),
)