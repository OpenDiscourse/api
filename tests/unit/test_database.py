"""Unit tests for database models and operations."""

import pytest
from datetime import datetime
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from govinfo_client.db.models import Base, Collection, Package, Granule, SearchCache


@pytest.fixture
def db_session():
    """Create an in-memory database for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


class TestDatabaseModels:
    """Test database models."""

    def test_create_collection(self, db_session):
        """Test creating a collection."""
        coll = Collection(
            collection_code="BILLS",
            collection_name="Congressional Bills",
            package_count=197925,
            granule_count=None,
        )

        db_session.add(coll)
        db_session.commit()

        # Query it back
        stmt = select(Collection).where(Collection.collection_code == "BILLS")
        result = db_session.scalar(stmt)

        assert result is not None
        assert result.collection_code == "BILLS"
        assert result.package_count == 197925

    def test_create_package(self, db_session):
        """Test creating a package."""
        # First create a collection
        coll = Collection(
            collection_code="BILLS",
            collection_name="Congressional Bills",
            package_count=100,
        )
        db_session.add(coll)
        db_session.commit()

        # Create a package
        pkg = Package(
            package_id="BILLS-115hr1625enr",
            title="Test Bill",
            collection_id=coll.id,
            collection_code="BILLS",
            date_issued="2018-04-14",
        )

        db_session.add(pkg)
        db_session.commit()

        # Query it back
        stmt = select(Package).where(Package.package_id == "BILLS-115hr1625enr")
        result = db_session.scalar(stmt)

        assert result is not None
        assert result.title == "Test Bill"
        assert result.collection.collection_code == "BILLS"

    def test_package_relationships(self, db_session):
        """Test package-collection relationships."""
        coll = Collection(
            collection_code="FR",
            collection_name="Federal Register",
            package_count=100,
        )
        db_session.add(coll)
        db_session.commit()

        # Add multiple packages
        for i in range(3):
            pkg = Package(
                package_id=f"FR-2024-01-0{i+1}",
                collection_id=coll.id,
                collection_code="FR",
            )
            db_session.add(pkg)

        db_session.commit()

        # Check relationship
        stmt = select(Collection).where(Collection.collection_code == "FR")
        result = db_session.scalar(stmt)

        assert len(result.packages) == 3

    def test_create_granule(self, db_session):
        """Test creating a granule."""
        # Create collection and package first
        coll = Collection(
            collection_code="CREC",
            collection_name="Congressional Record",
            package_count=100,
        )
        db_session.add(coll)
        db_session.commit()

        pkg = Package(
            package_id="CREC-2024-01-03",
            collection_id=coll.id,
            collection_code="CREC",
        )
        db_session.add(pkg)
        db_session.commit()

        # Create granule
        granule = Granule(
            granule_id="CREC-2024-01-03-pt1-PgH1",
            title="House Section",
            package_id=pkg.id,
            package_identifier="CREC-2024-01-03",
            granule_class="HOUSE",
        )

        db_session.add(granule)
        db_session.commit()

        # Query it back
        stmt = select(Granule).where(Granule.granule_id == "CREC-2024-01-03-pt1-PgH1")
        result = db_session.scalar(stmt)

        assert result is not None
        assert result.title == "House Section"
        assert result.package.package_id == "CREC-2024-01-03"

    def test_search_cache(self, db_session):
        """Test search cache model."""
        import hashlib

        query = "test query"
        query_hash = hashlib.sha256(query.encode()).hexdigest()

        cache = SearchCache(
            query_hash=query_hash,
            query=query,
            results={"count": 10, "items": []},
            result_count=10,
            expires_at=datetime.utcnow(),
        )

        db_session.add(cache)
        db_session.commit()

        # Query it back
        stmt = select(SearchCache).where(SearchCache.query_hash == query_hash)
        result = db_session.scalar(stmt)

        assert result is not None
        assert result.query == query
        assert result.result_count == 10

    def test_json_fields(self, db_session):
        """Test JSON field storage."""
        coll = Collection(
            collection_code="TEST",
            collection_name="Test Collection",
            package_count=1,
        )
        db_session.add(coll)
        db_session.commit()

        pkg = Package(
            package_id="TEST-123",
            collection_id=coll.id,
            collection_code="TEST",
            download_links={"pdf": "http://example.com/pdf", "xml": "http://example.com/xml"},
            metadata={"custom_field": "custom_value", "number": 42},
        )

        db_session.add(pkg)
        db_session.commit()

        # Query and verify JSON data
        stmt = select(Package).where(Package.package_id == "TEST-123")
        result = db_session.scalar(stmt)

        assert result.download_links["pdf"] == "http://example.com/pdf"
        assert result.metadata["custom_field"] == "custom_value"
        assert result.metadata["number"] == 42
