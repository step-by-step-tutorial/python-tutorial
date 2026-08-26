import os
from dataclasses import dataclass
from types import MappingProxyType

from data_platform.config.keys import Key


@dataclass(frozen=True)
class MessagingSettings:
    bootstrap_servers: str
    channel_name: str
    audit_channel_name: str
    starting_offsets: str


messaging = MappingProxyType(
    {
        Key.HOUSE_KAFKA_CONSUMER: MessagingSettings(
            bootstrap_servers=os.getenv("DATA_PLATFORM_HOUSE_STREAMING_BOOTSTRAP_SERVERS", "localhost:9092"),
            channel_name=os.getenv("DATA_PLATFORM_HOUSE_CHANNEL_NAME", "house.events.v1"),
            audit_channel_name=os.getenv("DATA_PLATFORM_HOUSE_AUDIT_CHANNEL_NAME", "house.audit.events.v1"),
            starting_offsets=os.getenv("DATA_PLATFORM_HOUSE_STREAMING_STARTING_OFFSETS", "earliest"),
        ),
        Key.HOUSE_KAFKA_PRODUCER: MessagingSettings(
            bootstrap_servers=os.getenv("DATA_PLATFORM_HOUSE_STREAMING_BOOTSTRAP_SERVERS", "localhost:9092"),
            channel_name=os.getenv("DATA_PLATFORM_HOUSE_CHANNEL_NAME", "house.events.v1"),
            audit_channel_name=os.getenv("DATA_PLATFORM_HOUSE_AUDIT_CHANNEL_NAME", "house.audit.events.v1"),
            starting_offsets=os.getenv("DATA_PLATFORM_HOUSE_STREAMING_STARTING_OFFSETS", "earliest"),
        ),
        Key.ONLINE_SHOPPING_KAFKA_CONSUMER: MessagingSettings(
            bootstrap_servers=os.getenv("DATA_PLATFORM_ONLINE_SHOPPING_STREAMING_BOOTSTRAP_SERVERS", "localhost:9092"),
            channel_name=os.getenv("DATA_PLATFORM_ONLINE_SHOPPING_CHANNEL_NAME", "online-shopping.events.v1"),
            audit_channel_name=os.getenv("DATA_PLATFORM_ONLINE_SHOPPING_AUDIT_CHANNEL_NAME", "online-shopping.audit.events.v1"),
            starting_offsets=os.getenv("DATA_PLATFORM_ONLINE_SHOPPING_STREAMING_STARTING_OFFSETS", "earliest"),
        ),
        Key.AUDIT_KAFKA_PRODUCER: MessagingSettings(
            bootstrap_servers=os.getenv("DATA_PLATFORM_AUDIT_STREAMING_BOOTSTRAP_SERVERS", "localhost:9092"),
            channel_name=os.getenv("DATA_PLATFORM_AUDIT_STREAM_CHANNEL_NAME", "audit.events.v1"),
            audit_channel_name=os.getenv("DATA_PLATFORM_AUDIT_CHANNEL_NAME", "audit.audit.events.v1"),
            starting_offsets=os.getenv("DATA_PLATFORM_AUDIT_STREAMING_STARTING_OFFSETS", "earliest"),
        ),
        Key.AUDIT_KAFKA_CONSUMER: MessagingSettings(
            bootstrap_servers=os.getenv("DATA_PLATFORM_AUDIT_STREAMING_BOOTSTRAP_SERVERS", "localhost:9092"),
            channel_name=os.getenv("DATA_PLATFORM_AUDIT_STREAM_CHANNEL_NAME", "audit.events.v1"),
            audit_channel_name=os.getenv("DATA_PLATFORM_AUDIT_CHANNEL_NAME", "audit.audit.events.v1"),
            starting_offsets=os.getenv("DATA_PLATFORM_AUDIT_STREAMING_STARTING_OFFSETS", "earliest"),
        ),
    }
)
