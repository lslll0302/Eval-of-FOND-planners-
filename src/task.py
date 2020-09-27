import pandas as pd
import os 
import glob
import re

#import mysql.connector
#from mysql.connector import Error
from utils import get_project_root



problems_sum = []
root_path = get_project_root()
fpath=str(root_path)+'/benchmarks/' 


folder_name=os.listdir(fpath)
folder_name.sort()

#this file is help users to decide 1.which domain 2.how many problems 3.which planner 4.how many cpus
cpu_max = 4
#1.prp 2.sat
planners = [[1,2],
            ['prp','sat']]

domain_indexs=[]
domain_names=[]
prob_start_points = []
prob_end_points = []
chosed_planners = []


def listdir(path, char_, list_name):  
    
    for file in os.listdir(path):
        file_path = os.path.join(path, file)
        if os.path.isdir(file_path):
            listdir(file_path, list_name)
                
        elif os.path.splitext(file_path)[1] == '.pddl':
            f_name=os.path.splitext(file_path)[0]
            f_name=os.path.split(f_name)[1]
            if char_ in f_name:
                list_name.append(file_path)
            
	                  

                
 
def save_file_path_to_csv():
    domain_path=[]
    problem_path=[]
    listdir(path,'d',domain_path)
    listdir(path,'p',problem_path)
    domain_path.sort()
    problem_path.sort()
    
    problems_sum.append(len(problem_path))
    csv_list = [domain_path, problem_path]

    df = pd.DataFrame(csv_list)
    df=df.T
    df.columns=['domain_path','problem_path']
    df.index += 1 
    df.to_csv(str(root_path)+'/Database/path/'+folder_name[i]+'.csv', index_label='index')

    #print(df)

def save_folder_to_csv():  
    csv_list = [folder_name, problems_sum]
    df = pd.DataFrame(csv_list)
    df=df.T
    df.columns=['domain_name','problem_size']
    df.index += 1 
    df.to_csv(str(root_path)+'/Database/benchmarks.csv', index_label='index')

    #print(df)  



def get_range(input_range,show_str):
    regex1 = re.compile('\d+')  
    regex2 = re.compile('\d+-\d+')   
    
    while True:
        list_s1=[]
        list_s2=[]
        list_sum = []   
        try:
            input_str = input(show_str) 
            #domain_str = input('Please chose which domain you want to test:\n0.All'+'\nFrom range'+' 1-'+ str(rowcount)+'\n')               
                
            list_s2 = regex2.findall(input_str)
            for s in list_s2:
                input_str=input_str.replace(s,'')
                s_=[]
                s_=regex1.findall(s)
                if(int(s_[0])<= int(s_[1])):
                    a=int(s_[0])
                    b=int(s_[1])
                else:
                    a=int(s_[1])
                    b=int(s_[0])
                for i in range(a,b+1):
                    list_sum.append(i)    
                
            list_s1 = regex1.findall(input_str)

            for s in list_s1:
                #if the input include 0, return all domains
                if(int(s)==0):
                    if(isinstance(input_range, int)):
                        list_sum = []
                        for i in range(1,input_range+1):   
                            list_sum.append(i)
                    elif(isinstance(input_range, list)):
                        list_sum = input_range
                    break
                #else, return selected domains
                else:
                    list_sum.append(int(s))

            #remove duplicates elements in list
            list_sum = list(set(list_sum))
            #check selected domains in range
            if(isinstance(input_range, int)):
                if list_sum[-1] in range(1,input_range+1) and list_sum[0] in range(1,input_range+1):                               
                    break
            elif(isinstance(input_range, list)):
                if (set(list_sum).issubset(set(input_range))):                               
                    break
        except (ValueError):
            pass
        print('Wrong input vaule!')
        continue
    return list_sum

#get the index of which domain users want to test
def get_domain_index(rowcount):
    show_str=('Please chose which domain you want to test:\n'+
              '0.All\n'+
              'a,b-c.From range'+' 1-'+ str(rowcount)+' select a,b-c domains\n')
    return get_range(rowcount,show_str)
    


#get the problem size of all domains
def get_prob_size(domain_idxs, prob_sizes, domain_namess):
    new_domain_idxs=[]
    prob_sp=[]
    prob_ep=[]
    show_str = ('Please select problems range for testing:\n'+ 
                '0.All problems for all selected domains\n'+
                'a,b-c.All problems for selected a,b-c domains'+ ', custom specific problems range for remaining domains\n')
    domain_prob_all =  get_range(domain_idxs,show_str)

    for d in domain_prob_all:
        new_domain_idxs.append(d)
        prob_sp.append(1)
        #print(domain_prob_all)
        #print(prob_sizes)
        prob_ep.append(prob_sizes[domain_idxs.index(d)])
        #print(prob_ep)
    domain_prob_spec = list(set(domain_idxs)-set(domain_prob_all))

    show_str1 = ('Please select problems range for testing:\n'+
                 '0.All problems for selected domain\n'+
                 'a,b-c.Custom specific problems range for selected domain\n')

    
    for d in domain_prob_spec:
        prob_size=[]
        print('\n',d,'  ', domain_namess[domain_idxs.index(d)],'   size:', prob_sizes[domain_idxs.index(d)])
        prob_size = get_range(int(prob_sizes[domain_idxs.index(d)]),show_str1)
        new_domain_idxs.append(d)
        prob_sp.append(prob_size[0])
        for p in prob_size:
            if(prob_size.index(p) == len(prob_size)-1):
                prob_ep.append(p)
            elif(prob_size[prob_size.index(p)+1]-p != 1):
                prob_ep.append(p)
                prob_sp.append(prob_size[prob_size.index(p)+1])
                new_domain_idxs.append(d)

    return new_domain_idxs, prob_sp, prob_ep

     
    
#get which planner users want to test 
def get_planner( d, s, e ):
    d_= []
    s_= []
    e_= []
    show_str = ('\nPlease select one planner for testing:\n 1.prp\n 2.sat\n'+
                 '0.All planners\n'+
                 'a,b-c.Select specific planners\n')
    select_planners = get_range(planners[0],show_str)
    planners_=[]

    for planner_id in select_planners:
        for i in d:
            planners_.append(planners[1][planners[0].index(planner_id)])  
        d_ = d_+ d
        s_ = s_+ s
        e_ = e_+ e
    return planners_, d_, s_, e_
    
    

#end program
def check_end():
    while True:
        try:
            input_num = int(input('\nHave you finished entering data?\n 1.Yes\n 2.No, I wish to contiune\n'))
            if input_num in range(1,3):  
                if input_num == 1:
                    return True
                else: 
                    return False             
                break
        except (ValueError):
            pass
        print('Wrong input vaule!')
        continue
    return False  
    
#the online mysql host      
'''  
host="den1.mysql6.gear.host",
      user="benchmarks",
      password="Mx9G0h8q?9W_"  
'''  
    
#the local mysql host        
'''             
try:  
    connection = mysql.connector.connect(host='localhost',
                                         database='planning_benchmarks',
                                         user='root',
                                         password='2747')

    sql_select_Query = "select * from benchmarks"
    cursor = connection.cursor()
    cursor.execute(sql_select_Query)
    records = cursor.fetchall() 
    print('MySQL connection is started...')
    print("Total number of domains in benchmarks is: ", cursor.rowcount)   
    mat = "{:1}\t{:28}\t{:1}" 
      
    while True:  
        print(mat.format('\nIndex','Domain name', '#inst'))
        for row in records:       
            print(mat.format(row[0], row[1], row[2]))
          
        domain_index = get_domain_index(cursor.rowcount)    
        domain_indexs.append(domain_index)

        for row in records:   
            if (row[0] == domain_index):
                domain_names.append(row[1])
                inst_size = row[2]    
   
        prob_start_point = get_prob_start_point(inst_size) 
        if prob_start_point == 0:
            prob_start_point = 1
            prob_end_point = row[2]
        else:    
            prob_end_point = get_prob_end_point(prob_start_point, inst_size)
            
        prob_start_points.append(prob_start_point)
        prob_end_points.append(prob_end_point)
        
        planner_id = get_planner()
        chosed_planners.append(planners[planner_id-1])
        
        
        if check_end():
            task_name=input('Please enter a task name for saving your task data into a csv file:\n')
            break
        
except Error as e:
    print("Error reading data from MySQL table", e)
finally:
    if (connection.is_connected()):
        connection.close()
        cursor.close()
        print("MySQL connection is closed")
'''

#update database before create task
for i in range(len(folder_name)):
    path='benchmarks/'+folder_name[i]+'/'   
    os.chdir(root_path)
    save_file_path_to_csv()

save_folder_to_csv()


#create task
#the virtual database in local
while True:
    bm = pd.read_csv(str(root_path) +'/Database/benchmarks.csv') 
    print('\n') 
    print(bm.to_string(index=False))
    
    domain_indexs = get_domain_index(len(bm)) 
    domain_names_ = []
    problem_sizes_ = []
    print('Selected domains are:', domain_indexs, '\n')   

    
    for i in domain_indexs:
        domain_names_.append(bm['domain_name'][i-1])
        problem_sizes_.append(bm['problem_size'][i-1] )


    prob_start_points_=[]
    prob_end_points_=[]

    (domain_indexs,prob_start_points_,prob_end_points_) = get_prob_size(domain_indexs, problem_sizes_, domain_names_)
    
    

    (chosed_planners_,domain_indexs,prob_start_points_,prob_end_points_)  = get_planner(domain_indexs, prob_start_points_,prob_end_points_)
    chosed_planners = chosed_planners + chosed_planners_

    for i in domain_indexs:
        domain_names.append(bm['domain_name'][i-1])
    prob_start_points = prob_start_points + prob_start_points_
    prob_end_points = prob_end_points + prob_end_points_

    
    if check_end():
        task_name=input('Please enter a task name(exclude ".csv") for saving your task data into a csv file:\n')
        break            
                


#write task data into csv
csv_list = [ domain_names, prob_start_points, prob_end_points, chosed_planners]
csv_list = [[row[i] for row in csv_list] for i in range(len(csv_list[0]))]

df = pd.DataFrame(csv_list, columns=[ 'domain_name', 'start_problem', 'end_problem', 'planner'])
df.index += 1 
df.to_csv(str(root_path)+'/src/task/'+task_name+'.csv', index_label='index')

print(df)
















