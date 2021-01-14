import pandas as pd
import psycopg2
import streamlit as st
import datetime
from configparser import ConfigParser



@st.cache
def get_config(filename='database.ini', section='postgresql'):
    parser = ConfigParser()
    parser.read(filename)
    return {k: v for k, v in parser.items(section)}


def query_db(sql: str):
    # print(f'Running query_db(): {sql}')

    db_info = get_config()

    # Connect to an existing database
    conn = psycopg2.connect(**db_info)

    # Open a cursor to perform database operations
    cur = conn.cursor()

    # Execute a command: this creates a new table
    cur.execute(sql)

    # Obtain data
    data = cur.fetchall()
    
    column_names = [desc[0] for desc in cur.description]

    # Make the changes to the database persistent
    conn.commit()

    # Close communication with the database
    cur.close()
    conn.close()

    df = pd.DataFrame(data=data, columns=column_names)

    return df
def insert_db(sql: str):
    # print(f'Running query_db(): {sql}')

    db_info = get_config()

    # Connect to an existing database
    conn = psycopg2.connect(**db_info)

    # Open a cursor to perform database operations
    cur = conn.cursor()

    # Execute a command: this creates a new table
    cur.execute(sql)

    # Obtain data
    conn.commit()

    # Close communication with the database
    cur.close()
    conn.close()

def Create_Order(product_code,office_code,customer_number,quantity):
     
    current_day = datetime.date.today() 
    formatted_date = datetime.date.strftime(current_day, "%m/%d/%Y")
    
    latest_order_number_sql = 'select MAX(order_number)+1 as order_number from orders;'
    order_number = query_db(latest_order_number_sql).loc[0]
    order_number = order_number['order_number']
    
    insert_order_sql = f"""insert into orders values({order_number},'{formatted_date}','{formatted_date}',{customer_number});"""
    insert_db(insert_order_sql)
    
    get_price_sql = f"""select selling_price from products where product_code = '{product_code}';"""
    price = query_db(get_price_sql).loc[0]
    price = price['selling_price']
    price = float(quantity)*float(price)
    
    insert_order_details_sql = f""" insert into order_details values ({order_number},'{product_code}','{office_code}',{quantity},{price});""" 
    insert_db(insert_order_details_sql)

    query_amt = f"""select sum(price) as amount from order_details where order_number={order_number};"""
    order_amt = query_db(query_amt).loc[0]
    order_amt = float(order_amt['amount'])
    
    updated_quantity_query = f"""select quantity from inventory where office_Code ='{office_code}' and product_code='{product_code}';"""
    updated_quantity = query_db(updated_quantity_query).loc[0]
    updated_quantity = int(updated_quantity['quantity']) - int(quantity)
    
    change_inventory_query = f"""update inventory set quantity = {updated_quantity}
                                where product_code = '{product_code}' and office_code = '{office_code}';"""
    insert_db(change_inventory_query)
    
    
    insert_payments_query = f""" insert into payments values({customer_number},{order_number},'{formatted_date}',{order_amt});"""
    insert_db(insert_payments_query)
    
    st.write(f"this customer {customer_number} ordered this product {product_code} from this office {office_code} in this quantity {quantity} for this price {price}")
    return order_number+1

'## Order Section: Place your order here'

'Identify yourself'
sql_customer_names = 'select firstname from customers;'
customer_names = query_db(sql_customer_names)['firstname'].tolist()
customer_name = st.selectbox('Choose a customer', customer_names, key='order')
if customer_name:
    sql_customer = f"select customer_number from customers where firstname = '{customer_name}';"
    customer_info = query_db(sql_customer).loc[0]
    customer_number = customer_info['customer_number']

'Select Product and Office'
sql_product_names = 'select product_name from products;'
product_names = query_db(sql_product_names)['product_name'].tolist()
product_name = st.selectbox('Choose a product', product_names)
if product_name:
    sql_product = f"select product_code from products where product_name = '{product_name}';"
    product_info = query_db(sql_product).loc[0]
    product_code = product_info['product_code']

    sql_product_details = f"""select p.product_name, o.office_name, p.selling_price, i.quantity as available
                           from products p, offices o, inventory i
                           where i.product_code = '{product_code}' and o.office_code = i.office_code
                           and i.product_code = p.product_code"""
    prod_details = query_db(sql_product_details)
    st.dataframe(prod_details)
    
    'Chose an seller to buy from'
    sql_office_name = f"""select office_name from inventory as i, offices as o 
                          where i.product_code = '{product_code}' 
                          and o.office_code = i.office_code;"""
    office_names = query_db(sql_office_name)['office_name'].tolist()
    office_name = st.selectbox('Choose an office', office_names)
    if office_name:
        sql_office = f"select office_code from offices where office_name = '{office_name}';"
        office_info = query_db(sql_office).loc[0]
        office_code = office_info['office_code']
    quantity = st.number_input("Quantity to order",min_value=0,max_value=100,value=1)
    if st.button("Order and Pay"):
        Create_Order(product_code,office_code,customer_number,quantity)

'## Customer Dashboard'         
'Multiselect: Display amount spent by chosen customers till date'
sql_customer_names = 'select firstname from customers;'
names = query_db(sql_customer_names)['firstname'].tolist()
names_mulsel = st.multiselect('Choose customers', names)
if names_mulsel:
    names_mulsel_str = ','.join(["'" + name + "'" for name in names_mulsel]) 
    sql_customers = f"""select c.firstname, sum(p.amount) as amount_spent from customers c, payments p 
                    where c.firstname in ({names_mulsel_str}) and c.customer_number = p.customer_number 
                    group by c.firstname order by amount_spent desc;"""
    spending_customer = query_db(sql_customers)
    st.dataframe(spending_customer)

'Multiselect: Chose city wise customer spending'
sql_cities = 'select distinct city from customer_addresses;'
cities = query_db(sql_cities)['city'].tolist()
cities_mulsel = st.multiselect('Choose cities', cities)
if cities_mulsel:
    cities_mulsel_str = ','.join(["'" + city + "'" for city in cities_mulsel])
    sql_cities = f"""select ca.city, sum(p.amount) as amount_spent from customers c, payments p, customer_addresses ca 
                    where ca.city in ({cities_mulsel_str}) and c.customer_number = p.customer_number and c.customer_number = ca.customer_number 
                    group by ca.city order by amount_spent desc;"""
    spending_cities = query_db(sql_cities)
    st.dataframe(spending_cities)

'Customer wise order History'
sql_customer_names = 'select firstname from customers;'
customer_names = query_db(sql_customer_names)['firstname'].tolist()
customer_name = st.selectbox('Choose a customer', customer_names, key='dash1')

if customer_name:
    st.write(f"Purchase history for {customer_name}")
    sql_customer = f"select customer_number from customers where firstname = '{customer_name}';"
    customer_info = query_db(sql_customer).loc[0]
    customer_number = customer_info['customer_number']

    sql_purchase_history = f"""select o.order_number,p.product_name as product,sum(od.quantity) as quantity
                                from products p, orders o, order_details od,customers c
                                where o.customer_number = {customer_number}
                                and o.customer_number = c.customer_number
                                and o.order_number = od.order_number
                                and od.product_code = p.product_code
                                group by o.order_number,p.product_name
                                order by o.order_number desc;"""

    purchase_history = query_db(sql_purchase_history)
    st.dataframe(purchase_history)

'## Office Dashboard'
'Best selling products based on offices'
sql_offices = 'select distinct office_name from offices;'
offices = query_db(sql_offices)['office_name'].tolist()
office = st.selectbox('Choose any Office', offices)
if office:
    sql_offices = f"""select o.office_name, p.product_name, sum(od.price) as amount_spent, sum(od.quantity) as total_ordered_quantity from offices o, products p, order_details od 
                    where o.office_name = '{office}' and o.office_code = od.office_code and od.product_code = p.product_code
                    group by o.office_name, p.product_name 
                    order by amount_spent desc;"""
    spending_offices = query_db(sql_offices)
    st.dataframe(spending_offices)

'Performance of Offices'

sql_office_perf = """select o.office_name, sum(od.price) revenue
                    from offices o,order_details od,products p
                    where  o.office_code = od.office_code
                    and od.product_code = p.product_code
                    group by o.office_code,o.office_name
                    order by revenue desc; """

office_performance = query_db(sql_office_perf)
st.dataframe(office_performance)
bfo = office_performance.head(1) # best performing office
wfo = office_performance.tail(1) # worst performing office

st.write(f"The best performaing office is {bfo['office_name'].iloc[0]} with a revenue of {bfo['revenue'].iloc[0]}")
st.write(f"The worst performaing office is {wfo['office_name'].iloc[0]} with a revenue of {wfo['revenue'].iloc[0]}")

'# Need Help?'

'Contact Store for any help needed'
sql_office_names = 'select office_name from offices;'
office_names = query_db(sql_office_names)['office_name'].tolist()
office_name = st.selectbox('Choose an office to contact', office_names, key='order')
if office_name:
    info_query = f"""select e.firstname firstname,e.lastname lastname,
                        e.email,e.job_title,o.office_name,o.phone,
                        oa.office_address, oa.city,oa.stat,oa.country,oa.postal_code
                    from offices o, office_addresses oa,employees e
                    where o.office_name = '{office_name}'
                    and o.office_code = oa.office_code
                    and e.office_code = o.office_code;
                    """
    info = query_db(info_query).loc[0]
    st.write(f"Contact Name: {info['lastname']} {info['firstname']}")
    st.write(f"Store Number: {info['phone']}")
    st.write(f"Contact Email: {info['email']}")
    st.write(f"Position: {info['job_title']}")
    st.write(f"Address:{info['office_address']} {info['city']} {info['stat']} {info['country']} {info['postal_code']}")