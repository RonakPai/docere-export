'''
All LLM Classes.
'''

import vertexai
import json

import keys

from vertexai.generative_models import GenerativeModel, GenerationConfig, HarmCategory, HarmBlockThreshold, Content, Part
from google.oauth2 import service_account

class GeminiLLM:

    def __init__(self,
                temperature: float = None,
                top_p: float = None,
                system_instruction: str = None,
                history_as_string: str = "",
                verbose: bool = False,):
        
        self.verbose = verbose
        
        credentials_json = {
        "type": "service_account",
        "project_id": keys.VERTEX_AI_PROJECT_ID,
        "private_key_id": keys.VERTEX_AI_PRIVATE_KEY_ID,
        "private_key": keys.VERTEX_AI_PRIVATE_KEY,
        "client_email": keys.VERTEX_AI_CLIENT_EMAIL,
        "client_id": keys.VERTEX_AI_CLIENT_ID,
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": keys.VERTEX_AI_CLIENT_X509_CERT_URL,
        "universe_domain": "googleapis.com"
        }
        self.credentials = service_account.Credentials.from_service_account_info(credentials_json)
        self.vertex_ai_location = "us-west1"
        vertexai.init(project=keys.VERTEX_AI_PROJECT_ID, location=self.vertex_ai_location, credentials=self.credentials)

        self.safety_settings = {
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        }
        self.model_name = "gemini-1.5-pro"
        self.llm_config = GenerationConfig(temperature=temperature, top_p=top_p)
        self.system_instruction = system_instruction 
        self.llm = GenerativeModel(model_name=self.model_name, 
                                   system_instruction=self.system_instruction,
                                   generation_config=self.llm_config, 
                                   safety_settings=self.safety_settings,)
        if history_as_string == "":
            self.chat = self.llm.start_chat()
        else:
            self.set_history_from_string(history_as_string=history_as_string)

    def switch_vertex_ai_location(self,):
        if self.vertex_ai_location == "us_east1":
            self.vertex_ai_location = "us-central1"
            vertexai.init(project=keys.VERTEX_AI_PROJECT_ID, location=self.vertex_ai_location, credentials=self.credentials)
        elif self.vertex_ai_location == "us-central1":
            self.vertex_ai_location = "us-west1"
            vertexai.init(project=keys.VERTEX_AI_PROJECT_ID, location=self.vertex_ai_location, credentials=self.credentials)
        else: # self.vertex_ai_location == "us-west1":
            self.vertex_ai_location = "us-east1"
            vertexai.init(project=keys.VERTEX_AI_PROJECT_ID, location=self.vertex_ai_location, credentials=self.credentials)

    def generate_content(self,
                         prompt: str,):
        try:
            response = self.llm.generate_content(prompt)
        except Exception as e:
            try:
                self.switch_vertex_ai_location()
                self.llm = GenerativeModel(model_name=self.model_name, generation_config=self.llm_config, system_instruction=self.system_instruction, safety_settings=self.safety_settings)
                response = self.llm.generate_content(prompt)
            except Exception as e:
                try:
                    self.switch_vertex_ai_location()
                    self.llm = GenerativeModel(model_name=self.model_name, generation_config=self.llm_config, system_instruction=self.system_instruction, safety_settings=self.safety_settings)
                    response = self.llm.generate_content(prompt)
                except Exception as e:
                    self.switch_vertex_ai_location()
                    self.llm = GenerativeModel(model_name=self.model_name, generation_config=self.llm_config, system_instruction=self.system_instruction, safety_settings=self.safety_settings)
                    raise(e)
        if self.verbose:
            print("[{}]\nINPUT: {} CHARACTERS.\nOUTPUT: {} CHARACTERS.".format(self.model_name.upper(), self.llm.count_tokens(prompt).total_billable_characters, self.llm.count_tokens(response.text).total_billable_characters))
        return response
    
    def send_message(self,
                     prompt: str,):
        response = self.chat.send_message(prompt)
        if self.verbose:
            print("[{}]\nINPUT: {} CHARACTERS.\nOUTPUT: {} CHARACTERS.".format(self.model_name.upper(), self.llm.count_tokens(prompt).total_billable_characters, self.llm.count_tokens(response.text).total_billable_characters))
        return response
    
    def set_history(self,
                    history):
        self.chat = self.llm.start_chat(history=history)
    
    def get_history(self):
        return self.chat.history

    def set_history_from_string(self,
                                history_as_string):
        chat_history = []
        for element in json.loads(history_as_string):
            chat_history.append(Content(role=element['role'], parts=[Part.from_text(element['text'])]))
        self.chat = self.llm.start_chat(history=chat_history)

    def get_history_as_string(self):
        chat_history = []
        for element in self.chat.history:
            chat_history.append({"role": element.role,
                                 "text": element.parts[0].text.strip()})
        return json.dumps(chat_history)

class GeminiFlashLLM:

    def __init__(self,
                temperature: float = None,
                top_p: float = None,
                system_instruction: str = None,
                verbose: bool = False,):
        
        self.verbose = verbose
        
        credentials_json = {
        "type": "service_account",
        "project_id": keys.VERTEX_AI_PROJECT_ID,
        "private_key_id": keys.VERTEX_AI_PRIVATE_KEY_ID,
        "private_key": keys.VERTEX_AI_PRIVATE_KEY,
        "client_email": keys.VERTEX_AI_CLIENT_EMAIL,
        "client_id": keys.VERTEX_AI_CLIENT_ID,
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": keys.VERTEX_AI_CLIENT_X509_CERT_URL,
        "universe_domain": "googleapis.com"
        }
        self.credentials = service_account.Credentials.from_service_account_info(credentials_json)
        self.vertex_ai_location = "us-west1"
        vertexai.init(project=keys.VERTEX_AI_PROJECT_ID, location=self.vertex_ai_location, credentials=self.credentials)

        self.safety_settings = {
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        }
        self.model_name = "gemini-1.5-flash"
        self.llm_config = GenerationConfig(temperature=temperature, top_p=top_p)
        self.system_instruction = system_instruction
        self.llm = GenerativeModel(model_name=self.model_name, 
                                   generation_config=self.llm_config, 
                                   system_instruction=self.system_instruction,
                                   safety_settings=self.safety_settings)

    def switch_vertex_ai_location(self,):
        if self.vertex_ai_location == "us_east1":
            self.vertex_ai_location = "us-central1"
            vertexai.init(project=keys.VERTEX_AI_PROJECT_ID, location=self.vertex_ai_location, credentials=self.credentials)
        elif self.vertex_ai_location == "us-central1":
            self.vertex_ai_location = "us-west1"
            vertexai.init(project=keys.VERTEX_AI_PROJECT_ID, location=self.vertex_ai_location, credentials=self.credentials)
        else: # self.vertex_ai_location == "us-west1":
            self.vertex_ai_location = "us-east1"
            vertexai.init(project=keys.VERTEX_AI_PROJECT_ID, location=self.vertex_ai_location, credentials=self.credentials)

    def generate_content(self,
                         prompt: str,):
        try:
            response = self.llm.generate_content(prompt)
        except Exception as e:
            try:
                self.switch_vertex_ai_location()
                self.llm = GenerativeModel(model_name=self.model_name, generation_config=self.llm_config, system_instruction=self.system_instruction, safety_settings=self.safety_settings)
                response = self.llm.generate_content(prompt)
            except Exception as e:
                try:
                    self.switch_vertex_ai_location()
                    self.llm = GenerativeModel(model_name=self.model_name, generation_config=self.llm_config, system_instruction=self.system_instruction, safety_settings=self.safety_settings)
                    response = self.llm.generate_content(prompt)
                except Exception as e:
                    self.switch_vertex_ai_location()
                    self.llm = GenerativeModel(model_name=self.model_name, generation_config=self.llm_config, system_instruction=self.system_instruction, safety_settings=self.safety_settings)
                    raise(e)
        if self.verbose:
            print("[{}]\nINPUT: {} CHARACTERS.\nOUTPUT: {} CHARACTERS.".format(self.model_name.upper(), self.llm.count_tokens(prompt).total_billable_characters, self.llm.count_tokens(response.text).total_billable_characters))
        return response
    
class Gemini_1_0_LLM:

    def __init__(self,
                temperature: float = None,
                top_p: float = None,
                system_instruction: str = None,
                history_as_string: str = "",
                verbose: bool = False,):
        
        self.verbose = verbose
        
        credentials_json = {
        "type": "service_account",
        "project_id": keys.VERTEX_AI_PROJECT_ID,
        "private_key_id": keys.VERTEX_AI_PRIVATE_KEY_ID,
        "private_key": keys.VERTEX_AI_PRIVATE_KEY,
        "client_email": keys.VERTEX_AI_CLIENT_EMAIL,
        "client_id": keys.VERTEX_AI_CLIENT_ID,
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": keys.VERTEX_AI_CLIENT_X509_CERT_URL,
        "universe_domain": "googleapis.com"
        }
        self.credentials = service_account.Credentials.from_service_account_info(credentials_json)
        self.vertex_ai_location = "us-west1"
        vertexai.init(project=keys.VERTEX_AI_PROJECT_ID, location=self.vertex_ai_location, credentials=self.credentials)

        self.safety_settings = {
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        }
        self.model_name = "gemini-1.0-pro"
        self.llm_config = GenerationConfig(temperature=temperature, top_p=top_p)
        self.system_instruction = system_instruction 
        self.llm = GenerativeModel(model_name=self.model_name, 
                                   system_instruction=self.system_instruction,
                                   generation_config=self.llm_config, 
                                   safety_settings=self.safety_settings,)
        if history_as_string == "":
            self.chat = self.llm.start_chat()
        else:
            self.set_history_from_string(history_as_string=history_as_string)

    def switch_vertex_ai_location(self,):
        if self.vertex_ai_location == "us_east1":
            self.vertex_ai_location = "us-central1"
            vertexai.init(project=keys.VERTEX_AI_PROJECT_ID, location=self.vertex_ai_location, credentials=self.credentials)
        elif self.vertex_ai_location == "us-central1":
            self.vertex_ai_location = "us-west1"
            vertexai.init(project=keys.VERTEX_AI_PROJECT_ID, location=self.vertex_ai_location, credentials=self.credentials)
        else: # self.vertex_ai_location == "us-west1":
            self.vertex_ai_location = "us-east1"
            vertexai.init(project=keys.VERTEX_AI_PROJECT_ID, location=self.vertex_ai_location, credentials=self.credentials)

    def generate_content(self,
                         prompt: str,):
        try:
            response = self.llm.generate_content(prompt)
        except Exception as e:
            try:
                self.switch_vertex_ai_location()
                self.llm = GenerativeModel(model_name=self.model_name, generation_config=self.llm_config, system_instruction=self.system_instruction, safety_settings=self.safety_settings)
                response = self.llm.generate_content(prompt)
            except Exception as e:
                try:
                    self.switch_vertex_ai_location()
                    self.llm = GenerativeModel(model_name=self.model_name, generation_config=self.llm_config, system_instruction=self.system_instruction, safety_settings=self.safety_settings)
                    response = self.llm.generate_content(prompt)
                except Exception as e:
                    self.switch_vertex_ai_location()
                    self.llm = GenerativeModel(model_name=self.model_name, generation_config=self.llm_config, system_instruction=self.system_instruction, safety_settings=self.safety_settings)
                    raise(e)
        if self.verbose:
            print("[{}]\nINPUT: {} CHARACTERS.\nOUTPUT: {} CHARACTERS.".format(self.model_name.upper(), self.llm.count_tokens(prompt).total_billable_characters, self.llm.count_tokens(response.text).total_billable_characters))
        return response
    
    def send_message(self,
                     prompt: str,):
        response = self.chat.send_message(prompt)
        if self.verbose:
            print("[{}]\nINPUT: {} CHARACTERS.\nOUTPUT: {} CHARACTERS.".format(self.model_name.upper(), self.llm.count_tokens(prompt).total_billable_characters, self.llm.count_tokens(response.text).total_billable_characters))
        return response
    
    def set_history(self,
                    history):
        self.chat = self.llm.start_chat(history=history)
    
    def get_history(self):
        return self.chat.history

    def set_history_from_string(self,
                                history_as_string):
        chat_history = []
        for element in json.loads(history_as_string):
            chat_history.append(Content(role=element['role'], parts=[Part.from_text(element['text'])]))
        self.chat = self.llm.start_chat(history=chat_history)

    def get_history_as_string(self):
        chat_history = []
        for element in self.chat.history:
            chat_history.append({"role": element.role,
                                 "text": element.parts[0].text.strip()})
        return json.dumps(chat_history)