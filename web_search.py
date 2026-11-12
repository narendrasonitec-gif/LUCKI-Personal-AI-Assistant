from ddgs import DDGS


# =========================================================
# INDEPENDENT WEB SEARCH
# =========================================================

def search_web(query, max_results=6):

    try:

        print(f"Lucki Web Search: {query}")

        results = DDGS().text(
            query,
            max_results=max_results
        )

        if not results:
            return None

        cleaned = []

        for i, result in enumerate(results, start=1):

            title = result.get("title", "").strip()
            body = result.get("body", "").strip()
            url = result.get("href", "").strip()

            if not title and not body:
                continue

            cleaned.append(
                f"""
RESULT {i}

Title:
{title}

Summary:
{body}

URL:
{url}
""".strip()
            )

        if not cleaned:
            return None

        return "\n\n".join(cleaned)

    except Exception as e:

        print("Web Search Error:", e)

        return None


# =========================================================
# SEARCH WITH MULTIPLE QUERIES
# =========================================================

def smart_search(query, max_results=6):

    result = search_web(
        query,
        max_results=max_results
    )

    return result