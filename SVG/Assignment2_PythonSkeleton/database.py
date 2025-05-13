#!/usr/bin/env python3
from datetime import datetime, date

import psycopg2

#####################################################
##  Database Connection
#####################################################

"""
Connect to the database using the connection string
"""


def openConnection():
    # connection parameters - ENTER YOUR LOGIN AND PASSWORD HERE

    myHost = "127.0.0.1"
    userid = "postgres"
    passwd = ""

    # Create a connection to the database
    conn = None
    try:
        # Parses the config file and connects using the connect string
        conn = psycopg2.connect(
            database="postgres", user=userid, password=passwd, host=myHost  # userid
        )

    except psycopg2.Error as sqle:
        print("psycopg2.Error : " + sqle.pgerror)

    # return the connection to use
    return conn


"""
Validate salesperson based on username and password
"""
conn = openConnection()


def checkLogin(login, password):

    cur = conn.cursor()
    # use sql query also works
    # query_sql="SELECT * FROM check_login(%s, %s)"
    # login=login.lower()
    # cur.execute(query_sql, (login, password))
    # use callproc function
    cur.callproc("check_login", [login.lower(), password])
    result = cur.fetchone()
    # userInfo=[result[0],result[2],result[3]]
    cur.close()
    if result:
        userInfo = [result[0], result[2], result[3]]
        # return Response.success(message="Login Successfully",data=userInfo)
        return userInfo
    else:
        return None
        # return Response.error(message="Login Failed")


"""
    Retrieves the summary of car sales.

    This method fetches the summary of car sales from the database and returns it 
    as a collection of summary objects. Each summary contains key information 
    about a particular car sale.

    :return: A list of car sale summaries.
"""


def getCarSalesSummary():
    cur = conn.cursor()
    # query_sql='''SELECT * FROM get_car_sales_summary()'''
    # cur.execute(query_sql)
    cur.callproc("get_car_sales_summary")
    rows = cur.fetchall()
    summary = []
    for row in rows:
        summary.append(
            {
                "make": row[0],
                "model": row[1],
                "availableUnits": row[2],
                "soldUnits": row[3],
                "soldTotalPrices": row[4],
                "lastPurchaseAt": row[5].strftime("%d-%m-%Y") if row[5] else "",
            }
        )
    cur.close()
    return summary


"""
    Finds car sales based on the provided search string.

    This method searches the database for car sales that match the provided search 
    string. See assignment description for search specification

    :param search_string: The search string to use for finding car sales in the database.
    :return: A list of car sales matching the search string.
"""


def findCarSales(searchString):
    print(
        "Searching car sales using search string: " + searchString
    )  # it returns model name like gx
    cur = conn.cursor()
    pattern = f"%{searchString}%"
    query_sql = """
    select carsaleid,ma.makename,mo.modelname,builtyear,odometer,price,issold,saledate, concat(c.firstname,' ',c.lastname) as Buyer, concat(s.firstname,' ',s.lastname) AS salespersonName  from carsales cs
    left join Customer c on cs.buyerid = c.customerid
    left join Salesperson s on cs.salespersonid=s.username
    inner join Make as ma on cs.makecode =ma.MakeCode
    inner join Model as mo on cs.modelcode =mo.modelcode
        where (ma.makename ILIKE %s OR mo.modelname ILIKE %s or CONCAT(c.firstname, ' ', c.lastname) ILIKE %s OR CONCAT(s.firstname, ' ', s.lastname) ILIKE %s)
        AND (cs.issold = FALSE OR cs.saledate >= CURRENT_DATE - INTERVAL '3 years')
    order by issold,saledate asc,ma.makename asc,mo.modelname asc;"""

    cur.execute(query_sql, (pattern, pattern, pattern, pattern))
    rows = cur.fetchall()
    carsale_list_find = []
    cur.close()
    for row in rows:
        carsale_list_find.append(
            {
                "carsale_id": row[0],
                "make": row[1],
                "model": row[2],
                "builtYear": row[3],
                "odometer": row[4],
                "price": float(row[5]),
                "isSold": row[6],
                "sale_date": row[7].strftime("%d-%m-%Y") if row[7] else "",
                "buyer": row[8],
                "salesperson": row[9],
            }
        )
    return carsale_list_find


"""
    Adds a new car sale to the database.

    This method accepts a CarSale object, which contains all the necessary details 
    for a new car sale. It inserts the data into the database and returns a confirmation 
    of the operation.

    :param car_sale: The CarSale object to be added to the database.
    :return: A boolean indicating if the operation was successful or not.
"""


def addCarSale(makename, modelname, builtYear, odometer, price):
    cur = conn.cursor()
    # search for the valid name of make and model if we can't find any of them then return error
    # invalid cases:
    odometer = int(odometer)
    price = float(price)
    builtYear = int(builtYear)

    if odometer < 0 or price < 0: # Odometer and price must be positive values
        return False

    if builtYear > 2025: # Built year must be before 2026
        return False

    # get makecode
    # makecode = None
    # modelcode = None
    query_makename = (
        ""
    )
    query_makecode = (
        "select MakeCode from Make where lower(makename)=lower(%s) limit 1" # select from Make
    )
    cur.execute(query_makecode, (makename,))
    row = cur.fetchone()
    if row:
        makecode = row[0] # use exist code
    else:
        # new_makecode = makename[:3].upper() # create make code, first 3 letters
        # # insert into new make
        # cur.execute("INSERT INTO Make (Makecode, Makename) VALUES (%s, %s)",(new_makecode, makename))
        # makecode = new_makecode
        return False


    # get model
    query_modelcode = "select ModelCode from Model where lower(Modelname)=lower(%s) limit 1"
    cur.execute(query_modelcode, (modelname,))
    row = cur.fetchone()
    if row:
        modelcode = row[0]
    else:
        # create new model
        # new_modelcode = modelname.lower().replace(' ', '')
        # cur.execute("""
        #     INSERT INTO Model (ModelCode, ModelName, MakeCode)
        #     VALUES (%s, %s, %s)
        #     """, (new_modelcode, modelname, makecode))
        # modelcode = new_modelcode
        return False



    inser_query = """
    insert into carsales (makecode, modelcode, builtYear, odometer, price,issold)
    values (%s, %s, %s, %s, %s,FALSE)
    """
    try:
        cur.execute(inser_query, (makecode, modelcode, builtYear, odometer, price))
        conn.commit()

    except psycopg2.Error as e:
        conn.rollback()
        print("psycopg2.Error : " + str(e))
        return False
    cur.close()
    return True


"""
    Updates an existing car sale in the database.

    This method updates the details of a specific car sale in the database, ensuring
    that all fields of the CarSale object are modified correctly. It assumes that 
    the car sale to be updated already exists.

    :param car_sale: The CarSale object containing updated details for the car sale.
    :return: A boolean indicating whether the update was successful or not.
"""


def updateCarSale(carsaleid, customer, salesperosn, saledate):
    # print(customer, salesperosn, saledate)
    customer = customer.strip()
    salesperosn = salesperosn.strip()
    saledate = saledate.strip()
    # check the saleinfo, check this car is sold or not only the car that not be sold can be update, but i'm not sure
    # whether do this check or not, or we may allowed that the car has been sold to change info
    cur = conn.cursor()
    # check customer is valid
    query_customer = "select CustomerID from Customer where lower(CustomerID)=lower(%s)"
    cur.execute(query_customer, (customer,))
    customerInfo = cur.fetchone()
    if not customerInfo:
        print("The customer is not in the database")
        return False
    customerId = customerInfo[0]
    # check  salesperson is valid
    query_salesperson = (
        "select UserName from Salesperson where lower(UserName)=lower(%s)"
    )
    cur.execute(query_salesperson, (salesperosn,))
    salespersonInfo = cur.fetchone()
    if not salespersonInfo:
        print("The salesperson is not in the database")
        return False
    salespersonID = salespersonInfo[0]
    try:
        input_date = datetime.strptime(saledate, "%Y-%m-%d").date()
    except ValueError:
        print("The date entered is not a valid date")
        return False
    if input_date > date.today():
        print("The sale entered is in the future")
        return False
    # print(customerId,salespersonID,saledate)
    update_query = """
    update CarSales set BuyerID=%s, SalespersonID=%s, SaleDate=%s,IsSold=%s
    where CarSaleID=%s
    """
    try:
        cur.execute(
            update_query, (customerId, salespersonID, input_date, True, carsaleid)
        )
        conn.commit()
    except psycopg2.Error as e:
        conn.rollback()
        print("psycopg2.Error : " + str(e))
        return False
    return True
