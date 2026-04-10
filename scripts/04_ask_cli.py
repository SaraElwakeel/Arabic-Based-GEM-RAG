from __future__ import annotations

from src.service.qa_service import MuseumQAService


def main() -> None:
    service = MuseumQAService()
    print("Egyptian Museums RAG CLI")
    print("Type 'exit' to quit.\n")

    while True:
        question = input("Question: ").strip()
        if question.lower() in {"exit", "quit"}:
            break
        result = service.ask(question)
        print("\nAnswer:\n")
        print(result.answer)
        print("\nSources:")
        for i, src in enumerate(result.sources, start=1):
            print(f"{i}. {src.museum_name} | {src.page_title}")
            print(f"   {src.source_url}")
        print("\n" + "-" * 80 + "\n")


if __name__ == "__main__":
    main()
