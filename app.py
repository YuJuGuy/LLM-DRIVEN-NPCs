from reflectionmanger import ReflectionManager
from groq import Groq
import json
import os
from dotenv import load_dotenv
load_dotenv()


manager = ReflectionManager()
load_reflections = manager.get_reflections()
print(load_reflections)
MODEL = 'llama3-70b-8192'
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
def reflection_frank(text, description):
    instructions = """You are a reflection manager for a character in a game called Frank. Frank is a blacksmith who crafts weapons and armor for adventurers.
        Your task is to help Frank reflect on his interactions with his customers. You will see a series of conversations between Frank and his customers.
        So you will be proivded with input and output of Frank conversation with his customers. You will decide wether to save the information or not.
        
        When you receive a message, you perform a sequence of steps consisting of:
        1. Analyze the input and output of the conversation.
        2. Decide if the information is important and should be remembered.
        3. If the information is important, save it to the memory.
        4. If the information is not important, do not save it to the memory.
        5. If the information is already in the memory, do not save it again.
        6. You can also edit or delete the information in the memory.
        
        
        Rules:
        1. You can only save the information that is important.
        2. You can only save the information once.
        3. If the information is already saved, do not save it again just output that it is already saved.
        
        You will be provided with the tools to add edit and delete the information in the memory."""
    
    messages=[
        {"role": "system", "content": f"YOU MUST FOLLOW THESE INSTRUCTIONS CAREFULLY.\n{instructions}\n1. Write the reflections from a thinking pov not just saving it as it is."},
        {"role": "user", "content": f"Here is the text already saved:\n1. {load_reflections}\n1. And Here is the text: {text} by {description}. Remember if the memory already has the text do not save it again just output pass."}
    ]
    tools = [
        {
            "type": "function",
            "function": {
                "name": "add_reflection",
                "description": "add the reflection to the memory",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "The refelction you want to add.",
                        }
                    },
                },
            },
        }
    ]
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=tools,
        tool_choice="auto",
        max_tokens=4096
    )
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls
    if tool_calls:

        available_functions = {
            "add_reflection": manager.add_reflection,
        }  

        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            function_response = function_to_call(**function_args)
            print(function_response)
    
if __name__ == "__main__":
    chat_completion = reflection_frank("You know what Joesan, I love fish", "Frank")
    print(chat_completion)
    