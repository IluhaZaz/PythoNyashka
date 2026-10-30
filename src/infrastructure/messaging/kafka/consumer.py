from aiokafka import AIOKafkaConsumer


def create_consumer(
    bootstrap_servers: str, topic: str, group_id: str,
) -> AIOKafkaConsumer:
    return AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id=group_id,
        enable_auto_commit=False,
        auto_offset_reset="earliest",
    )
