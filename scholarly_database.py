"""Provides a class for accessing and operating on a SQLite database.

Provides the class `ScholarlyDatabase` for accessing a SQLite database
and inserting records in the students table and award criteria table.

"""
import sqlite3
import json
from student_record import StudentRecord
from award_criteria_record import AwardCriteriaRecord
from student_data_reader import StudentDataReader
from pypika import Query, Table, Field, Schema, Column, Columns, Order


class ScholarlyDatabase:
    """Class to operate SQLite3 database.

    Class to allow easy manipulation and operation of a SQLite database with
    the tables `students` and `award_criteria`.
    """

    __students_table_name: str = "students"
    __award_criteria_table_name: str = "award_criteria"
    __students_columns: list[Column] = Columns(
        ("name", "TEXT"),
        ("student_ID", "TEXT PRIMARY KEY"),
        ("cum_gpa", "REAL"),
        ("major", "TEXT"),
        ("classification", "TEXT"),
        ("earned_credits", "INTEGER"),
        ("enrolled", "TEXT"),
        ("email", "TEXT"),
        ("gender", "TEXT"),
        ("in_state", "TEXT"),
    )
    __award_criteria_columns: list[Column] = Columns(
        ("name", "TEXT PRIMARY KEY"), ("criteria", "JSON")
    )

    def __init__(self, file_path: str) -> None:
        """Creates an instance of ScholarlyDatabase.

        Creates an instance of ScholarlyDatabase for accessing and
        performing queries on the SQLite3 database.

        Args:
            file_path (str): File path for the SQLite3 database.
        """
        self.file_path: str = file_path

    @classmethod
    def students_table_name(cls) -> str:
        """Returns the name of the `students` table.

        Returns the name of the `students` table.

        Returns:
            Name of the `students` table as a `str`.
        """
        return cls.__students_table_name

    @classmethod
    def award_criteria_table_name(cls) -> str:
        """Returns the name of the `award_criteria` table.

        Returns the name of the `award_criteria` table.

        Returns:
            Name of the `award_criteria` table as a `str`.
        """
        return cls.__award_criteria_table_name

    @classmethod
    def students_table_columns(cls) -> list[Column]:
        """Returns the columns for the `students` table.

        Returns the columns for the `students` table.

        Returns:
            Columns for the `students` table as `list[Column]`.

        """
        return cls.__students_columns

    @classmethod
    def award_criteria_columns(cls) -> list[Column]:
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
        query: Query = Query.into(self.__students_table_name).insert(*record.to_tuple())
        conn: sqlite3.Connection = sqlite3.connect(self.file_path)
        cursor: sqlite3.Cursor = conn.cursor()

        cursor.execute(str(query))
        conn.commit()
        conn.close()

    def insert_award_criteria(self, record: AwardCriteriaRecord) -> None:
        """Inserts award critiera into the `award_criteria` table.

        Inserts award criteria into the `award_criteria` table.

        Args:
            record (AwardRecord): An award record.
        """
        query: Query = Query.into(self.__award_criteria_table_name).insert(
            record.name, json.dumps(record.criteria)
        )
        conn: sqlite3.Connection = sqlite3.connect(self.file_path)
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

        conn: sqlite3.Connection = sqlite3.connect(self.file_path)
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
        conn: sqlite3.Connection = sqlite3.connect(self.file_path)
        cursor: sqlite3.Cursor = conn.cursor()

        cursor.execute(str(query))
        conn.commit()
        conn.close()

    def select_award_criteria(self, award_name: str) -> dict[str]:
        """Gets all the student records.

        Returns all the student records from the `students` table.

        Returns:
            All of the student records as

        """
        query: Query = Query.from_(self.__award_criteria_table_name).select("*")

        conn: sqlite3.Connection = sqlite3.connect(self.file_path)
        cursor: sqlite3.Cursor = conn.cursor()
        cursor.execute(str(query))

        data = cursor.fetchone()
        result: dict = {"name": None, "criteria": None}

        # If item exists, convert into dict
        if data:
            result["name"] = data[0]
            result["criteria"] = json.loads(data[1])

        conn.commit()
        conn.close()

        return result

    def select(self, query: Query, key=None) -> list[StudentRecord]:
        # TODO: Implement this better
        conn: sqlite3.Connection = sqlite3.connect(self.file_path)
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
            All of the student records as

        """
        query: Query = (
            Query.from_(self.__students_table_name)
            .select("*")
            .orderby("cum_gpa", order=Order.desc)
        )

        conn: sqlite3.Connection = sqlite3.connect(self.file_path)
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
        self.drop_table(self.__students_table_name)
        self.create_table(self.__students_table_name, self.__students_columns)

        reader: StudentDataReader = StudentDataReader(file_path)
        data: list[StudentRecord] = reader.read_values()

        # Insert student records into database
        for record in data:
            self.insert_student(record)

    def award_critiera_json_to_table(self, file_path: str):
        pass


# Example sqlite3 operations
if __name__ == "__main__":
    from rich import print

    db = ScholarlyDatabase("temp.sqlite")

    db.create_table(
        ScholarlyDatabase.award_criteria_table_name(),
        ScholarlyDatabase.award_criteria_columns(),
    )

    # criteria = {"cum_gpa": {"$gte": 4.0, "$lte": 0.0}}
    # db.insert_award_criteria("Scholarship", criteria)
    db.select_award_criteria("Scholarship")