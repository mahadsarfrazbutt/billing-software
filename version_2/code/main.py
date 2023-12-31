"""
    Please compile, please compile,
    It would surely make me smile,
    When I glance at the clock,
    And thirty minutes has gone by non-stop,
    I think that I've won, that I've beaten the odds,
    But alas it is not the day, says the evil programming gods
    As this is all a ruse, just one big long deception,
    Since my terminal froze ten minutes ago, from an UndefinedException
"""

from PyQt5.QtWidgets import *
from PyQt5.Qt import Qt
from PyQt5 import uic
from PyQt5 import QtCore, QtWidgets, QtGui  # Used in the drop down shadows
import sqlite3
import resources
import resources_admin
import sys
import os

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS2
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


# Establish connection with db
dbconn = sqlite3.connect(resource_path('storeDB.db'))
dbcursor = dbconn.cursor()


counter = 0
class splashScreen(QMainWindow):
    def __init__(self):
        print('splash screen...')
        super(splashScreen, self).__init__()
        uic.loadUi(resource_path("screens\\splash_screen.ui"), self)


        # Remove plain window
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        # Drop Shadow
        self.dropShadowFrame.setGraphicsEffect(QtWidgets.QGraphicsDropShadowEffect(blurRadius=6, xOffset=0, yOffset=0,
                                                                              color=QtGui.QColor(234, 221, 186, 180)))

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.progress)
        self.timer.start(50)

        # Change loading status
        QtCore.QTimer.singleShot(0, lambda: self.label_loading.setText('<strong>LOADING DATABASE...</strong>'))
        QtCore.QTimer.singleShot(1500, lambda: self.label_loading.setText('<strong>LOADING USER INTERFACE...</strong>'))
        QtCore.QTimer.singleShot(3000, lambda: self.label_loading.setText('<strong>LOADING... PLEASE WAIT</strong>'))


        self.show()

    def progress(self):
        global counter
        self.progressBar.setValue(counter)

        if counter > 100:
            self.timer.stop()
            self.close()
            self.window = LoginWindow()
            self.window.show()

        counter += 1

class AdminWindow(QMainWindow):
    def __init__(self):
        print('admin panel...')
        super(AdminWindow, self).__init__()
        uic.loadUi(resource_path("screens\\control.ui"), self)
        self.setWindowTitle("billing")

        # Remove outer borders of main screen and leave only the two designed frames
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        # Create drop shadow effect around screen
        self.frame_left.setGraphicsEffect(QtWidgets.QGraphicsDropShadowEffect(blurRadius=30, xOffset=0, yOffset=0,
                                                                              color=QtGui.QColor(234, 221, 186, 180)))
        self.lbl_frame_right.setGraphicsEffect(QtWidgets.QGraphicsDropShadowEffect(blurRadius=30, xOffset=0, yOffset=0,
                                                                             color=QtGui.QColor(234, 221, 186, 180)))

        # Set table column width on main screen
        self.table_inventory.setColumnWidth(0, 200)
        self.table_inventory.setColumnWidth(1, 90)
        self.table_inventory.setColumnWidth(2, 60)

        self.fill_employee()  # fill up employees table
        self.fill_inventory()  # fill up inventory table

        self.addemployee.clicked.connect(self.newemployee)
        self.btn_logout.clicked.connect(self.logout)

    def fill_employee(self):
        dbcursor.execute('SELECT * FROM employees')
        data = dbcursor.fetchall()
        row = 0
        for i in data:
            self.table_employees.insertRow(row)  # Insert a row into the table
            self.table_employees.setItem(row, 0, QTableWidgetItem(str(i[1])))
            self.table_employees.setItem(row, 1, QTableWidgetItem(str(i[2])))
            self.table_employees.setItem(row, 2, QTableWidgetItem(str(i[3])))
            salary = '$' + str(i[4])
            self.table_employees.setItem(row, 3, QTableWidgetItem(salary))
            row += 1

    def fill_inventory(self):
        dbcursor.execute('SELECT name, quantity FROM Inventory')
        data = dbcursor.fetchall()
        row = 0
        for i in data:
            self.table_inventory.insertRow(row)
            self.table_inventory.setItem(row, 0, QTableWidgetItem(str(i[0])))
            self.table_inventory.setItem(row, 1, QTableWidgetItem(str(i[1])))

            # global spinbox
            spinbox = QSpinBox(self.table_inventory)
            spinbox.setObjectName('sb_order_quantity')
            spinbox.setMinimum(1)
            self.table_inventory.setCellWidget(row, 2, spinbox)

            btn_order = QPushButton(self.table_inventory)
            btn_order.setObjectName('btn_order')
            btn_order.setText('order')
            if i[1] < 5:
                btn_order.setStyleSheet('color: white; '
                                        'background-color: rgba(220, 53, 69, 1);'
                                        'border-radius: 10px;'
                                        'font: 10pt "Segoe UI";')
            else:
                btn_order.setStyleSheet('border-radius: 10px;'
                                        'border: 1px solid grey;'
                                        'font: 10pt "Segoe UI";')
            self.table_inventory.setCellWidget(row, 3, btn_order)
            btn_order.clicked.connect(self.order_products)

            row += 1

    def newemployee(self):
        employee_name = self.le_name.text()
        employee_passw = self.le_passw.text()
        employee_position = self.le_position.text()
        employee_salary = self.le_salary.text()

        if employee_name == '' or employee_passw == '' or employee_position == '' or employee_salary == '':
            self.lbl_message.setStyleSheet('color: red')
            self.lbl_message.setText('Please fill out all required fields')
            return None
        else:
            try: employee_salary = int(employee_salary)
            except:
                self.lbl_message.setStyleSheet('color: red')
                self.lbl_message.setText('Recheck salary input')
                return None

            dbcursor.execute('INSERT INTO employees(name, password, position, salary) VALUES(?, ?, ?, ?)',
                             (employee_name, employee_passw, employee_position, employee_salary))
            self.lbl_message.setStyleSheet('color: green')
            self.lbl_message.setText('Employee added!')
            dbconn.commit()
            self.table_employees.setRowCount(0)
            self.fill_employee()

    def order_products(self):
        current_row = self.table_inventory.currentRow()  # When a button is pressed it will lead to its row being active
                                    # and as a result there is no need to extract button name
        item_name = self.table_inventory.item(current_row, 0).text()
        reorder_quantity = self.table_inventory.cellWidget(current_row, 2).value()

        dbcursor.execute('UPDATE Inventory SET quantity=quantity+? WHERE name=?',
                         (reorder_quantity, item_name))
        dbcursor.execute("UPDATE Inventory SET on_order='False' WHERE name=?",
                         (item_name,))
        dbconn.commit()
        self.lbl_message_2.setText('Product Ordered!')

    def logout(self):
        self.close()  # Closes the main window
        self.window = LoginWindow()  # Creates Login Window object
        self.window.show()

class MainWindow(QMainWindow):
    offer = False  # decides whether item to be added is offer or not
    deal_name = ''
    deal_price = ''
    deal_item = ''
    deal_item_quantity = ''
    rowcount = 0  # controls the number of rows in the purchases table and stores index of current row
    complainttext = ''  # the complaint text entered

    def __init__(self):
        print('main window opened...')
        super(MainWindow, self).__init__()
        uic.loadUi(resource_path("screens\\main.ui"), self)
        self.setWindowTitle("billing")

        # Remove outer borders of main screen and leave only the two designed frames
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        # Create drop shadow effect around screen
        self.frame_left.setGraphicsEffect(QtWidgets.QGraphicsDropShadowEffect(blurRadius=30, xOffset=0, yOffset=0,
                                                                              color=QtGui.QColor(234, 221, 186, 180)))
        self.frame_top.setGraphicsEffect(QtWidgets.QGraphicsDropShadowEffect(blurRadius=30, xOffset=0, yOffset=0,
                                                                             color=QtGui.QColor(234, 221, 186, 180)))
        self.stacked_widget.setGraphicsEffect(QtWidgets.QGraphicsDropShadowEffect(blurRadius=30, xOffset=0, yOffset=0,
                                                                             color=QtGui.QColor(234, 221, 186, 180)))

        # Screen Transitions
        self.btn_main.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        self.btn_topoffers.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        self.btn_complaint.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2))

        self.ui_main()  # Establish main page ui

        # Button events of main screen (main billing window)
        self.btn_additem.clicked.connect(self.additems_main)
        self.btn_delitem.clicked.connect(self.delitem_main)
        self.btn_total.clicked.connect(self.gentotal_main)
        self.btn_change.clicked.connect(self.genchange_main)
        self.btn_newbill.clicked.connect(self.newbill_main)
        self.btn_logout.clicked.connect(self.logout)

        # Button events of top offers screen
        self.offer1_add.clicked.connect(self.add_to_bucket_offers)
        self.offer2_add.clicked.connect(self.add_to_bucket_offers)
        self.offer3_add.clicked.connect(self.add_to_bucket_offers)
        self.offer4_add.clicked.connect(self.add_to_bucket_offers)

        # Events of complaint screen
        self.option1.clicked.connect(self.unenablele_complain)
        self.option1.clicked.connect(self.text_complain)
        self.option2.clicked.connect(self.unenablele_complain)
        self.option2.clicked.connect(self.text_complain)
        self.option3.clicked.connect(self.unenablele_complain)
        self.option3.clicked.connect(self.text_complain)
        self.option4.clicked.connect(self.enablele_complain)
        self.option4.clicked.connect(self.text_complain)
        self.btn_submit.clicked.connect(self.submit_complain)

    def enablele_complain(self):
        self.specify.setEnabled(True)
        self.btn_submit.setEnabled(True)

    # This function is created so that the line edit becomes inactive when option has been changed
    def unenablele_complain(self):  # This function is created so that the line edit becomes inactive when option has been changed
        self.specify.setEnabled(False)
        self.specify.setText('')
        self.btn_submit.setEnabled(True)

    # Establish appropriate complaint text which can be added into db
    def text_complain(self):
        option = str(self.sender().objectName())  # Option name which called function
        if option == 'option1':
            self.complainttext = 'Items are consistently out of stock'
        elif option == 'option2':
            self.complainttext = 'Unhelpful customer service'
        elif option == 'option3':
            self.complainttext = 'Items are of bad quality'
        elif option == 'option4':
            self.complainttext = 'Other'
        print(self.complainttext)

    # Submit complaint
    def submit_complain(self):
        if self.complainttext == "Other":
            self.complainttext = self.specify.toPlainText()  # converting text edit, data into normal text

        customer_name = self.le_name.text()
        complaint_date = self.le_date.text()

        if customer_name == '' or complaint_date == '':
            self.lbl_message_3.setText("Please fill all required fields")
            self.lbl_message_3.setStyleSheet('color: red')
        else:
            dbcursor.execute("INSERT INTO Complaint(date, customer_name, detail) VALUES(?, ?, ?)",
                             (complaint_date, customer_name, self.complainttext))
            dbconn.commit()
            self.lbl_message_3.setStyleSheet('color: green')
            self.lbl_message_3.setText("Complaint Submitted. We hope your issue will be resolved soon")

    def ui_main(self):
        # Set table column width on main screen
        self.table_items.setColumnWidth(0, 280)
        self.table_items.setColumnWidth(1, 90)
        self.table_items.setColumnWidth(2, 90)
        self.table_items.setColumnWidth(3, 90)

        # Filling up items combo box on main screenQQQ
        dbcursor.execute('SELECT * FROM Inventory')
        rows = dbcursor.fetchall()
        products = list()
        for row in rows:
            products.append(row[1])
        self.combo_additems.addItems(products)

        # Add Employee Name and counter number from the login screen
        self.lbl_employee_2.setText(str(name))
        self.lbl_counter_2.setText(str(counter))

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Enter:
            self.additems_main()

    # Add items into table
    def additems_main(self):
        addition_required = True  # This variable decides whether a new row will be added or not
        if self.offer == True:
            item_bought = self.deal_name
            unit_price = self.deal_price

            deal_item = self.deal_item
            quantity = self.deal_item_quantity

            dbcursor.execute('SELECT quantity from Inventory WHERE name=?', (deal_item, ))
            original_item_quantity = dbcursor.fetchone()[0]
            if original_item_quantity < quantity:
                self.lbl_message.setText('Offer out of stock!')
                self.lbl_message.setStyleSheet('color: red')
                return None
            else:
                dbcursor.execute("UPDATE Inventory SET quantity=quantity-? WHERE name=?",
                                 (quantity, deal_item))
                dbconn.commit()
                self.lbl_message.setStyleSheet('color: green')
                self.lbl_message.setText('Added to Bucket!')

            dbcursor.execute('SELECT quantity from Inventory WHERE name=?', (deal_item, ))  # This line is executed again to get most recent quantity value
            if dbcursor.fetchone()[0] < 5:  # If items are to be ordered
                dbcursor.execute("UPDATE Inventory SET on_order='True' WHERE name=?",
                                 (deal_item,))
                dbconn.commit()

        else:  # Normal item added through combo box
            item_bought = self.combo_additems.currentText()  # item_bought stores the item in the combo box when 'Add' Button is pressed
            dbcursor.execute("SELECT * FROM Inventory where name=?", (item_bought,))
            data = dbcursor.fetchone()  # Fetches data from database
            unit_price = data[2]
            quantity = data[3]

            if quantity == 0:
                self.lbl_warning.setText("Item out of stock")
                return None  # Exit the function but do not quit the program
            else:
                dbcursor.execute("UPDATE Inventory SET quantity=quantity-1 WHERE name=?",
                                 (item_bought,))  # Decreases quantity of the item by 1 in the DB

            # Re-order Functionality
            if quantity < 5:
                dbcursor.execute("UPDATE Inventory SET on_order='True' WHERE name=?",
                                 (item_bought,))
        dbconn.commit()
        self.lbl_warning.setText("")  # To empty the out-of-stock label

        if self.table_items.item(0, 0) is not None:  # If there are rows already in the database
            total_rows = self.table_items.rowCount()

            for row in range(total_rows):  # Loop over the rows in the table
                item = self.table_items.item(row, 0).text()
                if item != item_bought:
                    continue
                item_quantity = self.table_items.item(row, 1).text()
                new_quantity = int(item_quantity) + 1
                self.table_items.setItem(row, 1, QTableWidgetItem(
                    str(new_quantity)))  # QTableWidgetItem only takes strings
                self.table_items.setItem(row, 3, QTableWidgetItem(str(unit_price * new_quantity)))

                addition_required = False  # There is no need for a new row as quantity has been incremented
                # WARNING: Do not remove the break below...
                break  # This is so that program does not have to execute useless loops and to solve a bug which caused another row of item_bought to appear with quantity 1

        if addition_required is True or self.table_items.item(0, 0) is None:  # If the table is empty or item has not been bought before
            self.table_items.insertRow(self.rowcount)  # Insert a row into the table
            self.table_items.setItem(self.rowcount, 0, QTableWidgetItem(item_bought))
            self.table_items.setItem(self.rowcount, 1, QTableWidgetItem(
                '1'))  # The item will be added the first time so quantity will be one
            self.table_items.setItem(self.rowcount, 2, QTableWidgetItem(str(unit_price)))
            self.table_items.setItem(self.rowcount, 3, QTableWidgetItem(str(unit_price * 1)))

            self.rowcount += 1  # rowcount is incremented by one each time unique new item is bought purchase has its own row
        self.offer = False  # Prepare for next calling of function

    def delitem_main(self):
        current_row = self.table_items.currentRow()  # The currently selected row
        self.table_items.removeRow(current_row)
        self.rowcount -= 1  # This is done so the program can add another item as row count will be confused
                                        # (One row number will be reduced due to deletion)

    def gentotal_main(self):
        # DO NOT REMOVE THE COMMENT BELOW... WILL COME HANDY FOR FUTURE PAINS
        # self.main_btn_delitem.setEnabled(False)  # There is no logic for the delete item button to remain active after total has been generated
        total_rows = self.table_items.rowCount()
        total = 0
        for row in range(total_rows):
            sub_total = self.table_items.item(row, 3).text()
            total = total + int(sub_total)

        self.lbl_total_2.setText(str(total))

    def genchange_main(self):
        try:
            total = float(self.lbl_total_2.text())
            payed = float(self.le_payed.text())
            change = total - payed
        except Exception as error:  # total and payed can be None if the employee presses the enter key before total is generated
            self.lbl_warning.setText("Error in Calculating change!")
            print(error)
            return None

        if payed < total:
            self.lbl_warning.setText("Error in Calculating change!")
        else:
            change = str(change)  # Replace only on strings
            change = change.replace("-", "")  # Remove the minus sign (change is mostly greater than total)
            self.lbl_change_2.setText(change)
            self.lbl_warning.setText("")

    def newbill_main(self):
        self.table_items.setRowCount(0)  # Clears the table
        self.rowcount = 0  # The table will now have 0 rows (Also, so that the program can add the new items easily)

        self.lbl_total_2.clear()
        self.le_payed.clear()
        self.lbl_change_2.clear()
        # self.btn_delitem.setEnabled(True) --> Set true only if delete button is disabled on calculating total

    def logout(self):
        self.close()  # Closes the main window
        self.window = LoginWindow()  # Creates Login Window object
        self.window.show()

    def add_to_bucket_offers(self):
        self.offer = True

        deal = str(self.sender().objectName())  # Object name which called function
        deal_num = deal.split('_')[0][5:6]  # All object had special format in order to know data of which object clicked

        dbcursor.execute('SELECT id, name, contents, price FROM Top_Offers WHERE id=?', (deal_num, ))
        data  = dbcursor.fetchone()
        self.deal_name = data[1]
        self.deal_price = data[3]
        deal_contents = data[2]
        self.deal_item_quantity = int(deal_contents[0:2])
        self.deal_item = deal_contents[3:]  # The starting index is 2 because it has to account for a space in the contents column in the db

        self.additems_main()

class LoginWindow(QMainWindow):
    def __init__(self):
        print('login window opened...')
        # Load ui file from folder
        super(LoginWindow, self).__init__()
        uic.loadUi(resource_path("Screens\\login.ui"), self)
        self.setWindowTitle("billing")

        # Remove outer borders of main screen and leave only the two designed frames
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        # Create drop shadow effect around screen
        self.login_lb_frameleft.setGraphicsEffect(QtWidgets.QGraphicsDropShadowEffect(blurRadius=30, xOffset=0, yOffset=0, color=QtGui.QColor(234, 221, 186, 180)))
        self.login_lb_frameright.setGraphicsEffect(QtWidgets.QGraphicsDropShadowEffect(blurRadius=30, xOffset=0, yOffset=0,color=QtGui.QColor(234, 221, 186, 180)))

        self.login_btn_login.clicked.connect(self.login)
        self.login_btn_admin.clicked.connect(self.adminopen)

    # Allow login function to be called using enter key
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Enter:
            self.login()

    def login(self):
        global name, counter  # to be displayed on main screen

        name = self.login_le_username.text()
        passw = self.login_le_passw.text()
        counter = self.login_le_counter.text()

        dbcursor.execute('SELECT * FROM employees WHERE name=? AND password=? ', (name, passw))
        try:
            rows = dbcursor.fetchone()  # If there is no match in db then row will be none
            if rows is None:  # If inputted data is wrong and there is no match in the db
                print('Incorrect credentials')
                self.login_lbl_warning.setText('Error! Incorrect Credentials')
                return None
            counter = int(counter)
        except ValueError:  # Error in converting counter to integer
            self.login_lbl_warning.setText('Recheck Counter Number')
            return None
        except Exception as error:  # Any error in accessing db
            print(error)
            return None

        if (len(rows) > 0) and (0 < counter < 6):  # See if the input is right (authentication)
            self.login_lbl_warning.setText("")
            print('logged in')
            self.close()  # Closes the previous login window
            self.window = MainWindow()  # Creates main window
            self.window.show()
        else:
            self.login_lbl_warning.setText('Recheck Counter Number')

    def adminopen(self):
        self.close()  # Closes the previous login window
        self.window = AdminWindow()  # Creates main window
        self.window.show()


# Creates login window object
app = QApplication([])
window = splashScreen()
app.exec_()
