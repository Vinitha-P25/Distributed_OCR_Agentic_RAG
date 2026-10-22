from ddgs import DDGS


def search_web(query: str, max_results: int = 5) -> list[dict]:
    """
    Search the web and return a list of relevant results.
    """

    query = query.strip()

    if not query:
        return []

    try:
        with DDGS() as ddgs:
            results = list(
                ddgs.text(
                    query,
                    max_results=max_results,
                )
            )

        return [
            {
                "title": result.get("title", ""),
                "url": result.get("href", ""),
                "snippet": result.get("body", ""),
            }
            for result in results
        ]

    except Exception as error:
        raise RuntimeError(
            f"Web search failed: {error}"
        ) from error


if __name__ == "__main__":
    question = input("Enter a web-search query: ")

    results = search_web(question)

    if not results:
        print("No web results found.")

    for index, result in enumerate(results, start=1):
        print(f"\nResult {index}")
        print("Title:", result["title"])
        print("URL:", result["url"])
        print("Snippet:", result["snippet"])