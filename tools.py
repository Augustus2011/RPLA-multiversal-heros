#clean string
import re
import json

#other apis
import requests

#azure
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential
from openai import AzureOpenAI


#vertexai
import vertexai
from vertexai import generative_models
from vertexai.generative_models import GenerativeModel, Part
import os



#gemini
from google import genai
from google.genai.types import GenerationConfig

#anthropic
import anthropic

#nebius
from openai import OpenAI

#env
from dotenv import load_dotenv
import os 




load_dotenv()

def initialize_vertexai(
    credential_json_path: str,
) -> None:
    """
    Initialize the Vertex AI client.
    """
    with open(credential_json_path, "r", encoding="utf-8") as f:
        credentials = json.load(f)

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credential_json_path
    vertexai.init(project=credentials["project_id"], location="us-central1")


GEMINI_SAFETY_SETTING = [
    generative_models.SafetySetting(
        category=generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        threshold=generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
    ),
    generative_models.SafetySetting(
        category=generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
        threshold=generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
    ),
    generative_models.SafetySetting(
        category=generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT,
        threshold=generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
    ),
]



def get_processed_cids(jsonl_path):
    processed_cids = set()
    if os.path.exists(jsonl_path):
        with open(jsonl_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    data = json.loads(line.strip())
                    processed_cids.add(data["CID"])  # Track already processed CIDs
                except json.JSONDecodeError:
                    print("Warning: Skipping corrupted line in JSONL file")
    return processed_cids


def clean_unwanted_txt(text)->str:
    patterns = [
        r'Resolution:?.*',  
        r'The Inner Conflict:?.*',
        r'Conclusion:?.*',
        r'Scene Conclusion:?.*',
        r'Conclusion of the Scene:?.*',
        r'The Decision:?.*',
        r'Outcome Reflection:?.*',
        r'Resolution Proposal:?.*',
        r'Choice and Reflection:?.*',
        r'Off the scene:?.*',
        r'Interlude:?.*',
        r'Proposal:?.*'
    ]

    for pattern in patterns:
        text = re.sub(pattern, '', text, flags=re.DOTALL | re.IGNORECASE)
    return text

def clean_event(event):
    event = re.sub(r"\s+", " ", event.strip())
    
    if "_" in event:
        event = " ".join(dict.fromkeys(event.replace("_", "").split()))
    
    return event

def clean_markdown(text)->str:

    
    text = re.sub(r'\*\*\*(.*?)\*\*\*', r'\1', text)
    text = re.sub(r'(\*\*|__)(.*?)\1', r'\2', text)
    text = re.sub(r'(\*|_)(.*?)\1', r'\2', text)
    text = re.sub(r'~~(.*?)~~', r'\1', text)

    text = re.sub(r'^\s*#{1,6}\s*(.*?)$', r'\1\n', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*[-*+]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'`([^`]+)`', r'\1', text)
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    text = re.sub(r'!\[([^\]]*)\]\([^\)]+\)', r'\1', text)
    text = re.sub(r'^\s*>+\s?', '', text, flags=re.MULTILINE)

    text = re.sub(r'</?([a-zA-Z0-9]+)(?:\s[^>]*)?>', lambda m: m.group(0) if m.group(0).startswith('<') and m.group(0).endswith('>') else '', text)

    text = re.sub(r'\n{2,}', '\n\n', text).strip()

    return text


def gpt4o(input_prompt:str="")->str:
    client=client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    response = client.chat.completions.create(
        model="gpt-4o-mini-2024-07-18",
        messages=[{"role": "user", "content": input_prompt}],
        temperature=0.1,
    )
    return response.choices[0].message.content


def azure_r1(input_prompt:str="")->str:
    #example of input_prompt
    # """You are a tony stark “iron man” from 'MCU: The Heroes', 'Wreck-It Ralph (Franchise)'. Tony Stark was a character portrayed by #RobertDowneyJr. in the Marvel Cinematic Universe (MCU) film franchise, based on the Marvel Comics character of the same name and known commonly by his alter ego, Iron Man. In the films, Stark was an industrialist, genius inventor, hero, and former playboy who was the CEO of Stark Industries before handing it over to his wife Pepper Potts. Answer the decision from what you have done".\ntony stark “iron man” from MCU: The Heroes ,Wreck-It Ralph (Franchise). Tony Stark was a character portrayed by #RobertDowneyJr. in the Marvel Cinematic Universe (MCU) film franchise, based on the Marvel Comics character of the same name and known commonly by his alter ego, Iron Man. In the films, Stark was an industrialist, genius inventor, hero, and former playboy who was the CEO of Stark Industries before handing it over to his wife Pepper Potts.  After graduating from MIT at age 17 with summa cum laude honors, you're relaxing by the pool when your father Howard Stark confronts you about your future. As a brilliant young graduate who has already achieved so much, how do you respond to your father's pressure about "starting to do things in life"?
    # A) Take Initiative - Get up from the pool and present your detailed plans to prove your responsibility
    # B) Maintain Distance - Dismiss his concerns by saying you "have a plan" and continue relaxing
    # C) Seek Compromise - Have a genuine discussion about balancing your desires with his expectations
    # D) Confront Directly - Challenge his lifelong emotional distance and question his right to make demands now"""
    client = ChatCompletionsClient(
        endpoint=os.environ["AZURE_INFERENCE_ENDPOINT"],
        credential=AzureKeyCredential(os.environ["AZURE_R1_INFERENCE_CREDENTIAL"]),
        model="DeepSeek-R1",
    )
    try:
        response = client.complete(
            messages=[UserMessage(content=input_prompt)],
            temperature=0.6,
            timeout=1000
        )
        return clean_markdown(response.choices[0].message.content)
    except:
        return "Error: API request timed out"
    

def sonnet_37(input_prompt:str="")->str:
    client = anthropic.Anthropic(api_key=os.environ["CLAUDE_KEY"])
    try:
        response=client.messages.create(
                model="claude-3-7-sonnet-20250219",
                messages=[
                    {
                        "role": "user",
                        "content": input_prompt,
                    },
                ],
                max_tokens=1024,
                temperature=0.6,
            )
        return response.content[0].text
    except:
        return "Error: API request timed out"
    



def deepseek_v3(input_prompt:str="")->str:
    client = OpenAI(
        base_url="https://api.studio.nebius.ai/v1/",
        api_key=os.environ.get("NEBIUS_KEY"),
    )
    
    messages = [{"type": "text", "text": input_prompt}]
    response = client.chat.completions.create(
        model="deepseek-ai/DeepSeek-V3",
        messages=[{"role": "user", "content": messages}],
        max_tokens=1024,
        temperature=0.6,
    )

    return response.choices[0].message.content
    
# def azure_r1_zero(input_prompt:str="")->str:
#     #example of input_prompt
#     # """You are a tony stark “iron man” from 'MCU: The Heroes', 'Wreck-It Ralph (Franchise)'. Tony Stark was a character portrayed by #RobertDowneyJr. in the Marvel Cinematic Universe (MCU) film franchise, based on the Marvel Comics character of the same name and known commonly by his alter ego, Iron Man. In the films, Stark was an industrialist, genius inventor, hero, and former playboy who was the CEO of Stark Industries before handing it over to his wife Pepper Potts. Answer the decision from what you have done".\ntony stark “iron man” from MCU: The Heroes ,Wreck-It Ralph (Franchise). Tony Stark was a character portrayed by #RobertDowneyJr. in the Marvel Cinematic Universe (MCU) film franchise, based on the Marvel Comics character of the same name and known commonly by his alter ego, Iron Man. In the films, Stark was an industrialist, genius inventor, hero, and former playboy who was the CEO of Stark Industries before handing it over to his wife Pepper Potts.  After graduating from MIT at age 17 with summa cum laude honors, you're relaxing by the pool when your father Howard Stark confronts you about your future. As a brilliant young graduate who has already achieved so much, how do you respond to your father's pressure about "starting to do things in life"?
#     # A) Take Initiative - Get up from the pool and present your detailed plans to prove your responsibility
#     # B) Maintain Distance - Dismiss his concerns by saying you "have a plan" and continue relaxing
#     # C) Seek Compromise - Have a genuine discussion about balancing your desires with his expectations
#     # D) Confront Directly - Challenge his lifelong emotional distance and question his right to make demands now"""
#     client = ChatCompletionsClient(
#         endpoint=os.environ["AZURE_INFERENCE_ENDPOINT"],
#         credential=AzureKeyCredential(os.environ["AZURE_R1_INFERENCE_CREDENTIAL"]),
#         model="DeepSeek-R1-zero",
#     )
#     try:
#         response = client.complete(
#             messages=[UserMessage(content=input_prompt)],
#             temperature=0.6,
#             timeout=1000
#         )
#         return clean_markdown(response.choices[0].message.content)
#     except:
#         return "Error: API request timed out"
    

def r1_zero(input_prompt: str = "") -> str:
    url = "https://api.hyperbolic.xyz/v1/chat/completions"
    key = os.getenv("R1_API_KEY")
    if not key:
        raise ValueError("R1_API_KEY is missing from environment variables")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {key}"
    }
    data = {
        "messages": [{"role": "user", "content": input_prompt}],
        "model": "deepseek-ai/DeepSeek-R1-Zero",
        "temperature": 0.6,
        "max_tokens": 1024,
    }

    try:
        response = requests.post(url, headers=headers, json=data,timeout=1000)
        response.raise_for_status()

        if not response.text.strip():
            print("Warning: API returned an empty response")
            return "Error: Empty response from API"

        response_data = response.json()


        if "choices" not in response_data or not response_data["choices"]:
            print(f"Error: Unexpected API response format: {response_data}")
            return f"Error: Invalid response format - {response_data}"

        return clean_markdown(response_data["choices"][0]["message"]["content"])

    except requests.exceptions.Timeout:
        return "Error: API request timed out"
    except requests.exceptions.RequestException as e:
        return f"Error: API request failed - {str(e)}"
    except ValueError as e:
        return f"Error: JSON decoding failed - {str(e)}"

def r1(input_prompt: str = "") -> str:
    url = "https://api.hyperbolic.xyz/v1/chat/completions"
    key = os.getenv("R1_API_KEY")
    if not key:
        raise ValueError("R1_API_KEY is missing from environment variables")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {key}"
    }
    data = {
        "messages": [{"role": "user", "content": input_prompt}],
        "model": "deepseek-ai/DeepSeek-R1",
        "temperature": 0.6,
        "max_tokens": 1024,
    }

    try:
        response = requests.post(url, headers=headers, json=data,timeout=1000)
        response.raise_for_status()

        if not response.text.strip():
            print("Warning: API returned an empty response")
            return "Error: Empty response from API"

        response_data = response.json()


        if "choices" not in response_data or not response_data["choices"]:
            print(f"Error: Unexpected API response format: {response_data}")
            return f"Error: Invalid response format - {response_data}"

        return clean_markdown(response_data["choices"][0]["message"]["content"])

    except requests.exceptions.Timeout:
        return "Error: API request timed out"
    except requests.exceptions.RequestException as e:
        return f"Error: API request failed - {str(e)}"
    except ValueError as e:
        return f"Error: JSON decoding failed - {str(e)}"


def o1(input_prompt:str="")->str:
    azure_openai_client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-12-01-preview",
    )
    response = azure_openai_client.chat.completions.create(
        model="o1-new",  # o3-mini
        messages=[
            {
                "role": "user",
                "content": input_prompt,
            },
        ],
    )
    return response.choices[0].message.content


def o3_mini(input_prompt:str="")->str:
    client = AzureOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version="2024-12-01-preview",
    )

    response = client.chat.completions.create(
        model="o3-mini",
        messages=[{"role": "user", "content": input_prompt}]
    )
    return response.choices[0].message.content


def gpt4o_mini(input_prompt:str="")->str:
    client = AzureOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_4o_mini_ENDPOINT"),
        api_key=os.getenv("AZURE_4o_mini_INFERENCE_CREDENTIAL"),
        api_version="2024-12-01-preview",
    )

    response = client.chat.completions.create(
        model="gpt-4-o-mini",
        temperature=0.6,
        messages=[{"role": "user", "content": input_prompt}]
    )

    return response.choices[0].message.content


def gemini2_flash_thinking(input_prompt:str="")->str:

    client = genai.Client(api_key=os.getenv("GEMINI_API"))

    response = client.models.generate_content(
        model="gemini-2.0-flash-thinking-exp-01-21",
        contents=input_prompt,
        config={
            "max_output_tokens": 1024,
            "temperature": 0.6
        }
    )
    return clean_markdown(response.text)


def gemini2_flash(input_prompt:str="")->str:

    client = genai.Client(api_key=os.getenv("GEMINI_API"))

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=input_prompt,
        config={
            "max_output_tokens": 1024,
            "temperature": 0.6 #0.6
        }
    )
    return clean_markdown(response.text)






def gemini_j(text:str):
    client = GenerativeModel("gemini-2.0-flash") #gemini-2.5-flash-preview-04-17
    responses = client.generate_content(
            contents=[text],
            generation_config={
                "temperature": 0.1,
            },
            safety_settings=GEMINI_SAFETY_SETTING,
        )


    text_result = responses.candidates[0].content.text
    return text_result



# def gemini15_pro(input_prompt:str="")->str:
#     client = genai.Client(api_key=os.getenv("GEMINI_API"))

#     response = client.models.generate_content(
#         model="gemini-1.5-pro",
#         contents=input_prompt,
#     )
    
#     return clean_markdown(response.text)