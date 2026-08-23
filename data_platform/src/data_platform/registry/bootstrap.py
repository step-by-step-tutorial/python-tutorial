def initialize_registries() -> None:
    from data_platform.house.dataset import register_house_dataset
    from data_platform.house.event_converter import register_house_event_converter
    from data_platform.house.ingestors import register_house_ingestors, register_house_lazy_ingestors
    from data_platform.sale.dataset import register_sale_dataset
    from data_platform.sale.event_converter import register_sale_event_converter
    from data_platform.sale.ingestors import register_sale_ingestors, register_sale_lazy_ingestors

    register_sale_dataset()
    register_house_dataset()
    register_sale_event_converter()
    register_house_event_converter()
    register_sale_ingestors()
    register_house_ingestors()
    register_sale_lazy_ingestors()
    register_house_lazy_ingestors()
