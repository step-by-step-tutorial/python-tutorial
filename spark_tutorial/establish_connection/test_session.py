from spark_tutorial.establish_connection import session_factory


def test_connection_establishment_between_local_machine_and_containerized_spark():
    """
    Test the Spark connection can be established between the local machine and dockerized spark_tutorial.

        GIVEN: nothing
        WHEN: create session
        THEN: return a spark_tutorial session
    """
    actual = session_factory.create_session()
    assert actual is not None
    actual.stop()
