import mysql.connector
from mysql.connector import errorcode, MySQLConnection, CMySQLConnection
from mysql.connector.cursor_cext import CMySQLCursor

from modules import global_vars


def connectToDatabase(firstConnect=False):
    """
    Connect to the database with given data

    Parameters
    ---------------

    firstConnect: bool
        Indicates whether the connection is the first one to be made. First connections run additional
        table creation queries and validate the process.

    Raises
    ---------------
    db: CMySQLConnection
        The access was denied, login and/or password does not match

    db: CMySQLConnection
        The connection was not successful. Error reason is provided

    cursor: CMySQLCursor
        Table creation queries could not be processed. The reason for error is provided

    Returns
    ----------------
    db: CMySQLConnection
        Object of MySQL database connection. Opened and operating

    cursor: CMySQLCursor
        Object of MySQL database cursor. Needed for query processing
    """
    try:
        db = mysql.connector.connect(
            host='localhost', user='root', password='', database="employee_safety_system")
    except mysql.connector.Error as error:
        if error.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            raise ConnectionError(
                "Connection was not successful. The access was denied. Recheck the login and password.")
        else:
            raise ConnectionError(
                "Cannot establish connection. Reason: %s" % error)
    else:
        cursor = db.cursor(buffered=True)
        if firstConnect:
            try:
                cursor.execute(
                    "CREATE TABLE IF NOT EXISTS accounts (id INT NOT NULL auto_increment PRIMARY KEY, "
                    "login VARCHAR(128), password VARCHAR(64), name VARCHAR(128), "
                    "type INT, creationDate INT, lastLogin INT);")
                cursor.execute(
                    "CREATE TABLE IF NOT EXISTS pswdResets (id INT NOT NULL auto_increment PRIMARY KEY, userID INT "
                    "NOT NULL, code VARCHAR(8), initDate INT, expDate INT, USED INT);")
                cursor.execute(
                    "CREATE TABLE IF NOT EXISTS workplaces (id INT NOT NULL auto_increment PRIMARY KEY, userID INT "
                    "NOT NULL, name VARCHAR(64), position INT, state_activation BOOLEAN, state_notifications BOOLEAN);"
                )
                cursor.execute(
                    "CREATE TABLE IF NOT EXISTS logs (id INT NOT NULL auto_increment PRIMARY KEY,"
                    "workplaceID INT NOT NULL, cameraID INT NOT NULL, alertReason VARCHAR(64), alertAction VARCHAR(64),"
                    "date DATETIME, seen BOOLEAN DEFAULT 0);"
                )
                cursor.execute(
                    """CREATE TABLE IF NOT EXISTS rooms (
                    ID int(11) NOT NULL auto_increment PRIMARY KEY,
                    x1 float NOT NULL,
                    y1 float NOT NULL,
                    x2 float NOT NULL,
                    y2 float NOT NULL,
                    name varchar(20),
                    generated_id int(11) NOT NULL,
                    floor INT(2) NOT NULL,
                    workspace_id INT(5) NOT NULL
                    )"""
                )
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS cameras (
                    ID int(11) NOT NULL auto_increment PRIMARY KEY,
                    x1 float NOT NULL,
                    y1 float NOT NULL,
                    name varchar(20) COLLATE utf8_polish_ci NOT NULL,
                    generated_id int(11) NOT NULL,
                    rules VARCHAR(16) NOT NULL DEFAULT '',
                    actions VARCHAR(16) NOT NULL DEFAULT '',
                    floor INT(2) NOT NULL,
                    workspace_id INT(5) NOT NULL
                    )"""
                               )

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS doors (
                    ID int(11) NOT NULL auto_increment PRIMARY KEY,
                    x1 float NOT NULL,
                    y1 float NOT NULL,
                    x2 float NOT NULL,
                    y2 float NOT NULL,
                    generated_id int(11) NOT NULL,
                    floor INT(2) NOT NULL,
                    workspace_id INT(5) NOT NULL
                    )"""
                               )
            except mysql.connector.Error as error:
                raise TimeoutError("Cannot process query. Reason: %s" % error)
        return db, cursor


def closeDatabaseConnection(db: CMySQLConnection, cursor: CMySQLCursor):
    """
    Closes connection to the database. Ensures closing of both handles; db and cursor

    Parameters
    -----------------
    db: CMySQLConnection
        Handle of database
    cursor: CMySQLCursor
        Handle of cursor - executive power

    Raises
    -----------------
    db: CMySQLConnection, cursor: CMySQLCursor
        Closing the connection not possible. Maybe the connection was never opened?
    """
    try:
        db.close()
        cursor.close()
    except mysql.connector.Error as error:
        raise Exception(
            "Couldn't close connection. Maybe it is closed already or was never opened? Reason: %s" % error)


def checkIsEmailInDatabase(recoveryEmail):
    """
    Checks whether the provided E-mail address is located within the database.

    Return value
    ---------------------
    True: bool
        If address was found
    False: bool
        Otherwise
    """
    db, cursor = connectToDatabase()
    cursor.execute("SELECT * FROM accounts WHERE login=%s", (recoveryEmail,))
    results = cursor.fetchone()
    closeDatabaseConnection(db, cursor)
    if results is not None:
        return True
    else:
        return False


def setNewPassword(password):
    """
    Updates user's password after he successfully managed to input verification code

    Params
    ------------------
    password: str
        New password provided by the user
    """
    db, cursor = connectToDatabase()
    cursor.execute("UPDATE accounts SET password=%s WHERE id=%s",
                   (password, global_vars.userID))
    db.commit()
    closeDatabaseConnection(db, cursor)


def insertNewWorkplace(name, notifications_status):
    db, cursor = connectToDatabase()
    cursor.execute("INSERT INTO workplaces VALUES(null, %s, %s, 1, 1, %s);", (global_vars.userID, name,
                                                                              1 if notifications_status else 0))
    db.commit()
    closeDatabaseConnection(db, cursor)
