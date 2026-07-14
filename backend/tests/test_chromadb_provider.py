import pytest

from src.domain.providers.knowledge_index import IndexedVector
from src.infrastructure.providers.knowledge_index.chromadb import ChromaDBProvider
from src.shared.exceptions import ValidationException


@pytest.fixture
def provider() -> ChromaDBProvider:
    """Fixture to provide a clean, ephemeral ChromaDBProvider for each test."""
    p = ChromaDBProvider(persist_directory=None)
    # Ensure starting clean
    p.reset_index()
    return p


def test_provider_info(provider: ChromaDBProvider) -> None:
    """Verifies that provider identity properties are correct."""
    assert provider.provider_name == "ChromaDB"
    assert isinstance(provider.provider_version, str)
    assert provider.provider_version != ""


def test_collection_management(provider: ChromaDBProvider) -> None:
    """Verifies collection creation, existence checks, duplicate rejection, and deletion."""
    col_name = "test_collection"

    # Initially does not exist
    assert not provider.has_collection(col_name)

    # Creation
    provider.create_collection(col_name)
    assert provider.has_collection(col_name)

    # Re-creating same collection should raise ValidationException
    with pytest.raises(ValidationException, match="already exists"):
        provider.create_collection(col_name)

    # Deletion
    provider.delete_collection(col_name)
    assert not provider.has_collection(col_name)

    # Deleting non-existent should raise ValidationException
    with pytest.raises(ValidationException, match="does not exist"):
        provider.delete_collection(col_name)


def test_batch_insertion_and_ordering(provider: ChromaDBProvider) -> None:
    """Verifies batch insertion preserves ordering and metadata."""
    col_name = "batch_test"
    provider.create_collection(col_name)

    vectors = [
        IndexedVector(
            identifier="id-1",
            vector=[0.1, 0.2, 0.3],
            metadata={
                "embedding_id": "e1",
                "chunk_id": "c1",
                "book_id": "b1",
                "page_number": 1,
                "chapter_id": "ch1",
                "section_id": "s1",
                "model_identifier": "m1",
            },
        ),
        IndexedVector(
            identifier="id-2",
            vector=[0.4, 0.5, 0.6],
            metadata={
                "embedding_id": "e2",
                "chunk_id": "c2",
                "book_id": "b1",
                "page_number": 2,
                "chapter_id": "ch1",
                "section_id": "s2",
                "model_identifier": "m1",
            },
        ),
    ]

    provider.add_vectors(col_name, vectors)

    # Retrieve stats and check counts
    stats = provider.get_statistics(col_name)
    assert stats.total_vectors == 2
    assert stats.embedding_dimension == 3

    # Similarity search check to verify ordering/mapping
    search_batch = provider.query_similarity(col_name, vector=[0.1, 0.2, 0.3], limit=2)
    assert len(search_batch.results) == 2
    assert search_batch.results[0].identifier == "id-1"
    assert search_batch.results[1].identifier == "id-2"


def test_metadata_persistence(provider: ChromaDBProvider) -> None:
    """Verifies metadata is persisted accurately alongside the vectors."""
    col_name = "metadata_test"
    provider.create_collection(col_name)

    meta = {
        "embedding_id": "emb-999",
        "chunk_id": "chunk-999",
        "book_id": "book-999",
        "page_number": 42,
        "chapter_id": "chapter-999",
        "section_id": "section-999",
        "model_identifier": "model-999",
        "extra_custom_field": "custom-val",
    }

    vectors = [IndexedVector(identifier="v-1", vector=[0.1] * 128, metadata=meta)]
    provider.add_vectors(col_name, vectors)

    result = provider.query_similarity(col_name, vector=[0.1] * 128, limit=1)
    assert len(result.results) == 1
    retrieved_meta = result.results[0].metadata

    # Check each required field
    assert retrieved_meta["embedding_id"] == "emb-999"
    assert retrieved_meta["chunk_id"] == "chunk-999"
    assert retrieved_meta["book_id"] == "book-999"
    assert retrieved_meta["page_number"] == 42
    assert retrieved_meta["chapter_id"] == "chapter-999"
    assert retrieved_meta["section_id"] == "section-999"
    assert retrieved_meta["model_identifier"] == "model-999"
    assert retrieved_meta["extra_custom_field"] == "custom-val"


def test_duplicate_insertion(provider: ChromaDBProvider) -> None:
    """Verifies that inserting duplicate identifiers throws ValidationException."""
    col_name = "duplicate_test"
    provider.create_collection(col_name)

    v1 = IndexedVector(
        identifier="id-1",
        vector=[0.1] * 4,
        metadata={
            "embedding_id": "e1",
            "chunk_id": "c1",
            "book_id": "b1",
            "page_number": 1,
            "chapter_id": "ch1",
            "section_id": "s1",
            "model_identifier": "m1",
        },
    )

    # 1. In-batch duplicates
    with pytest.raises(ValidationException, match="Duplicate identifier in batch"):
        provider.add_vectors(col_name, [v1, v1])

    # Add single successfully
    provider.add_vectors(col_name, [v1])

    # 2. Database level duplicates
    v2 = IndexedVector(
        identifier="id-1",
        vector=[0.2] * 4,
        metadata={
            "embedding_id": "e1",
            "chunk_id": "c1",
            "book_id": "b1",
            "page_number": 1,
            "chapter_id": "ch1",
            "section_id": "s1",
            "model_identifier": "m1",
        },
    )
    with pytest.raises(ValidationException, match="already exist in the index"):
        provider.add_vectors(col_name, [v2])


def test_update_vectors(provider: ChromaDBProvider) -> None:
    """Verifies updating existing vectors and rejecting updates for non-existent ones."""
    col_name = "update_test"
    provider.create_collection(col_name)

    vec = IndexedVector(
        identifier="id-up",
        vector=[1.0, 1.0],
        metadata={
            "embedding_id": "e1",
            "chunk_id": "c1",
            "book_id": "b1",
            "page_number": 1,
            "chapter_id": "ch1",
            "section_id": "s1",
            "model_identifier": "m1",
        },
    )
    provider.add_vectors(col_name, [vec])

    # Perform update
    updated_vec = IndexedVector(
        identifier="id-up",
        vector=[2.0, 2.0],
        metadata={
            "embedding_id": "e1",
            "chunk_id": "c1",
            "book_id": "b1",
            "page_number": 1,
            "chapter_id": "ch1",
            "section_id": "s1",
            "model_identifier": "m1",
            "extra": "updated",
        },
    )
    provider.update_vectors(col_name, [updated_vec])

    # Verify update
    res = provider.query_similarity(col_name, vector=[2.0, 2.0], limit=1)
    assert res.results[0].metadata.get("extra") == "updated"

    # Attempt update on non-existent vector
    non_existent = IndexedVector(
        identifier="id-ghost",
        vector=[2.0, 2.0],
        metadata={
            "embedding_id": "e1",
            "chunk_id": "c1",
            "book_id": "b1",
            "page_number": 1,
            "chapter_id": "ch1",
            "section_id": "s1",
            "model_identifier": "m1",
        },
    )
    with pytest.raises(ValidationException, match="Cannot update non-existent vector"):
        provider.update_vectors(col_name, [non_existent])


def test_deletion(provider: ChromaDBProvider) -> None:
    """Verifies deleting vectors by ID list or metadata filter."""
    col_name = "delete_test"
    provider.create_collection(col_name)

    v1 = IndexedVector(
        identifier="id-1",
        vector=[0.1, 0.1],
        metadata={
            "embedding_id": "e1",
            "chunk_id": "c1",
            "book_id": "b1",
            "page_number": 1,
            "chapter_id": "ch1",
            "section_id": "s1",
            "model_identifier": "m1",
        },
    )
    v2 = IndexedVector(
        identifier="id-2",
        vector=[0.2, 0.2],
        metadata={
            "embedding_id": "e2",
            "chunk_id": "c2",
            "book_id": "b2",
            "page_number": 2,
            "chapter_id": "ch1",
            "section_id": "s2",
            "model_identifier": "m1",
        },
    )
    provider.add_vectors(col_name, [v1, v2])
    assert provider.get_statistics(col_name).total_vectors == 2

    # Delete by ID
    provider.delete_vectors(col_name, identifiers=["id-1"])
    assert provider.get_statistics(col_name).total_vectors == 1

    # Delete by metadata filter
    provider.delete_vectors(col_name, filter_metadata={"book_id": "b2"})
    assert provider.get_statistics(col_name).total_vectors == 0

    # Calling delete with neither ID nor metadata filter raises ValidationException
    msg = "Must specify either identifiers or filter_metadata"
    with pytest.raises(ValidationException, match=msg):
        provider.delete_vectors(col_name)


def test_similarity_search_filtering(provider: ChromaDBProvider) -> None:
    """Verifies similarity search is functional with limit and metadata filters."""
    col_name = "search_test"
    provider.create_collection(col_name)

    v1 = IndexedVector(
        identifier="id-1",
        vector=[1.0, 0.0],
        metadata={
            "embedding_id": "e1",
            "chunk_id": "c1",
            "book_id": "filter-book",
            "page_number": 1,
            "chapter_id": "ch1",
            "section_id": "s1",
            "model_identifier": "m1",
        },
    )
    v2 = IndexedVector(
        identifier="id-2",
        vector=[0.9, 0.1],
        metadata={
            "embedding_id": "e2",
            "chunk_id": "c2",
            "book_id": "other-book",
            "page_number": 2,
            "chapter_id": "ch1",
            "section_id": "s2",
            "model_identifier": "m1",
        },
    )
    provider.add_vectors(col_name, [v1, v2])

    # Search without filter
    res = provider.query_similarity(col_name, vector=[1.0, 0.0], limit=2)
    assert len(res.results) == 2
    assert res.total_candidates == 2
    assert isinstance(res.search_duration, float)

    # Search with filter matching v1
    res_filtered = provider.query_similarity(
        col_name, vector=[1.0, 0.0], limit=2, filter_metadata={"book_id": "filter-book"}
    )
    assert len(res_filtered.results) == 1
    assert res_filtered.results[0].identifier == "id-1"


def test_empty_collection(provider: ChromaDBProvider) -> None:
    """Verifies that actions on non-existent collection raise ValidationException."""
    col_name = "non_existent_collection"

    with pytest.raises(ValidationException, match="does not exist"):
        provider.add_vectors(col_name, [])

    with pytest.raises(ValidationException, match="does not exist"):
        provider.update_vectors(col_name, [])

    with pytest.raises(ValidationException, match="does not exist"):
        provider.delete_vectors(col_name, identifiers=["some-id"])

    with pytest.raises(ValidationException, match="does not exist"):
        provider.query_similarity(col_name, vector=[0.1], limit=1)

    with pytest.raises(ValidationException, match="does not exist"):
        provider.get_statistics(col_name)


def test_invalid_vectors_and_metadata(provider: ChromaDBProvider) -> None:
    """Verifies validation exceptions for empty vectors or missing metadata."""
    col_name = "invalid_fields_test"
    provider.create_collection(col_name)

    # 1. Empty vectors list
    with pytest.raises(ValidationException, match="Vector list must not be empty"):
        provider.add_vectors(col_name, [])

    # 2. Empty vector
    v_empty = IndexedVector(identifier="v-empty", vector=[], metadata={"book_id": "b1"})
    with pytest.raises(ValidationException, match="Empty or missing vector"):
        provider.add_vectors(col_name, [v_empty])

    # 3. Missing metadata
    v_no_meta = IndexedVector(identifier="v-no-meta", vector=[0.1], metadata={})
    with pytest.raises(ValidationException, match="Missing metadata"):
        provider.add_vectors(col_name, [v_no_meta])

    # 4. Missing required metadata keys
    v_partial_meta = IndexedVector(
        identifier="v-partial",
        vector=[0.1],
        metadata={"book_id": "b1"},  # missing other required fields
    )
    with pytest.raises(ValidationException, match="Missing required metadata key"):
        provider.add_vectors(col_name, [v_partial_meta])


def test_dimension_mismatch(provider: ChromaDBProvider) -> None:
    """Verifies that dimension mismatch throws ValidationException."""
    col_name = "dimension_test"
    provider.create_collection(col_name)

    v1 = IndexedVector(
        identifier="id-1",
        vector=[0.1, 0.2],
        metadata={
            "embedding_id": "e1",
            "chunk_id": "c1",
            "book_id": "b1",
            "page_number": 1,
            "chapter_id": "ch1",
            "section_id": "s1",
            "model_identifier": "m1",
        },
    )
    v2_wrong = IndexedVector(
        identifier="id-2",
        vector=[0.3, 0.4, 0.5],  # Dimension 3 instead of 2
        metadata={
            "embedding_id": "e2",
            "chunk_id": "c2",
            "book_id": "b1",
            "page_number": 2,
            "chapter_id": "ch1",
            "section_id": "s2",
            "model_identifier": "m1",
        },
    )

    # Batch dimension mismatch
    with pytest.raises(ValidationException, match="Dimension mismatch in batch"):
        provider.add_vectors(col_name, [v1, v2_wrong])

    # Add v1 successfully
    provider.add_vectors(col_name, [v1])

    # Try to add wrong dimension afterwards
    with pytest.raises(ValidationException, match="does not match collection dimension"):
        provider.add_vectors(col_name, [v2_wrong])


def test_reset_index(provider: ChromaDBProvider) -> None:
    """Verifies that reset_index drops all created collections."""
    col_1 = "collection_1"
    col_2 = "collection_2"

    provider.create_collection(col_1)
    provider.create_collection(col_2)

    assert provider.has_collection(col_1)
    assert provider.has_collection(col_2)

    provider.reset_index()

    assert not provider.has_collection(col_1)
    assert not provider.has_collection(col_2)
