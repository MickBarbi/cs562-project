import os
import psycopg2
import psycopg2.extras
import tabulate
from dotenv import load_dotenv

q1 = """with nj as (
select cust, prod, avg(quant) as avg_1_quant
from sales
where state = 'NJ'
group by cust, prod
),

ny as (
select cust, prod, avg(quant) as avg_2_quant
from sales
where state = 'NY'
group by cust, prod
), 

ct as (
select cust, prod, avg(quant) as avg_3_quant
from sales
where state = 'CT'
group by cust, prod
)

select * from nj natural join ny natural join ct
where avg_1_quant > avg_2_quant and avg_3_quant > avg_2_quant and avg_1_quant > avg_3_quant
order by cust,prod
"""

q2 = """
with feb as (
select cust, state, sum(quant) as sum_1_quant, count(quant) as count_1_quant
from sales
where month = 2
group by cust, state
),

april as (
select cust, state, max(quant) as max_2_quant
from sales
where month = 4
group by cust, state
)

select * from feb natural join april
order by cust,state
"""

q3 = """
with nj as (
select cust, year, avg(quant) as avg_1_quant, min(quant) as min_1_quant
from sales
where state = 'NJ'
group by cust, year
),

eighteenth as (
select cust, year, max(quant) as max_2_quant
from sales
where day = 18
group by cust, year
)

select cust, year, avg_1_quant, max_2_quant, min_1_quant from nj natural join eighteenth
order by cust,year
"""

q4 = """
with april as (
select prod, cust, year, avg(quant) as avg_1_quant
from sales
where month = 4
group by prod, cust, year
),

june as (
select prod, cust, year, sum(quant) as sum_2_quant
from sales
where month = 6
group by prod, cust, year
)

select * from april natural join june
order by prod,cust,year
"""

q5 = """
with nj as (
select cust, prod, sum(quant) as sum_1_quant, count(quant) as count_1_quant
from sales
where state = 'NJ'
group by prod, cust
),

twentysixteen as (
select cust, prod, min(quant) as min_2_quant, max(quant) as max_2_quant
from sales
where year = 2016
group by prod, cust
),

ny as (
select cust, prod, avg(quant) as avg_3_quant
from sales
where state = 'NY'
group by prod, cust
)

select * from nj natural join twentysixteen natural join ny
where count_1_quant > min_2_quant and max_2_quant > avg_3_quant
order by cust,prod
"""

def query():
    """
    Used for testing standard queries in SQL.
    """
    load_dotenv()

    user = os.getenv('USER')
    password = os.getenv('PASSWORD')
    dbname = os.getenv('DBNAME')
    
    user = 'postgres'

    conn = psycopg2.connect("dbname="+dbname+" user="+user+" password="+password, port = 5433,
                            cursor_factory=psycopg2.extras.DictCursor)
    cur = conn.cursor()
    # cur.execute("SELECT * FROM sales WHERE quant > 10")
    cur.execute(q5)
    
    return tabulate.tabulate(cur.fetchall(),
                             headers="keys", tablefmt="psql")


def main():
    print(query())


if "__main__" == __name__:
    main()
