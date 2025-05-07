import subprocess


def main():
    """
    This is the generator code. It should take in the MF structure and generate the code
    needed to run the query. That generated code should be saved to a 
    file (e.g. _generated.py) and then run.
    """

    # body = """
    # for row in cur:
    #     if row['quant'] > 10:
    #         _global.append(row)
    # """

    body = """
    # S = ['cust', 'prod', 'sum_1_quant', 'count_2_quant']
    # n = 2
    # V = ['cust', 'prod']
    # F = ['sum_1_quant', 'count_2_quant']
    # sigma = ["1.state=NJ", "2.state=NY"]
    # # G = None

    # S = ['cust', 'prod', 'max_1_quant', 'sum_1_quant', 'count_2_quant', 'avg_3_quant']
    # F = ['max_1_quant', 'sum_1_quant', 'count_2_quant', 'avg_3_quant']

    S = ['cust', 'prod', 'avg_1_quant', 'avg_2_quant', 'avg_3_quant']
    n = 2
    V = ['cust', 'prod']
    F = ['avg_1_quant', 'avg_2_quant', 'avg_3_quant']
    sigma = ["1.state=NJ", "2.state=NY", "3.state=CT"]
    # G = None
    G = 'avg_1_quant > avg_2_quant and avg_3_quant > avg_2_quant and avg_1_quant > avg_3_quant'
    # G = 'avg_1_quant > avg_2_quant'

    #Example to copy and paste for user input
    # S = cust,prod,avg_1_quant,avg_2_quant
    # n = 2
    # V = cust,prod
    # F = avg_1_quant,avg_2_quant
    # sigma = 1.state=NJ,2.state=NY
    # G = avg_1_quant > avg_2_quant

    input_type = 'txt_file'

    if input_type == 'User':
        S = input('Input S clause in form of: s1,s2,etc: ').split(',')
        n = int(input('Input n value: '))
        V = input('Input group by attributes in form of: gb1,gb2,etc: ').split(',')
        F = input('Input F aggregate functions in form of: avg_1_quant,avg_2_quant,etc: ').split(',')
        sigma = input('Input sigma grouping conditions in form of: 1.state=NJ,2.st=NY: ').split(',')
        G = input('Input having clause as single string in form of: avg_1_quant > avg_2_quant or avg_2_quant > avg_3_quant: ')

    elif input_type == 'txt_file':
        f = open('q1.txt', 'r')
        S = f.readline().strip().split(',')
        n = int(f.readline().strip())
        V = f.readline().strip().split(',')
        F = f.readline().strip().split(',')
        sigma = f.readline().strip().split(',')
        G = f.readline().strip()
    
    else: #default query if don't want to do user input or read from file
        S = ['cust', 'prod', 'avg_1_quant', 'avg_2_quant', 'avg_3_quant']
        # S = ['cust', 'prod', 'avg_1_quant']
        n = 2
        V = ['cust', 'prod']
        F = ['avg_1_quant', 'avg_2_quant', 'avg_3_quant']
        # F = ['avg_1_quant']
        sigma = ["1.state=NJ", "2.state=NY", "3.state=CT"]
        # sigma = ["1.state=NJ"]
        G = 'avg_1_quant > avg_2_quant and avg_3_quant > avg_2_quant and avg_1_quant > avg_3_quant'
        # G = None
        
    #MF-Struct initialization (Dictionary)
    mf_struct = {}
    avg_dict = {}
    for row in cur:
        gb_attr = row[V[0]]
        for i in range(1, n):
            gb_attr += '_' + row[V[i]]
        
        for sig in sigma:
            sig_split = [sig.split('.')[0]] + sig.split('.')[1].split('=')

            for f in F:
                f_split = f.split('_')
                if f_split[1] == sig_split[0] and row[sig_split[1]] == sig_split[2]:
                
                    if (gb_attr) in mf_struct:
                    
                        if f_split[0] == 'sum':
                            mf_struct[gb_attr][f] += row['quant']
                        if f_split[0] == 'count':
                            mf_struct[gb_attr][f] += 1
                        if f_split[0] == 'min':
                            if mf_struct[gb_attr][f] > row['quant']:
                                mf_struct[gb_attr][f] = row['quant']
                        if f_split[0] == 'max':
                            if mf_struct[gb_attr][f] < row['quant']:
                                mf_struct[gb_attr][f] = row['quant']
                        if f_split[0] == 'avg':

                            if gb_attr in avg_dict:
                                if f in avg_dict[gb_attr]:
                                    avg_dict[gb_attr][f]['sum'] += row['quant']
                                    avg_dict[gb_attr][f]['count'] += 1
                                else:
                                    avg_dict[gb_attr][f] = {'sum':row['quant'], 'count':1}
                            else:
                                avg_dict[gb_attr] = {f: {'sum':row['quant'], 'count':1}}
                                
                            mf_struct[gb_attr][f] = avg_dict[gb_attr][f]['sum'] / avg_dict[gb_attr][f]['count']
                
                    else:
                    #if group by attribute is not in mf_struct, add it
                        mf_struct[gb_attr] = {(agg if (agg[0:3] == 'sum') or (agg[0:3] == 'avg') or (agg[0:3] == 'min') or (agg[0:3] == 'max') else agg):(row['quant'] if (agg[0:3] == 'sum') or (agg[0:3] == 'avg') or (agg[0:3] == 'min') or (agg[0:3] == 'max') else 1) for agg in F}
                        if f_split[0] == 'avg':
                            avg_dict[gb_attr] = {f: {'sum':row['quant'], 'count': 1}}

            
    
    #used for having clause
    def check(g1, operator, g2, row):
        if operator == '<': return row[g1] < row[g2]
        if operator == '>': return row[g1] > row[g2]
        if operator == '<=': return row[g1] <= row[g2]
        if operator == '>=': return row[g1] >= row[g2]
        if operator == '=': return row[g1] == row[g2]
        if operator == '!=': return row[g1] != row[g2]
    
    #having clause handling
    if G is not None:        
        g_split = G.split(' ')
    else: 
        g_split = ''

    tmp_mf = {}
    if len(g_split) != 0:
        g1 = g_split[0]
        comp = g_split[1]
        g2 = g_split[2]

        for key, value in mf_struct.items():
            if check(g1, comp, g2, value):
                tmp_mf[key] = value

        for i in range(3, len(g_split), 4):
            
            and_or = g_split[i]
            g1 = g_split[i+1]
            comp = g_split[i+2]
            g2 = g_split[i+3]

            if and_or == 'or':
                for key, value in mf_struct.items():
                    if check(g1, comp, g2, value):
                        tmp_mf[key] = value
            if and_or == 'and':
                for i in list(tmp_mf):
                    if check(g1, comp, g2, tmp_mf[i]) and i in tmp_mf:
                        continue
                    else:
                        tmp_mf.pop(i)
                    
        mf_struct = tmp_mf
        
    mf_struct = dict(sorted(mf_struct.items()))
                        
    #prepare mf_struct for output
    for key, value in mf_struct.items():
        key_split = key.split("_")
        new_row = []
        for i in range(n):
            new_row.append(key_split[i])
        for key2, value2 in value.items():
            new_row.append(value2)
        _global.append(new_row)

    """


    # Note: The f allows formatting with variables.
    #       Also, note the indentation is preserved.
    tmp = f"""
import os
import psycopg2
import psycopg2.extras
import tabulate
from dotenv import load_dotenv

# DO NOT EDIT THIS FILE, IT IS GENERATED BY generator.py

def query():
    load_dotenv()

    user = os.getenv('USER')
    password = os.getenv('PASSWORD')
    dbname = os.getenv('DBNAME')
    user = 'postgres'

    conn = psycopg2.connect("dbname="+dbname+" user="+user+" password="+password, port = 5433,
                            cursor_factory=psycopg2.extras.DictCursor)
    cur = conn.cursor()
    cur.execute("SELECT * FROM sales")
    
    _global = []
    {body}
    
    # return tabulate.tabulate(_global,
    #                     headers="keys", tablefmt="psql")

    return tabulate.tabulate(_global,
                        headers=S, tablefmt="psql")
    
def main():
    print(query())
    
if "__main__" == __name__:
    main()
    """

    # Write the generated code to a file
    open("_generated.py", "w").write(tmp)
    # Execute the generated code
    subprocess.run(["python", "_generated.py"])


if "__main__" == __name__:
    main()
