#!/usr/bin/env python3

from griptape.drivers import OpenAiPromptDriver
from griptape.structures import Agent
from griptape.tools import WebScraper
from griptape.events import StartPromptEvent, FinishPromptEvent
from griptape.memory.structure import ConversationMemory
from griptape.tasks import PromptTask, ToolkitTask
from griptape.structures import Pipeline
from griptape import utils
from griptape.loaders import WebLoader
from griptape.engines import VectorQueryEngine
from griptape.tools import KnowledgeBaseClient

import openai

def handle_prompt_event(event, token_counter):
    print(event)
    token_counter.add_tokens(event.token_count)


if __name__ == "__main__":
    namespace = "travel-expert"
    token_counter = utils.TokenCounter()
    web_scraper = WebScraper()
    engine = VectorQueryEngine()

    artifacts = WebLoader().load(
        "https://www.thetrainline.com/destinations/trains-to-edinburgh",
    )

    engine.vector_store_driver.upsert_text_artifacts(
        {namespace: artifacts}
    )

    kb_client = KnowledgeBaseClient(
        description="Contains information about travel destinations. "
        "Use it to answer any travel-related questions.",
        query_engine=engine,
        namespace=namespace
    )

    pipeline = Pipeline(
        prompt_driver=OpenAiPromptDriver(
            model="gpt-3.5-turbo-16k",
        ),
        memory=ConversationMemory(),
        event_listeners={
            StartPromptEvent: [
                lambda e: handle_prompt_event(e, token_counter)
            ],
            FinishPromptEvent: [
                lambda e: handle_prompt_event(e, token_counter)
            ]
        }
    )


    pipeline.add_tasks(
        ToolkitTask(
            tools=[web_scraper, kb_client]
        ),
    )

    pipeline.run("What are the names of the Pandas in Edinburgh Zoo?")

    print(f"total tokens: {token_counter.tokens}")
