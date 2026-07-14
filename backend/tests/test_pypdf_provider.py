from io import BytesIO

import pypdf
from pypdf.generic import NameObject

from src.infrastructure.providers.document.pypdf import PyPDFProvider
from src.shared.exceptions import ProviderException


def test_pypdf_provider_valid_pdf() -> None:
    # 1. Create a valid 2-page PDF in memory
    writer = pypdf.PdfWriter()
    writer.add_blank_page(width=100, height=100)
    writer.add_blank_page(width=100, height=100)
    writer.add_metadata(
        {
            "/Title": "Test PDF Title",
            "/Author": "Test Author",
            "/Subject": "Test Subject",
            "/Creator": "Test Creator",
            "/Producer": "Test Producer",
        }
    )

    stream = BytesIO()
    writer.write(stream)
    stream.seek(0)

    # 2. Instantiate provider and execute checks
    provider = PyPDFProvider()

    res = provider.extract_document(stream)
    assert res.is_success is True
    assert res.value.page_count == 2
    assert len(res.value.pages) == 2
    assert res.value.pages[0].page_number == 1
    assert res.value.pages[1].page_number == 2
    assert res.value.metadata["title"] == "Test PDF Title"
    assert res.value.metadata["author"] == "Test Author"
    assert res.value.metadata["subject"] == "Test Subject"
    assert res.value.metadata["creator"] == "Test Creator"
    assert res.value.metadata["producer"] == "Test Producer"


def test_pypdf_provider_encrypted_pdf() -> None:
    writer = pypdf.PdfWriter()
    writer.add_blank_page(width=100, height=100)
    writer.encrypt("user_pass", "owner_pass")

    stream = BytesIO()
    writer.write(stream)
    stream.seek(0)

    provider = PyPDFProvider()
    res = provider.extract_document(stream)
    assert res.is_failure is True
    assert isinstance(res.error, ProviderException)
    assert "Encrypted PDF detected" in str(res.error)


def test_pypdf_provider_empty_pdf() -> None:
    stream = BytesIO(b"")
    provider = PyPDFProvider()
    res = provider.extract_document(stream)
    assert res.is_failure is True
    assert isinstance(res.error, ProviderException)
    assert "Empty document detected" in str(res.error)


def test_pypdf_provider_invalid_pdf() -> None:
    stream = BytesIO(b"garbage pdf bytes")
    provider = PyPDFProvider()
    res = provider.extract_document(stream)
    assert res.is_failure is True
    assert isinstance(res.error, ProviderException)
    assert "Extraction failed" in str(res.error)


def test_pypdf_provider_extract_page_text() -> None:
    writer = pypdf.PdfWriter()
    page = writer.add_blank_page(width=100, height=100)

    # Inject low level content stream to represent page text
    font_dict = pypdf.generic.DictionaryObject(
        {
            NameObject("/Type"): NameObject("/Font"),
            NameObject("/Subtype"): NameObject("/Type1"),
            NameObject("/BaseFont"): NameObject("/Helvetica"),
        }
    )
    fonts = pypdf.generic.DictionaryObject({NameObject("/F1"): font_dict})

    from typing import Any

    page[NameObject("/Resources")] = pypdf.generic.DictionaryObject()
    resources: Any = page[NameObject("/Resources")]
    resources[NameObject("/Font")] = fonts

    # Text content stream with trailing whitespaces and line endings
    stream_content = b"BT /F1 12 Tf 20 50 Td (  Hello World  \r\n  Line 2  ) Tj ET"
    contents_stream = pypdf.generic.DecodedStreamObject()
    contents_stream._data = stream_content
    page[NameObject("/Contents")] = contents_stream

    stream = BytesIO()
    writer.write(stream)
    stream.seek(0)

    provider = PyPDFProvider()

    res = provider.extract_document(stream)
    assert res.is_success is True
    assert res.value.page_count == 1
    # Should strip leading/trailing whitespace and normalize line endings
    assert res.value.pages[0].text == "Hello World  \n  Line 2"


def test_pypdf_provider_unicode_handling() -> None:
    writer = pypdf.PdfWriter()
    writer.add_blank_page(width=100, height=100)
    # Unicode emoji and special characters in metadata
    writer.add_metadata(
        {
            "/Title": "Unicode 📚 Title",
            "/Author": "Unicode 👤 Author",
        }
    )

    stream = BytesIO()
    writer.write(stream)
    stream.seek(0)

    provider = PyPDFProvider()
    res = provider.extract_document(stream)
    assert res.is_success is True
    assert res.value.metadata["title"] == "Unicode 📚 Title"
    assert res.value.metadata["author"] == "Unicode 👤 Author"
