from pathlib import Path


def split_text_into_chunks(
    text: str,
    chunk_size: int = 300,
    overlap: int = 50
) -> list[str]:

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError(
            "overlap must be non-negative and smaller than chunk_size"
        )

    # Remove unnecessary whitespace
    text = " ".join(text.split())

    if not text:
        return []

    chunks = []
    start = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))

        chunk = text[start:end]
        chunks.append(chunk)

        if end == len(text):
            break

        start = end - overlap

    return chunks


if __name__ == "__main__":

    project_dir = Path(__file__).resolve().parent.parent
    input_file = project_dir / "extracted_text.txt"

    if not input_file.exists():
        print("Extracted text file not found.")
    else:
        text = input_file.read_text(encoding="utf-8")

        chunks = split_text_into_chunks(
            text,
            chunk_size=100,
            overlap=20
        )

        print(f"Total chunks created: {len(chunks)}")

        for index, chunk in enumerate(chunks, start=1):
            print(f"\n--- Chunk {index} ---")
            print(chunk)