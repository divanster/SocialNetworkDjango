import asyncio
import threading
import json
import logging
import uuid

from aiokafka import AIOKafkaProducer
from django.conf import settings
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)


class UUIDEncoder(json.JSONEncoder):
    """
    Converts UUID objects to strings before JSON encoding.
    """
    def default(self, obj):
        if isinstance(obj, uuid.UUID):
            return str(obj)
        return super().default(obj)


class KafkaService:
    """
    Singleton wrapper around an async AIOKafkaProducer, exposing a sync API.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    # One‐time setup of encryption
                    key = settings.KAFKA_ENCRYPTION_KEY
                    if not key:
                        raise ValueError("KAFKA_ENCRYPTION_KEY must be set")
                    cls._instance._cipher_suite = Fernet(key.encode())
                    cls._instance._producer = None
        return cls._instance

    async def _get_producer(self):
        """
        Lazily start the AIOKafkaProducer with idempotence, acks, compression, and linger.
        """
        if self._producer is None:
            p = AIOKafkaProducer(
                bootstrap_servers=settings.KAFKA_BROKER_URL,
                acks="all",
                enable_idempotence=True,
                compression_type="lz4",
                linger_ms=100,
            )
            await p.start()
            self._producer = p
            logger.info("AIOKafkaProducer started (idempotent, acks=all, compression=lz4)")
        return self._producer

    def _encrypt(self, message: dict) -> bytes:
        """
        JSON-encode + encrypt via Fernet.
        """
        try:
            raw = json.dumps(message, cls=UUIDEncoder).encode("utf-8")
            return self._cipher_suite.encrypt(raw)
        except Exception as e:
            logger.error(f"Error encrypting Kafka message: {e}")
            raise

    def send_message(self, topic_key: str, message: dict, retries: int = 3):
        """
        Synchronously send an encrypted message to Kafka, retrying up to `retries` times.
        """
        topic = settings.KAFKA_TOPICS.get(topic_key)
        if not topic:
            raise ValueError(f"Unknown Kafka topic key: {topic_key}")

        payload = self._encrypt(message)
        last_exc = None

        for attempt in range(1, retries + 1):
            try:
                async def _do_send():
                    producer = await self._get_producer()
                    # send_and_wait returns RecordMetadata
                    return await producer.send_and_wait(topic, value=payload)

                loop = asyncio.new_event_loop()
                try:
                    result = loop.run_until_complete(_do_send())
                    logger.info(f"[KafkaService] Sent to '{topic}' (attempt {attempt}): {message}")
                    return result
                finally:
                    loop.close()

            except Exception as e:
                last_exc = e
                logger.error(f"[KafkaService] Attempt {attempt} failed for topic '{topic}': {e}")
                if attempt == retries:
                    logger.error(f"[KafkaService] Gave up after {retries} attempts.")
                    raise

        # in case somehow the loop never sends
        raise last_exc or RuntimeError("Failed to send message to Kafka")

    def flush(self):
        """
        Flush any pending messages.
        """
        if self._producer:
            async def _do_flush():
                await self._producer.flush()

            loop = asyncio.new_event_loop()
            try:
                loop.run_until_complete(_do_flush())
                logger.info("AIOKafkaProducer flush completed")
            finally:
                loop.close()

    def close(self):
        """
        Stop the producer and release resources.
        """
        if self._producer:
            async def _do_close():
                await self._producer.stop()

            loop = asyncio.new_event_loop()
            try:
                loop.run_until_complete(_do_close())
                logger.info("AIOKafkaProducer stopped")
            finally:
                loop.close()
            self._producer = None
