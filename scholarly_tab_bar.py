from PyQt6.QtWidgets import (
    QWidget,
    QTabWidget,
    QFormLayout,
    QLayout,
    QBoxLayout,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QToolButton,
    QToolTip,
    QGroupBox,
    QComboBox,
)
from PyQt6.QtGui import QAction, QDoubleValidator, QValidator, QIntValidator, QIcon
from typing import Callable
from scholarly_scholarship_tab import ScholarlyScholarshipTab
from scholarly_manage_scholarships_tab import ScholarlyManageScholarshipsTab
from scholarly_outstanding_student_awards_tab import (
    ScholarlyOutstandingStudentAwardsTab,
)
import os

BASE_DIR: str = os.path.dirname(__file__)

# Function that takes no parameters, and returns nothing
voidCallBack: Callable[[], None] = lambda: None


class ScholarlyTabBar(QTabWidget):
    """Tab bar for Scholarly app."""

    def __init__(
        self,
        scholarship_tab: ScholarlyScholarshipTab = None,
        manage_scholarships_tab: ScholarlyManageScholarshipsTab = None,
        outstanding_student_awards_tab: ScholarlyOutstandingStudentAwardsTab = None,
    ) -> None:
        """Creates a new instance of ScholarlyTabBar

        Args:
            scholarship_tab (ScholarlyScholarshipTab, optional): Scholarship tab. Defaults to None.
            manage_scholarships_tab (ScholarlyManageScholarshipsTab, optional): Manage Scholarships tab. Defaults to None.
            outstanding_student_awards_tab (ScholarlyOutstandingStudentAwardsTab, optional): Outstanding Student Awards tab. Defaults to None.
        """
        super().__init__()

        # Add scholarship tab
        self.scholarship_tab: ScholarlyScholarshipTab = scholarship_tab
        self.scholarship_tab_name: str = "Select Scholarship Recipients"
        self.setScholarshipTab(self.scholarship_tab)

        # Add manage scholarships tab
        self.manage_scholarships_tab = manage_scholarships_tab
        self.manage_scholarships_tab_name: str = "Manage Scholarships"
        self.setManageScholarShipsTab(manage_scholarships_tab)

        # Add outstanding student awards tab
        self.outstanding_student_awards_tab = outstanding_student_awards_tab
        self.outstanding_student_awards_tab_name: str = "Outstanding Student Awards"
        self.setOutstandingStudentAwardTab(self.outstanding_student_awards_tab)

    def setScholarshipTab(self, tab: ScholarlyScholarshipTab) -> None:
        """Sets the Scholarship tab

        Args:
            tab (ScholarlyScholarshipTab): Scholarship tab.
        """ 
        self.removeTab(0)
        self.insertTab(0, tab, self.scholarship_tab_name)
        self.setTabIcon(0, QIcon(os.path.join(BASE_DIR, "assets/icons/education.svg")))

    def setManageScholarShipsTab(self, tab: ScholarlyManageScholarshipsTab) -> None:
        """Sets the Manage Scholarships tab

        Args:
            tab (ScholarlyManageScholarshipsTab): Manage Scholarships tab.
        """
        self.removeTab(1)
        self.insertTab(1, tab, self.manage_scholarships_tab_name)
        self.setTabIcon(
            1, QIcon(os.path.join(BASE_DIR, "assets/icons/filter_settings.svg"))
        )

    def setOutstandingStudentAwardTab(
        self, tab: ScholarlyOutstandingStudentAwardsTab
    ) -> None:
        """Sets the Oustandsting Student Awards tab

        Args:
            tab (ScholarlyOutstandingStudentAwardsTab): Outstanding Student Awards tab.
        """
        self.removeTab(2)
        self.insertTab(2, tab, self.outstanding_student_awards_tab_name)
        self.setTabIcon(2, QIcon(os.path.join(BASE_DIR, "assets/icons/medal.svg")))


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication

    a = QApplication([])
    s = ScholarlyTabBar(
        ScholarlyScholarshipTab(),
        ScholarlyManageScholarshipsTab(),
        ScholarlyOutstandingStudentAwardsTab(),
    )
    s.show()
    a.exec()
