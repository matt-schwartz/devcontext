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
import chromadb

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'devcontext.vector')

# Initialize client
client = chromadb.PersistentClient(path=DB_PATH)
collection = client.get_or_create_collection("dev_context")

# Store event with embedding
def store_with_embedding(id, content, type, project, timestamp) -> None:
    collection.add(
        documents=[content],
        metadatas=[{
            'type': type,
            'project': project,
            'timestamp': timestamp 
        }],
        ids=[id]
    )


def query(q: str):
    results = collection.query(
        query_texts=[q],
        n_results=10,         # TODO: This is completely arbitrary; Experiment to fill available context as well as sort by relevance or timeliness
        where=None,
    )
    return results
