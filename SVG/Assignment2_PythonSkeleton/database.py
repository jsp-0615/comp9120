#!/usr/bin/env python3
from datetime import datetime, date

import psycopg2
from response import Response
#####################################################
##  Database Connection
#####################################################

'''
Connect to the database using the connection string
'''
def openConnection():
    # connection parameters - ENTER YOUR LOGIN AND PASSWORD HERE

    myHost = "127.0.0.1"
    userid = "postgres"
    passwd = "0615..jsp."
    
    # Create a connection to the database
    conn = None
    try:
        # Parses the config file and connects using the connect string
        conn = psycopg2.connect(database="usyd_25s1",#userid
                                    user=userid,
                                    password=passwd,
                                    host=myHost)

    except psycopg2.Error as sqle:
        print("psycopg2.Error : " + sqle.pgerror)
    
    # return the connection to use
    return conn

'''
Validate salesperson based on username and password
'''
conn = openConnection()
def checkLogin(login, password):

    cur = conn.cursor()
    query_sql="select * from Salesperson where LOWER(username)=LOWER(%s) and password=%s"
    login=login.lower()
    cur.execute(query_sql, (login, password))
    result=cur.fetchone()
    userInfo=[result[0],result[2],result[3]]
    cur.close()
    if result:
        # return Response.success(message="Login Successfully",data=userInfo) 我想要的写法
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
    query_sql='''select makecode as make,modelcode as model,
           SUM(CASE WHEN issold=FALSE THEN 1 else 0 END) as availableUnits,
           SUM(CASE WHEN issold=True THEN 1 else 0 END) as soldUnits,
           SUM(CASE WHEN issold=True THEN price else 0 END) as soldTotalPrices,
           MAX(CASE WHEN issold = TRUE THEN saledate ELSE NULL END) AS lastPurchaseAt
    from carsales
    group by makecode, modelcode
    order by makecode,modelcode;'''
    cur.execute(query_sql)
    rows=cur.fetchall()
    summary=[]
    for row in rows:
        summary.append({
            "make": row[0],
            "model": row[1],
            "availableUnits": row[2],
            "soldUnits": row[3],
            "soldTotalPrices": row[4],
            "lastPurchaseAt": row[5].strftime("%d-%m-%Y") if row[5] else "",
        })
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
    print("Searching car sales using search string: " + searchString)# it returns model name like gx
    cur = conn.cursor()
    pattern = f"%{searchString}%"
    query_sql='''
    select carsaleid,makecode,modelcode,builtyear,odometer,price,issold,saledate, concat(c.firstname,' ',c.lastname) as Buyer, concat(s.firstname,' ',s.lastname) AS salespersonName  from carsales cs
    left join Customer c on cs.buyerid = c.customerid
    left join Salesperson s on cs.salespersonid=s.username
        where (cs.modelcode ILIKE %s OR cs.makecode ILIKE %s or CONCAT(c.firstname, ' ', c.lastname) ILIKE %s OR CONCAT(s.firstname, ' ', s.lastname) ILIKE %s)
        AND (cs.issold = FALSE OR cs.saledate >= CURRENT_DATE - INTERVAL '3 years')
    order by issold,saledate asc,makecode,modelcode;'''

    cur.execute(query_sql, (pattern,pattern,pattern,pattern))
    rows=cur.fetchall()
    carsale_list_find=[]
    cur.close()
    for row in rows:
        carsale_list_find.append({
            "carsale_id": row[0],
            "make": row[1],
            "model": row[2],
            "builtYear": row[3],
            "odometer": row[4],
            "price": float(row[5]),
            "isSold": row[6],
            "sale_date": row[7].strftime("%d-%m-%Y") if row[7] else "",
            "buyer": row[8],
            "salesperson": row[9]
        })
    return carsale_list_find

"""
    Adds a new car sale to the database.

    This method accepts a CarSale object, which contains all the necessary details 
    for a new car sale. It inserts the data into the database and returns a confirmation 
    of the operation.

    :param car_sale: The CarSale object to be added to the database.
    :return: A boolean indicating if the operation was successful or not.
"""
def addCarSale(make, model, builtYear, odometer, price):
    cur = conn.cursor()
    # search for the valid name of make and model if we can't find any of them then return error
    query_makecode="select MakeCode from Model where lower(MakeCode)=lower(%s) limit 1"
    cur.execute(query_makecode, (make,))
    row=cur.fetchone()
    if not row:
        return False
    makecode=row[0]
    query_modelcode="select ModelCode from Model where lower(ModelCode)=lower(%s) or lower(ModelName) =lower(%s)  limit 1"
    cur.execute(query_modelcode, (model,model))
    row=cur.fetchone()
    if not row:
        return False
    modelcode=row[0]
    query_vaildation="select * from Model where MakeCode=%s and ModelCode=%s"
    cur.execute(query_vaildation,(makecode,modelcode))
    row=cur.fetchone()
    if not row:
        print("The model and make are not the paired")
        return False
    if int(odometer) < 0 or int(price) < 0:
        return False
    inser_query='''
    insert into carsales (makecode, modelcode, builtYear, odometer, price,issold)
    values (%s, %s, %s, %s, %s,FALSE)
    '''
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
    customer=customer.strip()
    salesperosn=salesperosn.strip()
    saledate=saledate.strip()
    #check the saleinfo, check this car is sold or not only the car that not be sold can be update, but i'm not sure
    #whether do this check or not, or we may allowed that the car has been sold to change info
    cur = conn.cursor()
    # check customer is valid
    query_customer="select CustomerID from Customer where lower(CustomerID)=lower(%s)"
    cur.execute(query_customer, (customer,))
    customerInfo=cur.fetchone()
    if not customerInfo:
        print("The customer is not in the database")
        return False
    customerId=customerInfo[0]
    #check  salesperson is valid
    query_salesperson='select UserName from Salesperson where lower(UserName)=lower(%s)'
    cur.execute(query_salesperson, (salesperosn,))
    salespersonInfo=cur.fetchone()
    if not salespersonInfo:
        print("The salesperson is not in the database")
        return False
    salespersonID=salespersonInfo[0]
    try:
        input_date=datetime.strptime(saledate, "%Y-%m-%d").date()
    except ValueError:
        print("The date entered is not a valid date")
        return False
    if input_date > date.today():
        print("The sale entered is in the future")
        return False
    # print(customerId,salespersonID,saledate)
    update_query='''
    update CarSales set BuyerID=%s, SalespersonID=%s, SaleDate=%s,IsSold=%s
    where CarSaleID=%s
    '''
    try:
        cur.execute(update_query, (customerId, salespersonID, input_date,True,carsaleid))
        conn.commit()
    except psycopg2.Error as e:
        conn.rollback()
        print("psycopg2.Error : " + str(e))
        return False
    return True
