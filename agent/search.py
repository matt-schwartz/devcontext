# Copyright 2026 Matthew Schwartz
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from dataclasses import dataclass
from urllib import response

from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import InMemorySaver
from langchain.tools import tool, ToolRuntime

import storage.vector
import settings

os.environ["ANTHROPIC_API_KEY"] = settings.ANTHROPIC_API_KEY

SYSTEM_PROMPT = """You are a helpful assistant that provides answers based on the provided context. 

You have access to one tool: `search_context(query: str) -> str`. This tool allows you to search for relevant context based on a query. You can use this tool to retrieve information that may help you answer questions.

If the context does not contain enough information to answer the question, respond with "I don't have enough information to answer that question."
Do not make up answers or provide information not present in the context.
"""

@tool
def search_context(query: str) -> str:
    """Search for references to the query in the reference documents."""
    results = storage.vector.query(query)

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    ids = results.get("ids", [[]])[0]

    # Build context from retrieved documents
    context = "\n\n".join(
        f"[Source: {id}]\n{doc}" for id, doc in zip(ids, documents)
    )

    return context


@dataclass
class ResponseFormat:
    answer: str
    sources: list[dict]


def chat():
    model = init_chat_model(
        "claude-sonnet-4-6",
        timeout=10,
        max_tokens=1024
    )
    checkpointer = InMemorySaver()
    agent = create_agent(
        model=model,
        system_prompt=SYSTEM_PROMPT,
        tools=[search_context],
        response_format=ToolStrategy(ResponseFormat),
        checkpointer=checkpointer,
    )
    # `thread_id` is a unique identifier for a given conversation.
    config = {"configurable": {"thread_id": "1"}}

    try:
        while True:
            query = input("Enter your query: ")
            # result = search_context(query, project=None)

            response = agent.invoke(
                {"messages": [{"role": "user", "content": query}]},
                config=config,
            )

            print(response['structured_response'].answer)
            # print("\nSources:")
            # sources = response['structured_response'].sources
            # for source in sources:
            #     print(f"ID: {source['id']}, Metadata: {source['metadata']}, Document: {source['document']}")

            # sources = [
            #     {"id": id, "document": doc, "metadata": meta}
            #     for id, doc, meta in zip(ids, documents, metadatas)
            # ]
            # for source in result["sources"]:
            #     print(f"ID: {source['id']}, Metadata: {source['metadata']}, Document: {source['document']}")
    except KeyboardInterrupt:
        print("\nExiting...")
        return


if __name__ == "__main__":
    chat()
