from sqlalchemy import Column, Integer, String, DateTime, text
from sqlalchemy.types import TIMESTAMP

from .database import Base


class Sip(Base):
    __tablename__ = 'sip'
    id = Column(String(20), primary_key=True)
    keyword = Column(String(30), primary_key=True)
    data = Column(String(255))
    flags = Column(Integer)


class User(Base):
    __tablename__ = 'users'
    extension = Column(String(20), primary_key=True)
    password = Column(String(20))
    name = Column(String(50))
    voicemail = Column(String(50))
    ringtimer = Column(Integer)
    noanswer = Column(String(100))
    recording = Column(String(50))
    outboundcid = Column(String(50))
    sipname = Column(String(50))
    mohclass = Column(String(80))
    noanswer_cid = Column(String(20))
    busy_cid = Column(String(20))
    chanunavail_cid = Column(String(20))
    noanswer_dest = Column(String(255))
    busy_dest = Column(String(255))
    chanunavail_dest = Column(String(255))


class Device(Base):
    __tablename__ = 'devices'
    id = Column(String(20), primary_key=True)
    tech = Column(String(20))
    dial = Column(String(50))
    devicetype = Column(String(20))
    user = Column(String(50))
    description = Column(String(50))
    emergency_cid = Column(String(100), )


class Group(Base):
    __tablename__ = 'api_groups'
    group_id = Column(String(2), primary_key=True)
    title = Column(String(50))


class Log(Base):
    __tablename__ = 'api_logs'
    id = Column(Integer(), primary_key=True)
    timestamp = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    ip = Column(String(20))
    type_name = Column(String(20))
    column_name = Column(String(20))
    value = Column(String(50))
