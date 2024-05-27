import datetime

import pytest
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType

from data_frame_basic_operation import person

INITIALIZE_SPARK = True


def expected_column_of_schema():
    return [
        "ID", "Salutation", "FirstName", "LastName", "DateOfBirth", "Gender", "MaritalStatus",
        "BirthNationality", "CurrentNationality",
        "Country", "Province", "City", "ZipCode", "Street", "HouseNumber",
        "MobilePhone", "EmailAddress",
        "JobTitle", "FieldOfStudy", "AcademicDegree"
    ]


def stub_multi_person():
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


def fake_person():
    return []


def fake_schema():
    return StructType()


def fake_session():
    session = SparkSession.builder.getOrCreate()
    yield session
    session.stop()


@pytest.fixture(scope='session')
def get_test_session(request) -> SparkSession:
    session = person.create_session()

    if hasattr(request, 'param') and request.param == INITIALIZE_SPARK:
        person.insert(session, person.get_schema(), stub_multi_person())

    yield session
    session.stop()


def test_connection_establishment_between_local_machine_and_containerized_spark():
    """
    Test the Spark connection can be established between the local machine and dockerized spark.

        GIVEN: nothing
        WHEN: create session
        THEN: return a spark session
    """
    actual = person.create_session()
    assert actual is not None
    actual.stop()


def test_given_schema_then_return_schema():
    """
    Test that the schema is correct.

        GIVEN: nothing
        WHEN: get the schema
        THEN: return the schema
    """
    actual = person.get_schema()
    assert [field.name for field in actual.fields] == expected_column_of_schema()


def test_given_data_when_insert_then_return_data_frame(get_test_session):
    """
    Tests the insertion of data in DataFrame.

        GIVEN: session, schema, data
        WHEN: insert data
        THEN: populated data frame
    """
    given_session = get_test_session
    given_schema = person.get_schema()
    given_data = stub_multi_person()

    actual = person.insert(given_session, given_schema, given_data)

    assert actual.columns == expected_column_of_schema()
    assert actual.count() == 3

    actual.show()


@pytest.mark.parametrize("session, schema, data, message", [
    (None, fake_schema(), fake_person(), "Spark session should not be null"),
    (fake_session(), None, fake_person(), "Schema should not be null"),
    (fake_session(), fake_schema(), None, "data should not be null"),
])
def test_given_invalid_data_when_insert_then_rais_value_error(session, schema, data, message):
    """
    Test data validation of insertion in DataFrame.

        GIVEN: session, schema, data
        WHEN: insert data
        THEN: raises ValueError
    """
    given_session = session
    given_schema = schema
    given_data = data

    with pytest.raises(ValueError) as exc_info:
        person.insert(given_session, given_schema, given_data)

    assert str(exc_info.value) == message


@pytest.mark.parametrize("get_test_session", [INITIALIZE_SPARK], indirect=True)
def test_given_id_then_return_row(get_test_session):
    """
    Test the finding one row of a DataFrame by ID.

        GIVEN: session, row ID
        WHEN: select by ID
        THEN: returns a row
    """
    given_id = 1
    given_session = get_test_session

    actual = person.select_by_id(given_session, given_id)

    assert actual.columns == expected_column_of_schema()
    assert actual.count() == 1

    actual.show()


@pytest.mark.parametrize("session, row_id, message", [
    (None, 0, "Spark session should not be null"),
    (fake_session(), None, "Row ID should not be null"),
])
def test_given_invalid_data_when_select_id_then_rais_value_error(session, row_id, message):
    """
    Test data validation of finding by ID in DataFrame.

        GIVEN: session, row ID
        WHEN: select by ID
        THEN: raises ValueError
    """
    given_session = session
    given_row_id = row_id

    with pytest.raises(ValueError) as exc_info:
        person.select_by_id(given_session, given_row_id)

    assert str(exc_info.value) == message
