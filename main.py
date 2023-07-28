#!/usr/bin/env python3

from langchain.document_loaders import BSHTMLLoader
from langchain.document_loaders import WebBaseLoader
from vlite import VLite
import openai

from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI

from langchain.chains import LLMChain
from langchain.schema import BaseOutputParser

from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

DEBUG=False
WEB_GET=False
PERSIST=False

db = VLite()
llm = OpenAI()
chat_model = ChatOpenAI()

def load_and_store_pages():
    loader = WebBaseLoader([
        "https://www.thetrainline.com/destinations/trains-to-edinburgh",
        "https://www.thetrainline.com/destinations/trains-to-london",
        "https://www.thetrainline.com/destinations/trains-to-bath"
    ])

    scrape_data = loader.aload()
    if PERSIST:
        for page in scrape_data:
            if (page.metadata):
                data = {
                    'content': page.page_content,
                    'title': page.metadata["title"]
                }

                db.memorize(data)
            else:
                print("No page metadata")

    return scrape_data

def debug_print(msg):
    if DEBUG:
        print(msg)

def translation_prompt():
    template = "You are a helpful agent that translates {input_lang} to {output_lang}"
    system_message_prompt = SystemMessagePromptTemplate.from_template(template)
    return system_message_prompt

class CommaSeparatedListOutputParser(BaseOutputParser):
    def parse(self, text: str):
        """Parse the output of an LLM call."""
        return text.strip().split(", ")

if __name__ == "__main__":
    scrape_data = []
    if WEB_GET:
        scrape_data = load_and_store_pages()

    human_template = "{query}"
    human_prompt = HumanMessagePromptTemplate.from_template(human_template)

    chat_prompt = ChatPromptTemplate.from_messages([translation_prompt(), human_prompt])

    chain = LLMChain(
        llm=llm,
        prompt=chat_prompt,
        output_parser=CommaSeparatedListOutputParser()
    )

    answer = chain.run(
        input_lang="English",
        output_lang="English",
        query="What are the name of the Pandas at Edinburgh Zoo"
    )

    print(answer)
