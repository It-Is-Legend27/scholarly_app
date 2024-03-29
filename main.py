"""Main Program for creating the Scholarly App GUI

This file contains the `ScholarlyMainWindow` class, which is the
contains methods for creating the application's GUI.

"""
import sys
import webbrowser
import os
from datetime import datetime
from PyQt6.QtWidgets import *
from PyQt6.QtGui import (
    QAction,
    QCloseEvent,
    QIcon,
    QPalette,
    QColor,
    QIntValidator,
    QDoubleValidator,
    QFont,
    QPixmap,
)
from PyQt6.QtCore import QEvent, Qt, QSize, QModelIndex, pyqtSlot
from student_table_model import StudentTableModel
from student_record import StudentRecord, read, write
from award_criteria_record import AwardCriteriaRecord
from scholarly_database import ScholarlyDatabase
from letter_writer import LetterVariables, LetterWriter
from scholarly_menu_bar import ScholarlyMenuBar
# Absolute address for file to prevent issues with
# relative addresses when building app with PyInstaller
BASE_DIR:str = os.path.dirname(__file__)

class ScholarlyMainWindow(QMainWindow):
    """Class for implementing the GUI for the Scholarly app.

    Class for implementing the GUI for the Scholarly application.
    """

    def __init__(self):
        """Creates an instance of ScholarlyMainWindow.

        Creates an instance of ScholarlyMainWindow, the GUI for the application.
        """
        super().__init__()
        self.menu_bar:ScholarlyMainWindow = None
        self.student_table: StudentTableModel = None
        self.student_table_view: QTableView = None
        self.database: ScholarlyDatabase = ScholarlyDatabase(os.path.join(BASE_DIR, "database/scholarly.sqlite"))

        self.initialize_ui()

    def initialize_ui(self):
        """Initializes GUI components on the GUI.

        Initializes the GUI components of the GUI for the application.
        """
        # Set window properties
        self.setWindowTitle("Scholarly")
        self.setWindowIcon(QIcon(os.path.join(BASE_DIR, "assets/icons/scholarly.ico")))
        self.setGeometry(200, 200, 500, 500)

        # Initalize menu bar
        self.initialize_menubar()

        # Initilize table
        self.initialize_central_widget()

    def initialize_central_widget(self):
        """Initializes the central widget for the main window.

        Initializes the central widget for the main window of
        the application.
        """
        central_widget: QWidget = QWidget()
        horizontal_layout: QHBoxLayout = QHBoxLayout()

        # Set central widget background color to maroon
        # central_widget.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        # central_widget.setStyleSheet("background-color: maroon;")

        # Create model and table view widget
        self.student_table = StudentTableModel()
        self.student_table_view: QTableView = QTableView()

        # Set table view background color to white
        # self.student_table_view.setAttribute(
        #     Qt.WidgetAttribute.WA_StyledBackground, True
        # )
        # self.student_table_view.setStyleSheet("background-color: white;")

        # Enable selecting multiple rows
        self.student_table_view.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.student_table_view.setSelectionMode(
            QAbstractItemView.SelectionMode.MultiSelection
        )

        # Add table view to central widget
        self.student_table_view.setModel(self.student_table)
        horizontal_layout.addWidget(self.student_table_view)

        # Select Scholarship Groupbox
        scholarship_groupbox: QGroupBox = QGroupBox("Select Scholarship")
        scholarship_layout: QVBoxLayout = QVBoxLayout()
        scholarship_groupbox.setLayout(scholarship_layout)

        # Load items in comboxbox
        self.scholarship_combobox: QComboBox = QComboBox()
        self.load_scholarship_combobox()

        self.scholarship_combobox.currentTextChanged.connect(self.scholarship_changed)
        # Keep disabled until file is opened
        self.scholarship_combobox.setDisabled(True)
        scholarship_layout.addWidget(self.scholarship_combobox)

        # Fields and text boxes for generating letters
        letter_info_widget: QWidget = QWidget()
        letter_info_layout: QFormLayout = QFormLayout()
        letter_info_widget.setLayout(letter_info_layout)

        # Text boxes
        self.sender_name_textbox: QLineEdit = QLineEdit()
        self.sender_title_textbox: QLineEdit = QLineEdit()
        self.sender_email_textbox: QLineEdit = QLineEdit()
        self.award_amount_textbox: QLineEdit = QLineEdit()
        self.award_amount_textbox.setValidator(QDoubleValidator())
        self.template_path_textbox:QLineEdit = QLineEdit()
        self.dest_dir_path_textbox: QLineEdit = QLineEdit()
        self.academic_year_textbox: QLineEdit = QLineEdit()

        # Select template letter button
        self.select_template_button: QToolButton = QToolButton()
        self.select_template_button.setText("Browse")
        self.select_template_button.setToolTip("Select template letter file.")
        self.select_template_button.clicked.connect(self.select_template)

        # Layout for selecting template letter button
        select_template_layout: QHBoxLayout = QHBoxLayout()
        select_template_layout.addWidget(self.select_template_button)
        select_template_layout.addWidget(self.template_path_textbox)

        # Select directory button
        self.select_directory_button: QToolButton = QToolButton()
        self.select_directory_button.setText("Browse")
        self.select_directory_button.setToolTip("Select the destination directory.")
        self.select_directory_button.clicked.connect(self.select_directory)

        # Add textboxes to form layout
        letter_info_layout.addRow("Sender Name", self.sender_name_textbox)
        letter_info_layout.addRow("Sender Title", self.sender_title_textbox)
        letter_info_layout.addRow("Sender Email", self.sender_email_textbox)
        letter_info_layout.addRow("Amount", self.award_amount_textbox)
        letter_info_layout.addRow("Academic Year", self.academic_year_textbox)

        # Layout for selecting destination directory
        select_dir_layout: QHBoxLayout = QHBoxLayout()
        select_dir_layout.addWidget(self.select_directory_button)
        select_dir_layout.addWidget(self.dest_dir_path_textbox)

        # Add template letter layout to letter info layout
        letter_info_layout.addRow("Template Letter", select_template_layout)

        # Add layout to letter info layout
        letter_info_layout.addRow("Destination Directory", select_dir_layout)
        scholarship_layout.addWidget(letter_info_widget)

        # Generate Letters button
        generate_letters: QToolButton = QToolButton()
        generate_letters.setText("Generate Letters")
        generate_letters.setToolTip(
            "Generates Scholarship Letter for selected students."
        )
        generate_letters.clicked.connect(self.generate_letters)

        # Add widget to scholarship components layout
        scholarship_layout.addWidget(generate_letters)

        # Add scholarship groupbox to horizontal layout
        horizontal_layout.addWidget(scholarship_groupbox)

        # Add layout to central widget, and add central widget to main window
        central_widget.setLayout(horizontal_layout)
        self.setCentralWidget(central_widget)

    def initialize_menubar(self):
        """Initializes the menu bar for the main window.

        Initializes the menu bar for the main window of the appllication.
        """
        self.menu_bar: ScholarlyMenuBar = ScholarlyMenuBar(self.open_file, self.save_file, self.close_file, self.about, self.help, self.close)
        self.setMenuBar(self.menu_bar)

    @pyqtSlot()
    def open_file(self) -> None:
        """Slot (event handler) for "Open" action.

        Function called when "Open" action is activated. Shows
        a file dialog for opening a file, then reads the data
        from the file into the database and the table.
        """
        # [1] ChatGPT, response to "Write me python code for a PyQT6 menu bar with a File tab and Open button.". OpenAI [Online]. https://chat.openai.com/ (accessed February 29, 2024).
        # Current user's Documents Directory
        user_documents_path: str = os.path.join(os.path.expanduser("~"), "Documents")

        # Open file dialog, and gets the selected file path
        file_path, _ = QFileDialog.getOpenFileName(
            parent=self,
            caption="Open File",
            directory=user_documents_path,
            filter="CSV (*.csv)",
        )

        # If no file is specified, do nothing
        if not file_path:
            return

        try:
            # Insert data from file to database
            self.database.student_csv_to_table(file_path)
        # If invalid data file, show error message
        except Exception as e:
            QMessageBox.critical(
                self,
                "Invalid File",
                f"The file is not a CSV file, or is malformed.\n{type(e).__name__}: {e}",
            )

        # Retrieve data from the database
        student_data = self.database.select_all_students()

        # Store data into table
        self.student_table = StudentTableModel(student_data)
        self.student_table_view.setModel(self.student_table)

        # Enable scholarship combobox
        self.scholarship_combobox.setEnabled(True)
        self.scholarship_combobox.setCurrentIndex(0)

    @pyqtSlot()
    def save_file(self) -> None:
        """Slot (event handler) for "Save" action.

        Function called when "Save" action is activated. Shows
        a file dialog for saving a file, then stores the data from the table
        into the selected CSV file.
        """
        # [1] ChatGPT, response to "Write me python code for a PyQT6 menu bar with a File tab and Open button.". OpenAI [Online]. https://chat.openai.com/ (accessed February 29, 2024).
        # Current user's Documents Directory
        user_documents_path: str = os.path.join(os.path.expanduser("~"), "Documents")

        # Open file dialog, and gets the selected file path
        file_path, _ = QFileDialog.getSaveFileName(
            parent=self,
            caption="Open File",
            directory=user_documents_path,
            filter="CSV (*.csv)",
        )

        # If no file is specified, do nothing
        if not file_path:
            return

        # Retrieve data from table
        student_data: list[StudentRecord] = self.student_table.get_all_data()

        # Write to CSV file
        write(file_path, student_data)

    @pyqtSlot()
    def close_file(self) -> None:
        """Slot (event handler) for close action.

        Function that is called when "Close" action is activated. Clears the database
        and clears the table.
        """
        self.scholarship_combobox.setDisabled(True)
        self.scholarship_combobox.setCurrentIndex(0)
        self.database.drop_table(ScholarlyDatabase.students_table_name())
        self.student_table = StudentTableModel()
        self.student_table_view.setModel(self.student_table)
        
    def closeEvent(self, event: QCloseEvent) -> None:
        """Event handler for closing the application.

        Event handler triggered when the application is closed.
        Shows a message box asking the user if they are sure they want to close
        the application.
        """
        reponse: QMessageBox.StandardButton = QMessageBox.question(
            self,
            "Exit",
            "Are you sure you want to close the program? Any unsaved data will be lost.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reponse == QMessageBox.StandardButton.Yes:
            self.close_file()
            event.accept()
        else:
            event.ignore()

    @pyqtSlot()
    def about(self) -> None:
        """Slot (event handler) for "About" action.

        Function called when "About" action is activated.
        Opens the default web browser on the device and opens
        a tab to the link for the about information.
        """
        # TODO: Add functionality for About menu
        webbrowser.open(
            "https://github.com/It-Is-Legend27/scholarly_app/blob/main/README.md"
        )

    @pyqtSlot()
    def help(self) -> None:
        """Slot (event handler) for "Help" action.

        Function called when "Help" action is activated.
        Opens the default web browser on the device and opens
        a tab to the link for the manual for the application.
        """
        # TODO: Add functionality for Help menu
        webbrowser.open(
            "https://github.com/It-Is-Legend27/scholarly_app/blob/main/README.md"
        )

    @pyqtSlot()
    def generate_letters(self):
        """Slot (event handler) for "generate letters" button.

        Function that is called when "generate letters" button is pressed. Generates
        the letters based on the selections in the table.
        """
        student_data: list[StudentRecord] = self.get_selected_rows()
        
        # If no selection has been made, show warning message
        if not student_data:
            QMessageBox.warning(self, "No Selection", "No selection has been made. Make a selection on the table.")
            return

        curr_time:datetime = datetime.now()
        date:str = f"{curr_time.strftime("%B")} {curr_time.day}, {curr_time.year}"

        scholarship_name:str = self.scholarship_combobox.currentText()
        sender_name:str = self.sender_name_textbox.text()
        sender_title:str = self.sender_title_textbox.text()
        sender_email:str = self.sender_email_textbox.text()
        amount:str = self.award_amount_textbox.text()
        academic_year:str = self.academic_year_textbox.text()
        dir_path:str = self.dest_dir_path_textbox.text()

        # Ensure text boxes are not empty, if so, show warning
        if not sender_name:
            QMessageBox.warning(self, "Enter Sender Name", "Sender name is empty. Please enter the sender name.")
            return
        elif not sender_title:
            QMessageBox.warning(self, "Enter Sender Title", "Sender name is empty. Please enter the sender title.")
            return
        elif not sender_email:
            QMessageBox.warning(self, "Enter Sender Email", "Sender email is empty. Please enter the sender email.")
            return
        elif not amount:
            QMessageBox.warning(self, "Enter Amount", "The amount is empty. Please enter the amount.")
            return
        elif not academic_year:
            QMessageBox.warning(self, "Enter Academic Year", "The academic year is empty. Please enter the academic year.")
            return
        elif not dir_path:
            QMessageBox.warning(self, "Enter Destination Directory", "Destination directory is empty. Please enter the destination directory.")
            return

        for student in student_data:

            student_last_name, student_first_name = student.name.replace(" ", "").split(",")

            student_name:str = f"{student_first_name} {student_last_name}"
            
            letter_vars:LetterVariables = None

            try:
                letter_vars:LetterVariables = LetterVariables(student_name, date, amount, scholarship_name, academic_year, sender_name, sender_email, sender_title)
            except ValueError as e:
                QMessageBox.critical(self, "Invalid Arguments", f"Invalid arguments in the textboxes.\n{type(e).__name__}: {e}")
                raise e
                return
            
            letter_writer:LetterWriter = LetterWriter("assets/templates/template_letter.docx", f"{dir_path}/{student_name}.docx", letter_vars.to_dict())
            letter_writer.writer_letter()
        
        # Open File Explorer to show letters
        os.startfile(dir_path)
            
    def get_selected_rows(self)-> list[StudentRecord]:
        """Returns the student data from the selection.

        Returns the student data from the selected rows.

        Returns:
            A list of StudentRecord.
        """
        indices: list[QModelIndex] = (
            self.student_table_view.selectionModel().selectedRows()
        )

        data: list[StudentRecord] = []

        for index in indices:
            data.append(self.student_table.get_row(index.row()))

        return data

    @pyqtSlot()
    def select_directory(self):
        """Slot (event handler) for choosing destination directory.

        Function called when "Browse" button on the "Destination Directory" field
        section is pressed. Opens file dialog for selecting a directory.
        """
        user_documents_path: str = os.path.join(os.path.expanduser("~"), "Documents")

        # Open file dialog, and gets the selected file path
        dir_path: str = QFileDialog.getExistingDirectory(
            parent=self,
            caption="Select directory",
            directory=user_documents_path,
            options=QFileDialog.Option.ShowDirsOnly,
        )
        # If no file is specified, do nothing
        if not dir_path:
            return

        # Change textbox text to directory path
        self.dest_dir_path_textbox.setText(dir_path)

    @pyqtSlot()
    def select_template(self):
        """Slot (event handler) for choosing template letter file.

        Function called when "Browse" button on the "Template Letter" field
        section is pressed. Opens file dialog for selecting a docx file.
        """
        templates_path: str = os.path.join(BASE_DIR, "assets/templates")

        # Open file dialog, and get the selected file path
        file_path, _ = QFileDialog.getOpenFileName(
            parent=self,
            caption="Select Template Letter",
            directory=templates_path,
            filter="Word Documents (*.docx)",
        )

        # If no file is specified, do nothing
        if not file_path:
            return

        # Change textbox text to directory path
        self.template_path_textbox.setText(file_path)

    @pyqtSlot()
    def scholarship_changed(self):
        """Called when selection is changed in scholarship_combobox

        Called when selection is changed in scholarship_combobox
        """
        scholarship_name:str = self.scholarship_combobox.currentText()

        if scholarship_name == "":
            # Clear selection
            self.student_table_view.clearSelection()
            
            # Reset table to have entire contents of database
            student_data:list[StudentRecord] = self.database.select_all_students()
            self.student_table = StudentTableModel(student_data)
            self.student_table_view.setModel(self.student_table)
        else:
            self.student_table_view.clearSelection()
            award_criteria_record:AwardCriteriaRecord = self.database.select_award_criteria(scholarship_name)
            student_data:list[StudentRecord] = self.database.select_students_by_criteria(award_criteria_record)
            self.student_table = StudentTableModel(student_data)
            self.student_table_view.setModel(self.student_table)

    def load_scholarship_combobox(self):
        """Populates scholarship combobox with scholarship names.

        Populates scholarship combobox with scholarship names from the
        award criteria table in the database.
        """
        self.scholarship_combobox.clear()

        # Add empty item for representing no filter / no selection
        self.scholarship_combobox.addItem("")
        
        # Retrieve all award criteria
        records:list[AwardCriteriaRecord] = self.database.select_all_award_criteria()

        # Add award names to combobox
        for record in records:
            self.scholarship_combobox.addItem(record.name)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window: ScholarlyMainWindow = ScholarlyMainWindow()
  
    # Displays the main window for the application
    window.show()
    
    # Run application
    sys.exit(app.exec())
