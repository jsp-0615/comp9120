DROP TABLE IF EXISTS Make;
DROP TABLE IF EXISTS Model;
DROP TABLE IF EXISTS Salesperson;
DROP TABLE IF EXISTS Customer;
DROP TABLE IF EXISTS CarSales;

CREATE TABLE Salesperson (
    UserName VARCHAR(10) PRIMARY KEY,
    Password VARCHAR(20) NOT NULL,
    FirstName VARCHAR(50) NOT NULL,
    LastName VARCHAR(50) NOT NULL,
	UNIQUE(FirstName, LastName)
);

INSERT INTO Salesperson VALUES 
('jdoe', 'Pass1234', 'John', 'Doe'),
('brown', 'Passwxyz', 'Bob', 'Brown'),
('ksmith1', 'Pass5566', 'Karen', 'Smith');

CREATE TABLE Customer (
    CustomerID VARCHAR(10) PRIMARY KEY,
    FirstName VARCHAR(50) NOT NULL,
    LastName VARCHAR(50) NOT NULL,
    Mobile VARCHAR(20) NOT NULL
);

INSERT INTO Customer VALUES 
('c001', 'David', 'Wilson', '4455667788'),
('c899', 'Eva', 'Taylor', '5566778899'),
('c199',  'Frank', 'Anderson', '6677889900'),
('c910', 'Grace', 'Thomas', '7788990011'),
('c002',  'Stan', 'Martinez', '8899001122'),
('c233', 'Laura', 'Roberts', '9900112233'),
('c123', 'Charlie', 'Davis', '7712340011'),
('c321', 'Jane', 'Smith', '9988990011'),
('c211', 'Alice', 'Johnson', '7712222221');

CREATE TABLE Make (
    MakeCode VARCHAR(5) PRIMARY KEY,
    MakeName VARCHAR(20) UNIQUE NOT NULL
);

INSERT INTO Make VALUES ('MB', 'Mercedes Benz');
INSERT INTO Make VALUES ('TOY', 'Toyota');
INSERT INTO Make VALUES ('VW', 'Volkswagen');
INSERT INTO Make VALUES ('LEX', 'Lexus');
INSERT INTO Make VALUES ('LR', 'Land Rover');

CREATE TABLE Model (
    ModelCode VARCHAR(10) PRIMARY KEY,
    ModelName VARCHAR(20) UNIQUE NOT NULL,
    MakeCode VARCHAR(10) NOT NULL,  
    FOREIGN KEY (MakeCode) REFERENCES Make(MakeCode)
);

INSERT INTO Model (ModelCode, ModelName, MakeCode) VALUES
('aclass', 'A Class', 'MB'),
('cclass', 'C Class', 'MB'),
('eclass', 'E Class', 'MB'),
('camry', 'Camry', 'TOY'),
('corolla', 'Corolla', 'TOY'),
('rav4', 'RAV4', 'TOY'),
('defender', 'Defender', 'LR'),
('rangerover', 'Range Rover', 'LR'),
('discosport', 'Discovery Sport', 'LR'),
('golf', 'Golf', 'VW'),
('passat', 'Passat', 'VW'),
('troc', 'T Roc', 'VW'),
('ux', 'UX', 'LEX'),
('gx', 'GX', 'LEX'),
('nx', 'NX', 'LEX');

CREATE TABLE CarSales (
  CarSaleID SERIAL primary key,
  MakeCode VARCHAR(10) NOT NULL REFERENCES Make(MakeCode),
  ModelCode VARCHAR(10) NOT NULL REFERENCES Model(ModelCode),
  BuiltYear INTEGER NOT NULL CHECK (BuiltYear BETWEEN 1950 AND EXTRACT(YEAR FROM CURRENT_DATE)),
  Odometer INTEGER NOT NULL,
  Price Decimal(10,2) NOT NULL,
  IsSold Boolean NOT NULL,
  BuyerID VARCHAR(10) REFERENCES Customer,
  SalespersonID VARCHAR(10) REFERENCES Salesperson,
  SaleDate Date
);

INSERT INTO CarSales (MakeCode, ModelCode, BuiltYear, Odometer, Price, IsSold, BuyerID, SalespersonID, SaleDate) VALUES
                 ('MB', 'cclass', 2020, 64210, 72000.00, TRUE, 'c001', 'jdoe', '2024-03-01'),
                 ('MB', 'eclass', 2019, 31210, 89000.00, FALSE, NULL, NULL, NULL),
                 ('TOY', 'camry', 2021, 98200, 37200.00, TRUE, 'c123', 'brown', '2023-12-07'),
                 ('TOY', 'corolla', 2022, 65000, 35000.00, TRUE, 'c910', 'jdoe', '2024-09-21'),
                 ('LR', 'defender', 2018, 115000, 97000.00, FALSE, NULL, NULL, NULL),
                 ('VW', 'golf', 2023, 22000, 33000.00, TRUE, 'c233', 'jdoe', '2023-11-06'),
                 ('LEX', 'nx', 2020, 67000, 79000.00, TRUE, 'c321', 'brown', '2025-01-01'),
                 ('LR', 'discosport', 2021, 43080, 85000.00, TRUE, 'c211', 'ksmith1', '2021-01-27'),
                 ('TOY', 'rav4', 2019, 92900, 48000.00, FALSE, NULL, NULL, NULL),
                 ('MB', 'aclass', 2022, 47000, 57000.00, TRUE, 'c199', 'jdoe', '2025-03-01'),
                 ('LEX', 'ux', 2023, 23000, 70000.00, TRUE, 'c899', 'brown', '2023-01-01'),
                 ('VW', 'passat', 2020, 63720, 42000.00, FALSE, NULL, NULL, NULL),
                 ('MB', 'eclass', 2021, 12000, 155000.00, TRUE, 'c002', 'ksmith1', '2024-10-01'),
                 ('LR', 'rangerover', 2017, 60000, 128000.00, FALSE, NULL, NULL, NULL),
                 ('TOY', 'camry', 2025, 10, 49995.00, FALSE, NULL, NULL, NULL),
                 ('LR', 'discosport', 2022, 53000, 89900.00, FALSE, NULL, NULL, NULL),
                 ('MB', 'cclass', 2023, 55000, 82100.00, FALSE, NULL, NULL, NULL),
                 ('MB', 'aclass', 2025, 5, 78000.00, FALSE, NULL, NULL, NULL),
                 ('MB', 'aclass', 2015, 8912, 12000.00, TRUE, 'c199', 'jdoe', '2020-03-11'),
                 ('TOY', 'camry', 2024, 21000, 42000.00, FALSE, NULL, NULL, NULL),
                 ('LEX', 'gx', 2025, 6, 128085.00, FALSE, NULL, NULL, NULL),
                 ('MB', 'eclass', 2019, 99220, 105000.00, FALSE, NULL, NULL, NULL),
                 ('VW', 'golf', 2023, 53849, 43000.00, FALSE, NULL, NULL, NULL),
                 ('MB', 'cclass', 2022, 89200, 62000.00, FALSE, NULL, NULL, NULL);

-- stored procedures

-- functions.sql

DROP FUNCTION IF EXISTS check_login(character varying,character varying);
-- Function to validate salesperson login
CREATE OR REPLACE FUNCTION check_login(input_username VARCHAR(10), input_password VARCHAR(20))
RETURNS TABLE(username VARCHAR(10), password VARCHAR(20), firstname VARCHAR(50), lastname VARCHAR(50)) AS $$
BEGIN
    RETURN QUERY
    select
        Salesperson.username,
        Salesperson.password,
        Salesperson.firstname,
        Salesperson.lastname
    from Salesperson
    where LOWER(Salesperson.username)=LOWER(input_username) and Salesperson.password=input_password;
END;
$$ LANGUAGE plpgsql;

DROP FUNCTION IF EXISTS get_car_sales_summary();
-- Function to get car sales summary
CREATE OR REPLACE FUNCTION get_car_sales_summary()
RETURNS TABLE(
    make VARCHAR(10),
    model VARCHAR(10),
    availableUnits INTEGER,
    soldUnits INTEGER,
    soldTotalPrices NUMERIC,
    lastPurchaseAt DATE
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        ma.makename AS make,
        mo.modelname AS model,
        SUM(CASE WHEN issold=FALSE THEN 1 ELSE 0 END)::INTEGER AS availableUnits,
        SUM(CASE WHEN issold=TRUE THEN 1 ELSE 0 END)::INTEGER AS soldUnits,
        SUM(CASE WHEN issold=TRUE THEN price ELSE 0 END)::NUMERIC AS soldTotalPrices,
        MAX(CASE WHEN issold = TRUE THEN saledate ELSE NULL END) AS lastPurchaseAt
    from Model as mo
    left join Make as ma on mo.makecode =ma.MakeCode
    left join carsales as c on c.modelcode =mo.modelcode
    GROUP BY ma.makename, mo.modelname
    ORDER BY ma.makename asc, mo.modelname asc;
END;
$$ LANGUAGE plpgsql;



-- Example:

-- Check login
-- SELECT * FROM check_login('jdoe', 'Pass1234');

-- Get car sales summary
-- SELECT * FROM get_car_sales_summary();

