import dotenv
import os
from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    HarmBlockThreshold,
    HarmCategory,
)
from langchain_openai import ChatOpenAI
from langchain.memory import ChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from pathlib import Path
import datetime

DATA_PATH = "improved_data.txt"
dotenv.load_dotenv()
chat_history = ChatMessageHistory()

RULES_TEXT = ""
RULES = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "1. You are the AI game master of text-based interactive game where players act as Astarion, "
            "a knight belonging to house Stark, in the fantasy world ASOIAF. Your role is to guide the player through "
            "an RPG experience based on their decisions in a linear format."
            "3. Do not mention you are a terminal"
            "4. Do not mention the original plot of the novel"
            "5. Only output pure text paragraphs",
        ),
        MessagesPlaceholder(variable_name="messages")
    ]
)

# llm = ChatGoogleGenerativeAI(
#     model="gemini-pro", convert_system_message_to_human=True,
#     safety_settings={
#         HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
#         HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
#         HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
#         HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
#     },
#     temperature=0
# )


# key = os.getenv('OPENAI_API_KEY')
# print(key)

llm = ChatOpenAI(openai_api_key="", model_name="gpt-3.5-turbo", temperature=0)

def generate_content(user_message: str):
    return llm.invoke(user_message).content


class Chat:
    def __init__(self, debug=False) -> None:
        self.debug = debug
        self.log_dir = "logs"
        if not Path(self.log_dir).exists():
            Path(self.log_dir).mkdir()
        self.log_file = Path(self._generate_log_file_name())
        if not self.log_file.exists():
            self.log_file.touch()
        self.chain = RULES | llm
        self.chat_history = ChatMessageHistory()

    def generate_content(self, user_message: str):
        # if self.debug:
        #     print("generate_content", user_message)
        return llm.invoke(user_message).content

    def _generate_log_file_name(self):
        # Generate a unique log file name using instance id and timestamp
        timestamp = datetime.datetime.now().strftime("%Y_%m_%d_%H%M")
        return f"{self.log_dir}/chatbot_log_{id(self)}_{timestamp}.txt"

    def log_message(self, message: str):
        # Log both user and AI messages
        with self.log_file.open('a', encoding='utf-8') as log_file:
            log_file.write(f"{message}\n")

    def add_to_message_history(self, message: str, is_ai_message: bool, write_to_log=True):
        # if write_to_log:
        self.log_message(message)
        if is_ai_message:
            self.chat_history.add_ai_message(message)
        else:
            self.chat_history.add_user_message(message)

    def send_message(self, user_message: str, keep_in_history=True) -> str:
        self.chat_history.add_user_message(user_message)
        resp = self.chain.invoke(
            {"messages": self.chat_history.messages}
        )
        self.chat_history.add_ai_message(resp.content)
        # if self.debug:
        #     print("user_message: ", user_message)
        #     print("ai_message: ", resp.content)
        #     print("\n\n\n")
        if keep_in_history:
            self.log_message(user_message)
        else:
            del self.chat_history.messages[-1]
            del self.chat_history.messages[-1]
        return resp.content


if __name__ == "__main__":
    chat = Chat(debug=True)
    while True:
        q = input()
        chat.send_message(q)
