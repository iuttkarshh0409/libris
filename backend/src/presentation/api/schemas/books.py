from pydantic import BaseModel


class BookSummaryResponse(BaseModel):
    id: str
    title: str | None = None
    author: str | None = None
    subject: str | None = None
    edition: str | None = None
    pages: int
    index_status: str
    file_name: str
    upload_timestamp: str


class BookUploadResponse(BaseModel):
    message: str
    book: BookSummaryResponse
