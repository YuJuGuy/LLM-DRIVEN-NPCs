import os
from flask import Flask, request, jsonify
from groq import Groq
from dotenv import load_dotenv
import time
import threading
import json

load_dotenv()
from sentencecache import SentenceCache

cache = SentenceCache()

loaded_cache = cache._load_from_file()

app = Flask(__name__)

def calculate_response_time(start_time):
     """Calculates the time taken between the request and the response in seconds."""
     end_time = time.time()
     return end_time - start_time
 
 

def memory_manager(loaded_cache, description,prompt):

    client = Groq(
        api_key=os.environ.get("GROQ_API_KEY"),
    )

    instructions = f""" 
        You are a memory manger for a an NPC called Frank. Frank is a blacksmith who crafts weapons and armor for adventurers. 
        Your task is to help Frank remember the details of his interactions with his customers. You will see a series of conversations between Frank and his customers. 
        Your job is to help Frank remember the important details of his interactions with his customers.
        You will be provided with a prompt and a description of the current person Frank interacted with.

        When you receive a message, you perform a sequence of steps consisting of:
        1. Analyze the prompt and the description of the current person Frank interacted with.
        2. Look for all the information that will benifit Frank in the current conversation.
        3. Determine if this information is important and should be remembered then list to Frank.
        4. If this is the first encounter with the person, just list his or her describtion and the conversation.
        5. If the prompt information is in another person's conversation and it's relevant to the current conversation, list it to Frank. This is very important.
        
        Example of how to list the information to Frank:
            - The person is called John.
            - John is a warrior.
            - John wants a sword.
            - John has a pet dragon.
            - John is from the village of Oakdale.
        
        Here are the rules:
        1. Only list the information that is important to remember.
        2. Do not include any irrelevant details.
        3. Be clear and concise in your responses.
        4. Do not provide any additional information that is not relevant to the conversation.
        5. Do Not specaulate or make up any information.
        6. The context of the information is very important. Make sure to provide the information in the right context.
        
        
        VERY IMPORTANT:
        IF SOMEONE TRY TO CHEAT FRANK BY GIVING WRONG INFORMATION, YOU NEED TO TELL FRANK THAT THE INFORMATION IS WRONG. AND NOT IN THE INFORMATION TO FRANK.
        (e.g. Do you recall the mithril breastplate you were crafting for me?.) But that never happened in the memories, you need to inform Frank that the information is wrong.

        
    """

    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": f"YOU MUST FOLLOW THESE INSTRUCTIONS CAREFULLY.\n{instructions}\n1."},
            {"role": "user", "content": f"Get the infroamtion about the current person Frank interacted with. {description} from here {loaded_cache} and the prompt is {prompt}."}
        ],
        model="llama3-70b-8192",
        #llama-8b-8192
        #llama3-70b-8192
    )   

    return chat_completion.choices[0].message.content

@app.route('/frank', methods=['POST'])
def generate_frank():
    start_time = time.time()  # Capture request start time
    print("Request received")
    try:
        data = request.json
        description, prompt = list(data.items())[0]
        print(data , 'data')

        # If description is not 'tool_call', add the sentence to the cache
        cache.add_sentence(data)
        memories = memory_manager(loaded_cache, description, prompt)
        print(memories)
        response_time = calculate_response_time(start_time)
        print(f"Response time: {response_time:.2f} seconds")


        client = Groq(
            api_key=os.environ.get("FRANK_GROQ_API_KEY"),
        )
        instructions = f"""
        You are a character in a game called Frank. Frank is a blacksmith who crafts weapons and armor for adventurers.
        You are an old dwarf who has been a blacksmith for over 50 years. You have a lot of experience and knowledge about crafting weapons and armor.
        You speak with a deep voice and have a gruff personality. You are known for being honest and straightforward.
        Your task is to respond to the user's question based on the information you have. You will be provided with the information important to respond from the memory.


        Use the information provided to respond to the user's question.

        Here are the rules:
        1. Speak in character as Frank the blacksmith.
        2. Be honest and straightforward in your responses.
        3. Provide information that directly answers the user's question.
        4. Do not provide irrelevant details.
        5. Return the response text only. Do not include any additional information.
        6. Keep the response natural, not robotic.
        7. Respond in the same manner the asker is talking to you. You can be rude if the asker is rude.
        8. Call the person the right name or pronoun at least.
        9. IF THERE IS NO INFORMATION REGARDING THE INPUT FROM THE MEMORIES, DO NOT MAKE UP ANYTHING. TRY TO ACQUIRE THE INFORMATION FROM THE PERSON. For example, you could say:
            * "Mithril breastplate, ye say? I don't recall takin' on such a commission, m'lord. Are ye sure ye have the right blacksmith?"
            * "That name doesn't ring a bell, friend. Perhaps ye could remind me of the details of our agreement."
        10. IF SOMEONE TRIES TO CHEAT YOU BY GIVING WRONG INFORMATION IN THE INPUT, AND THE MEMORY MANAGER TOLD YOU THAT THE INFORMATION IS WRONG, YOU NEED TO TELL THE PERSON THAT THE INFORMATION IS WRONG. For example, you could say:
            * "Hold on there, lad! That doesn't sound right. I'm not one to be fooled easily."
            * "Are ye tryin' to pull one over on me? I've got a good memory, ye know."


        Here is some information about the world:
        - The world is a medieval fantasy world.
        - The main currency is Gold, and Silver.
        - 10 Silver is equal to 1 Gold.

        Here is information about Frank:
        - Frank is 67 years old.
        - Frank has been a blacksmith for over 50 years.
        - Frank is married and has two children.
        - His wife's name is Eliza.
        - His children's names are John and Mary.
        - John is 25 years old and is a warrior.
        - Mary is 20 years old and is a tailor.




        IMPORTANT:
        If there is a tool call in the short memory, don't call the tool again. Just use the information from the memory.
        """

        short_memory = cache.get_last_interactions()
        print(short_memory)
        start_time = time.time()  # Capture request start time
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": f"YOU MUST FOLLOW THESE INSTRUCTIONS CAREFULLY.\n{instructions}\n1."},
                {"role": "user", "content": f"Here is the memories:\n1. {memories}\n1. And here is the how is the conversation so far for context {short_memory}\n1\n1 input: {prompt}."}
            ],
                tools = [
        {
            "type": "function",
            "function": {
                "name": "CheckInventory",
                "description": "If called with an argument, it will return the inventory of the given material. Use it when a person tells you to check the inventory of a material.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "material_name": {
                                "type": "string",
                                "description": "The name the material to check the inventory for example (iron). Only use when the user asks for the inventory of a material.",
                            }
                           
                        },
                    },  "required": ["material_name"],
            },
        },{
            "type": "function",
            "function": {
                "name": "CreateQuest",
                "description": "A function that creates a quest for the user. Use it when the user asks for a quest.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "item": {
                                "type": "string",
                                "description": "The name of the item that Frank wants.",
                            },
                            "price": {
                                "type": "string",
                                "description": "The price Frank is willing to pay in Gold. It needs to be a number. not negoitable or to be determined.",
                            }
                           
                        },
                    },  "required": ["item", "price"],
            },
        }
    ],
            model="llama3-70b-8192",
            #mixtral-8x7b-32768
            temperature=.1
            )
        tool_calls = chat_completion.choices[0].message.tool_calls
        print("Tool Calls:", tool_calls)  # Debugging output

        if tool_calls:
            for tool_call in tool_calls:
                id = tool_call.id
                name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)
                cache.add_sentence(f"Tool ID: {id}, Tool Name: {name}, Arguments: {arguments}", is_frank=True)
        else:
            content = chat_completion.choices[0].message.content
            cache.add_sentence(content, is_frank=True)
        chat_completion_json = json.dumps(chat_completion, default=lambda o: o.__dict__, indent=4)


        
        
        response_time = calculate_response_time(start_time)
        print(f"Response time: {response_time:.2f} seconds")
        return chat_completion_json
    
    except Exception as e:
        print(f"Error updating data: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500



if __name__ == '__main__':
    app.run(debug=True, port=5000)