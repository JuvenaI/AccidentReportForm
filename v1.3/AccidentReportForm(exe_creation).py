from PyQt5.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout, QWidget, QCheckBox, QLineEdit, QFrame, QCalendarWidget, QDialog, QTimeEdit, QDateEdit, QAbstractSpinBox, QTextEdit, QScrollArea, QGraphicsView, QGraphicsScene, QGraphicsProxyWidget, QFileDialog
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QCursor
from PyQt5 import QtCore
import sys
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Spacer, Table, TableStyle, Image, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from PIL import Image as img
from pathlib import Path
import os


# https://stackoverflow.com/questions/31836104/pyinstaller-and-onefile-how-to-include-an-image-in-the-exe-file
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS2
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class IconButton(QPushButton):
    def __init__(self, blank, cross, parent=None):
        super().__init__(parent)
        self.blank = blank
        self.cross = cross
        self.setCursor(QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.setFixedSize(25, 25)
        self.setIcon(self.cross)
        self.none_size = QtCore.QSize(0, 0)
        self.full_size = QtCore.QSize(20, 20)

        self.setIconSize(self.none_size)
        self.setStyleSheet("""
            border: none;
            background-color: transparent;
            padding: 100px;
            
        """)
        self.activated = False

    def enterEvent(self, event):
        self.setIconSize(self.full_size)

    def leaveEvent(self, event):
        self.setIconSize(self.none_size)

        
class ReportFormApp:
    def __init__(self):
        with open(resource_path('data\\texts\\lg.txt'), 'r') as f:
            self.language = f.read()
        self.display_body = False
        self.translatable = {}
        self.accent_color = 'teal'
        self.background_color = "#e4fffd"

        self.texts = {}

        for lg in ("fr", "en", "de"):
            with open(resource_path(f"data\\texts\\{lg}.txt"), 'r', encoding='utf8') as fichier:
                tab = [line[:-1].split(" = ") for line in fichier.readlines()]
                self.texts[lg] = {line[0] : line[1] for line in tab}

        self.answer = {
            "category": "",
            "report type": "",
            "date": "",
            "hour": "",
            "place": "",
            "equipment": "",
            "people": "",
            "situation": [],
            "description": "",
            "injury": "",
            "organs": [],
            "comments" : "",
            "logo" : "",
            "attachment" : [],
            "save" : "",
            "name" : ""
        }

        self.app = QApplication([])
        self.window = QWidget()
        self.window.setWindowTitle("Fiche de compte-rendu accident / presque accident / danger")

        self.create_widgets()
        self.center_window()
        self.apply_style()
        self.setup_layout()

        self.window.show()
        sys.exit(self.app.exec())

    def create_widgets(self):
        self.header_layout = self.create_header_layout()
        self.question_1_layout, self.category_checkboxes, self.report_checkboxes = self.create_question_1_layout()
        self.people_layout, self.people_box = self.create_people_layout()
        self.info_layout, self.info_boxes = self.create_info_layout()
        self.situation_layout = self.create_situation_layout()
        self.description_layout, self.description_box = self.create_description_layout()
        self.injury_layout, self.comment_box = self.create_injury_layout()
        self.attachment_layout = self.create_attachment_layout()


        self.export_button = self.create_button(self.texts[self.language]["export"])
        self.export_button.clicked.connect(self.export)
        self.translatable["export"] = self.export_button

    def center_window(self):
        screen_geometry = self.app.desktop().screenGeometry()
        window_width = 1_000
        window_height = 800
        x = (screen_geometry.width() - window_width) // 2
        y = (screen_geometry.height() - window_height) // 2
        self.window.setGeometry(x, y, window_width, window_height)

    def apply_style(self):
        self.window.setWindowIcon(QIcon(resource_path("icon.ico")))
        self.window.setStyleSheet(f"background: {self.background_color}")

    def setup_layout(self):
        self.main_layout = QVBoxLayout()
        self.main_layout.addLayout(self.header_layout)

        # Create a scrollable widget to hold all the content
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setContentsMargins(30, 10, 30, 10)
        scroll_widget.setLayout(scroll_layout)

        # Add all the elements to the scroll layout

        scroll_layout.addWidget(self.create_h_separator())
        row_1_layout = QGridLayout()
        cat_people_layout = QVBoxLayout()
        cat_people_layout.addLayout(self.question_1_layout)
        cat_people_layout.addWidget(self.create_h_separator())
        cat_people_layout.addLayout(self.people_layout)
        row_1_layout.addLayout(cat_people_layout, 0, 0)
        row_1_layout.addWidget(self.create_v_separator(), 0, 1)
        row_1_layout.addLayout(self.info_layout, 0, 2)
        row_1_layout.setColumnStretch(0, 1)
        row_1_layout.setColumnStretch(2, 1)
        scroll_layout.addLayout(row_1_layout)

        scroll_layout.addWidget(self.create_h_separator())
        scroll_layout.addLayout(self.situation_layout)
        scroll_layout.addWidget(self.create_h_separator())
        scroll_layout.addLayout(self.description_layout)
        scroll_layout.addWidget(self.create_h_separator())

        self.harm_layout = QHBoxLayout()
        self.harm_layout.addLayout(self.injury_layout, stretch=1)


        scroll_layout.addLayout(self.harm_layout)
        scroll_layout.addWidget(self.create_h_separator())
        scroll_layout.addLayout(self.attachment_layout)
        scroll_layout.addWidget(self.create_h_separator())


        # Create the scroll area and set its widget to the scrollable widget
        scroll_area = QScrollArea()
        scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                margin-top: 10px;
                margin-bottom: 10px;
            }
            QScrollBar:vertical {
                border: none;
                background-color: transparent;  
                width: 19px;
                margin: 0px 10px 0px 0px;
            }
            QScrollBar:vertical:hover {
                border-radius: 7px;
                background-color: #dadada;
                margin: 0px 5px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background-color: teal;  
                min-height: 20px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                border-radius: 7px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background-color: transparent;
                height: 12px;
                subcontrol-position: top;
                subcontrol-origin: margin;
            }
                                  """)
        
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)

        # Add the scroll area to the main layout
        self.main_layout.addWidget(scroll_area)

        self.main_layout.addWidget(self.export_button, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        self.main_layout.setContentsMargins(0, 20, 0, 20)

        self.window.setLayout(self.main_layout)



    def create_header_layout(self):
        header_layout = QHBoxLayout()

        flag_layout = QHBoxLayout()
        flag_layout.setContentsMargins(20, 0, 0, 0)
        languages = ('fr', 'de', 'en')
        for lg in languages:
            button = QPushButton()
            button.setCursor(QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
            #button.setCursor(QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
            icon = QIcon(resource_path(f"data\\images\\flag_{lg}.png"))
            button.setIcon(icon)
            button.setFixedSize(QtCore.QSize(64, 64))
            button.setIconSize(QtCore.QSize(48, 48))
            button.setStyleSheet("border-style: 15px 'white' solid;" + "padding-left: 10px;")
            button.clicked.connect(lambda _, lg=lg: self.switch_language(lg))
            flag_layout.addWidget(button)

        header_layout.addLayout(flag_layout)

        self.title = QLabel(self.texts[self.language]["title"])
        self.title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        #self.title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.title.setMinimumWidth(900)
        self.title.setMaximumWidth(1100)
        self.title.setFixedHeight(80)
        self.title.setStyleSheet(
            f"background: {self.accent_color};"
            "font-size: 36px;"
            "font-family: Ubuntu;"
            "border-radius: 20px;"
            "padding: 15%;"
            "color: 'white';"
            "margin-left: 80px;"
            "margin-right: 80px;"
        )
        self.translatable["title"] = (self.title)
        header_layout.addWidget(self.title)

        return header_layout

    def create_question_1_layout(self):
        question_layout = QGridLayout()

        category_checkboxes = {}
        report_checkboxes = {}

        # First question

        category_0 = self.create_subtitle(self.texts[self.language]["category_0"])
        self.translatable["category_0"] = category_0
        question_layout.addWidget(category_0, 0, 0)

        for i in range (1, 3):
            category_checkboxes[f"category_{i}"] = self.create_checkbox(self.texts[self.language][f"category_{i}"])

        for i, item in enumerate(category_checkboxes.items(), start=2):
            key, value = item[0], item[1]
            others = [v for v in category_checkboxes.values()]
            others.remove(value)
            value.stateChanged.connect(lambda state, name=key, others=others: self.update_category_state(state, name, others))
            self.translatable[key] = value
            question_layout.addWidget(value, i, 0)


        # Second question

        report_0 = self.create_subtitle(self.texts[self.language]["report_0"])
        self.translatable["report_0"] = report_0
        question_layout.addWidget(report_0, 0, 1)

        for i in range (1, 5):
            report_checkboxes[f"report_{i}"] = self.create_checkbox(self.texts[self.language][f"report_{i}"])

        for i, item in enumerate(report_checkboxes.items(), start=1):
            key, value = item[0], item[1]
            others = [v for v in report_checkboxes.values()]
            others.remove(value)
            value.stateChanged.connect(lambda state, name=key, others=others: self.update_report_state(state, name, others))
            self.translatable[key] = value
            question_layout.addWidget(value, i, 1)

        return question_layout, category_checkboxes, report_checkboxes

    def create_people_layout(self):
        people_layout = QVBoxLayout()

        people = self.create_subtitle(self.texts[self.language]["people"])
        self.translatable["people"] = people
        people_layout.addWidget(people)

        input_box = self.create_text_input()
        people_layout.addWidget(input_box)
        people.setContentsMargins(0, 0, 10, 0)

        return people_layout, input_box
    
    def create_info_layout(self):
        info_layout = QGridLayout()

        text = {}
        boxes = {}

        for i, q in enumerate(("date", "hour", "place")):

            text[q] = self.create_subtitle(self.texts[self.language][q])
            text[q].setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
            self.translatable[q] = text[q]
            info_layout.addWidget(text[q], i, 0)

            if q == "place":
                boxes[q] = self.create_text_input()
                info_layout.addWidget(boxes[q], i, 1, 1, 2)

        boxes["date"] = QDateEdit()
        boxes["date"].setDate(QtCore.QDate.currentDate())
        boxes["date"].setButtonSymbols(QAbstractSpinBox.NoButtons)
        
        boxes["date"].setStyleSheet(
            f"border: 2px solid {self.accent_color};"
            "border-radius: 5px;"
            "padding-top: 5px;"
            "padding-bottom: 5px;"
            "padding-left: 5px;"
            "padding-right: 10px;"
            "background-color: white;"
            "font-size: 16px;"
        )
        info_layout.addWidget(boxes["date"], 0, 1, 1, 2)


        calendar_button = QPushButton()
        icon = QIcon(resource_path("data\\images\\calendar.png"))      # Icon found on https://www.freepik.com/icon/calendar_55281#fromView=keyword&term=Calendar&page=1&position=6 Icon by Freepik
        calendar_button.setIcon(icon)
        calendar_button.setCursor(QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        calendar_button.setFixedSize(35, 35)
        calendar_button.setIconSize(QtCore.QSize(20, 20))
        calendar_button.setStyleSheet("border-radius: 5px; background-color: none;")
        calendar_button.clicked.connect(self.open_calendar)

        info_layout.addWidget(calendar_button, 0, 2)

        boxes["hour"] = QTimeEdit()
        boxes["hour"].setTime(QtCore.QTime.currentTime())
        boxes["hour"].setButtonSymbols(QAbstractSpinBox.NoButtons)
        boxes["hour"].setStyleSheet(
            f"border: 2px solid {self.accent_color};"
            "border-radius: 5px;"
            "padding-top: 5px;"
            "padding-bottom: 5px;"
            "padding-left: 5px;"
            "padding-right: 10px;"
            "background-color: white;"
            "font-size: 16px;"
        )
        info_layout.addWidget(boxes["hour"], 1, 1, 1, 2)


        equipment = self.create_subtitle(self.texts[self.language]["equipment"])
        self.translatable["equipment"] = equipment
        info_layout.addWidget(equipment, 3, 0, 1, 3)

        boxes["equipment"] = self.create_text_input()
        info_layout.addWidget(boxes["equipment"], 4, 0, 1, 3)
        info_layout.setContentsMargins(10, 0, 0, 0)

        return info_layout, boxes

    def create_situation_layout(self):
        situation_layout = QGridLayout()

        situation_0 = self.create_subtitle(self.texts[self.language]["situation_0"])
        self.translatable["situation_0"] = situation_0
        situation_layout.addWidget(situation_0, 0, 0, 1, 2)

        checkboxes = {}

        for i in range (1, 30):
            checkboxes[f"situation_{i}"] = self.create_checkbox(self.texts[self.language][f"situation_{i}"])

        other_layout = QHBoxLayout()
        checkboxes["situation_30"] = self.create_checkbox(self.texts[self.language]["situation_30"])

        for i, item in enumerate(checkboxes.items(), start=1):
            key, value = item[0], item[1]
            others = [v for v in checkboxes.values()]
            others.remove(value)
            value.stateChanged.connect(lambda state, name=key,checkbox=value, others=others: self.update_situation_state(state, name, checkbox, others))
            self.translatable[key] = value
            if i <= 15:
                x = i
                y = 0
            else:
                x = i - 15
                y = 1
            situation_layout.addWidget(value, x, y)

        
        others = [v for v in checkboxes.values()]
        others.remove(checkboxes["situation_30"])
        checkboxes["situation_30"].stateChanged.connect(lambda state, name='situation_30', checkbox=value, others=others: self.update_situation_state(state, name, checkbox, others))
        self.translatable["situation_30"] = checkboxes["situation_30"]
        other_layout.addWidget(checkboxes["situation_30"])

        self.situation_input = QLineEdit()
        self.situation_input.setEnabled(False)
        self.situation_input.setStyleSheet(
            "border: none;"
            "background-color: transparent;"
        )
        other_layout.addWidget(self.situation_input)

        situation_layout.addLayout(other_layout, 15, 1)
        situation_layout.setColumnStretch(0, 1)
        situation_layout.setColumnStretch(1, 1)

        return situation_layout
    
    def create_description_layout(self):
        description_layout = QVBoxLayout()

        description = self.create_subtitle(self.texts[self.language]["description"])
        self.translatable["description"] = description
        description_layout.addWidget(description)

        description_input = self.create_large_text_input()
        

        description_layout.addWidget(description_input)

        return description_layout, description_input
    
    def create_injury_layout(self):
        injury_layout = QVBoxLayout()

        injury_0 = self.create_subtitle(self.texts[self.language]["injury_0"])
        self.translatable["injury_0"] = injury_0
        injury_layout.addWidget(injury_0)

        checkboxes={}
        checkboxes_layout = QVBoxLayout()
        checkboxes_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        
        for i in range (1,5):
            checkboxes[f"injury_{i}"] = self.create_checkbox(self.texts[self.language][f"injury_{i}"])

        for key, value in checkboxes.items():
            others = [v for v in checkboxes.values()]
            others.remove(value)
            value.stateChanged.connect(lambda state, name=key, checkbox=value, others=others: self.update_injury_state(state, name, checkbox, others))
            self.translatable[key] = value
            checkboxes_layout.addWidget(value)

        injury_layout.addLayout(checkboxes_layout)

        injury_layout.addWidget(self.create_h_separator())

        injury_5 = self.create_subtitle(self.texts[self.language]["injury_5"])
        injury_5.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.translatable["injury_5"] = injury_5
        injury_layout.addWidget(injury_5)

        comments_input = self.create_large_text_input()
        injury_layout.addWidget(comments_input, stretch=1)


        return injury_layout, comments_input
    
    def create_body_layout(self):
        body_layout = QVBoxLayout()

        body_0 = self.create_subtitle(self.texts[self.language]["body_0"])
        self.translatable["body_0"] = body_0
        body_layout.addWidget(body_0)

        text = "" if self.answer["organs"] == [] else self.texts[self.language]["body_36"] + " ".join([f"{org}," for org in self.answer["organs"]])[:-1]

        body_36 = QLabel(text)
        body_36.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        body_36.setWordWrap(True)
        body_36.setStyleSheet(
            "font-size: 16px"
        )
        self.translatable["body_36"] = body_36
        body_layout.addWidget(body_36)

        body_37 = self.create_button(self.texts[self.language]["body_37"])
        body_37.setStyleSheet(
                    "border: 2px solid grey;"
                    "border-radius: 5px;"
                    "background: grey;"
                    "padding-top: 5px;"
                    "padding-bottom: 5px;"
                    "color: white;"
                    "margin-top: 0px;"
                    "margin-bottom: 0px;"
                    "font-size: 16px"
                )
        body_37.setEnabled(False)
        body_37.clicked.connect(self.clear_body)
        self.translatable["body_37"] = body_37
        body_layout.addWidget(body_37, alignment=QtCore.Qt.AlignCenter)
        
        image_view = self.create_body_image()
        body_layout.addWidget(image_view, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)


        return body_layout, image_view
    
    def create_attachment_layout(self):
        attachment_layout = QVBoxLayout()

        attachment_0 = self.create_subtitle(self.texts[self.language]["attachment_0"])
        self.translatable["attachment_0"] = attachment_0
        attachment_layout.addWidget(attachment_0)

        self.attachment_button_layout = QHBoxLayout()

        attachment_1 = self.create_button(self.texts[self.language]["attachment_1"])
        self.translatable["attachment_1"] = attachment_1
        attachment_1.clicked.connect(self.add_company_logo)


        attachment_2 = self.create_button(self.texts[self.language]["attachment_2"])
        self.translatable["attachment_2"] = attachment_2
        attachment_2.clicked.connect(self.update_attachment_files)

        self.attachment_button_layout.addWidget(attachment_1, stretch=1)
        self.attachment_button_layout.addWidget(attachment_2, stretch=1)
        attachment_layout.addLayout(self.attachment_button_layout)

        return attachment_layout


        
    def create_checkbox(self, text):
        checkbox = QCheckBox(text)
        checkbox.setCursor(QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        url = resource_path('data/images/check.png')
        style = """
            QCheckBox {
                spacing: 5px;
                font-size: 15px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border: 2px solid teal;
                border-radius: 4px;
                background-color: white;
            }
            QCheckBox::indicator:unchecked:hover {
                background-color: #e4fffd;
            }
            QCheckBox::indicator:checked {
                background-color: teal;
        """
        image = f"    image: url('{url}')}}"
        checkbox.setStyleSheet(style+image)
        return checkbox
    
    def create_text_input(self):
        box = QLineEdit()
        box.setCursor(QtCore.Qt.CursorShape.IBeamCursor)
        box.setStyleSheet(
            f"border: 2px solid {self.accent_color};"
            "border-radius: 5px;"
            "padding-top: 5px;"
            "padding-bottom: 5px;"
            "padding-left: 10px;"
            "padding-right: 10px;"
            "background-color: white;"
            "font-size: 16px"
        )
        return box
    
    def create_large_text_input(self):
        input = QTextEdit()
        input.setStyleSheet("""
            QTextEdit {
                border: 2px solid teal;
                border-radius: 5px;
                padding-top: 5px;
                padding-bottom: 5px;
                padding-left: 10px;
                padding-right: 10px;
                background-color: white;
                font-size: 16px;
                line-height: 20px;
            }
            QScrollBar:vertical {
                border: none;
                border-radius: 4px;
                background-color: white;
                width: 10px;
                margin: 0px 3px 0px 0px;
            }
            QScrollBar:vertical:hover {
                border-radius: 5px;
                background-color: #dadada;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background-color: teal;  /* Couleur de la poignée */
                min-height: 20px;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical:hover {
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background-color: transparent;
                height: 12px;
                subcontrol-position: top;
                subcontrol-origin: margin;
            }
            QScrollBar:horizontal {
                border: none;
                border-radius: 4px;
                background-color: white;
                height: 10px;
                margin: 0px 0px 3px 0px;
            }
            QScrollBar:horizontal:hover {
                border-radius: 5px;
                background-color: #dadada;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:horizontal {
                background-color: teal;  /* Couleur de la poignée */
                min-width: 20px;
                border-radius: 3px;
            }
            QScrollBar::handle:horizontal:hover {
                border-radius: 5px;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                border: none;
                background-color: transparent;
                width: 12px;
                subcontrol-position: left;
                subcontrol-origin: margin;
            }
                                        """)
        
        return input
    
    def create_button(self, text:str):
        button = QPushButton(text)
        button.setCursor(QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        button.setMinimumWidth(200)
        button.setMaximumWidth(500)
        button.setStyleSheet(
            f"border: 2px solid {self.accent_color};"
            "border-radius: 5px;"
            f"background: {self.accent_color};"
            "padding-top: 10px;"
            "padding-bottom: 10px;"
            "color: white;"
            "margin-top: 0px;"
            "margin-bottom: 0px;"
            "font-size: 16px;"
        )

        return button

    def create_v_separator(self):
        separator_line = QFrame()
        separator_line.setFrameShape(QFrame.VLine)
        separator_line.setFrameShadow(QFrame.Sunken)
        separator_line.setFixedWidth(12)
        separator_line.setStyleSheet(
            "background-color: black;"
            "margin-left: 10px;"
            "padding-right: 150px;"
            )
        return separator_line
    
    def create_h_separator(self):
        separator_line = QFrame()
        separator_line.setFrameShape(QFrame.HLine)
        separator_line.setFrameShadow(QFrame.Sunken)
        separator_line.setFixedHeight(17)
        separator_line.setStyleSheet(
            "background-color: black;"
            "margin-top: 15px;"
        )
        return separator_line

    def create_subtitle(self, text:str):
        subtitle = QLabel(text)
        subtitle.setWordWrap(True)
        subtitle.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet(
            "margin: 20px;"
            "color: black;"
            "font-size: 20px;"
            "text-decoration: underline;"
        )
        return subtitle



    def open_calendar(self):
        selected_date = QtCore.QDate.fromString(self.info_boxes["date"].text(), "dd/MM/yyyy")
        calendar = QCalendarWidget()
        calendar.setSelectedDate(selected_date)
        if self.language == 'fr':
            locale = QtCore.QLocale(QtCore.QLocale.French)
        elif self.language == 'en':
            locale = QtCore.QLocale(QtCore.QLocale.English)
        elif self.language == 'de':
            locale = QtCore.QLocale(QtCore.QLocale.German)
        calendar.setLocale(locale)

        calendar.clicked.connect(self.update_date_input)

        self.dialog = QDialog()
        self.dialog.setWindowTitle("Calendrier")
        self.dialog.setLayout(QVBoxLayout())
        self.dialog.layout().addWidget(calendar)
        self.dialog.exec_()

    def create_body_image(self):
        image_view = QGraphicsView()
        scene = QGraphicsScene(image_view)
        image_view.setScene(scene)
        image_view.setFixedHeight(730)
        image_view.setStyleSheet("border:none;")
        image_view.setRenderHint(QPainter.Antialiasing)

        # Charger l'image et la définir comme arrière-plan
        image = QPixmap(resource_path("data\\images\\body.png"))
        scene.addPixmap(image)

        self.body_buttons = {}
        blank = QIcon(resource_path("data\\images\\blank.png"))
        cross = QIcon(resource_path("data\\images\\cross.png"))
        
        for i in range(1, 36):
            button = IconButton(blank=blank, cross=cross)
            self.body_buttons[f"body_{i}"] = button
            self.body_buttons[f"body_{i}"].clicked.connect(lambda _, name=f"body_{i}", button = self.body_buttons[f"body_{i}"]: self.update_body_state(name, button))

        # Créer et positionner les boutons sur l'image
        #self.body_buttons["body_1"].setFixedSize(30, 20)

        self.body_buttons["body_1"].setFixedSize(63, 30); self.add_button(scene, self.body_buttons["body_1"], QtCore.QPointF(85, 20))
        self.body_buttons["body_2"].setFixedSize(16, 13); self.add_button(scene, self.body_buttons["body_2"], QtCore.QPointF(97, 50))
        self.body_buttons["body_3"].setFixedSize(16, 13); self.add_button(scene, self.body_buttons["body_3"], QtCore.QPointF(119, 50))
        self.body_buttons["body_4"].setFixedSize(17, 29); self.add_button(scene, self.body_buttons["body_4"], QtCore.QPointF(78, 60))
        self.body_buttons["body_5"].setFixedSize(17, 29); self.add_button(scene, self.body_buttons["body_5"], QtCore.QPointF(138, 60))
        self.body_buttons["body_6"].setFixedSize(17, 14); self.add_button(scene, self.body_buttons["body_6"], QtCore.QPointF(107, 62))
        self.body_buttons["body_7"].setFixedSize(26, 14); self.add_button(scene, self.body_buttons["body_7"], QtCore.QPointF(103, 76))
        self.body_buttons["body_8"].setFixedSize(35, 16); self.add_button(scene, self.body_buttons["body_8"], QtCore.QPointF(99, 90))
        self.body_buttons["body_9"].setFixedSize(47, 36); self.add_button(scene, self.body_buttons["body_9"], QtCore.QPointF(93, 105))
        self.body_buttons["body_10"].setFixedSize(107, 101); self.add_button(scene, self.body_buttons["body_10"], QtCore.QPointF(63, 140))
        self.body_buttons["body_11"].setFixedSize(113, 91); self.add_button(scene, self.body_buttons["body_11"], QtCore.QPointF(60, 242))
        self.body_buttons["body_12"].setFixedSize(61, 133); self.add_button(scene, self.body_buttons["body_12"], QtCore.QPointF(48, 350))
        self.body_buttons["body_13"].setFixedSize(61, 133); self.add_button(scene, self.body_buttons["body_13"], QtCore.QPointF(125, 350))
        self.body_buttons["body_14"].setFixedSize(61, 58); self.add_button(scene, self.body_buttons["body_14"], QtCore.QPointF(48, 484))
        self.body_buttons["body_15"].setFixedSize(61, 58); self.add_button(scene, self.body_buttons["body_15"], QtCore.QPointF(125, 484))
        self.body_buttons["body_16"].setFixedSize(58, 109); self.add_button(scene, self.body_buttons["body_16"], QtCore.QPointF(43, 543))
        self.body_buttons["body_17"].setFixedSize(58, 109); self.add_button(scene, self.body_buttons["body_17"], QtCore.QPointF(133, 543))
        self.body_buttons["body_18"].setFixedSize(39, 34); self.add_button(scene, self.body_buttons["body_18"], QtCore.QPointF(61, 655))
        self.body_buttons["body_19"].setFixedSize(39, 34); self.add_button(scene, self.body_buttons["body_19"], QtCore.QPointF(134, 655))
        self.body_buttons["body_20"].setFixedSize(49, 33); self.add_button(scene, self.body_buttons["body_20"], QtCore.QPointF(52, 688))
        self.body_buttons["body_21"].setFixedSize(49, 33); self.add_button(scene, self.body_buttons["body_21"], QtCore.QPointF(133, 688))
        self.body_buttons["body_22"].setFixedSize(35, 60); self.add_button(scene, self.body_buttons["body_22"], QtCore.QPointF(28, 137))
        self.body_buttons["body_23"].setFixedSize(35, 60); self.add_button(scene, self.body_buttons["body_23"], QtCore.QPointF(170, 137))
        self.body_buttons["body_24"].setFixedSize(53, 138); self.add_button(scene, self.body_buttons["body_24"], QtCore.QPointF(7, 197))
        self.body_buttons["body_25"].setFixedSize(53, 138); self.add_button(scene, self.body_buttons["body_25"], QtCore.QPointF(171, 197))
        self.body_buttons["body_26"].setFixedSize(32, 29); self.add_button(scene, self.body_buttons["body_26"], QtCore.QPointF(0, 335))
        self.body_buttons["body_27"].setFixedSize(32, 29); self.add_button(scene, self.body_buttons["body_27"], QtCore.QPointF(203, 335))
        self.body_buttons["body_28"].setFixedSize(37, 66); self.add_button(scene, self.body_buttons["body_28"], QtCore.QPointF(0, 363))
        self.body_buttons["body_29"].setFixedSize(37, 66); self.add_button(scene, self.body_buttons["body_29"], QtCore.QPointF(201, 363))
        self.body_buttons["body_30"].setFixedSize(62, 60); self.add_button(scene, self.body_buttons["body_30"], QtCore.QPointF(360, 18))
        self.body_buttons["body_31"].setFixedSize(126, 53); self.add_button(scene, self.body_buttons["body_31"], QtCore.QPointF(329, 78))
        self.body_buttons["body_32"].setFixedSize(119, 161); self.add_button(scene, self.body_buttons["body_32"], QtCore.QPointF(332, 132))
        self.body_buttons["body_33"].setFixedSize(136, 80); self.add_button(scene, self.body_buttons["body_33"], QtCore.QPointF(323, 293))
        self.body_buttons["body_34"].setFixedSize(55, 176); self.add_button(scene, self.body_buttons["body_34"], QtCore.QPointF(317, 517))
        self.body_buttons["body_35"].setFixedSize(55, 176); self.add_button(scene, self.body_buttons["body_35"], QtCore.QPointF(408, 517))

        return image_view

    def add_button(self, scene, button, position):
        proxy = QGraphicsProxyWidget()
        proxy.setWidget(button)
        proxy.setPos(position)
        scene.addItem(proxy)

    def switch_language(self, lg):
        self.language = lg
        with open(resource_path('data\\texts\\lg.txt'), 'w') as f:
            f.write(lg)
        for key, value in self.translatable.items():
            value.setText(self.texts[lg][key])
        
        text = "" if self.answer["organs"] == [] else self.texts[self.language]["body_36"] + " ".join([f"{self.texts[self.language][org]}," for org in self.answer["organs"]])[:-1]
        try:
            self.translatable["body_36"].setText(text)
        except:
            pass

    def update_category_state(self, state, name, other_checkboxes):
        if state == QtCore.Qt.Checked:
            for checkbox in other_checkboxes:
                checkbox.setChecked(False)
            self.answer["category"] = name

    def update_report_state(self, state, name, other_checkboxes):
        if state == QtCore.Qt.Checked:
            for checkbox in other_checkboxes:
                checkbox.setChecked(False)
            self.answer["report type"] = name

    def update_date_input(self, date):
        
        date = date.toString("dd/MM/yyyy").split("/")
        y, m, d = int(date[2]), int(date[1]), int(date[0])
        self.info_boxes["date"].setDate(QtCore.QDate(y, m, d))
        self.dialog.close()

    def update_situation_state(self, state, name, current_checkbox, other_checkboxes):
        if state == QtCore.Qt.Checked:
            # for checkbox in other_checkboxes:
            #     checkbox.setChecked(False)
            if current_checkbox.text()[:2] == "30":
                self.situation_input.setEnabled(True)
                self.situation_input.setCursor(QtCore.Qt.IBeamCursor)
                self.situation_input.setStyleSheet(
                    f"border: 2px solid {self.accent_color};"
                    "border-radius: 5px;"
                    "padding-left: 5px;"
                    "padding-right: 5px;"
                    "background-color: white;"
                    "margin-right: 35px;"
                    "font-size: 15px;"
                )
            else:
                self.answer["situation"].append(name)
        else:
            if current_checkbox.text()[:2] == "30":
                self.situation_input.setEnabled(False)
                self.situation_input.setText('')
                self.situation_input.setStyleSheet(
                    "border: none;"
                    "background-color: transparent;"
                )
            else:
                self.answer["situation"].remove(name)

    def update_injury_state(self, state, name, current_checkbox, other_checkboxes):
        if state == QtCore.Qt.Checked:
            for checkbox in other_checkboxes:
                checkbox.setChecked(False)
            text = current_checkbox.text()
            self.answer["injury"] = name

            if text != self.texts[self.language]["injury_1"]:
                if not self.display_body:
                    self.display_body = True
                    self.body_layout, self.body_image = self.create_body_layout()
                    self.harm_layout.insertLayout(1, self.body_layout, stretch=1)
            else:
                self.display_body = False
                try:
                    for i in reversed(range(self.body_layout.count())):
                        widget_item = self.body_layout.itemAt(i)
                        if widget_item.widget():
                            widget_item.widget().hide()
                    self.harm_layout.removeItem(self.body_layout)
                except:
                    pass

    def update_body_state(self, name, button):
        if name in self.answer["organs"]:
            self.answer["organs"].remove(name)
            if self.answer["organs"] == []:
                self.translatable["body_37"].setEnabled(False)
                self.translatable["body_37"].setStyleSheet(
                    "border: 2px solid grey;"
                    "border-radius: 5px;"
                    "background: grey;"
                    "padding-top: 5px;"
                    "padding-bottom: 5px;"
                    "color: white;"
                    "margin-top: 0px;"
                    "margin-bottom: 0px;"
                    "font-size: 16px;"
                )
        else:
            self.answer["organs"].append(name)
            if len(self.answer["organs"]) == 1:
                self.translatable["body_37"].setEnabled(True)
                self.translatable["body_37"].setStyleSheet(
                    f"border: 2px solid {self.accent_color};"
                    "border-radius: 5px;"
                    f"background: {self.accent_color};"
                    "padding-top: 5px;"
                    "padding-bottom: 5px;"
                    "color: white;"
                    "margin-top: 0px;"
                    "margin-bottom: 0px;"
                    "font-size: 16px"
                )
        self.translatable["body_36"].setText(self.texts[self.language]["body_36"] + " ".join([f"{self.texts[self.language][org]}," for org in self.answer["organs"]])[:-1])

        if button.activated:
            button.activated = False
            button.none_size = QtCore.QSize(0, 0)
            button.setIconSize(button.none_size)
        else:
            button.activated = True
            button.none_size = QtCore.QSize(13, 13)
            button.setIconSize(button.full_size)

        

    def clear_body(self):
        self.answer["organs"] = []
        self.translatable["body_36"].setText("")
        self.translatable["body_37"].setEnabled(False)
        self.translatable["body_37"].setStyleSheet(
                    "border: 2px solid grey;"
                    "border-radius: 5px;"
                    "background: grey;"
                    "padding-top: 5px;"
                    "padding-bottom: 5px;"
                    "color: white;"
                    "margin-top: 0px;"
                    "margin-bottom: 0px;"
                    "font-size: 16px;"
                )
        for value in self.body_buttons.values():
            value.activated = False
            value.none_size = QtCore.QSize(0, 0)
            value.setIconSize(value.none_size)
        
    def add_company_logo(self):
        file_dialog = QFileDialog()
        prompt = self.texts[self.language]["attachment_3"]
        logo_path = file_dialog.getOpenFileName(self.window, prompt, "", "Tous les fichiers (*);;Images (*.jpg *.png *ico *jpeg)")[0]
        if logo_path:
            self.answer["logo"] = logo_path
            self.logo_layout = QHBoxLayout()

            logo = QPixmap(logo_path)
            logo = logo.scaled(QtCore.QSize(200, logo.height()), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            logo_label = QLabel()
            logo_label.setPixmap(logo)
            self.logo_layout.addWidget(logo_label)

            delete_logo = QPushButton()
            delete_logo.setCursor(QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
            delete_logo.setStyleSheet(f"border: none; background-color:teal; padding-right:4px; padding-left:4px; padding-top:6px; padding-bottom:6px")
            delete_logo.setIcon(QIcon(resource_path("data\\images\\close.png")))
            delete_logo.setIconSize(QtCore.QSize(20, 20))
            delete_logo.clicked.connect(self.remove_logo)
            self.logo_layout.addWidget(delete_logo, alignment=QtCore.Qt.AlignTop | QtCore.Qt.AlignRight)

            self.logo_layout.addWidget(QLabel(), stretch=1)

            self.attachment_button_layout.insertLayout(1, self.logo_layout, stretch=0)

            self.attachment_button_layout.itemAt(0).widget().hide()

    def remove_logo(self):
        self.answer["logo"] = ""
        for i in reversed(range(self.logo_layout.count())):
            widget_item = self.logo_layout.itemAt(i)
            if widget_item.widget():
                widget_item.widget().hide()
        
        self.attachment_button_layout.itemAt(0).widget().show()

    def update_attachment_files(self):

        file_dialog = QFileDialog()
        prompt = self.texts[self.language]["attachment_3"]
        path = file_dialog.getOpenFileName(self.window, prompt, "", "Images (*.jpg *.png *ico *jpeg);;Tous les fichiers (*)")[0]

        if path:
            if self.attachment_layout.count() == 2:
                self.selected_files = QHBoxLayout()
                self.selected_files.setContentsMargins(0, 0, 0, 15)
                attachment_4 = QLabel(self.texts[self.language]["attachment_4"])
                self.translatable["attachment_4"] = attachment_4
                self.selected_files.addWidget(attachment_4)
                self.selected_files.addWidget(QLabel(), stretch=1)

                self.attachment_layout.insertLayout(1, self.selected_files)

            self.answer["attachment"].append(path)
            if len(path.split('/')) > 1:
                name = path.split('/')[-1]
            else:
                name = path.split('/')[-1]

            button = QPushButton(name)
            button.setStyleSheet("""
                                 border: 2px solid black;
                                 border-radius:10px;
                                 padding:5px;
                                 font-size: 16px;
                                 """)
            button.setCursor(QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
            button.clicked.connect(lambda _, path = path, button = button: self.remove_attachment(path, button))
            self.selected_files.insertWidget(1, button, alignment=QtCore.Qt.AlignLeft, stretch=0)

    def remove_attachment(self, path, widget):
        self.answer["attachment"].remove(path)
        widget.hide()
        self.selected_files.removeWidget(widget)
        

    def export(self):
        self.answer["people"] = self.people_box.text()
        for key, value in self.info_boxes.items():
            self.answer[key] = value.text()
        if self.situation_input.text() != "":
            self.answer["situation"].append(self.situation_input.text())
        self.answer["description"] = self.description_box.toPlainText().replace('\u200e', '')
        self.answer["comments"] = self.comment_box.toPlainText()


        file_dialog = QFileDialog()

        default_filename = self.texts[self.language]['title']+'_'+ "-".join(self.answer['date'].split('/')) + ".pdf"
        initial_dir = str(Path.home())
        file_path, _ = file_dialog.getSaveFileName(self.window,
                                                   self.texts[self.language]["ex_prompt"],
                                                   initial_dir+'/'+default_filename,
                                                   "PDF files (*.pdf);;All files (*)",
                                                   options=QFileDialog.Options(QFileDialog.ShowDirsOnly))

        if file_path:
            folder_path = os.path.dirname(file_path)  # Folder path
            filename = os.path.basename(file_path)    # Chosen name for the file
            self.answer["save"] = folder_path
            self.answer['name'] = filename
            print(self.answer)
            if self.display_body:
                for value in self.body_buttons.values():
                    if value.activated:
                        value.setIconSize(QtCore.QSize(20, 20))
                pixmap = QPixmap(self.body_image.size())
                painter = QPainter(pixmap)
                painter.fillRect(pixmap.rect(), QtCore.Qt.white)
                self.body_image.render(painter)
                painter.end()
                pixmap.save(resource_path('data\\images\\body_capture.png'))
                for value in self.body_buttons.values():
                    if value.activated:
                        value.setIconSize(value.none_size)

            for key in ('category', 'report type', 'injury'):
                if self.answer[key] == '':
                    self.answer[key] = 'None'

            pdf = PDFGenerator(self.answer, self.texts, self.language)
            print('done')

class PDFGenerator:
    def __init__(self, answer, texts, language) -> None:
        self.answer, self.texts, self.language = answer, texts, language
        self.full_box = Image(resource_path("data\\images\\box.png"), 12, 12)
        self.empty_box = Image(resource_path("data\\images\\empty_box.png"), 12, 12)

        # Different styles
        self.title_style = ParagraphStyle(
            "TitleStyle",
            fontSize=18,
            alignment=TA_CENTER,  # Align center
            leading=20  # Line height
        )
        self.subtitle_style = ParagraphStyle(
            "SubtitleStyle",
            fontSize=10,
            underline=True,
            underLineColor=colors.black,
            alignment=TA_CENTER,
            leading=10
        )
        self.base_style = ParagraphStyle(
            "BaseStyle",
            fontSize=10,
            alignment = TA_JUSTIFY,
            leading = 11,
            underLineColor=colors.black,
        )
        self.checkbox_style = ParagraphStyle(
            "Checkbox",
            fontSize=15,
            leading=15,
            alignment=TA_CENTER,
            borderColor=colors.black,
            borderWidth=1,
            borderRadius=2,
            borderPadding=0
        )
        self.create_pdf()

    def create_pdf(self):
        self.doc = SimpleDocTemplate(self.answer['save']+"/"+self.answer['name'],
                                pagesize=A4,
                                leftMargin=20,
                                rightMargin=20,
                                topMargin=20,
                                bottomMargin=20)
        self.quarter, self.half = self.doc.width/4, self.doc.width/2
        self.story = []

        total_pages = 2 if self.answer['attachment'] != [] else 1

        self.story.append(self.create_header())
        self.story.append(Spacer(1, 10))
        self.story.append(self.create_row1())
        self.story.append(self.create_situation())
        self.story.append(self.create_description())
        if self.answer['injury'] in ('injury_1', 'None'):
            self.story.append(self.create_injury_body_comment())
        else: self.story.append(self.create_injury_body_comment(2))

        if total_pages == 2:
            for pict in self.answer['attachment']:
                try:
                    i = img.open(pict)
                    w, h = i.size
                    w, h = self.doc.width, h*(self.doc.width/w)
                    if h>self.doc.height:
                        w, h = i.size
                        w, h = w*(self.doc.height/h), self.doc.height
                    self.story.append(Image(pict, w, h))
                    self.story.append(Spacer(0, 10))
                except:
                    self.story.append(Paragraph(pict.split('\\')[-1], self.subtitle_style))
                    self.story.append(Spacer(0, 10))
            
            self.story.pop()
        
        self.doc.build(self.story)

    def create_header(self):
        # Header
        if self.answer['logo'] == '': logo_path = resource_path('data\\images\\blank.png')
        else: logo_path = self.answer['logo']
        logo = img.open(logo_path)
        logo_w, logo_h = logo.size
        desired_max_size = 50
        if max(logo_w, logo_h) == logo_w:
            logo_h, logo_w = logo_h * (desired_max_size / logo_w), desired_max_size
        else:
            logo_w, logo_h = logo_w * (desired_max_size / logo_h), desired_max_size

        
        header_table_data = [
            [Image(logo_path, width=logo_w, height=logo_h), Paragraph(self.texts[self.language]['pdf_title'], style=self.title_style), Paragraph(f"", self.title_style)]
        ]
        
        header_table = Table(header_table_data, colWidths=[50, self.doc.width-100, 50], rowHeights=[50])
        
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('INNERGRID', (0, 0), (-1, -1), 1, colors.black),  # Inner grid
            ('BOX', (0, 0), (-1, -1), 1, colors.black),        # Outer border
        ]))

        return header_table
    
    def create_row1(self):

        titles = [[
            Paragraph("<u>"+self.texts[self.language]['category_0']+"</u>", style=self.subtitle_style),
            Paragraph("<u>"+self.texts[self.language]['report_0']+"</u>", self.subtitle_style)
            ]]
        
        titles_table = Table(titles, colWidths=[self.quarter-30, self.quarter+44], rowHeights=[13])
        
        titles_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER')
        ]))
        

        checkboxes = [
            ["", ""],
            [],
            [],
            ["", ""]
        ]

        for i in range(1, 3):
            checkboxes[i].append(self.full_box if self.answer['category'][-1] == str(i) else self.empty_box)
            checkboxes[i].append(Paragraph(self.texts[self.language][f'category_{i}'], self.base_style))
        
        for i in range(1, 5):
            checkboxes[i-1].append(self.full_box if self.answer['report type'][-1] == str(i) else self.empty_box)
            checkboxes[i-1].append(Paragraph(self.texts[self.language][f'report_{i}'], self.base_style))

        checkboxes_table = Table(checkboxes, colWidths=[15, self.quarter-45, 15, self.quarter+29])

        checkboxes_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT')

        ]))

        people_data= [
            [Paragraph("<u>"+self.texts[self.language]['people']+"</u>", self.subtitle_style)],
            [Paragraph(self.answer['people'], self.base_style)]
        ]
        people_table = Table(people_data, colWidths=self.half+14)

        info_data = [
            [Paragraph("<u>"+self.texts[self.language]['date']+"</u>", self.subtitle_style), Paragraph(self.answer['date'], self.base_style)],
            [Paragraph("<u>"+self.texts[self.language]['hour']+"</u>", self.subtitle_style), Paragraph(self.answer['hour'], self.base_style)],
            [Paragraph("<u>"+self.texts[self.language]['place']+"</u>", self.subtitle_style), Paragraph(self.answer['place'], self.base_style)]
        ]
        info_table = Table(info_data, colWidths=[self.quarter+5, self.quarter-19], rowHeights=[30.35 for _ in range(3)])

        info_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),

        ]))

        equipment_data= [
            [Paragraph("<u>"+self.texts[self.language]['equipment']+"</u>", self.subtitle_style)],
            [Paragraph(self.answer['equipment'], self.base_style)]
        ]
        equipment_table = Table(equipment_data, colWidths=self.half-14)

        column1_data = [
            [titles_table],
            [checkboxes_table],
            [people_table]
        ]
        column1_table = Table(column1_data, colWidths=[self.half+14])

        column1_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('LINEABOVE', (-1, -1), (-1, -1), 1, colors.black)

        ]))

        column2_data = [
            [info_table],
            [equipment_table]
        ]
        column2_table = Table(column2_data, colWidths=[self.half-14])

        column2_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('LINEABOVE', (-1, -1), (-1, -1), 1, colors.black)
        ]))

        row1_data = [
            [column1_table, column2_table]
        ]
        row1_table = Table(row1_data, colWidths=(self.half+14, self.half-14))

        row1_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('INNERGRID', (0, 0), (-1, -1), 1, colors.black),  # Inner grid
            ('BOX', (0, 0), (-1, -1), 1, colors.black),        # Outer border
        ]))

        return row1_table
    
    def create_situation(self):
        checkboxes_data = []
        resp = []
        for sit in self.answer["situation"]:
            if sit in self.texts[self.language].keys():
                resp.append(int(sit.split('_')[1]))
            else: resp.append(30); text = ' '+sit

        for i in range(1, 31):
            if i<=15:
                checkboxes_data.append([])
                y = i-1
            else: y=i-16
            if i in resp:
                checkboxes_data[y].append(self.full_box)
                if i == 30:
                    checkboxes_data[y].append(Paragraph(self.texts[self.language][f'situation_{i}']+text, self.base_style))
                else:
                    checkboxes_data[y].append(Paragraph(self.texts[self.language][f'situation_{i}'], self.base_style))
            else:
                checkboxes_data[y].append(self.empty_box)
                checkboxes_data[y].append(Paragraph(self.texts[self.language][f'situation_{i}'], self.base_style))

        checkboxes_table = Table(checkboxes_data, colWidths=[15, self.half-15, 15, self.half-15])
        checkboxes_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (0, -1), 3),
            ('TOPPADDING', (2, 0), (2, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
        ]))

        situation_table = Table([[Paragraph('<u>'+self.texts[self.language]['situation_0']+'</u>', self.subtitle_style)], [checkboxes_table]], colWidths=self.doc.width)
        situation_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('BOX', (0, 0), (-1, -1), 1, colors.black), # Outer border
        ]))

        return situation_table
    
    def create_description(self):
        """description_table = Table(
            [[Paragraph('<u>'+self.texts[self.language]['description']+'</u>', self.subtitle_style)],
            [Paragraph(self.answer['description'], self.base_style)]],
            colWidths=[self.doc.width])"""
        description_table = Table(
            [[Paragraph('<u>'+self.texts[self.language]['description']+'</u> '+self.answer['description'], self.base_style)]],
            colWidths=[self.doc.width])
        
        description_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('BOX', (0, 0), (-1, -1), 1, colors.black), # Outer border
            ('BOTTOMPADDING', (0,0), (-1, -1), 6)
        ]))
        return description_table
    
    def create_injury_body_comment(self, width=1):
        checkboxes_data = [[], [], [], []]
        for i in range(1, 5):
            checkboxes_data[i-1].append(self.full_box if self.answer['injury'][-1] == str(i) else self.empty_box)
            checkboxes_data[i-1].append(Paragraph(self.texts[self.language][f'injury_{i}']))

        checkboxes_table = Table(checkboxes_data, colWidths=[15, self.half-55])

        if width == 1:
            injury_table = Table([[Paragraph('<u>'+self.texts[self.language]['injury_0']+'</u>', self.subtitle_style)], [checkboxes_table]], colWidths=[self.half-70])
            main_table = Table([[injury_table, Paragraph('<u>'+self.texts[self.language]['injury_5']+'</u> '+self.answer['comments'], self.base_style)]], colWidths=[self.half-70, self.half+70])
            main_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (0, 0), 'MIDDLE'),
            ('VALIGN', (-1, -1), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('INNERGRID', (0, 0), (-1, -1), 1, colors.black),  # Inner grid
            ('BOX', (0, 0), (-1, -1), 1, colors.black),        # Outer border
             ]))
            return main_table
        
        else:            
            injury_table = Table([[Paragraph('<u>'+self.texts[self.language]['injury_0']+'</u>', self.subtitle_style)], [checkboxes_table]], colWidths=[(self.half+self.quarter)/2-5])
            organs_table = Table([[Paragraph('<u>'+self.texts[self.language]['pdf_body']+'</u>', self.subtitle_style)], [Paragraph(", ".join([self.texts[self.language][organ] for organ in self.answer['organs']]), self.base_style)]], colWidths=[(self.quarter+self.half)/2-5])
            row1_table = Table([[injury_table, organs_table]], colWidths=[(self.half+self.quarter)/2-5 for _ in range(2)])
            row1_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('BOTTOMPADDING', (0,0), (-1, -1), 0),
                ('TOPPADDING', (0,0), (-1, -1), 0),
            ]))
            text_table = Table([[row1_table], [Paragraph('<u>'+self.texts[self.language]['injury_5']+'</u> '+self.answer['comments'], self.base_style)]], colWidths=(self.half+self.quarter-10))
            text_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('INNERGRID', (0, 0), (-1, -1), 1, colors.black), # Outer border
                ('BOTTOMPADDING', (0,0), (-1, -1), 6)
            ]))
            main_table = Table([[text_table, Image(resource_path("data\\images\\body_capture.png"), width=self.quarter, height=730*(self.quarter/505))]], colWidths=[self.half+self.quarter-10, self.quarter+10])
            main_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('BOX', (0, 0), (-1, -1), 1, colors.black), # Outer border
                ('INNERGRID', (0, 0), (-1, -1), 1, colors.black), # Outer border
                ('BOTTOMPADDING', (0,0), (-1, -1), 6)
            ]))
            return main_table

        

if __name__ == '__main__':
    app_instance = ReportFormApp()

