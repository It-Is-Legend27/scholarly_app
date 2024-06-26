"""Provides a class for accessing and operating on a SQLite database.

Provides the class `ScholarlyDatabase` for accessing a SQLite database
and inserting records in the students table and award criteria table.

"""

import sqlite3
import json
from student_record import (
    StudentRecord,
    read_student_data_from_csv,
    write_student_data_to_csv,
)
from award_criteria_record import AwardCriteriaRecord
from pypika import Query, Table, Field, Schema, Column, Columns, Order


class FileIsOpenError(Exception):
    """Class for defining the "FileIsOpen" exception."""

    pass


class ScholarlyDatabase:
    """Class to operate SQLite3 database.

    Class to allow easy manipulation and operation of a SQLite database with
    the tables `students` and `award_criteria`.
    """

    __award_criteria_table_name: str = "award_criteria"

    __students_columns: list[Column] = Columns(
        ("name", "TEXT"),
        ("student_ID", "TEXT PRIMARY KEY"),
        ("cum_gpa", "REAL"),
        ("major", "TEXT COLLATE NOCASE"),
        ("classification", "TEXT COLLATE NOCASE"),
        ("earned_credits", "INTEGER"),
        ("enrolled", "TEXT COLLATE NOCASE"),
        ("email", "TEXT"),
        ("gender", "TEXT COLLATE NOCASE"),
        ("in_state", "TEXT COLLATE NOCASE"),
    )
    __award_criteria_columns: list[Column] = Columns(
        ("name", "TEXT PRIMARY KEY COLLATE NOCASE"),
        ("criteria", "JSON"),
        ("limit", "INTEGER"),
        ("sort", "JSON"),
    )

    def __init__(self, file_path: str, students_table_name=None) -> None:
        """Creates an instance of ScholarlyDatabase.

        Creates an instance of ScholarlyDatabase for accessing and
        performing queries on the SQLite3 database.

        Args:
            file_path (str): File path for the SQLite3 database.
        """
        self.database_path: str = file_path
        self.students_table_name = students_table_name

    def get_students_table_name(self) -> str:
        """Returns the name of the student table in usage.

        Returns:
            str: Name of table.
        """
        return self.students_table_name

    def set_students_table_name(self, table_name: str) -> None:
        """Sets the name of the student table in usage.

        Args:
            table_name (str): Name of the table.
        """
        self.students_table_name = table_name

    @classmethod
    def get_award_criteria_table_name(cls) -> str:
        """Returns the name of the `award_criteria` table.

        Returns the name of the `award_criteria` table.

        Returns:
            Name of the `award_criteria` table as a `str`.
        """
        return cls.__award_criteria_table_name

    @classmethod
    def get_students_table_columns(cls) -> list[Column]:
        """Returns the columns for the `students` table.

        Returns the columns for the `students` table.

        Returns:
            Columns for the `students` table as `list[Column]`.

        """
        return cls.__students_columns

    @classmethod
    def get_award_criteria_columns(cls) -> list[Column]:
        """Returns the columns for the `award_criteria` table.

        Returns the columns for the `award_criteria` table.

        Returns:
            Columns for the `award_criteria` table as `list[Column]`.

        """
        return cls.__award_criteria_columns

    def insert_student(self, record: StudentRecord) -> None:
        """Inserts a student record into the `students` table.

        Inserts a `StudentRecord` into the `students` table.

        Args:
            record (StudentRecord): A student record.
        """
        query: Query = Query.into(self.students_table_name).insert(*record.to_tuple())
        conn: sqlite3.Connection = sqlite3.connect(self.database_path)
        cursor: sqlite3.Cursor = conn.cursor()

        cursor.execute(str(query))
        conn.commit()
        conn.close()

    def insert_award_criteria(self, record: AwardCriteriaRecord) -> None:
        """Inserts award criteria into the `award_criteria` table.

        Inserts award criteria into the `award_criteria` table.

        Args:
            record (AwardRecord): An award record.
        """
        query: Query = Query.into(self.__award_criteria_table_name).insert(
            record.name,
            json.dumps(record.criteria),
            record.limit,
            json.dumps(record.sort),
        )
        conn: sqlite3.Connection = sqlite3.connect(self.database_path)
        cursor: sqlite3.Cursor = conn.cursor()

        cursor.execute(str(query))
        conn.commit()
        conn.close()

    def remove_award_criteria(self, name: str) -> None:
        """Remove specified award criteria from table.

        Args:
            name (str): Name of the award criteria / scholarship.
        """
        query: Query = (
            Query.from_(self.__award_criteria_table_name)
            .where(Field("name") == name)
            .delete()
        )

        conn: sqlite3.Connection = sqlite3.connect(self.database_path)
        cursor: sqlite3.Cursor = conn.cursor()

        cursor.execute(str(query))
        conn.commit()
        conn.close()

    def update_award_criteria(
        self, name: str, criteria: dict, limit: int, sort: list
    ) -> None:
        """Update the specified award criteria.

        Args:
            name (str): Name of award criteria to update.
            criteria (dict): Criteria of the award.
            limit (int): Limit on returned matches.
            sort (list): List specifying sorting behavior.
        """
        query: Query = (
            Query.update(self.__award_criteria_table_name)
            .set(Field("criteria"), json.dumps(criteria))
            .set(Field("limit"), limit)
            .set(Field("sort"), json.dumps(sort))
            .where(Field("name") == name)
        )

        conn: sqlite3.Connection = sqlite3.connect(self.database_path)
        cursor: sqlite3.Cursor = conn.cursor()

        cursor.execute(str(query))
        conn.commit()
        conn.close()

    def create_table(self, table_name: str, columns: list[Column]):
        """Creates a table in a SQLite database.

        Creates a table in a SQlite Database file.

        Args:
            table_name (str): Name of the table.
            columns (list[Column]): Columns for the table.
        """
        query: Query = Query.create_table(table_name).columns(*columns).if_not_exists()

        conn: sqlite3.Connection = sqlite3.connect(self.database_path)
        cursor: sqlite3.Cursor = conn.cursor()

        cursor.execute(str(query))
        conn.commit()
        conn.close()

    def drop_table(self, table_name: str):
        """Drops a table from the database.

        Drops a table from the SQLite3 database.

        Args:
            table_name (str): Name of the table.
        """
        query: Query = Query.drop_table(table_name).if_exists()
        conn: sqlite3.Connection = sqlite3.connect(self.database_path)
        cursor: sqlite3.Cursor = conn.cursor()

        cursor.execute(str(query))
        conn.commit()
        conn.close()

    def select_award_criteria(self, award_name: str) -> AwardCriteriaRecord | None:
        """Gets the award criteria for a given award.

        Returns the award criteria for a given scholarship based on the name.

        Args:
            award_name (str): Name of the scholarship or award.
        Returns:
            Returns AwardCriteriaRecord if found, else returns None.
        """
        query: Query = (
            Query.from_(self.__award_criteria_table_name)
            .select("*")
            .where(Field("name") == award_name)
        )

        conn: sqlite3.Connection = sqlite3.connect(self.database_path)
        cursor: sqlite3.Cursor = conn.cursor()
        cursor.execute(str(query))

        data = cursor.fetchone()
        record: AwardCriteriaRecord = None
        # If record does exist
        if data:
            name, criteria, limit, sort = data
            record = AwardCriteriaRecord(
                name, json.loads(criteria), limit, json.loads(sort)
            )

        conn.commit()
        conn.close()

        return record

    def file_is_open(self, file_path: str) -> bool:
        """Checks if the file actively open or not.

        Args:
            file_path (str): Path to the file.

        Returns:
            bool: True if file is open, False otherwise.
        """
        query: Query = (
            Query.from_("sqlite_master")
            .select("name")
            .where(Field("type") == "table")
            .where(Field("name") == file_path)
        )

        conn: sqlite3.Connection = sqlite3.connect(self.database_path)
        cursor: sqlite3.Cursor = conn.cursor()
        cursor.execute(str(query))

        data = cursor.fetchone()

        file_exists: bool = False

        # If record does exist
        if data != None:
            file_exists = True

        conn.commit()
        conn.close()

        return file_exists

    def select_students_by_criteria(
        self, record: AwardCriteriaRecord
    ) -> list[StudentRecord]:
        """Get student records by criteria.

        Returns students records matching criteria from the `students` table.
        Args:
            record (AwardCriteriaRecord): Scholarship criteria.
        Returns:
            A list of StudentRecord matching the criteria for the award.
        """
        # The starting base query, if criteria is empty, becomes select all
        query: Query = Query.from_(self.students_table_name).select("*")

        # If sort is specified, apply to select statement
        if record.sort:
            for field, order in record.sort:
                sort_order: Order = None

                # If order is -1, order by descending
                if order == -1:
                    sort_order = Order.desc
                # If order is 1 or any other value, order by ascending
                else:
                    sort_order = Order.asc

                # Add sort criteria to query
                query = query.orderby(field, order=sort_order)

        # Add where clauses if criteria is not empty
        if record.criteria:
            # Iterate over criterion in criteria dict
            for field, item in record.criteria.items():
                # If the value for field is a dict, the apply conditions to query
                if isinstance(item, dict):
                    for key, val in item.items():
                        # If criteria is $in, check if value of field is in val
                        if key == "$in":
                            query = query.where(Field(field).isin(val))
                        # If criteria is $nin, check if value of field is NOT in val
                        elif key == "$nin":
                            query = query.where(Field(field).notin(val))
                        # If criteria is $gte, check if field val >= val
                        elif key == "$gte":
                            query = query.where(Field(field) >= val)
                        # If criteria is $gt, check if field val > val
                        elif key == "$gt":
                            query = query.where(Field(field) > val)
                        # If criteria is $lte, check if field val <= val
                        elif key == "$lte":
                            query = query.where(Field(field) <= val)
                        # If criteria is $lt, check if field val < val
                        elif key == "$lt":
                            query = query.where(Field(field) < val)
                        # If criteria is $eq, check if field val == val
                        elif key == "$eq":
                            query = query.where(Field(field) == val)
                        # If criteria is $ne, check if field val != val
                        elif key == "$ne":
                            query = query.where(Field(field) != val)
                # If the value for field is not a dict, simply match for equality
                else:
                    query = query.where(Field(field) == item)
        # If limit is specified, and not 0, add limit
        if record.limit:
            query = query.limit(record.limit)

        conn: sqlite3.Connection = sqlite3.connect(self.database_path)
        cursor: sqlite3.Cursor = conn.cursor()
        cursor.execute(str(query))

        data = cursor.fetchall()
        conn.commit()
        conn.close()

        student_records: list[StudentRecord] = []
        for record in data:
            student_records.append(StudentRecord(*record))

        return student_records

    def select_all_students(self) -> list[StudentRecord]:
        """Gets all the student records.

        Returns all the student records from the `students` table.

        Returns:
            All of the student records as StudentRecords
        """
        query: Query = (
            Query.from_(self.students_table_name)
            .select("*")
            .orderby("cum_gpa", order=Order.desc)
        )

        conn: sqlite3.Connection = sqlite3.connect(self.database_path)
        cursor: sqlite3.Cursor = conn.cursor()
        cursor.execute(str(query))

        data = cursor.fetchall()
        conn.commit()
        conn.close()

        student_records: list[StudentRecord] = []
        for record in data:
            student_records.append(StudentRecord(*record))

        return student_records

    def student_csv_to_table(self, file_path: str):
        """Gets student records from CSV and stores in the table.

        Reads in student records from a CSV file and stores them in
        the `students` table.

        Args:
            file_path (str): File path for the CSV file.
        """
        if self.file_is_open(file_path):
            raise FileIsOpenError(f"File '{file_path}' is already open.")

        self.set_students_table_name(file_path)
        self.drop_table(self.students_table_name)
        self.create_table(self.students_table_name, self.__students_columns)

        data: list[StudentRecord] = read_student_data_from_csv(file_path)

        # Insert student records into database
        for record in data:
            self.insert_student(record)

    def award_criteria_json_to_table(self, file_path: str):
        """Convienience function for populating table.

        Function to assist with populating award criteria table.

        Args:
            file_path (str): File path to JSON file.
        """
        with open(file_path, "r") as file:
            data: list = json.load(file)

            for record in data:
                self.insert_award_criteria(AwardCriteriaRecord(**record))

    def select_all_award_criteria(self) -> list[AwardCriteriaRecord]:
        """Returns all award criteria.

        Returns all award criteria in the table.

        Returns:
            A list of AwardCriteriaRecord.
        """
        query: Query = (
            Query.from_(self.__award_criteria_table_name)
            .select("*")
            .orderby("name", order=Order.asc)
        )

        conn: sqlite3.Connection = sqlite3.connect(self.database_path)
        cursor: sqlite3.Cursor = conn.cursor()
        cursor.execute(str(query))

        data: list = cursor.fetchall()
        conn.commit()
        conn.close()

        award_records: list[AwardCriteriaRecord] = []

        for name, criteria, limit, sort in data:
            award_records.append(
                AwardCriteriaRecord(name, json.loads(criteria), limit, json.loads(sort))
            )
        return award_records


# Example sqlite3 operations
if __name__ == "__main__":
    from rich import print

    db = ScholarlyDatabase("database/scholarly.sqlite")

    db.drop_table(ScholarlyDatabase.get_award_criteria_table_name())
    db.set_students_table_name("example_data/student_data2.csv")
    db.drop_table(db.get_students_table_name())
    db.student_csv_to_table("example_data/student_data2.csv")
    db.create_table(
        ScholarlyDatabase.get_award_criteria_table_name(),
        ScholarlyDatabase.get_award_criteria_columns(),
    )

    db.award_criteria_json_to_table("scholarships.json")
    c = db.select_award_criteria("Colleen and Richard Simpson")
    print(c)
    stud = db.select_students_by_criteria(c)
    print(stud)

    db.drop_table(db.get_students_table_name())
