import os
import sys
from google import genai
from google.genai import types
from dotenv import load_dotenv
from functions import *

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

system_prompt = """
You are a helpful AI coding agent.

When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

- List files and directories
- Read file contents
- Execute Python files with optional arguments
- Write or overwrite files

All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.

You have access to the directory of a calculator Python app.
You should start by calling functions until you have enough information to give a final response. You may want to check the current directory by using the get_files_info method first. Do not give a response until you are done using tools.
"""

def call_function(function_call_part, verbose=False):
    if verbose:
        print(f"Calling function: {function_call_part.name}({function_call_part.args})")
    else:
        print(f" - Calling function: {function_call_part.name}")
    function_call_part.args["working_directory"] = "calculator"
    match function_call_part.name:
        case "get_file_content":
            function_result = get_file_content(**function_call_part.args)
        case "get_files_info":
            function_result = get_files_info(**function_call_part.args)
        case "run_python_file":
            function_result = run_python_file(**function_call_part.args)
        case "write_file":
            function_result = write_file(**function_call_part.args)
        case _:
            return types.Content(
                role="tool",
                parts=[
                    types.Part.from_function_response(
                        name=function_call_part.name,
                        response={"error": f"Unknown function: {function_call_part.name}"},
                    )
                ],
            )
    return types.Content(
        role="tool",
        parts=[
            types.Part.from_function_response(
                name=function_call_part.name,
                response={"result": function_result},
            )
        ],
    )

def main():
    if len(sys.argv) < 2:
        print('Usage: uv main.py "<prompt>"')
        sys.exit(1)
    verbose = len(sys.argv) > 2 and "--verbose" in sys.argv[1:]
    user_prompt = sys.argv[1]
    if verbose and user_prompt == "--verbose":
        user_prompt = sys.argv[2]
    messages = [
        types.Content(role="user", parts=[types.Part(text=sys.argv[1])])
    ]
    available_functions = types.Tool(
        function_declarations=[
            schema_get_files_info,
            schema_write_file,
            schema_run_python_file,
            schema_get_file_content,
        ]
    )
    if verbose:
        print("User prompt: " + user_prompt)
    for _ in range(20):
        try:
            resp = client.models.generate_content(
                model = "gemini-2.5-flash-lite",
                contents=messages,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    tools=[available_functions],
                )
            )
            for candidate in resp.candidates if resp.candidates else []:
                if candidate.content: 
                    messages.append(candidate.content)
            if resp.function_calls:
                for function_call_part in resp.function_calls:
                    res = call_function(function_call_part, verbose)
                    try:
                        messages.append(types.Content(role="user", parts=[res.parts[0]])) # type: ignore
                        res = res.parts[0].function_response.response # type: ignore
                        if verbose: print(f"-> {res}")
                    except Exception as e:
                        raise Exception(f"Fatal Error function call doesn't contain .parts[0].function_response.response:{e}")
            elif resp.text:
                print(f"Response: {resp.text}")
                if verbose:
                    print("Prompt tokens: " + str(resp.usage_metadata.prompt_token_count if resp.usage_metadata else ""))
                    print("Response tokens: " + str(resp.usage_metadata.candidates_token_count if resp.usage_metadata else ""))
                break
        except Exception as e:
            print(e)
            return


if __name__ == "__main__":
    main()
