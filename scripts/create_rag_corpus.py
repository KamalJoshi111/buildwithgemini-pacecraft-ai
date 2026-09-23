# Script to create serverless Vertex AI RAG corpus and import Gutenberg text

import vertexai
from vertexai.preview import rag
from vertexai.preview.rag.utils import resources as rr

PROJECT_ID = "qwiklabs-gcp-03-3e15bc834bf2"
LOCATION = "us-central1"
GCS_PATH = "gs://pacecraft-ai-assets-qwiklabs-gcp-03-3e15bc834bf2/rag/pg49513.txt"

PARSING_PROMPT = (
    "Extract the individual useful facts, remedies, and descriptions described in this text. "
    "Ignore and omit all metadata, boilerplate, and Project Gutenberg headers/footers. "
    "Output clean, self-contained prose."
)


def main():
    print(f"Initializing Vertex AI RAG for project: {PROJECT_ID}, location: {LOCATION}...")
    vertexai.init(project=PROJECT_ID, location=LOCATION)

    # 1. Verify / set serverless mode
    cfg_name = f"projects/{PROJECT_ID}/locations/{LOCATION}/ragEngineConfig"
    try:
        cfg = rag.get_rag_engine_config(name=cfg_name)
        mode = getattr(getattr(cfg, "rag_managed_db_config", None), "mode", None)
        print(f"Current RAG Managed DB mode: {mode}")
        if not isinstance(mode, rr.Serverless):
            print("Configuring RAG engine serverless mode...")
            rag.update_rag_engine_config(
                rag_engine_config=rag.RagEngineConfig(
                    name=cfg_name,
                    rag_managed_db_config=rag.RagManagedDbConfig(mode=rr.Serverless()),
                )
            )
    except Exception as e:
        print(f"Serverless config check note: {e}")

    # 2. Check existing corpora or create new
    existing_corpora = list(rag.list_corpora())
    corpus = None
    for c in existing_corpora:
        if getattr(c, "display_name", "") == "herbal-corpus":
            corpus = c
            print(f"Found existing corpus: {corpus.name}")
            break

    if corpus is None:
        print("Creating new RAG corpus: herbal-corpus...")
        corpus = rag.create_corpus(
            display_name="herbal-corpus",
            embedding_model_config=rag.EmbeddingModelConfig(
                publisher_model="publishers/google/models/text-embedding-005"
            ),
        )
        print("Corpus Created Successfully!")

    print(f"CORPUS_NAME = \"{corpus.name}\"")

    # 3. Import + parse + chunk + embed
    print(f"Importing and indexing {GCS_PATH} into corpus...")
    resp = rag.import_files(
        corpus_name=corpus.name,
        paths=[GCS_PATH],
        transformation_config=rag.TransformationConfig(
            chunking_config=rag.ChunkingConfig(chunk_size=512, chunk_overlap=100)
        ),
        llm_parser=rag.LlmParserConfig(
            model_name="gemini-2.5-flash",
            custom_parsing_prompt=PARSING_PROMPT,
        ),
    )
    print(f"Import complete! Imported files count: {resp.imported_rag_files_count}")

    with open("corpus_info.txt", "w") as f:
        f.write(corpus.name)


if __name__ == "__main__":
    main()
