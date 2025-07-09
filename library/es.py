from elasticsearch import Elasticsearch
from datetime import datetime

es = Elasticsearch("http://localhost:9200")


def search_article(query):
    if query:
        body = {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["title", "content"]
                }
            },
            "sort": [
                {"created_at": {"order": "desc"}}
            ]
        }
    else:
        body = {
            "query": {
                "match_all": {}
            },
            "sort": [
                {"created_at": {"order": "desc"}}
            ]
        }

    res = es.search(index="articles", body=body)
    hits = res["hits"]["hits"]

    return [
        {
            "id": h["_id"],
            "title": h["_source"].get("title", ""),
            "content": h["_source"].get("content", ""),
            **({"content_json": h["_source"].get("content_json", {})} if not query else {}),
            "created_at": h["_source"].get("created_at", ""),
        }
        for h in hits
    ]


def get_article_by_id(article_id):
    try:
        res = es.get(index="articles", id=article_id)
        source = res.get("_source", {})
        return {
            "title": source.get("title", ""),
            "content_json": source.get("content_json", {}),
        }
    except Exception as e:
        print(f"Error fetching article by id: {e}")
        return None


def extract_text_from_tiptap(content_json):
    if isinstance(content_json, dict):
        if "text" in content_json:
            return content_json["text"]
        elif "content" in content_json:
            return " ".join(extract_text_from_tiptap(child) for child in content_json["content"])
    elif isinstance(content_json, list):
        return " ".join(extract_text_from_tiptap(child) for child in content_json)
    return ""


def add_article(title, content_json):
    doc = {
        "title": title,
        "content_json": content_json,
        "content": extract_text_from_tiptap(content_json),
        "created_at": datetime.now(),
    }

    res = es.index(index="articles", body=doc)
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3])
    return res
