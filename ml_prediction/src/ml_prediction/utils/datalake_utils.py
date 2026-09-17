def find_latest_partition(objects: list[dict]) -> list[dict]:
    partitions: dict[str, list[dict]] = {}
    for obj in objects:
        partition = obj["Key"].rsplit("/", 1)[0]
        partitions.setdefault(partition, []).append(obj)

    return max(partitions.values(), key=lambda sources: max(source.get("LastModified") for source in sources))
