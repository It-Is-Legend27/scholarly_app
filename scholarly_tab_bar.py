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
from PyQt6.QtGui import (
    QAction,
    QDoubleValidator,
    QValidator,
    QIntValidator,
    QIcon,
    QColor,
)
from PyQt6.QtCore import QSize
from typing import Callable
from scholarly_icons import ScholarlyIcon, Icons, IconSizes
from scholarly_generate_letters_tab import ScholarlyGenerateLettersTab
from scholarly_send_emails_tab import ScholarlySendEmailsTab
from scholarly_manage_scholarships_tab import ScholarlyManageScholarshipsTab
from scholarly_outstanding_student_awards_tab import (
    ScholarlyOutstandingStudentAwardsTab,
)
import os

# Function that takes no parameters, and returns nothing
voidCallBack: Callable[[], None] = lambda: None


class ScholarlyTabBar(QTabWidget):
    """Tab bar for Scholarly app."""

    def __init__(
        self,
        generate_letters_tab: ScholarlyGenerateLettersTab = None,
        send_emails_tab: ScholarlySendEmailsTab = None,
        manage_scholarships_tab: ScholarlyManageScholarshipsTab = None,
        outstanding_student_awards_tab: ScholarlyOutstandingStudentAwardsTab = None,
    ) -> None:
        """Creates a new instance of ScholarlyTabBar

        Args:
            generate_letters_tab (ScholarlyGenerateLettersTab, optional): Generate Letters Tab. Defaults to None.
            manage_scholarships_tab (ScholarlyManageScholarshipsTab, optional): Manage Scholarships tab. Defaults to None.
            outstanding_student_awards_tab (ScholarlyOutstandingStudentAwardsTab, optional): Outstanding Student Awards tab. Defaults to None.
        """
        super().__init__()

        # Add generate letters tab
        self.generate_letters_tab: ScholarlyGenerateLettersTab = generate_letters_tab
        self.generate_letters_tab_name: str = "Generate Acceptance Letters"
        self.setGenerateLettersTab(self.generate_letters_tab)

        # Add send emails tab
        self.send_emails_tab: ScholarlySendEmailsTab = send_emails_tab
        self.generate_letters_tab_name: str = "Send Emails"
        self.setSendEmailsTab(self.send_emails_tab)

        # Add manage scholarships tab
        self.manage_scholarships_tab = manage_scholarships_tab
        self.manage_scholarships_tab_name: str = "Manage Scholarships"
        self.setManageScholarShipsTab(manage_scholarships_tab)

        # Add outstanding student awards tab
        self.outstanding_student_awards_tab = outstanding_student_awards_tab
        self.outstanding_student_awards_tab_name: str = "Outstanding Student Awards"
        self.setOutstandingStudentAwardTab(self.outstanding_student_awards_tab)

        self.setIconSize(IconSizes.Medium.value)

    def setGenerateLettersTab(self, tab: ScholarlyGenerateLettersTab) -> None:
        """Sets the Generate Letters tab.

        Args:
            tab (ScholarlyGenerateLettersTab): Tab to be set.
        """
        self.removeTab(0)
        self.insertTab(0, tab, self.generate_letters_tab_name)
        self.setTabIcon(
            0, ScholarlyIcon(Icons.School, QColor("maroon"), IconSizes.Medium)
        )

    def setSendEmailsTab(self, tab: ScholarlySendEmailsTab) -> None:
        """Sets the Send Emails tab.

        Args:
            tab (ScholarlySendEmailsTab): Tab to be set.
        """
        self.removeTab(1)
        self.insertTab(1, tab, self.generate_letters_tab_name)
        self.setTabIcon(
            1, ScholarlyIcon(Icons.StackedEmail, QColor("red"), IconSizes.Medium)
        )

    def setManageScholarShipsTab(self, tab: ScholarlyManageScholarshipsTab) -> None:
        """Sets the Manage Scholarships tab

        Args:
            tab (ScholarlyManageScholarshipsTab): Manage Scholarships tab.
        """
        self.removeTab(2)
        self.insertTab(2, tab, self.manage_scholarships_tab_name)
        self.setTabIcon(
            2, ScholarlyIcon(Icons.Filter, QColor("black"), IconSizes.Medium)
        )

    def setOutstandingStudentAwardTab(
        self, tab: ScholarlyOutstandingStudentAwardsTab
    ) -> None:
        """Sets the Oustandsting Student Awards tab

        Args:
            tab (ScholarlyOutstandingStudentAwardsTab): Outstanding Student Awards tab.
        """
        self.removeTab(3)
        self.insertTab(3, tab, self.outstanding_student_awards_tab_name)
        self.setTabIcon(
            3, ScholarlyIcon(Icons.Trophy, QColor(204, 172, 0), IconSizes.Medium)
        )


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication

    a = QApplication([])
    s = ScholarlyTabBar(
        ScholarlyGenerateLettersTab(),
        ScholarlySendEmailsTab(),
        ScholarlyManageScholarshipsTab(),
        ScholarlyOutstandingStudentAwardsTab(),
    )
    s.show()
    a.exec()
