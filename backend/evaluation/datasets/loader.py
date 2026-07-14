import json

from pydantic import BaseModel, Field, ValidationError


class BenchmarkEntry(BaseModel):
    question: str
    expected_answer: str
    expected_pages: list[int] = Field(default_factory=list)
    expected_chunks: list[str] = Field(default_factory=list)
    expected_keywords: list[str] = Field(default_factory=list)
    expected_citations: list[str] = Field(default_factory=list)
    difficulty: str = "medium"
    category: str = "general"
    book: str = ""


class DatasetLoader:
    @staticmethod
    def load_json(filepath: str) -> list[BenchmarkEntry]:
        try:
            with open(filepath, encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, list):
                raise ValueError("Dataset must be a JSON list of objects.")

            entries = []
            for item in data:
                entry = BenchmarkEntry.model_validate(item)
                entries.append(entry)
            return entries
        except (json.JSONDecodeError, ValidationError, ValueError, FileNotFoundError) as e:
            raise ValueError(f"Failed to load or validate dataset JSON: {e}") from e
