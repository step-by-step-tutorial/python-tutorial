import datetime

import pytest
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType

from spark_tutorial.data_frame_basic import person_service, person_model, session_factory


def test_person_list():
    return [
        (
            1, "Ms.", "Alice", "Smith", datetime.datetime.strptime("1995-01-15", '%Y-%m-%d').date(), "Female", "Single",
            "American", "American",
            "USA", "New York", "New York", "10001", "5th Ave", 101,
            "1234567890", "alice.smith@example.com",
            "Engineer", "MIT", "Master's"
        ),
        (
            2, "Mr.", "Bob", "Jones", datetime.datetime.strptime("2000-02-25", '%Y-%m-%d').date(), "Male", "Married",
            "Canadian", "Canadian",
            "Canada", "Ontario", "Toronto", "M5A 1A1", "King St", 202,
            "2345678901", "bob.jones@example.com",
            "Designer", "University of Toronto", "Bachelor's"
        ),
        (
            3, "Mrs.", "Cindy", "Lee", datetime.datetime.strptime("1998-03-30", '%Y-%m-%d').date(), "Female", "Married",
            "British", "British", "UK",
            "England", "London", "E1 6AN", "Queen St", 303,
            "3456789012", "cindy.lee@example.com",
            "Teacher", "Oxford", "Master's"
        )
    ]


def given_session():
    session = SparkSession.builder.getOrCreate()
    yield session
    session.stop()


@pytest.fixture(scope='session')
def given_session_with_initialization(request) -> SparkSession:
    session = session_factory.create_session()
    person_service.insert(session, person_model.get_schema(), test_person_list())
    yield session
    session.stop()


def test_given_data_when_insert_then_return_data_frame(given_session_with_initialization):
    """
    Tests the insertion of data in DataFrame.

        GIVEN: session, schema, data
        WHEN: insert data
        THEN: populated data frame
    """
    given_session = given_session_with_initialization
    given_schema = person_model.get_schema()
    given_data = test_person_list()

    actual = person_service.insert(given_session, given_schema, given_data)
    assert actual.count() == 3
    actual.show()


def test_given_id_then_return_row(given_session_with_initialization):
    """
    Test the finding one row of a DataFrame by ID.

        GIVEN: session, row ID
        WHEN: select by ID
        THEN: returns a row
    """
    given_session = given_session_with_initialization
    given_id = 1

    actual = person_service.select_by_id(given_session, given_id)

    assert actual.count() == 1
    actual.show()


@pytest.mark.parametrize(
    "given_session, given_schema, given_data, expected_message",
    [
        (None, StructType(), [], "Spark session should not be null"),
        (given_session(), None, [], "Schema should not be null"),
        (given_session(), StructType(), None, "data should not be null"),
    ]
)
def test_given_invalid_data_when_insert_then_rais_value_error(
        given_session,
        given_schema,
        given_data,
        expected_message
):
    """
    Test data validation of insertion in DataFrame.

        GIVEN: session, schema, data
        WHEN: insert data
        THEN: raises ValueError
    """

    with pytest.raises(ValueError) as exc_info:
        person_service.insert(given_session, given_schema, given_data)

    assert str(exc_info.value) == expected_message


@pytest.mark.parametrize(
    "given_session, given_row_id, expected_message",
    [
        (None, 0, "Spark session should not be null"),
        (given_session(), None, "Row ID should not be null"),
    ]
)
def test_given_invalid_data_when_select_id_then_rais_value_error(
        given_session,
        given_row_id,
        expected_message
):
    """
    Test data validation of finding by ID in DataFrame.

        GIVEN: session, row ID
        WHEN: select by ID
        THEN: raises ValueError
    """

    with pytest.raises(ValueError) as exc_info:
        person_service.select_by_id(given_session, given_row_id)

    assert str(exc_info.value) == expected_message
