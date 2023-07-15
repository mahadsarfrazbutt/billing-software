from PyQt5.QtWidgets import *
from PyQt5.Qt import Qt
from PyQt5 import uic
import sqlite3
import resources

# Establish a connection to database
dbconn = sqlite3.connect('storeDB.sqlite')
dbcursor = dbconn.cursor()

class topoffersWindow(QMainWindow):
    def __init__(self):
        super(topoffersWindow, self).__init__()
        uic.loadUi("Screens\TopOffers.ui", self)
        self.setWindowTitle("billing")


class statsWindow(QMainWindow):
    def __init__(self):
        super(statsWindow, self).__init__()
        uic.loadUi("Screens\stats.ui", self)
        self.setWindowTitle("billing")


class fileComplaint(QMainWindow):
    option = None

    def __init__(self):
        # Set up Screen and load ui
        super(fileComplaint, self).__init__()
        uic.loadUi("Screens\FileComplaint.ui", self)
        self.setWindowTitle("billing")

        # Events
        self.radioButton_1.clicked.connect(self.unenableLineEdit)
        self.radioButton_1.clicked.connect(self.option1)

        self.radioButton_2.clicked.connect(self.unenableLineEdit)
        self.radioButton_2.clicked.connect(self.option2)

        self.radioButton_3.clicked.connect(self.unenableLineEdit)
        self.radioButton_3.clicked.connect(self.option3)

        self.radioButton_other.clicked.connect(self.enableLineEdit)
        self.radioButton_other.clicked.connect(self.option4)

        self.submit_button.clicked.connect(self.submit)

    def enableLineEdit(self):
        self.specify.setEnabled(True)
        self.submit_button.setEnabled(True)

    def unenableLineEdit(self):  # This function is created so that the line edit becomes inactive when option has been changed
        self.specify.setEnabled(False)
        self.submit_button.setEnabled(True)

    # Set values for option variable based on selected radio button
    def option1(self): self.option = "Items are consistently out of stock"
    def option2(self): self.option = "Unhelpful Customer Service"
    def option3(self): self.option = "Items are of bad quality"
    def option4(self): self.option = "Other"

    # Stores complaint in database and shows a success message
    def submit(self):
        self.label.setText("Complaint Submitted. We hope your issue will be resolved soon")
        if self.option == "Other":
            self.option = self.specify.toPlainText()
            dbcursor.execute("INSERT INTO Complaint(complaint) VALUES('" + self.option + "')")
            print(self.option)
        else:
            dbcursor.execute("INSERT INTO Complaint(complaint) VALUES('" + self.option + "')")
            print(self.option)
        dbconn.commit()


class reviewsWindow(QMainWindow):
    def __init__(self):
        super(reviewsWindow, self).__init__()
        uic.loadUi("Screens\Reviews.ui", self)
        self.setWindowTitle("billing")


class MainWindow(QMainWindow):
    rowcount = 0  # controls the number of rows in the purchases table and stores index of current row

    def __init__(self):
        # Loads ui and sets window title
        super(MainWindow, self).__init__()
        uic.loadUi("Screens\Main.ui", self)
        self.setWindowTitle("billing")

        # Add Employee Name and counter number from the login screen
        self.main_label_employeeName_2.setText(str(entered_name))
        self.main_label_counterNum_2.setText(str(counterNumber))

        # Add items to the combo box by selecting them from DB and running a loop
        dbcursor.execute("SELECT * FROM Inventory")
        items = dbcursor.fetchall()
        for item in items:
            name = item[1]
            self.main_combo_items.addItem(name)

        # Set table column width
        self.main_table_items.setColumnWidth(0, 280)
        self.main_table_items.setColumnWidth(1, 90)
        self.main_table_items.setColumnWidth(2, 90)
        self.main_table_items.setColumnWidth(3, 90)

        # Setting tooltips
        self.main_btn_addItem.setToolTip("Add item to purchases table")
        self.main_btn_newBill.setToolTip("Create new bill for new customer")
        self.main_btn_genChange.setToolTip("Generate Change")
        self.main_btn_topOffers.setToolTip("Open the top offers window")
        self.main_btn_stats.setToolTip("Open the Statistics window")
        self.main_btn_complaint.setToolTip("File a complaint")
        self.main_btn_reviews.setToolTip("Read reviews")

        # Events
        self.main_btn_addItem.clicked.connect(self.addItem)
        self.main_btn_topOffers.clicked.connect(self.topOffers)
        self.main_btn_stats.clicked.connect(self.statistics)
        self.main_btn_complaint.clicked.connect(self.fileComplaint)
        self.main_btn_reviews.clicked.connect(self.reviews)
        self.main_btn_delItem.clicked.connect(self.delItem)
        self.main_btn_newBill.clicked.connect(self.newBill)
        self.main_btn_genTotal.clicked.connect(self.genTotal)
        self.main_btn_genChange.clicked.connect(self.genChange)
        self.main_btn_logOut.clicked.connect(self.logOut)

    def keyPressEvent(self, event):  # Checks if enter key pressed
        if event.key() == Qt.Key_Enter:
            self.genChange()

    # Adds items to the purchases table or updates their quantity
    def addItem(self):
        addition_required = True  # This variable decides whether a new row will be added or not
        item_bought = self.main_combo_items.currentText()  # item_bought stores the item in the combo box when 'Add' Button is pressed
        dbcursor.execute("SELECT * FROM Inventory where name=?", (item_bought, ))
        data = dbcursor.fetchone()  # Fetches data from database
        unit_price = data[2]
        quantity = data[3]

        if quantity == 0:
            self.main_label_outOfStock.setText("Item out of stock")
            return None  # Exit the function but do not quit the program
        else:
            dbcursor.execute("UPDATE Inventory SET quantity=quantity-1 WHERE name=?", (item_bought, ))  # Decreases quantity of the item by 1 in the DB
            dbconn.commit()
            self.main_label_outOfStock.setText("")  # To empty the out of stock label

        if self.main_table_items.item(0, 0) is not None:  # If there are rows already in the database
            total_rows = self.main_table_items.rowCount()

            for row in range(total_rows): # Loop over the rows in the table
                item = self.main_table_items.item(row, 0).text()
                if item != item_bought:
                    continue
                item_quantity = self.main_table_items.item(row, 2).text()
                new_quantity = int(item_quantity) + 1
                self.main_table_items.setItem(row, 2, QTableWidgetItem(str(new_quantity)))  # QTableWidgetItem only takes strings
                self.main_table_items.setItem(row, 3, QTableWidgetItem(str(unit_price * new_quantity)))

                addition_required = False  # There is no need for a new row as quantity has been incremented
                break  # This is so that program does not have to execute useless loops and to solve a bug which caused another row of item_bought to appear with quantity 1

        if addition_required is True or self.main_table_items.item(0, 0) is None:  # If the table is empty or item has not been bought before
            self.main_table_items.insertRow(self.rowcount)  # Insert a row into the table
            self.main_table_items.setItem(self.rowcount, 0, QTableWidgetItem(item_bought))
            self.main_table_items.setItem(self.rowcount, 1, QTableWidgetItem(str(unit_price)))
            self.main_table_items.setItem(self.rowcount, 2, QTableWidgetItem('1'))  # The item will be added the first time so quantity will be one
            self.main_table_items.setItem(self.rowcount, 3, QTableWidgetItem(str(unit_price * 1)))

            self.rowcount += 1  # rowcount is incremented by one each time unique new item is bought purchase has its own row

    # Open the top offers window
    def topOffers(self):
        self.window = topoffersWindow()  # Creates object
        self.window.show()

    # Opens the statistics window
    def statistics(self):
        self.window = statsWindow()  # Creates object
        self.window.show()

    # Opens the file complaint window
    def fileComplaint(self):
        self.window = fileComplaint()  # Creates object
        self.window.show()

    # Open the reviews window
    def reviews(self):
        self.window = reviewsWindow()  # Creates object
        self.window.show()

    # Delete item in table
    def delItem(self):
        current_row = self.main_table_items.currentRow()  # The currently selected row
        self.main_table_items.removeRow(current_row)
        self.rowcount -= 1  # This is done so the program can add another item as row count will be confused (One row will be reduced due to deletion)

    # Delete all the contents of the screens because new customer has come
    def newBill(self):
        self.main_table_items.setRowCount(0)  # Clears the table
        self.rowcount = 0  # The table will now have 0 rows (Also, so that the program can add the new items easily)

        self.main_label_total_2.clear()
        self.main_lineEdit_payed.clear()
        self.main_label_change_2.clear()
        self.main_btn_delItem.setEnabled(True)

    # Generate Total
    def genTotal(self):
        self.main_btn_delItem.setEnabled(False)  # There is no logic for the delete item button to remain active after total has been generated
        total_rows = self.main_table_items.rowCount()
        total = 0
        for row in range(total_rows):
            sub_total = self.main_table_items.item(row, 3).text()
            total = total + int(sub_total)

        self.main_label_total_2.setText(str(total))

    # Generate Change
    def genChange(self):
        try:
            total = self.main_label_total_2.text()
            payed = self.main_lineEdit_payed.text()
            change = str(float(total) - float(payed))
        except Exception as error:  # total and payed can be None if the employee presses the enter key before total is generated
            print(error)
            return None

        change = change.replace("-", "")  # Remove the minus sign (change is mostly greater than total)
        self.main_label_change_2.setText(change)

    # Log Out
    def logOut(self):
        self.close()  # Closes the main window
        self.window = LoginWindow()  # Creates Login Window object
        self.window.show()


class LoginWindow(QMainWindow):
    def __init__(self):
        # Loads ui and sets window title
        super(LoginWindow, self).__init__()
        uic.loadUi("Screens\Login.ui", self)
        self.setWindowTitle("billing")
        self.show()

        self.logIn_buttn_login.clicked.connect(self.login)

    # Checks if entered key pressed
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Enter:
            self.login()

    def login(self):  # Open the main screen
        # Store the entered credentials
        global entered_name, counterNumber  # This is done so that entered_name and counterNumber can be displayed on main screen
        entered_name = self.logIn_lineEdit_name.text()
        entered_passw = self.logIn_lineEdit_passw.text()
        counterNumber = self.logIn_lineEdit_counter.text()

        dbcursor.execute("SELECT name, password FROM Employees WHERE name=? AND password=?", (entered_name, entered_passw))

        try:
            row = dbcursor.fetchone()  # If there is no result then row will be equal to None
            counterNumber = int(counterNumber)
        except Exception as error:
            print("Error in Logging In:", error)
            self.logIn_label_warning.setText("Inputted Credentials are incorrect")
            return None  # Exit the function but not quit the program

        if row is None or counterNumber < 1 or counterNumber > 6:  # Entered Credentials are wrong
            self.logIn_label_warning.setText("Inputted Credentials are incorrect")
        else:
            self.close()  # Closes the previous login window
            self.window = MainWindow()  # Creates main window
            self.window.show()


# Creates login window object
app = QApplication([])
window = LoginWindow()
app.exec_()
