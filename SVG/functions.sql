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

