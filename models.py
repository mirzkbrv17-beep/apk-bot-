from datetime import datetime
from sqlalchemy import String, Integer, BigInteger, Boolean, DateTime, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.db import Base

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str|None] = mapped_column(String(128), nullable=True)
    full_name: Mapped[str] = mapped_column(String(256), default="")
    blocked: Mapped[bool] = mapped_column(Boolean, default=False)
    language: Mapped[str] = mapped_column(String(8), default="uz")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class APK(Base):
    __tablename__ = "apks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(256), index=True)
    description: Mapped[str] = mapped_column(Text)
    file_id: Mapped[str] = mapped_column(Text)
    file_name: Mapped[str] = mapped_column(String(256), default="")
    file_size: Mapped[int] = mapped_column(BigInteger, default=0)
    version: Mapped[str] = mapped_column(String(64), default="Noma'lum")
    category: Mapped[str] = mapped_column(String(100), default="Boshqa")
    downloads: Mapped[int] = mapped_column(Integer, default=0)
    hidden: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class APKVersion(Base):
    __tablename__ = "apk_versions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    apk_id: Mapped[int] = mapped_column(ForeignKey("apks.id"))
    file_id: Mapped[str] = mapped_column(Text)
    version: Mapped[str] = mapped_column(String(64), default="Noma'lum")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Channel(Base):
    __tablename__ = "channels"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    chat_id: Mapped[str] = mapped_column(String(128), unique=True)
    title: Mapped[str] = mapped_column(String(256), default="")
    url: Mapped[str] = mapped_column(String(512), default="")

class Favorite(Base):
    __tablename__ = "favorites"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    apk_id: Mapped[int] = mapped_column(ForeignKey("apks.id"))
    __table_args__ = (UniqueConstraint("user_id", "apk_id"),)

class Download(Base):
    __tablename__ = "downloads"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    apk_id: Mapped[int] = mapped_column(ForeignKey("apks.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Review(Base):
    __tablename__ = "reviews"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger)
    apk_id: Mapped[int] = mapped_column(ForeignKey("apks.id"))
    rating: Mapped[int] = mapped_column(Integer)
    comment: Mapped[str] = mapped_column(Text, default="")

class Request(Base):
    __tablename__ = "apk_requests"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger)
    title: Mapped[str] = mapped_column(String(256))
    status: Mapped[str] = mapped_column(String(32), default="yangi")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Setting(Base):
    __tablename__ = "settings"
    key: Mapped[str] = mapped_column(String(128), primary_key=True)
    value: Mapped[str] = mapped_column(Text, default="")

class EmojiMap(Base):
    __tablename__ = "emoji_maps"
    key: Mapped[str] = mapped_column(String(128), primary_key=True)
    emoji: Mapped[str] = mapped_column(String(32), default="✨")
    custom_id: Mapped[str] = mapped_column(String(128), default="")
