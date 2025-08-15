statistics.py

store_name
location_long
location_lat
product_group
product_brand
product_name
sales_volume
date_of_manufacture
date_of_expiry
product_price
status                  omborda tovar bor yoki yo'qligini bildiradi

duration_of_expiry
discount
discount_percentage
discount_price
last_status
ultra_discount_percentage
ultra_discount




ZAPROSLAR:
1. generate a huge amount of data and save to csv file that columns name are :store_name location_long location_lat product_group product_brand product_name sales_volume date_of_manufacture date_of_expiry product_price status (yes or no).  Some columns value get data from this : FOOD PRODUCT GROUP
    1. Dairy Products
    * Products: Milk, yogurt, kefir, cheese, cottage cheese, cream, butter
    * Brands: Nestlé, Danone, Parmalat, President, Amul, Campina
    2. Bakery Products
    * Products: Wheat flour, pasta, bread, biscuits, noodles, buns
    * Brands: Barilla, Makfa, Ozon, Pioner, Yashkino
    3. Meat Products
    * Products: Beef, lamb, poultry, sausage, hot dogs, smoked meat
    * Brands: Tyson, Oscar Mayer, Hormel, Perdue, Cherkizovo
    4. Beverages
    * Products: Mineral water, carbonated drinks, juices, tea, coffee
    * Brands: Coca-Cola, Pepsi, Nestlé Pure Life, Lipton, Nescafé
    5. Sweets
    * Products: Chocolate, candies, cakes, ice cream, halva, jam
    * Brands: Mars, Ferrero, Milka, Nestlé, Roshen



2. 
    i need to advanced analysis with machine learning models and create new columns for the following:
    1. duration_of_expiry -- date_of_manufacture - date_of_expiry
    2. discount -- yes or no
    3. discount_percentage -- this coluumns need to use from machine leaarning model like, it depends of sales_volume, discount. if discount == yes discount_percentage get value else get zero. if sales_volume is greater than some value then discount_percentage shold be high. this columns should be generated from machine learning model.
    4. discount_price -- this depends on product_price and discount_percentage. get value of percentege of product_price
    5. last_status -- this columns depends on status (havening product in store),  duration_of_expiry -- if status column have yes and duration_of_expiry less than zero then last_status should be "yes" else "no"
    6. ultra_discount_percentage -- this columns depends on discount_percentage, if discount_percentage is greater than some value then ultra_discount_percentage should be discount_percentage else zero
    7. ultra_discount -- this columns depends on product_price and ultra_discount_percentage. get value of percentege of ultra_discount_percentage

3. 
    write a streamlit code that include in advanced plotting analysis that full data form. this potting include in 1. total statistics, 2. plotting by any filters, 3.  

    full process and advanced plotting with threshold of Advanced Analysis with Machine Learning for Store Data.
