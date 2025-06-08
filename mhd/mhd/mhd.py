import datetime
import enum
from typing import List, Optional

from sqlalchemy import (
    JSON,
    DateTime,
    ForeignKeyConstraint,
    Index,
    Integer,
    PrimaryKeyConstraint,
    Sequence,
    String,
    TypeDecorator,
    UniqueConstraint,
    text,
)
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class IntEnum(TypeDecorator):
    impl = Integer
    cache_ok = True

    def __init__(self, enumtype, *args, **kwargs):
        super(IntEnum, self).__init__(*args, **kwargs)
        self._enumtype = enumtype

    def process_bind_param(self, value, dialect):
        if isinstance(value, int):
            return value

        return value.value

    def process_result_value(self, value, dialect):
        return self._enumtype(value)


class StrEnum(TypeDecorator):
    impl = String
    cache_ok = True

    def __init__(self, enumtype, *args, **kwargs):
        super(StrEnum, self).__init__(*args, **kwargs)
        self._enumtype = enumtype

    def process_bind_param(self, value, dialect):
        if isinstance(value, self._enumtype):
            return value.value

        return value

    def process_result_value(self, value, dialect):
        return self._enumtype(value)


class Base(AsyncAttrs, DeclarativeBase):
    @classmethod
    def get_field_alias(cls, name: str) -> str:
        alias_exceptions = cls.get_field_alias_exceptions()
        if name in alias_exceptions:
            return alias_exceptions[name]
        return name

    def get_field_alias_exceptions(self):
        return {}


metadata = Base.metadata


unique_identifier_seq = Sequence("unique_identifier_seq", metadata=metadata)


class RepositoryStatus(enum.IntEnum):
    NEW = 0
    ACTIVE = 1
    INACTIVE = 2
    INVALID = 3


class ApiTokenStatus(enum.IntEnum):
    INVALID = 0
    VALID = 1


class DatasetStatus(enum.IntEnum):
    PRIVATE = 0
    PUBLIC = 1
    INVALID = 2


class DatasetRevisionStatus(enum.IntEnum):
    INVALID = 0
    VALID = 1


class Identifier(Base):
    __tablename__ = "identifier"
    __field_alias_exceptions__: dict[str, str] = {
        "id_": "id",
    }
    __table_args__ = (
        PrimaryKeyConstraint("id", name="identifier_pkey"),
        UniqueConstraint("prefix", name="identifier_prefix_key"),
        Index("ix_identifier_id", "id", unique=True),
    )

    id: Mapped[int] = mapped_column(Integer, unique_identifier_seq, primary_key=True)
    prefix: Mapped[str] = mapped_column(String(255))
    last_identifier: Mapped[int] = mapped_column(Integer)


class Repository(Base):
    __tablename__ = "repository"
    __field_alias_exceptions__: dict[str, str] = {
        "id_": "id",
    }
    __table_args__ = (
        PrimaryKeyConstraint("id", name="repository_pkey"),
        Index("ix_repository_id", "id", unique=True),
    )

    id: Mapped[int] = mapped_column(Integer, unique_identifier_seq, primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(String(512))
    join_datetime: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=text("now()")
    )
    status: Mapped[RepositoryStatus] = mapped_column(
        IntEnum(RepositoryStatus),
        nullable=False,
        default=RepositoryStatus.NEW,
    )
    public_key: Mapped[Optional[str]] = mapped_column(String(2028))

    api_tokens: Mapped[List["ApiToken"]] = relationship(
        "ApiToken", back_populates="repository"
    )


class ApiToken(Base):
    __tablename__ = "api_token"
    __field_alias_exceptions__: dict[str, str] = {
        "id_": "id",
    }
    __table_args__ = (
        ForeignKeyConstraint(
            ["repository_id"], ["repository.id"], name="api_token_repository_id_fkey"
        ),
        PrimaryKeyConstraint("id", name="api_token_pkey"),
        UniqueConstraint("name", "repository_id", name="uq_api_token_name"),
        Index("ix_api_token_id", "id", unique=True),
    )

    id: Mapped[int] = mapped_column(Integer, unique_identifier_seq, primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(String(512))
    token_hash: Mapped[str] = mapped_column(String(512))
    expiration_datetime: Mapped[datetime.datetime] = mapped_column(DateTime)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=text("now()")
    )
    modified_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    status: Mapped[ApiTokenStatus] = mapped_column(
        IntEnum(ApiTokenStatus),
        nullable=False,
        default=ApiTokenStatus.INVALID,
    )
    repository_id: Mapped[int] = mapped_column(Integer)
    repository: Mapped["Repository"] = relationship(
        "Repository", back_populates="api_tokens"
    )


class Dataset(Base):
    __tablename__ = "dataset"
    __table_args__ = (
        ForeignKeyConstraint(
            ["repository_id"], ["repository.id"], name="dataset_repository_id_fkey"
        ),
        PrimaryKeyConstraint("id", name="dataset_pkey"),
        Index("ix_dataset_accession", "accession", unique=True),
    )

    id: Mapped[int] = mapped_column(Integer, unique_identifier_seq, primary_key=True)
    accession: Mapped[str] = mapped_column(String(255))
    dataset_repository_identifier: Mapped[str] = mapped_column(
        String(255), nullable=False
    )

    repository_id: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(True), server_default=text("now()")
    )
    status: Mapped[DatasetStatus] = mapped_column(
        IntEnum(DatasetStatus),
        nullable=False,
        default=DatasetStatus.PRIVATE,
    )
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    revision: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    revision_datetime: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=True, default=None
    )

    repository: Mapped["Repository"] = relationship("Repository")
    dataset_revisions: Mapped[List["DatasetRevision"]] = relationship(
        "DatasetRevision", back_populates="dataset"
    )


class AnnouncementFile(Base):
    __tablename__ = "announcement_file"
    __table_args__ = (
        ForeignKeyConstraint(
            ["dataset_id"], ["dataset.id"], name="announcement_file_dataset_id_fkey"
        ),
        PrimaryKeyConstraint("id", name="announcement_file_pkey"),
        Index("ix_announcement_file_id", "id", unique=True),
    )

    id: Mapped[int] = mapped_column(Integer, unique_identifier_seq, primary_key=True)
    dataset_id: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=text("now()")
    )
    hash_sha256: Mapped[str] = mapped_column(String(512))
    uri: Mapped[str] = mapped_column(String(1024))
    file: Mapped[dict] = mapped_column(JSON)
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    dataset: Mapped["Dataset"] = relationship("Dataset")
    dataset_revisions: Mapped[List["DatasetRevision"]] = relationship(
        "DatasetRevision", back_populates="file"
    )


class DatasetRevision(Base):
    __tablename__ = "dataset_revision"
    __table_args__ = (
        ForeignKeyConstraint(
            ["dataset_id"], ["dataset.id"], name="dataset_revision_dataset_id_fkey"
        ),
        ForeignKeyConstraint(
            ["file_id"], ["announcement_file.id"], name="dataset_revision_file_id_fkey"
        ),
        PrimaryKeyConstraint("id", name="dataset_revision_pkey"),
        UniqueConstraint("dataset_id", "revision", name="uq_dataset_id_revision"),
        Index("ix_dataset_revision_id", "id", unique=True),
    )

    id: Mapped[int] = mapped_column(Integer, unique_identifier_seq, primary_key=True)
    dataset_id: Mapped[int] = mapped_column(Integer)
    revision: Mapped[int] = mapped_column(Integer)
    revision_datetime: Mapped[datetime.datetime] = mapped_column(DateTime)
    task_id: Mapped[str] = mapped_column(String(512), nullable=False)
    status: Mapped[DatasetRevisionStatus] = mapped_column(
        IntEnum(DatasetRevisionStatus),
        nullable=False,
        default=DatasetRevisionStatus.INVALID,
    )
    description: Mapped[str] = mapped_column(String(512), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=text("now()")
    )
    file_id: Mapped[int] = mapped_column(Integer)
    repository_revision: Mapped[Optional[int]] = mapped_column(Integer)
    repository_revision_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime
    )
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    dataset: Mapped["Dataset"] = relationship(
        "Dataset", back_populates="dataset_revisions"
    )
    file: Mapped["AnnouncementFile"] = relationship(
        "AnnouncementFile", back_populates="dataset_revisions"
    )
