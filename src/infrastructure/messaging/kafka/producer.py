from aiokafka import AIOKafkaProducer


def create_producer(bootstrap_servers: str, request_timeout_ms: int) -> AIOKafkaProducer:
    return AIOKafkaProducer(
        bootstrap_servers=bootstrap_servers,
        acks="all",
        request_timeout_ms=request_timeout_ms,
    )
