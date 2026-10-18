#DQN 学习指标增长型，开始的状态很容易区分。结束的状态不加空闲任务的格式
#有的话，任务结束的时刻进行判定，任务还可以分为只在时隙开始的时候进入执行队列，也可以分为在上一个任务结束后即可进入执行队列
#开始的时候进入执行队列。先执行这一版
import numpy as np
import random
import math
import queue
import sys
import pandas as pd
import json
import numpy as np
import tensorflow._api.v2.compat.v1 as tf
tf.disable_v2_behavior()
import json
import time
import os
os.environ["PATH"] += ";C:/Program Files/Graphviz/bin/"  
#任务大小是不一样的，所以不同的任务数量可以是表征系统状态的重要指标，
#全是5
#1：都在2以上
#2：都在2或2以下
#3;单执行器


NUM_EPISODE = 10000   #迭代的轮次数量 

n_iot = 4    #本地iot设备的处理能力
n_edge = 2   # 边缘服务器的数量
n_cloud = 1  #云服务器的数量
n_time = 10000  #总时隙数量，n_time * n_task_type为总的任务数量。
#n_task_type = 10
n_task_type = 10
n_no_task = 50
#max_delay = [3.5,7,3.5,3.5,3.5,3.5,3.5,3.5,3.5,3.5]    #各任务的最大截止时间 本地调试
max_delay = [6,6,6,6,6,6,6,6,6,6]     #各任务的最大截止时间  8.27从全是5变为
#task_size = [8106834,4878218,7080040,6273736,4392825, 4961446, 5418728, 5946748, 6273736,  7361044, 7862095, 8106834]   #各类型任务的数据大小
task_size = [8.106834 - 1,8.106834, 8.106834 + 1, 8.106834 + 2, 8.106834 + 3,
             8.106834 + 4, 8.106834 + 5, 8.106834 + 6, 8.106834 + 7, 8.106834 + 8]
#{'function_id': 2, 'data_size': 5038265.983670799, 'cpu_cycle': 831908888.9697027}
task_cpu_cycle_count = [2.39864428 + 3-0.5, 2.39864428 + 3-1, 
                        2.39864428 + 3-2, 2.39864428 + 3+0.5,  
                        2.39864428 + 3+1, 2.39864428 + 3+2, 
                        2.39864428 + 3-0.5, 2.39864428 + 3-1,  
                        2.39864428 + 3+0.5, 2.39864428 + 3+1]
keep_alive = [2,2.5,1.5,1,2.5,3,2.5,4,1.5,2] #
#keep_alive = [x * 1.8 for x in keep_alive]
#keep_alive = [40,   40.5,  30.5,  30,  40.50,  70,  40.5,  60,  30.5,  40]
#comp_cap_iot = 1.5e9 * np.ones(n_iot) /2.8          #本地iot设备的处理能力
comp_cap_iot = 1.5 * np.ones(n_iot)              # 0.8657628533333334
#comp_cap_edge = 3.8e10 * np.ones([n_edge]) #/3.68190       #各个边缘设备的处理能力
comp_cap_edge = 5.8 * np.ones([n_edge])          # 0.3417484947368421 + 0.9007593333333332      1.2425078280701753
#comp_cap_cloud = 4.45e11 * np.ones([n_cloud]) #/1.23086    #各个云设备的处理能力
comp_cap_cloud = 12.45 * np.ones([n_cloud])      # 0.2918301752808989   + 1.1259491666666666     1.4177793419475655

esc = 1e-27

pull_uplink_rate_iot =   14.000000 / 1.8 #/2         # 本地iot 设备拉取容器镜像的能力
pull_uplink_rate_edge =  24.000000 / 1.8  #/2.5         # 边缘 设备拉取容器镜像的能力
pull_uplink_rate_cloud = 50.000000 / 1.8 #/2.5         # 云 设备拉取容器镜像的能力
tran_edge_cap_iot = 8.000000 * np.ones([n_iot, n_edge]) #*2/3         0.9007593333333332       # 本地iot 设备向边缘设备传输任务的速率    
tran_cloud_cap_iot = 8.000000 / 1.19 * np.ones([n_iot, n_cloud])  #*2/3   1.1259491666666666    1.4177793419475655  # 本地iot 设备向云设备传输任务的速率 

edge_cps = 0.01 * 5      #边缘计算单价
cloud_cps = 0.002 * 3    #云计算单价
edge_request = 6e-3      #边缘的价格比云端更贵，其他方面优于云端
cloud_request = 2e-2      # 云计算请求收费

tr_power = 0.005  #执行能耗要大于传输能耗

n_actions = 1 + n_edge + n_cloud
#n_features =  1 + 1 * 10 + 1 * 10 + n_edge * 10 + n_cloud * 10
#n_features = 1 + 1  + 1  + n_edge  + n_cloud * n_task_type + 1 * n_task_type + n_edge * n_task_type + n_cloud * n_task_type
n_features_task = (1+      #  id 即优先级          task[iot_index][0][0]['function_id']
                   #1+      #  到达时间             task[iot_index][0][0]['到达时间']
                   1+      #  size  任务大小       task[iot_index][0][0]['data_size'] 
                   1+      #  cpu_cycle           task[iot_index][0][0]['cpu_cycle']
                   1+      #  max_delay           max_delay[task[iot_index][0][0]['function_id']]
                   1       #  keep_alive          keep_alive[task[iot_index][0][0]['function_id']]
                   )      
n_features_system_iot = (n_task_type+     #  n_task_type个任务，还有多少个未执行， all_task_wait_iot_comp_count[iot_index][n_task_type_index]    0,0,0,...,0
                     n_task_type +        #   n_task_type类，每类待执行的任务数量   per_task_wait_iot_comp_count_cpu_cycle[iot_index][n_task_type_index]  0*'cpu_cycle',0*'cpu_cycle',0*'cpu_cycle',...,0*'cpu_cycle'
                     n_task_type+     #  n_task_type个任务，还有多少个未传输，   all_task_wait_iot_tran_count[iot_index][n_task_type_index]     0,0,0,...,0
                     n_task_type+     #   n_task_type种任务的未传输的分量：     per_task_wait_iot_tran_count_size[iot_index][n_task_type_index]                                  0*'data_size',0*'data_size',0*'data_size',...,0*'data_size'
                     n_task_type +          #  n_task_type 个函数 代码剩余的保留时间：最大为2，没有负值   iot_pool[iot_index][n_task_type_index]
                     1+            # n_task_type种任务的未执行的总量：  all_task_wait_iot_comp_cpu_cycle[iot_index]      0*'cpu_cycle'+0*'cpu_cycle'+0*'cpu_cycle'+...+0*'cpu_cycle'
                     1+            #执行器还剩余多少没有执行                   task_on_process_local[iot_index]['remain']
                     1+                # n_task_type种任务的未传输的总量：       all_task_wait_iot_tran_size[iot_index]     0*'data_size'+0*'data_size'+0*'data_size'+...+0*'data_size'
                     1+                #传输执行器还有多少任务没有传输           task_on_transmit_local[iot_index]['remain']
                     1 +                  #   拉取函数代码的能力
                     1+                   #   本地计算能力
                     n_edge+              #    本地向边缘  的传输能力
                     n_cloud             #    本地向云  的传输能力
                     )
n_features_system_edge =(1+               #   拉取函数代码的能力
                        1+                #   边缘计算能力
                        1+                   #  n_task_type类任务还未执行的待执行总量     all_task_wait_edge_comp_size_cpu_cycle[iot_index][edge_index]                     0*'cpu_cycle'+0*'cpu_cycle'+0*'cpu_cycle'+...+0*'cpu_cycle'
                        1+                   #  执行器还剩余多少没有执行                   task_on_process_edge[iot_index][edge_index]['remain']
                        n_task_type +        #  n_task_type类任务还未执行的每类任务的数量  all_task_wait_edge_comp_count[iot_index][edge_index][n_task_type_index]       0,0,0,...,0
                        n_task_type+         #  n_task_type类任务还未执行的每类任务的数量  per_task_wait_edge_comp_count_cpu_cycle[iot_index][edge_index][n_task_type_index]        0*'cpu_cycle',0*'cpu_cycle',0*'cpu_cycle',...,0*'cpu_cycle'
                        n_task_type          #     n_task_type 个函数 代码剩余的保留时间： edge_pool[edge_index][n_task_type_index]
                        )
n_features_system_cloud = ( 1 +            #   拉取函数代码的能力
                          1 +               #   云计算能力
                          1+                  #  n_task_type类任务还未执行的待执行总量      all_task_wait_cloud_comp_size_cpu_cycle[iot_index][cloud_index] 0*'cpu_cycle'+0*'cpu_cycle'+0*'cpu_cycle'+...+0*'cpu_cycle'
                          1+                  #  执行器还剩余多少没有执行               task_on_process_cloud[iot_index][cloud_index]['remain']
                          n_task_type +        #  n_task_type类任务还未执行的每类任务的数量 all_task_wait_cloud_comp_count[iot_index][cloud_index][n_task_type_index]       0,0,0,...,0
                          
                          n_task_type+        #                                       per_task_wait_cloud_comp_count_cpu_cycle[iot_index][cloud_index][n_task_type_index]                 0*'cpu_cycle',0*'cpu_cycle',0*'cpu_cycle',...,0*'cpu_cycle'
                          n_task_type          #     n_task_type 个函数 代码剩余的保留时间：cloud_pool[cloud_index][n_task_type_index]
                          )
n_features_task_results = (1+               #时间，等待传输时延
                           1+               # 传输时延
                           1+               # 等待执行时延
                           1+               # 冷启动时延
                           1+               #执行时延
                           1+               #能耗 
                           1+               #花销
                           1+               #成功标志
                            1)              #冷启动标志
                           
n_features_system_other = (1+      #历史滑动窗口内的  平均任务成功数量
                           1+       #历史滑动窗口的  平均任务执行时间
                           1)      #历史滑动窗口获得的 平均奖励
#n_features = n_features_task +n_features_system_iot + n_features_system_edge * n_edge + n_features_system_cloud * n_cloud + n_features_task_results
n_features = (n_features_task +n_features_system_iot 
              + n_features_system_edge * n_edge 
              + n_features_system_cloud * n_cloud     #+1
              )
# 5 + 11 + 6 * 2 + 6
#print("n_features",n_features,n_features_task , n_features_system_edge , n_edge , n_features_system_cloud , n_cloud)

#待执行队列：
Queue_iot_comp = list()
Queue_iot_tran = list()
Queue_edge_comp = list()
Queue_cloud_comp = list()

for iot in range(n_iot):
    Queue_iot_comp.append(queue.Queue())
    Queue_iot_tran.append(queue.Queue()) 
    Queue_edge_comp.append(list()) 
    Queue_cloud_comp.append(list())
    for edge in range(n_edge):
        Queue_edge_comp[iot].append(queue.Queue())
    for cloud in range(n_cloud): 
        Queue_cloud_comp[iot].append(queue.Queue())

#待执行总量
all_task_wait_iot_comp_cpu_cycle = np.zeros(n_iot)
all_task_wait_iot_tran_size = np.zeros(n_iot)
all_task_wait_edge_comp_size_cpu_cycle = np.zeros([n_iot, n_edge])
all_task_wait_cloud_comp_size_cpu_cycle = np.zeros([n_iot, n_cloud])
#各设备各类型待执行任务的数量，初始时全为0
all_task_wait_iot_comp_count = np.zeros([n_iot,n_task_type])
all_task_wait_iot_tran_count = np.zeros([n_iot,n_task_type])
all_task_wait_iot_tran_edge_count = np.zeros([n_iot,n_edge])
all_task_wait_edge_comp_count = np.zeros([n_iot, n_edge,n_task_type])
all_task_wait_cloud_comp_count = np.zeros([n_iot, n_cloud,n_task_type])

per_task_wait_iot_comp_count_cpu_cycle = np.zeros([n_iot,n_task_type])
per_task_wait_iot_tran_count_size = np.zeros([n_iot,n_task_type])
per_task_wait_edge_comp_count_cpu_cycle = np.zeros([n_iot, n_edge,n_task_type])
per_task_wait_cloud_comp_count_cpu_cycle = np.zeros([n_iot, n_cloud,n_task_type])

# 执行器
task_on_process_local = list()       
task_on_transmit_local = list()
task_on_process_edge = list() 
task_on_process_cloud = list() 
for iot in range(n_iot):
    task_on_process_local.append({'function_id': -1,'data_size': 0,
                                  'cpu_cycle': 0, 'task_arrive_time': 0,
                                  'flag': 0,'critical_value':0, 'max_delay':0,
                                  'remain': 0})
    task_on_transmit_local.append({'function_id': -1,'data_size': 0,
                                   'cpu_cycle': 0, 'task_arrive_time': 0,                         
                                                'edge_logs': 0, 'cloud': 0, 'max_delay':0,
                                                'remain': 0,'iot_action':0})
    
    task_on_process_edge.append(list())
    task_on_process_cloud.append(list())  
    for edge in range(n_edge):
        task_on_process_edge[iot].append({'function_id': -1,'data_size': 0,
                                          'cpu_cycle': 0, 'task_arrive_time': 0,
                                          'tran_finish_time':0,'max_delay':0,
                                          'flag': 0,'critical_value':0,'remain': 0})
    for cloud in range(n_cloud):
        task_on_process_cloud[iot].append({'function_id': -1,'data_size': 0,
                                           'cpu_cycle': 0, 'task_arrive_time': 0,
                                           'tran_finish_time':0,'max_delay':0,
                                           'flag': 0,'critical_value':0,'remain': 0})
   


t_iot_comp = np.zeros([n_iot,n_task_type])       #每个iot设备为不同任务设置执行器，每个执行器匹配对应的设备的处理能力
t_iot_tran = np.zeros([n_iot,n_task_type])
#b_edge_comp = np.zeros([n_iot, n_edge])
b_edge_comp = np.zeros([n_edge,n_task_type])
#b_cloud_comp = np.zeros([n_iot, n_cloud])
b_cloud_comp = np.zeros([n_cloud,n_task_type])

#记录上次服务器调用功能函数的具体时间
iot_pool = np.zeros([n_iot, n_task_type]) #- np.ones
edge_pool = list()
for edge_index in range(n_edge):
    edge_pool.append(np.zeros([n_iot, n_task_type]))
cloud_pool = list()
for cloud_index in range(n_cloud):
    cloud_pool.append(np.zeros([n_iot, n_task_type]))
#max_value = np.max(test[0][:, column_index])     np.max(edge_pool[edge_index][:, n_task_type])

weight_1 =1#2.5   #时间成本的权重
weight_2=18#0.015   # 能耗成本的权重
weight_3=180#5      #  花销成本的权重
weight_4=0.2    #  容器冷启动时间成本的权重


def reward(iot_id,j_time,type_id,time,energy,money,unfinish_indi):
    #iot = int(iot_id)  #用户优先级
    max_energy = 0
    max_expense = 0
    t_id = int(type_id)
    max_delay_task = task[iot_id][j_time][0]['max_delay']
    
    if type_id != -1:
        #低优先级的任务 reward =  20 * np.exp(-2 * time / max_delay[t_id]) +40 * t_id 
        if unfinish_indi == 0:
            reward1 = 20 * np.exp(-2 * time / max_delay_task) +40 * t_id 
            
            #reward1 = 20 * np.exp(-2 * time / max_delay_task) +40 * t_id 
            
            # # reward = -5 * np.exp(-2 * time / max_delay_task) 
            # - (20 * np.exp(-2 * 0 / max_delay_task) * (t_id+1) +40 * t_id) -10*(t_id + 失败序号+1)
        else:
            reward1 = -5 * np.exp(-2 * time / max_delay_task) - (20 * np.exp(-2 * 0 / max_delay_task) * (t_id+1) +40 * t_id) -10*(t_id + unfinish_indi+1)
    else:
        print("当前任务是无效任务，但却要计算获得的奖励",iot_id,j_time,type_id)
    #计算花费的系统成本    
    reward2 = weight_1 * time + weight_2 * energy + money * weight_3 #+cold_start_delay * weight_4
    #print("reward1 , reward2",reward1 , reward2,reward1 - reward2)
    reward = reward1  - reward2   #/ 10
    #print(reward,reward1 , reward2,type_id)
    #reward = reward1
    return reward
reward_list_record = []
delay_list_record = []
delay_avg_list_record = []
energy_list_record = []
expense_list_record = []
energy_avg_list_record = []
expense_avg_list_record = []
unfinish_total_list_record = []
unfinish_total_list_record0 = []             #成功
unfinish_total_list_record1 = []            # 等待传输失败
unfinish_total_list_record2 = []            #传输失败
unfinish_total_list_record3 = []            #等待执行失败
unfinish_total_list_record4 = []            #冷启动失败
unfinish_total_list_record5 = []            #执行失败
utilization_ratio_record = []                  # 记录每个时隙的带宽利用率。
loss_list_record = []                               # 记录训练过程中的损失值。
action_record_iot = []                             # 记录每个时隙智能体的决策。
action_record_edge = [] 
action_record_cloud = [] 
choose_action_by_random = []
choose_action_by_net = []
slot_bandwidth_record = []
cold_count_list_record = []
warm_count_list_record = []
unfinish_indi_record = []
sucess_count_list_record = []

action = []
choose_action_way = []
reward_list = []
delay_list = []
energy_list = []
expense_list = []
unfinish_indi = []
cold_count_list = []
wait_trans_process_delay = []
transing_process_delay = []
wait_comp_process_delay = []
cold_start_delay = []
computing_process_delay = []
history_observation = []
for i in range(n_iot):
        action.append(-np.ones([n_time,1]))
        choose_action_way.append(-np.ones([n_time,1]))
        reward_list.append(np.zeros([n_time,1]))
        delay_list.append(np.zeros([n_time,1]))
        energy_list.append(np.zeros([n_time,1]))
        expense_list.append(np.zeros([n_time,1]))
        unfinish_indi.append(-np.ones([n_time,1]))
        cold_count_list.append(-np.ones([n_time,1]))
        wait_trans_process_delay.append(np.zeros([n_time,1]))
        transing_process_delay.append(np.zeros([n_time,1]))
        wait_comp_process_delay.append(np.zeros([n_time,1]))
        cold_start_delay.append(np.zeros([n_time,1]))
        computing_process_delay.append(np.zeros([n_time,1]))  
        history_observation.append(np.zeros([n_time,1], dtype=object))

#之前的观察值很容易获得，之后的观察值，怎么获取相应的观察值呢？
#需要执行一个任务，任务执行后状态发生改变，读取任务的状态吗？
#运行结束的当前时隙的状态。可能多个任务的观察值有相同的当前时隙状态。


def reset():
    
    global Queue_iot_comp, Queue_iot_tran,Queue_edge_comp,Queue_cloud_comp
    global all_task_wait_iot_comp_cpu_cycle,all_task_wait_iot_tran_size,all_task_wait_edge_comp_size_cpu_cycle ,all_task_wait_cloud_comp_size_cpu_cycle 
    global all_task_wait_iot_comp_count,all_task_wait_iot_tran_count ,all_task_wait_iot_tran_edge_count,all_task_wait_edge_comp_count ,all_task_wait_cloud_comp_count 
    global per_task_wait_iot_comp_count_cpu_cycle ,per_task_wait_iot_tran_count_size ,per_task_wait_edge_comp_count_cpu_cycle ,per_task_wait_cloud_comp_count_cpu_cycle 

    global task_on_process_local ,task_on_transmit_local ,task_on_process_edge ,task_on_process_cloud 
    global t_iot_comp, t_iot_tran, b_edge_comp, b_cloud_comp,iot_pool,edge_pool,cloud_pool
    global action,reward_list,delay_list,energy_list,expense_list,unfinish_indi,cold_count_list,wait_trans_process_delay
    global transing_process_delay,wait_comp_process_delay,cold_start_delay,computing_process_delay ,history_observation,reward_indicator
    t_iot_comp = np.zeros([n_iot,n_task_type])
    t_iot_tran = np.zeros([n_iot,n_task_type])
    #b_edge_comp = np.zeros([n_iot, n_edge])
    b_edge_comp = np.zeros([n_edge,n_task_type])
    #b_cloud_comp = np.zeros([n_iot, n_cloud])
    b_cloud_comp = np.zeros([n_cloud,n_task_type])  
    global action,choose_action_way,reward_list,delay_list,energy_list,expense_list,unfinish_indi,cold_count_list,wait_trans_process_delay
    global transing_process_delay,wait_comp_process_delay,cold_start_delay,computing_process_delay
    action = []
    choose_action_way = []
    reward_list = []
    delay_list = []
    energy_list = []
    expense_list = []
    unfinish_indi = []
    cold_count_list = []
    wait_trans_process_delay = []
    transing_process_delay = []
    wait_comp_process_delay = []
    cold_start_delay = []
    computing_process_delay = []
    history_observation = []
    reward_indicator = []
    for i in range(n_iot):
            action.append(-np.ones([n_time,1]))
            choose_action_way.append(-np.ones([n_time,1]))
            reward_list.append(np.zeros([n_time,1]))
            delay_list.append(np.zeros([n_time,1]))
            energy_list.append(np.zeros([n_time,1]))
            expense_list.append(np.zeros([n_time,1]))   #
            unfinish_indi.append(-np.ones([n_time,1]))
            cold_count_list.append(-np.ones([n_time,1]))
            wait_trans_process_delay.append(np.zeros([n_time,1]))
            transing_process_delay.append(np.zeros([n_time,1]))
            wait_comp_process_delay.append(np.zeros([n_time,1]))
            cold_start_delay.append(np.zeros([n_time,1]))
            history_observation.append(np.zeros([n_time,1], dtype=object))
            reward_indicator.append(np.zeros([n_time, 1]))
            computing_process_delay.append(np.zeros([n_time,1]))  
    Queue_iot_comp = list()
    Queue_iot_tran = list()
    Queue_edge_comp = list()
    Queue_cloud_comp = list()

    for iot in range(n_iot):
        Queue_iot_comp.append(queue.Queue())
        Queue_iot_tran.append(queue.Queue()) 
        Queue_edge_comp.append(list()) 
        Queue_cloud_comp.append(list())
        for edge in range(n_edge):
            Queue_edge_comp[iot].append(queue.Queue())
        for cloud in range(n_cloud): 
            Queue_cloud_comp[iot].append(queue.Queue())

    #待执行总量
    all_task_wait_iot_comp_cpu_cycle = np.zeros(n_iot)
    all_task_wait_iot_tran_size = np.zeros(n_iot)
    all_task_wait_edge_comp_size_cpu_cycle = np.zeros([n_iot, n_edge])
    all_task_wait_cloud_comp_size_cpu_cycle = np.zeros([n_iot, n_cloud])
    #各设备各类型待执行任务的数量，初始时全为0
    all_task_wait_iot_comp_count = np.zeros([n_iot,n_task_type])
    all_task_wait_iot_tran_count = np.zeros([n_iot,n_task_type])
    all_task_wait_iot_tran_edge_count = np.zeros([n_iot,n_edge])
    all_task_wait_edge_comp_count = np.zeros([n_iot, n_edge,n_task_type])
    all_task_wait_cloud_comp_count = np.zeros([n_iot, n_cloud,n_task_type])

    per_task_wait_iot_comp_count_cpu_cycle = np.zeros([n_iot,n_task_type])
    per_task_wait_iot_tran_count_size = np.zeros([n_iot,n_task_type])
    per_task_wait_edge_comp_count_cpu_cycle = np.zeros([n_iot, n_edge,n_task_type])
    per_task_wait_cloud_comp_count_cpu_cycle = np.zeros([n_iot, n_cloud,n_task_type])

    # 执行器
    task_on_process_local = list()       
    task_on_transmit_local = list()
    task_on_process_edge = list() 
    task_on_process_cloud = list() 
    for iot in range(n_iot):
        task_on_process_local.append({'function_id': -1,'data_size': 0,
                                    'cpu_cycle': 0, 'task_arrive_time': 0,
                                    'flag': 0,'critical_value':0, 'block': 0,
                                    'remain': 0,'max_delay':0})
        task_on_transmit_local.append({'function_id': -1,'data_size': 0,
                                    'cpu_cycle': 0, 'task_arrive_time': 0,                         
                                                    'edge_logs': 0, 'cloud': 0, 'max_delay':0,
                                                    'remain': 0,'iot_action':0})
        
        task_on_process_edge.append(list())
        task_on_process_cloud.append(list())  
        for edge in range(n_edge):
            task_on_process_edge[iot].append({'function_id': -1,'data_size': 0,
                                            'cpu_cycle': 0, 'task_arrive_time': 0,
                                            'tran_finish_time':0,'max_delay':0,
                                            'flag': 0,'critical_value':0,'remain': 0})
        for cloud in range(n_cloud):
            task_on_process_cloud[iot].append({'function_id': -1,'data_size': 0,
                                            'cpu_cycle': 0, 'task_arrive_time': 0,
                                            'tran_finish_time':0,'max_delay':0,
                                            'flag': 0,'critical_value':0,'remain': 0})           
            
    #容器池状态初始化
    global iot_pool,edge_pool,cloud_pool
    iot_pool = np.zeros([n_iot, n_task_type]) #- np.ones
    edge_pool = list()
    for edge_index in range(n_edge):
        edge_pool.append(np.zeros([n_iot, n_task_type]))
    cloud_pool = list()
    for cloud_index in range(n_cloud):
        cloud_pool.append(np.zeros([n_iot, n_task_type]))
        observation_all = np.zeros([n_iot, n_features-5])
    #print(np.shape(observation_all),n_features_task,n_features_system_iot,n_features_system_edge,n_features_system_cloud,n_features)
    for iot_index in range(n_iot):
        # task
        '''observation_all[iot_index, 0] = int(task[iot_index][0][0]['function_id'])        #id
        observation_all[iot_index, 1] = task[iot_index][0][0]['data_size'] 
        observation_all[iot_index, 2] = task[iot_index][0][0]['cpu_cycle']
        observation_all[iot_index, 3] = max_delay[0]  #max_delay[t]
        observation_all[iot_index, 4] = keep_alive[0] # keep_alive[t]'''
        #n_features_system_iot
        for n_task_type_index in range(n_task_type):
            #还有多少个未执行   0,0,0,...,0
            observation_all[iot_index, n_task_type_index] = all_task_wait_iot_comp_count[iot_index][n_task_type_index]
            #0*'cpu_cycle',0*'cpu_cycle',0*'cpu_cycle',...,0*'cpu_cycle'
            observation_all[iot_index, n_task_type * 1 + n_task_type_index] = per_task_wait_iot_comp_count_cpu_cycle[iot_index][n_task_type_index] 
            #还有多少个未传输  0,0,0,...,0
            observation_all[iot_index, n_task_type * 2 + n_task_type_index] = all_task_wait_iot_tran_count[iot_index][n_task_type_index]
            #0*'data_size',0*'data_size',0*'data_size',...,0*'data_size'
            observation_all[iot_index, n_task_type * 3 + n_task_type_index] = per_task_wait_iot_tran_count_size[iot_index][n_task_type_index]      
            observation_all[iot_index, n_task_type * 4 + n_task_type_index] = keep_alive[n_task_type_index]#np.min([j+ 1 - iot_pool[iot_index][n_task_type_index] , keep_alive[n_task_type_index]])               
        observation_all[iot_index, n_task_type * 5] = all_task_wait_iot_comp_cpu_cycle[iot_index]
        observation_all[iot_index, n_task_type * 5 + 1] = task_on_process_local[iot_index]['remain']
        observation_all[iot_index, n_task_type * 5 + 2] = all_task_wait_iot_tran_size[iot_index]
        observation_all[iot_index, n_task_type * 5 + 3] = task_on_transmit_local[iot_index]['remain']
        observation_all[iot_index, n_task_type * 5 + 4] = pull_uplink_rate_iot
        observation_all[iot_index, n_task_type * 5 + 5] = comp_cap_iot[iot_index]
        for i in range(n_edge):
            observation_all[iot_index, n_task_type * 5 + 6 + i] = tran_edge_cap_iot[iot_index][i]
        for i in range(n_cloud):
            observation_all[iot_index, n_task_type * 5 + 6 + n_edge + i] = tran_cloud_cap_iot[iot_index][i]
        
        #n_features_system_edge_0
        observation_all[iot_index,n_task_type * 5 + 6 + n_edge + n_cloud] = pull_uplink_rate_edge
        observation_all[iot_index, n_task_type * 5 + 6 + n_edge + n_cloud + 1] = 0      #与当前服务器通信的iot的设备数量
        observation_all[iot_index, n_task_type * 5 + 6 + n_edge + n_cloud + 2] = all_task_wait_edge_comp_size_cpu_cycle[iot_index][0]
        observation_all[iot_index, n_task_type * 5 + 6 + n_edge + n_cloud + 3] = task_on_process_edge[iot_index][0]['remain']
        
        for n_task_type_index in range(n_task_type):
            observation_all[iot_index, n_task_type * 5 + 6 + n_edge + n_cloud + 4 + n_task_type_index] = all_task_wait_edge_comp_count[iot_index][0][n_task_type_index]
            observation_all[iot_index, n_task_type * 6 + 6 + n_edge + n_cloud + 4 + n_task_type_index] = per_task_wait_edge_comp_count_cpu_cycle[iot_index][0][n_task_type_index]
            observation_all[iot_index, n_task_type * 7 + 6 + n_edge + n_cloud + 4 + n_task_type_index] = keep_alive[n_task_type_index]#np.min([j+ 1 - edge_pool[0][n_task_type_index] , keep_alive[n_task_type_index]])
    
        #n_features_system_edge_1
        observation_all[iot_index, n_task_type * 8 + 6 + n_edge + n_cloud + 4] = pull_uplink_rate_edge
        observation_all[iot_index, n_task_type * 8 + 6 + n_edge + n_cloud + 5] = 0     #与当前服务器通信的iot的设备数量
        observation_all[iot_index, n_task_type * 8 + 6 + n_edge + n_cloud + 6] = all_task_wait_edge_comp_size_cpu_cycle[iot_index][1]
        observation_all[iot_index, n_task_type * 8 + 6 + n_edge + n_cloud + 7] = task_on_process_edge[iot_index][1]['remain']
        for n_task_type_index in range(n_task_type):
            observation_all[iot_index, n_task_type * 8 + 6 + n_edge + n_cloud + 8 + n_task_type_index] = all_task_wait_edge_comp_count[iot_index][1][n_task_type_index]
            observation_all[iot_index, n_task_type * 9 + 6 + n_edge + n_cloud + 8 + n_task_type_index] = per_task_wait_edge_comp_count_cpu_cycle[iot_index][1][n_task_type_index]
            observation_all[iot_index, n_task_type * 10 + 6 + n_edge + n_cloud + 8 + n_task_type_index] = keep_alive[n_task_type_index]#np.min([j+ 1 - edge_pool[1][n_task_type_index] , keep_alive[n_task_type_index]])
    
        #n_features_system_cloud    np.min([j+ 1 - cloud_pool[0][n_task_type_index] , keep_alive[n_task_type_index]])
        observation_all[iot_index, n_task_type * 11 + 6 + n_edge + n_cloud + 8] = pull_uplink_rate_cloud
        observation_all[iot_index, n_task_type * 11 + 6 + n_edge + n_cloud + 9] = comp_cap_cloud[0]
        observation_all[iot_index, n_task_type * 11 + 6 + n_edge + n_cloud + 10] = all_task_wait_cloud_comp_size_cpu_cycle[iot_index][0]
        observation_all[iot_index, n_task_type * 11 + 6 + n_edge + n_cloud + 11] = task_on_process_cloud[iot_index][0]['remain']
        for n_task_type_index in range(n_task_type):
            observation_all[iot_index, n_task_type * 11 + 6 + n_edge + n_cloud + 12 + n_task_type_index] = all_task_wait_cloud_comp_count[iot_index][0][n_task_type_index] 
            observation_all[iot_index, n_task_type * 12 + 6 + n_edge + n_cloud + 12 + n_task_type_index] = per_task_wait_cloud_comp_count_cpu_cycle[iot_index][0][n_task_type_index]
            observation_all[iot_index, n_task_type * 13 + 6 + n_edge + n_cloud + 12 + n_task_type_index] = keep_alive[n_task_type_index]#np.min([j+ 1 - cloud_pool[0][n_task_type_index] , keep_alive[n_task_type_index]])    
    return observation_all
                     
def train(iot_RL_list, NUM_EPISODE):
    #RL_step = np.zeros([n_iot])
    #print("进入train训练过程")
    global Queue_iot_comp, Queue_iot_tran,Queue_edge_comp,Queue_cloud_comp
    global all_task_wait_iot_comp_cpu_cycle,all_task_wait_iot_tran_size,all_task_wait_edge_comp_size_cpu_cycle ,all_task_wait_cloud_comp_size_cpu_cycle 
    global all_task_wait_iot_comp_count,all_task_wait_iot_tran_count ,all_task_wait_iot_tran_edge_count ,all_task_wait_edge_comp_count ,all_task_wait_cloud_comp_count 
    global per_task_wait_iot_comp_count_cpu_cycle ,per_task_wait_iot_tran_count_size ,per_task_wait_edge_comp_count_cpu_cycle ,per_task_wait_cloud_comp_count_cpu_cycle 

    global task_on_process_local ,task_on_transmit_local ,task_on_process_edge ,task_on_process_cloud 
    global t_iot_comp, t_iot_tran, b_edge_comp, b_cloud_comp,iot_pool,edge_pool,cloud_pool
    global action,reward_list,delay_list,energy_list,expense_list,unfinish_indi,cold_count_list,wait_trans_process_delay
    global transing_process_delay,wait_comp_process_delay,cold_start_delay,computing_process_delay
    
    for episode in range(NUM_EPISODE):
        print("当前轮次：",episode)
        observation_all_reset = reset()   
        observation_all = observation_all_reset 
        for j in range(n_time):
            ###print("当前时隙：",j)
            for iot_index in range(n_iot):
                observation_sys = np.squeeze(observation_all[iot_index, :])
                if task[iot_index][j][0]['function_id'] != -1:
                    observation_task = [task[iot_index][j][0]['function_id'],task[iot_index][j][0]['data_size'],
                                            task[iot_index][j][0]['cpu_cycle'],
                                            task[iot_index][j][0]['max_delay'],
                                            keep_alive[task[iot_index][j][0]['function_id']]
                                            ]
                    observation = np.hstack((observation_task, observation_sys))
                    history_observation[iot_index][j][0] = observation
                    ###print("history_observation[iot_index][j][0]",j,history_observation[iot_index][j][0],history_observation[iot_index][j][0][0])
                    #update_index = np.where((1 - reward_indicator[iot_index][:][0] ) * delay_list[iot_index][:][0] > 0)[0]
                    update_index = []
                    for time_index in range(j):
                        if (1 - reward_indicator[iot_index][time_index][0] ) * delay_list[iot_index][time_index][0] > 0:
                            ##print(reward_indicator[iot_index][time_index][0],delay_list[iot_index][time_index][0])
                            update_index.append(time_index)
                    #print("update_index",update_index,j)
                    if len(update_index) != 0:
                        for update_ii in range(len(update_index)):
                            time_index = update_index[update_ii]
                            id_index = int(task[iot_index][time_index][0]['function_id'])
                            if id_index == -1:
                                print("update_index",update_index,j,time_index)
                                print("action[iot_index][time_index][0]",action[iot_index][time_index][0])
                                print("reward_indicator[iot_index][time_index][0]",reward_indicator[iot_index][time_index][0])
                                print("delay_list[iot_index][time_index][0]",delay_list[iot_index][time_index][0])
                            #print(f"当前时隙{j}完成还未存储的索引：",time_index)
                            reward_list[iot_index][time_index][0] = reward(iot_index,time_index,id_index,
                                                                       delay_list[iot_index][time_index][0],
                                                                       energy_list[iot_index][time_index][0],
                                                                       expense_list[iot_index][time_index][0],
                                                                       unfinish_indi[iot_index][time_index][0])
                            iot_RL_list[iot_index].store_transition(history_observation[iot_index][time_index][0],
                                                                action[iot_index][time_index][0],
                                                                reward_list[iot_index][time_index][0],
                                                                observation)
                            reward_indicator[iot_index][time_index][0] = 1
                    #else:
                    #    print("截止到当前时隙，没有味标记过的完成任务",j)        
                    action[iot_index][j][0] , choose_action_way[iot_index][j][0] = iot_RL_list[iot_index].choose_action(observation)
                    if action[iot_index][j][0] <0 or action[iot_index][j][0] > n_actions - 1:
                            print("网络选择了不属于动作空间的动作")
                if task[iot_index][j][0]['function_id'] == -1 and  j > n_time - n_no_task:
                    look_task_time_index = 0 
                    while look_task_time_index < n_time:
                        if task[iot_index][look_task_time_index][0]['function_id'] != -1:
                            observation_task = [task[iot_index][look_task_time_index][0]['function_id'],task[iot_index][look_task_time_index][0]['data_size'],
                                                    task[iot_index][look_task_time_index][0]['cpu_cycle'],
                                                    task[iot_index][look_task_time_index][0]['max_delay'],
                                                    keep_alive[task[iot_index][look_task_time_index][0]['function_id']]
                                                    ]
                            #print("look_task_time_index",look_task_time_index)
                            break
                        else:
                            look_task_time_index += 1
                    #observation_task = [-1,0,0,0,0]
                    observation = history_observation[iot_index][look_task_time_index][0]
                    '''if j == n_time - 1:
                        observation = history_observation[iot_index][look_task_time_index][0]
                    else:
                        observation = np.hstack((observation_task, observation_sys))'''
                    #print("history_observation[iot_index][j][0]",j,history_observation[iot_index][j][0],history_observation[iot_index][j][0][0])
                    #update_index = np.where((1 - reward_indicator[iot_index][:][0] ) * delay_list[iot_index][:][0] > 0)[0]
                    update_index = []
                    for time_index in range(j):
                        if (1 - reward_indicator[iot_index][time_index][0] ) * delay_list[iot_index][time_index][0] > 0:
                            #print(reward_indicator[iot_index][time_index][0],delay_list[iot_index][time_index][0])
                            update_index.append(time_index)
                    #print("update_index",update_index,j)
                    if len(update_index) != 0:
                        for update_ii in range(len(update_index)):
                            time_index = update_index[update_ii]
                            id_index = int(task[iot_index][time_index][0]['function_id'])
                            #print(f"当前时隙{j}完成还未存储的索引：",time_index)
                            reward_list[iot_index][time_index][0] = reward(iot_index,time_index,id_index,
                                                                       delay_list[iot_index][time_index][0],
                                                                       energy_list[iot_index][time_index][0],
                                                                       expense_list[iot_index][time_index][0],
                                                                       unfinish_indi[iot_index][time_index][0])
                            #print("reward_list[iot_index][time_index][0]",reward_list[iot_index][time_index][0])
                            iot_RL_list[iot_index].store_transition(history_observation[iot_index][time_index][0],
                                                                action[iot_index][time_index][0],
                                                                reward_list[iot_index][time_index][0],
                                                                observation)
                            reward_indicator[iot_index][time_index][0] = 1
                  
                    
                if task[iot_index][j][0]['function_id'] == -1:
                    action[iot_index][j][0] = -2
                if action[iot_index][j][0] == -1:
                    print(iot_index,j,"任务没做处理",observation[0])
                    
            observation_all_ = step(j,action) 
        
            observation_all = observation_all_
            
                 
            #如果当前时隙的任务的动作不等于-2，那就需要向执行队列中添加任务执行
            #如果当前时隙的任务的动作等于-2，直接从任务队列中找出任务。
            #下一时隙的任务不为空，记录当前时隙完成任务的结束状态。
            # 否则，直到找到下一时隙任务不为空的时间节点，作为之前未存储，但已经判定任务结束的结束状态。
            #做一个标记，记录当前时隙下完成任务，且没有被存储过的，把当前时隙的的状态存入。
            #检查传入的是单个iot的数据，还是多个iot的数据
            #RL_step[iot_index] += 1
                
        
        unfinish_indi_count = 0
        unfinish_indi0_count = 0
        unfinish_indi1_count = 0
        unfinish_indi2_count = 0
        unfinish_indi3_count = 0
        unfinish_indi4_count = 0
        unfinish_indi5_count = 0
        reward_list_count = 0
        finish_indi_count = 0
        non_indi_count = 0
        iot_a_result = 0
        edge_a_result = 0
        cloud_a_result = 0
        total_delay = 0
        total_energy = 0
        total_expense = 0
        cold_start_result  = 0
        warm_start_result = 0
        cold_start_non = 0
        total_cold_start = 0
        total_transing_process = 0
        total_computing_process = 0
        action_non = 0
        choose_action_by_random_count = 0
        choose_action_by_net_count = 0
        for i in range(n_iot):
            unfinish_indi_count = unfinish_indi_count + (np.sum(unfinish_indi[i] != 0)  - np.sum(unfinish_indi[i] == -1))
            finish_indi_count = finish_indi_count + np.sum(unfinish_indi[i] == 0)
            non_indi_count  = non_indi_count + np.sum(unfinish_indi[i] == -1)
            unfinish_indi0_count = unfinish_indi0_count + np.sum(unfinish_indi[i] == 0)
            unfinish_indi1_count = unfinish_indi1_count + np.sum(unfinish_indi[i] == 1)
            unfinish_indi2_count = unfinish_indi2_count + np.sum(unfinish_indi[i] == 2)
            unfinish_indi3_count = unfinish_indi3_count + np.sum(unfinish_indi[i] == 3)
            unfinish_indi4_count = unfinish_indi4_count + np.sum(unfinish_indi[i] == 4)
            unfinish_indi5_count = unfinish_indi5_count + np.sum(unfinish_indi[i] == 5)
            
            
            reward_list_count = reward_list_count + np.sum(reward_list[i])
            
            iot_a_result = iot_a_result + np.sum(action[i] == 0)
            edge_a_result = edge_a_result + np.sum(action[i] == 1) + np.sum(action[i] == 2)
            cloud_a_result = cloud_a_result + np.sum(action[i] == 3)
            action_non = action_non + np.sum(action[i] == -1)
            
            total_delay = total_delay + np.sum(delay_list[i])
            total_energy = total_energy + np.sum(energy_list[i])
            total_expense = total_expense + np.sum(expense_list[i])
            
            cold_start_result = cold_start_result + np.sum(cold_count_list[i] == 1)
            warm_start_result = warm_start_result + np.sum(cold_count_list[i] == 0)
            
            cold_start_non = cold_start_non + np.sum(cold_count_list[i] == -1)
            total_cold_start = total_cold_start + np.sum(cold_start_delay[i])
               
            total_transing_process =   total_transing_process + np.sum(transing_process_delay[i]) 
            total_computing_process = total_computing_process  + np.sum(computing_process_delay[i]) 
            #print(f"{episode}:",iot_RL_list[i].epsilon,iot_RL_list[i].beta,iot_RL_list[i].target_params_replaced_counter,iot_RL_list[i].learn_step_counter)
            choose_action_by_random_count = choose_action_by_random_count + np.sum(choose_action_way[i] == 1)
            choose_action_by_net_count = np.sum(choose_action_way[i] == 0)
        reward_list_record.append(reward_list_count)
        delay_list_record.append(total_delay)
        #delay_avg_list_record.append(total_energy)
        energy_list_record.append(total_energy)
        expense_list_record.append(total_expense)
        energy_avg_list_record = []
        expense_avg_list_record = []
        unfinish_total_list_record.append(unfinish_indi_count)
        unfinish_total_list_record0.append(unfinish_indi0_count)
        unfinish_total_list_record1.append(unfinish_indi1_count)
        unfinish_total_list_record2.append(unfinish_indi2_count)
        unfinish_total_list_record3.append(unfinish_indi3_count)
        unfinish_total_list_record4.append(unfinish_indi4_count)
        unfinish_total_list_record5.append(unfinish_indi5_count)
        
        utilization_ratio_record = []                  # 记录每个时隙的带宽利用率。
        loss_list_record = []                               # 记录训练过程中的损失值。 
        action_record_iot.append(iot_a_result) 
        action_record_edge.append(edge_a_result)
        action_record_cloud.append(cloud_a_result) 
        choose_action_by_random.append(choose_action_by_random_count)
        choose_action_by_net.append(choose_action_by_net_count)
        slot_bandwidth_record = []
        cold_count_list_record.append(cold_start_result)
        warm_count_list_record.append(warm_start_result)
        unfinish_indi_record = []
        sucess_count_list_record.append(finish_indi_count)

    
        np.savetxt(f'./结果分析/奖励-Dou_Due_priority_4_arrive_001_learning_99_discount_64_batchsize_x1_8_cold_delay_4_iot_10X_timeslot.csv', reward_list_record, delimiter=',')
        np.savetxt(f'./结果分析/丢失任务总数-Dou_Due_priority_4_arrive_001_learning_99_discount_64_batchsize_x1_8_cold_delay_4_iot_10X_timeslot.csv', unfinish_total_list_record, delimiter=',')
        np.savetxt(f'./结果分析/任务总时延-Dou_Due_priority_4_arrive_001_learning_99_discount_64_batchsize_x1_8_cold_delay_4_iot_10X_timeslot.csv', delay_list_record, delimiter=',')
        np.savetxt(f'./结果分析/任务总能耗-Dou_Due_priority_4_arrive_001_learning_99_discount_64_batchsize_x1_8_cold_delay_4_iot_10X_timeslot.csv', energy_list_record, delimiter=',')
        np.savetxt(f'./结果分析/任务总花费-Dou_Due_priority_4_arrive_001_learning_99_discount_64_batchsize_x1_8_cold_delay_4_iot_10X_timeslot.csv', expense_list_record, delimiter=',')
        np.savetxt(f'./结果分析/任务是冷启动-Dou_Due_priority_4_arrive_001_learning_99_discount_64_batchsize_x1_8_cold_delay_4_iot_10X_timeslot.csv', cold_count_list_record, delimiter=',')
        np.savetxt(f'./结果分析/任务是热启动-Dou_Due_priority_4_arrive_001_learning_99_discount_64_batchsize_x1_8_cold_delay_4_iot_10X_timeslot.csv', warm_count_list_record, delimiter=',')
        np.savetxt(f'./结果分析/成功任务总数-Dou_Due_priority_4_arrive_001_learning_99_discount_64_batchsize_x1_8_cold_delay_4_iot_10X_timeslot.csv', sucess_count_list_record, delimiter=',')
        np.savetxt(f'./结果分析/卸载结果iot_-Dou_Due_priority_4_arrive_001_learning_99_discount_64_batchsize_x1_8_cold_delay_4_iot_10X_timeslot.csv', action_record_iot, delimiter=',')
        np.savetxt(f'./结果分析/卸载结果edge_-Dou_Due_priority_4_arrive_001_learning_99_discount_64_batchsize_x1_8_cold_delay_4_iot_10X_timeslot.csv', action_record_edge, delimiter=',')
        np.savetxt(f'./结果分析/卸载结果cloud_-Dou_Due_priority_4_arrive_001_learning_99_discount_64_batchsize_x1_8_cold_delay_4_iot_10X_timeslot.csv', action_record_cloud, delimiter=',')
        #np.savetxt(f'./结果分析/任务执行标志0-总数-Dou_Due_priority_4_arrive_001_learning_99_discount_64_batchsize_x1_8_cold_delay_4_iot_10X_timeslot.csv', unfinish_total_list_record0, delimiter=',')
        #np.savetxt(f'./结果分析/任务执行标志1--Dou_Due_priority_4_arrive_001_learning_99_discount_64_batchsize_x1_8_cold_delay_4_iot_10X_timeslot.csv', unfinish_total_list_record1, delimiter=',')
        #np.savetxt(f'./结果分析/任务执行标志2--Dou_Due_priority_4_arrive_001_learning_99_discount_64_batchsize_x1_8_cold_delay_4_iot_10X_timeslot.csv', unfinish_total_list_record2, delimiter=',')
        #np.savetxt(f'./结果分析/任务执行标志3--Dou_Due_priority_4_arrive_001_learning_99_discount_64_batchsize_x1_8_cold_delay_4_iot_10X_timeslot.csv', unfinish_total_list_record3, delimiter=',')
        #np.savetxt(f'./结果分析/任务执行标志4--Dou_Due_priority_4_arrive_001_learning_99_discount_64_batchsize_x1_8_cold_delay_4_iot_10X_timeslot.csv', unfinish_total_list_record4, delimiter=',')
        #np.savetxt(f'./结果分析/任务执行标志5--Dou_Due_priority_4_arrive_001_learning_99_discount_64_batchsize_x1_8_cold_delay_4_iot_10X_timeslot.csv', unfinish_total_list_record5, delimiter=',')
        #np.savetxt(f'./结果分析/网络选择动作数量--Dou_Due_priority_4_arrive_001_learning_99_discount_64_batchsize_x1_8_cold_delay_4_iot_10X_timeslot.csv', choose_action_by_net, delimiter=',')
        #np.savetxt(f'./结果分析/随机选择动作数量--Dou_Due_priority_4_arrive_001_learning_99_discount_64_batchsize_x1_8_cold_delay_4_iot_10X_timeslot.csv', choose_action_by_random, delimiter=',')
        '''if episode == 10:
            return'''
    '''with open('./结果分析/卸载结果.json', 'w') as f:
        json.dump(action_record, f, ensure_ascii=False, indent=4)
        59-5
    learning_rate=0.00005,    (RL_step[iot_index][0] % 20 == 0)batch_size=128,reward_decay=0.99,alpha = 0.1,  beta_increment = 0.001, e_greedy=0.99,  replace_target_iter=100,memory_size=30000,  e_greedy_increment=0.0005, NUM_EPISODE = 10000

        '''
def step(j_time,action_time):
    #print("step开始时隙",j_time)
    global Queue_iot_comp, Queue_iot_tran,Queue_edge_comp,Queue_cloud_comp
    global all_task_wait_iot_comp_cpu_cycle,all_task_wait_iot_tran_size,all_task_wait_edge_comp_size_cpu_cycle ,all_task_wait_cloud_comp_size_cpu_cycle 
    global all_task_wait_iot_comp_count,all_task_wait_iot_tran_count ,all_task_wait_iot_tran_edge_count ,all_task_wait_edge_comp_count ,all_task_wait_cloud_comp_count 
    global per_task_wait_iot_comp_count_cpu_cycle ,per_task_wait_iot_tran_count_size ,per_task_wait_edge_comp_count_cpu_cycle ,per_task_wait_cloud_comp_count_cpu_cycle 

    global task_on_process_local ,task_on_transmit_local ,task_on_process_edge ,task_on_process_cloud 
    global t_iot_comp, t_iot_tran, b_edge_comp, b_cloud_comp,iot_pool,edge_pool,cloud_pool
    global action,reward_list,delay_list,energy_list,expense_list,unfinish_indi,cold_count_list,wait_trans_process_delay
    global transing_process_delay,wait_comp_process_delay,cold_start_delay,computing_process_delay   
    
    j=j_time
    
    
    #b把当前时隙的任务加入队列
    for iot_index in range(n_iot):
        if task[iot_index][j][0]['function_id'] != -1 and action_time[iot_index][j][0] != -2:
            tmp_dict = {'function_id':task[iot_index][j][0]['function_id'],'data_size': task[iot_index][j][0]['data_size'], 
                        'cpu_cycle':  task[iot_index][j][0]['cpu_cycle'], 'task_arrive_time': j,'max_delay': task[iot_index][j][0]['max_delay']}
            #print(tmp_dict)
            if action_time[iot_index][j][0] == 0:
                Queue_iot_comp[iot_index].put(tmp_dict)
                #对应函数类型加一 
                 
                #print()
                if tmp_dict['function_id'] == -1 or tmp_dict['max_delay'] == 0:
                    print("把一个空任务放在传输队列中了！！！！")
                #print(f"{tmp_dict['task_arrive_time']}时刻的任务放入本地队列")
                id_index =  int(tmp_dict['function_id'])
                all_task_wait_iot_comp_count[iot_index][id_index] +=1
                #对应函数类型的单数计量 + tmp_dict['cpu_cycle']
                per_task_wait_iot_comp_count_cpu_cycle[iot_index][id_index] +=tmp_dict['cpu_cycle']
                #对应计算队列的总量 + tmp_dict['cpu_cycle']
                all_task_wait_iot_comp_cpu_cycle[iot_index] +=tmp_dict['cpu_cycle']
            else:
                tmp_tran = {'function_id':task[iot_index][j][0]['function_id'],'data_size': task[iot_index][j][0]['data_size'],
                                'cpu_cycle': task[iot_index][j][0]['cpu_cycle'], 'task_arrive_time': j,
                                'iot_action':action_time[iot_index][j][0],'max_delay': task[iot_index][j][0]['max_delay']
                                }
                if tmp_tran['function_id'] == -1 or tmp_tran['max_delay'] == 0:
                    print("把一个空任务放在传输队列中了！！！！")
                Queue_iot_tran[iot_index].put(tmp_tran)
                #print(f"{tmp_dict['task_arrive_time']}时刻的任务放入传输队列")
                id_index =  int(tmp_tran['function_id'])
                all_task_wait_iot_tran_count[iot_index][id_index] +=1
                if tmp_tran['iot_action'] == 1:
                    all_task_wait_iot_tran_edge_count[iot_index][0] += 1
                if tmp_tran['iot_action'] == 2:
                    all_task_wait_iot_tran_edge_count[iot_index][1] += 1
                per_task_wait_iot_tran_count_size[iot_index][id_index]  +=tmp_tran['data_size']
                all_task_wait_iot_tran_size[iot_index]  +=tmp_tran['data_size']
    #执行器要是大于0，也可能是向云传输，这种情况怎办么版？
    #当前时隙开始：
    edge_count = np.zeros([1,n_edge])
    for edge_index in range(n_edge):
        #print("统计每个边缘通信的iot设备的数量")
        for iot_index in range(n_iot):
            if (task_on_transmit_local[iot_index]['remain'] > 0  and task_on_transmit_local[iot_index]['iot_action'] - 1 == edge_index) or (all_task_wait_iot_tran_edge_count[iot_index][edge_index] !=0 and  (not Queue_iot_tran[iot_index].empty())) or task_on_process_edge[iot_index][edge_index]['remain'] > 0 or (not Queue_edge_comp[iot_index][edge_index].empty()):
                edge_count[0][edge_index] += 1
    '''print(f"当前时隙{j}:",edge_count)
    for edge_index in range(n_edge):
        if edge_count[0][edge_index]==0:
            print(f"   边缘{edge_index}通信iot数量 为0 :",task_on_transmit_local[iot_index]['remain'] , task_on_transmit_local[iot_index]['iot_action']-1 ,all_task_wait_iot_tran_edge_count[iot_index][edge_index] ,not Queue_iot_tran[iot_index].empty(), task_on_process_edge[iot_index][edge_index]['remain'] ,not Queue_edge_comp[iot_index][edge_index].empty())
        if edge_count[0][edge_index]!=0: 
            print(f"   边缘{edge_index}通信iot数量 不为0 :",task_on_transmit_local[iot_index]['remain'] , task_on_transmit_local[iot_index]['iot_action']-1 ,all_task_wait_iot_tran_edge_count[iot_index][edge_index] ,not Queue_iot_tran[iot_index].empty(), task_on_process_edge[iot_index][edge_index]['remain'] ,not Queue_edge_comp[iot_index][edge_index].empty())
    '''
               
    
    
    #本地执行器
    for iot_index in range(n_iot):
        ##print("#本地执行器")
        slot_time_remain = 1
        while slot_time_remain >0:
            if task_on_process_local[iot_index]['remain'] ==0 and (not Queue_iot_comp[iot_index].empty()):
                while not Queue_iot_comp[iot_index].empty():
                    
                    get_task = Queue_iot_comp[iot_index].get()
                    id_index = int(get_task['function_id'])
                    time_index = int(get_task['task_arrive_time'])
                    
                    if time_index == 0:
                        print("本地取任务",slot_time_remain,get_task)
                    size_index = get_task['data_size']
                    cpu_index = get_task['cpu_cycle']
                    #print(f"{get_task['task_arrive_time']}时刻的任务放入本地执行器",j+1-slot_time_remain)
                    #任务数量减少一个
                    all_task_wait_iot_comp_count[iot_index][id_index] -=1
                    #单项任务cpu_cycle减少
                    per_task_wait_iot_comp_count_cpu_cycle[iot_index][id_index] -= get_task['cpu_cycle']
                    #总cpu_cycle减少
                    all_task_wait_iot_comp_cpu_cycle[iot_index] -= get_task['cpu_cycle']
                    wait_comp_process_delay[iot_index][time_index][0] = j + 1 - slot_time_remain - get_task['task_arrive_time']
                    if j + 1 - slot_time_remain - get_task['task_arrive_time'] >= get_task['max_delay']:
                        #print(f"任务{get_task['task_arrive_time']}时刻的任务 等待执行超时 而不会执行 失败")
                        cold_count_list[iot_index][time_index][0] = 2
                        cold_start_delay[iot_index][time_index][0] = 0
                        computing_process_delay[iot_index][time_index][0] = 0 
                        unfinish_indi[iot_index][time_index][0] = 3  
                        delay_list[iot_index][time_index][0] = j + 1 - slot_time_remain - get_task['task_arrive_time']  
                        energy_list[iot_index][time_index][0] = 0
                        expense_list[iot_index][time_index][0] = 0
                        #
                    else:
                        #print("任务在本地没有等待超时")
                        #print(f"{get_task['task_arrive_time']}时刻的任务放入本地执行器 执行冷热启动")
                        task_on_process_local[iot_index]['function_id'] = int(get_task['function_id'])
                        task_on_process_local[iot_index]['data_size'] = get_task['data_size']
                        task_on_process_local[iot_index]['cpu_cycle'] = get_task['cpu_cycle']
                        task_on_process_local[iot_index]['task_arrive_time']   = get_task['task_arrive_time']
                        task_on_process_local[iot_index]['remain'] = get_task['cpu_cycle']
                        task_on_process_local[iot_index]['max_delay'] = get_task['max_delay']
    
                        if j + 1 - slot_time_remain - iot_pool[iot_index][id_index] < keep_alive[id_index] and iot_pool[iot_index][id_index] != 0:
                            cold_count_list[iot_index][time_index][0] = 0
                            cold_start_delay[iot_index][time_index][0] = 0
                            task_on_process_local[iot_index]['flag'] = 0
                            task_on_process_local[iot_index]['block'] = 0
                            iot_pool[iot_index][id_index] = j + 1 - slot_time_remain
                            #print(f"{get_task['task_arrive_time']}时刻的任务放入本地执行器 热启动执行")
                        if j + 1 - slot_time_remain - iot_pool[iot_index][id_index] >= keep_alive[id_index] or iot_pool[iot_index][id_index] == 0:
                            cold_count_list[iot_index][time_index][0] = 1
                            cold_start_delay[iot_index][time_index][0] = task_on_process_local[iot_index]['data_size'] / pull_uplink_rate_iot
                            task_on_process_local[iot_index]['flag'] = cold_start_delay[iot_index][time_index][0]
                            #print(f"{get_task['task_arrive_time']}时刻的任务放入本地执行器 冷启动执行")
                            '''if wait_comp_process_delay[iot_index][time_index][0] + cold_start_delay_temp  - max_delay[id_index] >= 0:
                                cold_start_delay[iot_index][time_index][0] = max_delay[id_index] - wait_comp_process_delay[iot_index][time_index][0]
                                task_on_process_local[iot_index]['flag'] = cold_start_delay[iot_index][time_index][0]
                                task_on_process_local[iot_index]['block'] = 1
                            else:
                                cold_start_delay[iot_index][time_index][0] = cold_start_delay_temp
                                task_on_process_local[iot_index]['flag'] = cold_start_delay[iot_index][time_index][0]
                                task_on_process_local[iot_index]['block'] = 0'''
                        break
            
            if slot_time_remain >0 and task_on_process_local[iot_index]['remain'] >0 and task_on_process_local[iot_index]['flag'] > 0:
                #print(f"{task_on_process_local[iot_index]['task_arrive_time']}时刻的任务 冷启动过程中。。。。")
                task_on_process_local[iot_index]['flag'] -= slot_time_remain
                time_index = int(task_on_process_local[iot_index]['task_arrive_time'])
                if time_index == 0:
                        print("本地冷启动",slot_time_remain)
                id_index = int(task_on_process_local[iot_index]['function_id'])
                if task_on_process_local[iot_index]['flag'] > 0:           #执行器需要添加flag的标志数据
                    slot_time_remain = 0
                if task_on_process_local[iot_index]['flag'] <= 0:
                    slot_time_remain = -task_on_process_local[iot_index]['flag']
                    #print("slot_time_remain = -task_on_process_local[iot_index]['flag']",slot_time_remain,)
                    #还有时间可以执行，但是若标志为哪个的话，任务可以重新取了
                    if j + 1 - slot_time_remain - task_on_process_local[iot_index]['task_arrive_time'] >=task_on_process_local[iot_index]['max_delay']:
                        #print(f"{task_on_process_local[iot_index]['task_arrive_time']}时刻的任务 在冷启动过程中失败")
                        unfinish_indi[iot_index][time_index][0] = 4
                        computing_process_delay[iot_index][time_index][0] = 0
                        delay_list[iot_index][time_index][0] = j + 1 - slot_time_remain - task_on_process_local[iot_index]['task_arrive_time']
                        energy_list[iot_index][time_index][0] = esc * (comp_cap_iot[iot_index] ** 2) * ((computing_process_delay[iot_index][time_index][0]+ cold_start_delay[iot_index][time_index][0]) )
                        expense_list[iot_index][time_index][0] = 0 
                        task_on_process_local[iot_index]['function_id'] = -1
                        task_on_process_local[iot_index]['data_size'] = 0
                        task_on_process_local[iot_index]['cpu_cycle'] = 0
                        task_on_process_local[iot_index]['task_arrive_time'] = 0
                        task_on_process_local[iot_index]['remain'] = 0
                        task_on_process_local[iot_index]['flag'] = 0
                        task_on_process_local[iot_index]['max_delay'] = 0
                        task_on_process_local[iot_index]['block'] = 0 
                        iot_pool[iot_index][id_index] = j + 1 - slot_time_remain   #每个中括号都要检查一遍
                    else:
                        #print(f"{task_on_process_local[iot_index]['task_arrive_time']}时刻的任务在冷启动 成功",j + 1 - slot_time_remain)
                        task_on_process_local[iot_index]['flag'] = 0
                        iot_pool[iot_index][id_index] = j + 1 - slot_time_remain
                        ##print("任务在冷启动过程中没有失败",slot_time_remain,task_on_process_local[iot_index]['remain'],task_on_process_local[iot_index]['flag'])
                #if task_on_process_local[iot_index]['flag'] == 0:
                    #print()
            if slot_time_remain >0 and task_on_process_local[iot_index]['remain'] >0 and task_on_process_local[iot_index]['flag'] == 0: 
                #print(f"{task_on_process_local[iot_index]['task_arrive_time']}时刻的任务 执行中。。。",j + 1 - slot_time_remain)
                id_index = int(task_on_process_local[iot_index]['function_id'])
                time_index = int(task_on_process_local[iot_index]['task_arrive_time'])
                if time_index == 0:
                        print("本地执行",slot_time_remain)
                task_remain_time =  task_on_process_local[iot_index]['max_delay']  -(j + 1 - slot_time_remain - task_on_process_local[iot_index]['task_arrive_time'])
                #print(f"{task_on_process_local[iot_index]['task_arrive_time']}时刻的任务,task_remain_time,slot_time_remain",task_remain_time,slot_time_remain)
                if task_remain_time >= slot_time_remain:#截止时间是充足的：
                    task_on_process_local[iot_index]['remain'] = task_on_process_local[iot_index]['remain'] - comp_cap_iot[iot_index] *  slot_time_remain
                    if task_on_process_local[iot_index]['remain'] > 0:
                        #print("判断任务是否超时，但好像不用判断，因为剩余的时间是大于可执行的时间的，任务是否在最大时延内完成需要后续判断！")
                        slot_time_remain = 0
                        iot_pool[iot_index][id_index] = j + 1 - slot_time_remain
                    if task_on_process_local[iot_index]['remain'] <=0:
                        #print("任务已经完成，是在最大时延内完成的")
                        task_on_process_local[iot_index]['remain'] = task_on_process_local[iot_index]['remain'] + comp_cap_iot[iot_index] *  slot_time_remain
                        task_remain_need_time = task_on_process_local[iot_index]['remain'] / comp_cap_iot[iot_index]
                        task_on_process_local[iot_index]['remain'] = 0
                        slot_time_remain = slot_time_remain - task_remain_need_time
                        #print(f"{task_on_process_local[iot_index]['task_arrive_time']}时刻的任务 本地执行完1",j + 1 - slot_time_remain) 
                        unfinish_indi[iot_index][time_index][0] = 0
                        computing_process_delay[iot_index][time_index][0] = task_on_process_local[iot_index]['cpu_cycle']  / comp_cap_iot[iot_index]
                        delay_list[iot_index][time_index][0] = j + 1 - slot_time_remain - task_on_process_local[iot_index]['task_arrive_time']
                        energy_list[iot_index][time_index][0] = esc * (comp_cap_iot[iot_index] ** 2) * ((computing_process_delay[iot_index][time_index][0]+ cold_start_delay[iot_index][time_index][0]) )
                        expense_list[iot_index][time_index][0] = 0 
                        task_on_process_local[iot_index]['function_id'] = -1
                        task_on_process_local[iot_index]['data_size'] = 0
                        task_on_process_local[iot_index]['cpu_cycle'] = 0
                        task_on_process_local[iot_index]['task_arrive_time'] = 0
                        task_on_process_local[iot_index]['remain'] = 0
                        task_on_process_local[iot_index]['flag'] = 0
                        task_on_process_local[iot_index]['max_delay'] = 0
                        task_on_process_local[iot_index]['block'] = 0 
                        iot_pool[iot_index][id_index] = j + 1 - slot_time_remain        
                if task_remain_time < slot_time_remain:
                    task_on_process_local[iot_index]['remain'] = task_on_process_local[iot_index]['remain'] - comp_cap_iot[iot_index] *  task_remain_time
                    
                    if task_on_process_local[iot_index]['remain'] <= 0:
                        if task_on_process_local[iot_index]['remain'] == 0:
                            #print("任务在最大时延内，刚好完成，任务是执行成功")
                            slot_time_remain = slot_time_remain - task_remain_time
                        if task_on_process_local[iot_index]['remain'] < 0:
                            #print("任务是一定能在最大时延内完成的")
                            task_on_process_local[iot_index]['remain'] = task_on_process_local[iot_index]['remain'] + comp_cap_iot[iot_index] *  task_remain_time
                            task_remain_need_time = task_on_process_local[iot_index]['remain'] / comp_cap_iot[iot_index]
                            task_on_process_local[iot_index]['remain'] = 0
                            slot_time_remain = slot_time_remain - task_remain_need_time
                        unfinish_indi[iot_index][time_index][0] = 0
                        #print(f"{task_on_process_local[iot_index]['task_arrive_time']}时刻的任务 本地执行完2") 
                        computing_process_delay[iot_index][time_index][0] = task_on_process_local[iot_index]['cpu_cycle']  / comp_cap_iot[iot_index]
                        delay_list[iot_index][time_index][0] = j + 1 - slot_time_remain - task_on_process_local[iot_index]['task_arrive_time']
                        energy_list[iot_index][time_index][0] = esc * (comp_cap_iot[iot_index] ** 2) * ((computing_process_delay[iot_index][time_index][0]+ cold_start_delay[iot_index][time_index][0]) )
                        expense_list[iot_index][time_index][0] = 0 
                        task_on_process_local[iot_index]['function_id'] = -1
                        task_on_process_local[iot_index]['data_size'] = 0
                        task_on_process_local[iot_index]['cpu_cycle'] = 0
                        task_on_process_local[iot_index]['task_arrive_time'] = 0
                        task_on_process_local[iot_index]['remain'] = 0
                        task_on_process_local[iot_index]['flag'] = 0
                        task_on_process_local[iot_index]['max_delay'] = 0
                        task_on_process_local[iot_index]['block'] = 0 
                        iot_pool[iot_index][id_index] = j + 1 - slot_time_remain        
                    if task_on_process_local[iot_index]['remain'] > 0:
                        
                        slot_time_remain = slot_time_remain - task_remain_time
                        #print(f"{task_on_process_local[iot_index]['task_arrive_time']}时刻的任务 执行失败",j + 1 - slot_time_remain)
                        unfinish_indi[iot_index][time_index][0] = 5
                        computing_process_delay[iot_index][time_index][0] = (task_on_process_local[iot_index]['cpu_cycle'] - task_on_process_local[iot_index]['remain']) / comp_cap_iot[iot_index]
                        delay_list[iot_index][time_index][0] = j + 1 - slot_time_remain - task_on_process_local[iot_index]['task_arrive_time']
                        energy_list[iot_index][time_index][0] = esc * (comp_cap_iot[iot_index] ** 2) * ((computing_process_delay[iot_index][time_index][0]+ cold_start_delay[iot_index][time_index][0]) )
                        expense_list[iot_index][time_index][0] = 0 
                        task_on_process_local[iot_index]['function_id'] = -1
                        task_on_process_local[iot_index]['data_size'] = 0
                        task_on_process_local[iot_index]['cpu_cycle'] = 0
                        task_on_process_local[iot_index]['task_arrive_time'] = 0
                        task_on_process_local[iot_index]['remain'] = 0
                        task_on_process_local[iot_index]['flag'] = 0
                        task_on_process_local[iot_index]['max_delay'] = 0
                        task_on_process_local[iot_index]['block'] = 0 
                        iot_pool[iot_index][id_index] = j + 1 - slot_time_remain
                        #时间为 j + 1 - slot_time_remain - task_on_process_local[iot_index]['task_arrive_time']       
            if task_on_process_local[iot_index]['remain'] == 0 and Queue_iot_comp[iot_index].empty() and task_on_process_local[iot_index]['flag'] == 0:
                ##print("当前时隙，本地上没有任何任务，队列是空的 ，也没有任务在冷启动，执行器也是空闲的")
                slot_time_remain = 0        
        
       
    #本地传输器
    for iot_index in range(n_iot):
        slot_time_remain = 1
        while slot_time_remain >0:
            if task_on_transmit_local[iot_index]['function_id'] == -1 and task_on_transmit_local[iot_index]['remain'] ==0 and (not Queue_iot_tran[iot_index].empty()):
                while not Queue_iot_tran[iot_index].empty():
                    get_task = Queue_iot_tran[iot_index].get()
                    #print("本地传输get_task",get_task)
                    id_index = int(get_task['function_id'])
                    if id_index == -1:
                        print("从待 传输队列中取出一个无效任务   ")
                    time_index = int(get_task['task_arrive_time'])
                    if time_index == 0:
                        print("本地取传输",slot_time_remain)
                    #print(f"{get_task['task_arrive_time']}时刻的任务放入本地 传输器 ",j+1-slot_time_remain)
                    all_task_wait_iot_tran_count[iot_index][id_index] -=1
                    if get_task['iot_action'] == 1:
                        all_task_wait_iot_tran_edge_count[iot_index][0] -= 1
                    if get_task['iot_action'] == 2:
                        all_task_wait_iot_tran_edge_count[iot_index][1] -= 1    
                    per_task_wait_iot_tran_count_size[iot_index][id_index] -= get_task['data_size']
                    all_task_wait_iot_tran_size [iot_index] -= get_task['data_size']
                    wait_trans_process_delay[iot_index][time_index][0] = j + 1 - slot_time_remain - get_task['task_arrive_time']
                    if wait_trans_process_delay[iot_index][time_index][0] >= get_task['max_delay']:
                        #print(f"任务{get_task['task_arrive_time']}时刻的任务 等待传输超时 而不会执行", j + 1 - slot_time_remain)
                        transing_process_delay[iot_index][time_index][0] = 0
                        cold_count_list[iot_index][time_index][0] = 2
                        cold_start_delay[iot_index][time_index][0] = 0
                        computing_process_delay[iot_index][time_index][0] = 0 
                        unfinish_indi[iot_index][time_index][0] = 1
                        delay_list[iot_index][time_index][0] = wait_trans_process_delay[iot_index][time_index][0]
                        energy_list[iot_index][time_index][0] = 0
                        expense_list[iot_index][time_index][0] = 0
                    else:
                        #print(f"任务{get_task['task_arrive_time']}时刻的任务在本地没有等待传输超时，任务放进传输器", j + 1 - slot_time_remain)
                        task_on_transmit_local[iot_index]['function_id'] = int(get_task['function_id'])
                        task_on_transmit_local[iot_index]['data_size'] = get_task['data_size']
                        task_on_transmit_local[iot_index]['cpu_cycle'] = get_task['cpu_cycle']
                        task_on_transmit_local[iot_index]['max_delay'] = get_task['max_delay']
                        task_on_transmit_local[iot_index]['task_arrive_time']   = get_task['task_arrive_time']
                        task_on_transmit_local[iot_index]['iot_action'] = get_task['iot_action']
                        task_on_transmit_local[iot_index]['remain'] = get_task['data_size']
                        break
                    
            if slot_time_remain >0 and task_on_transmit_local[iot_index]['remain'] >0 and task_on_transmit_local[iot_index]['function_id'] != -1:
                #print(f"{task_on_transmit_local[iot_index]['task_arrive_time']}时刻的任务在 传输中,,,,,", j + 1 - slot_time_remain)
                tran_index_flag = int(task_on_transmit_local[iot_index]['iot_action'])
                if tran_index_flag == 1 or tran_index_flag ==2:
                    tran_index = tran_index_flag - 1
                    tran_iot_camp = tran_edge_cap_iot[iot_index][tran_index]
                elif tran_index_flag == 3:
                    tran_index = tran_index_flag - 3
                    tran_iot_camp = tran_cloud_cap_iot[iot_index][tran_index]
                else:
                    print("传输的动作不对")
                id_index = int(task_on_transmit_local[iot_index]['function_id'])
                time_index = int(task_on_transmit_local[iot_index]['task_arrive_time'])
                if time_index == 0:
                        print("本地取传输执行",slot_time_remain,task_on_transmit_local[iot_index])
                task_remain_time =   task_on_transmit_local[iot_index]['max_delay'] -(j + 1 - slot_time_remain - task_on_transmit_local[iot_index]['task_arrive_time'])
                #print(f"{task_on_transmit_local[iot_index]['task_arrive_time']}时刻的任务,判断当前，task_remain_time,slot_time_remain",task_remain_time,slot_time_remain)
                if task_remain_time > slot_time_remain and task_on_transmit_local[iot_index]['function_id'] != -1 :
                    task_on_transmit_local[iot_index]['remain'] = task_on_transmit_local[iot_index]['remain'] - tran_iot_camp *  slot_time_remain
                    if task_on_transmit_local[iot_index]['remain'] > 0:
                        ##print("判断任务传输是否超时，但好像不用判断，因为剩余的时间是大于可执行的时间的，任务是否在最大时延内完成需要后续判断！")
                        slot_time_remain = 0
                    if task_on_transmit_local[iot_index]['remain'] <= 0:   #最大时延剩余的多，因此等于的时候也有空余的时间在服务器等待执行
                            task_on_transmit_local[iot_index]['remain'] = task_on_transmit_local[iot_index]['remain'] + tran_iot_camp *  slot_time_remain
                            task_remain_need_time = task_on_transmit_local[iot_index]['remain'] / tran_iot_camp
                            task_on_transmit_local[iot_index]['remain'] = 0
                            slot_time_remain = slot_time_remain - task_remain_need_time 
                            #print(f"{task_on_transmit_local[iot_index]['task_arrive_time']}时刻的任务传输完成,",j + 1 - slot_time_remain)
                            
                            tmp_tran = {'function_id':task_on_transmit_local[iot_index]['function_id'],
                                'data_size':task_on_transmit_local[iot_index]['data_size'], 
                                'cpu_cycle': task_on_transmit_local[iot_index]['cpu_cycle'], 
                                'task_arrive_time': task_on_transmit_local[iot_index]['task_arrive_time'],
                                'max_delay': task_on_transmit_local[iot_index]['max_delay'],
                                'tran_finish_time': (j + 1 - slot_time_remain)   #为的是云边服务器加一个判断条件，j + 1 - slot_time_remain ==任务开始的时隙要大于tran_finish_time，不大的话，先空闲等待，取任务的时候，不能一棍子直接使得slot_time_remain = 0
                                }
                            if tmp_tran['function_id']==-1:
                                print("传输了一个无效任务，还把时间写入了")
                                
                            transing_process_delay[iot_index][time_index][0] = (j + 1 - slot_time_remain - 
                                                                                task_on_transmit_local[iot_index]['task_arrive_time']
                                                                                - wait_trans_process_delay[iot_index][time_index][0])
                            id_index = tmp_tran['function_id']
                            cpu_size = tmp_tran['cpu_cycle']
                            if tran_index_flag == 1 or tran_index_flag ==2:
                                tran_index = tran_index_flag - 1
                                Queue_edge_comp[iot_index][tran_index].put(tmp_tran)
                                #print(f"{task_on_transmit_local[iot_index]['task_arrive_time']}时刻的任务传输完成,放入边缘{tran_index}待执行队列",j + 1 - slot_time_remain )
                                all_task_wait_edge_comp_count[iot_index][tran_index][id_index] += 1
                                per_task_wait_edge_comp_count_cpu_cycle[iot_index][tran_index][id_index] += cpu_size
                                all_task_wait_edge_comp_size_cpu_cycle[iot_index][tran_index] += cpu_size
                            elif tran_index_flag == 3:
                                tran_index = tran_index_flag - 3
                                Queue_cloud_comp[iot_index][tran_index].put(tmp_tran)
                                #print(f"{task_on_transmit_local[iot_index]['task_arrive_time']}时刻的任务传输完成,放入云{tran_index}待执行队列",j + 1 - slot_time_remain )
                                all_task_wait_cloud_comp_count[iot_index][tran_index][id_index] += 1
                                per_task_wait_cloud_comp_count_cpu_cycle[iot_index][tran_index][id_index] += cpu_size
                                all_task_wait_cloud_comp_size_cpu_cycle[iot_index][tran_index] += cpu_size
                            else:
                                print("传输的动作不对")
                            task_on_transmit_local[iot_index]['function_id'] = -1
                            task_on_transmit_local[iot_index]['data_size'] = 0
                            task_on_transmit_local[iot_index]['cpu_cycle'] = 0
                            task_on_transmit_local[iot_index]['task_arrive_time']   = 0
                            task_on_transmit_local[iot_index]['iot_action'] = -1
                            task_on_transmit_local[iot_index]['max_delay'] = 0
                            task_on_transmit_local[iot_index]['remain'] = 0
                if task_remain_time <= slot_time_remain and task_on_transmit_local[iot_index]['function_id'] != -1 :
                    task_on_transmit_local[iot_index]['remain'] = task_on_transmit_local[iot_index]['remain'] - tran_iot_camp *  task_remain_time
                    if task_on_transmit_local[iot_index]['remain'] < 0:
                        task_on_transmit_local[iot_index]['remain'] = task_on_transmit_local[iot_index]['remain'] + tran_iot_camp *  task_remain_time
                        task_remain_need_time = task_on_transmit_local[iot_index]['remain'] / tran_iot_camp
                        task_on_transmit_local[iot_index]['remain'] = 0
                        slot_time_remain = slot_time_remain - task_remain_need_time
                        #print(f"{task_on_transmit_local[iot_index]['task_arrive_time']}时刻的任务 最大时延内可以传输完，并仍有剩余时间执行",j + 1 - slot_time_remain)
                        tmp_tran = {'function_id':task_on_transmit_local[iot_index]['function_id'],
                                'data_size':task_on_transmit_local[iot_index]['data_size'], 
                                'cpu_cycle': task_on_transmit_local[iot_index]['cpu_cycle'], 
                                'task_arrive_time': task_on_transmit_local[iot_index]['task_arrive_time'],
                                'max_delay': task_on_transmit_local[iot_index]['max_delay'],
                                'tran_finish_time': (j + 1 - slot_time_remain)   #为的是云边服务器加一个判断条件，j + 1 - slot_time_remain ==任务开始的时隙要大于tran_finish_time，不大的话，先空闲等待，取任务的时候，不能一棍子直接使得slot_time_remain = 0
                                }
                        if tmp_tran['function_id']==-1:
                                print("传输了一个无效任务1，还把时间写入了")
                                
                        transing_process_delay[iot_index][time_index][0] = (j + 1 - slot_time_remain - 
                                                                            task_on_transmit_local[iot_index]['task_arrive_time']
                                                                            - wait_trans_process_delay[iot_index][time_index][0])
                        id_index = tmp_tran['function_id']
                        cpu_size = tmp_tran['cpu_cycle']
                        if tran_index_flag == 1 or tran_index_flag ==2:
                            tran_index = tran_index_flag - 1
                            Queue_edge_comp[iot_index][tran_index].put(tmp_tran)
                            #print(f"{task_on_transmit_local[iot_index]['task_arrive_time']}时刻的任务传输完成,放入边缘{tran_index}待执行队列",j + 1 - slot_time_remain )
                            all_task_wait_edge_comp_count[iot_index][tran_index][id_index] += 1
                            per_task_wait_edge_comp_count_cpu_cycle[iot_index][tran_index][id_index] += cpu_size
                            all_task_wait_edge_comp_size_cpu_cycle[iot_index][tran_index] += cpu_size
                        elif tran_index_flag == 3:
                            tran_index = tran_index_flag - 3
                            Queue_cloud_comp[iot_index][tran_index].put(tmp_tran)
                            #print(f"{task_on_transmit_local[iot_index]['task_arrive_time']}时刻的任务传输完成,放入云{tran_index}待执行队列",j + 1 - slot_time_remain )
                            all_task_wait_cloud_comp_count[iot_index][tran_index][id_index] += 1
                            per_task_wait_cloud_comp_count_cpu_cycle[iot_index][tran_index][id_index] += cpu_size
                            all_task_wait_cloud_comp_size_cpu_cycle[iot_index][tran_index] += cpu_size
                        else:
                            print("传输的动作不对")
                        task_on_transmit_local[iot_index]['function_id'] = -1
                        task_on_transmit_local[iot_index]['data_size'] = 0
                        task_on_transmit_local[iot_index]['cpu_cycle'] = 0
                        task_on_transmit_local[iot_index]['task_arrive_time']   = 0
                        task_on_transmit_local[iot_index]['iot_action'] = -1
                        task_on_transmit_local[iot_index]['remain'] = 0
                        task_on_transmit_local[iot_index]['max_delay'] = 0
                        
                    if task_on_transmit_local[iot_index]['remain'] >= 0:
                        slot_time_remain = slot_time_remain - task_remain_time
                        #print(f"{task_on_transmit_local[iot_index]['task_arrive_time']}时刻的任务 最大时延的时，一定传输不完或者刚好传输完，都算是传输失败,",j + 1 - slot_time_remain)
                        transing_process_delay[iot_index][time_index][0] = (j + 1 - slot_time_remain - 
                                                                                task_on_transmit_local[iot_index]['task_arrive_time']
                                                                                - wait_trans_process_delay[iot_index][time_index][0])
                        unfinish_indi[iot_index][time_index][0] = 2   #传输失败
                        computing_process_delay[iot_index][time_index][0] = 0
                        delay_list[iot_index][time_index][0] = j + 1 - slot_time_remain - task_on_transmit_local[iot_index]['task_arrive_time']
                        energy_list[iot_index][time_index][0] = tr_power * transing_process_delay[iot_index][time_index][0]
                        expense_list[iot_index][time_index][0] = 0.01 * 2 * computing_process_delay[iot_index][time_index][0] + 6e-5
                        task_on_transmit_local[iot_index]['function_id'] = -1
                        task_on_transmit_local[iot_index]['data_size'] = 0
                        task_on_transmit_local[iot_index]['cpu_cycle'] = 0
                        task_on_transmit_local[iot_index]['task_arrive_time']   = 0
                        task_on_transmit_local[iot_index]['iot_action'] = -1
                        task_on_transmit_local[iot_index]['remain'] = 0
                        task_on_transmit_local[iot_index]['max_delay'] = 0
            if task_on_transmit_local[iot_index]['function_id'] == -1 and task_on_transmit_local[iot_index]['remain'] ==0 and  Queue_iot_tran[iot_index].empty():
                ##print("任务是在时隙初来的，不会在中间来传输任务")
                #slot_time_remain = slot_time_remain - 1/100
                #slot_time_remain = np.max([slot_time_remain,0])
                slot_time_remain = 0                        
    
    #边缘执行器                        
    for iot_index in range(n_iot):
        for edge_index in range(n_edge):
            slot_time_remain = 1 
            while slot_time_remain >0:
                #因为前面的传输，已经执行到当前时隙的结束了，因此Queue_edge_comp[iot_index][edge_index].empty()作为判断条件，不太适合
                if task_on_process_edge[iot_index][edge_index]['remain'] == 0 and Queue_edge_comp[iot_index][edge_index].empty():
                    slot_time_remain = 0
                if task_on_process_edge[iot_index][edge_index]['remain'] == 0 and (not Queue_edge_comp[iot_index][edge_index].empty()):  
                    while not Queue_edge_comp[iot_index][edge_index].empty():  
                        get_task =   Queue_edge_comp[iot_index][edge_index].get()   
                        id_index = int(get_task['function_id'])
                        time_index = int(get_task['task_arrive_time'])
                        if time_index == 0:
                            print(f"边缘取任务{edge_index}",slot_time_remain,get_task)
                        if  j + 1 - slot_time_remain <= get_task['tran_finish_time']:
                            slot_time_remain = j + 1 - get_task['tran_finish_time']
                        else:
                            slot_time_remain = slot_time_remain
                        #print(f"{get_task['task_arrive_time']}时刻的任务,从边缘{edge_index}待执行队列中取出",j + 1 - slot_time_remain,"任务进入边缘{edge_index}待执行队列的时间",get_task['tran_finish_time'])
                        if j + 1 - slot_time_remain < get_task['tran_finish_time']:
                            #print("边缘取任务的时间比任务还早!!!!!!")
                            #slot_time_remain = j + 1 - get_task['tran_finish_time']
                            return 
                        all_task_wait_edge_comp_count[iot_index][edge_index][id_index] -= 1
                        per_task_wait_edge_comp_count_cpu_cycle[iot_index][edge_index][id_index] -= get_task['cpu_cycle']
                        all_task_wait_edge_comp_size_cpu_cycle[iot_index][edge_index] -= get_task['cpu_cycle']
                        wait_comp_process_delay[iot_index][time_index][0] = j + 1 - slot_time_remain - get_task['tran_finish_time']
                        if j + 1 - slot_time_remain - get_task['task_arrive_time'] >= get_task['max_delay']:
                            #print(f"{get_task['task_arrive_time']}时刻的任务 边缘 {edge_index} 等待执行超时 而不会执行,失败") 
                            cold_count_list[iot_index][time_index][0] = 2
                            cold_start_delay[iot_index][time_index][0] = 0
                            computing_process_delay[iot_index][time_index][0] = 0
                            unfinish_indi[iot_index][time_index][0] = 3
                            delay_list[iot_index][time_index][0] = j + 1 - slot_time_remain - get_task['task_arrive_time']
                            energy_list[iot_index][time_index][0] = (tr_power * transing_process_delay[iot_index][time_index][0] 
                                                    + esc * ((comp_cap_edge[edge_index] / edge_count[0][edge_index]) ** 2) * ((computing_process_delay[iot_index][time_index][0]+cold_start_delay[iot_index][time_index][0])))
                            if edge_count[0][edge_index] == 0:
                                print("有任务在边缘执行，任务在当前的边缘统计的数据为0；是错误的")
                            expense_list[iot_index][time_index][0] = 0.01 * 2 * computing_process_delay[iot_index][time_index][0] + 6e-5  
                        else:
                            #print(f"{get_task['task_arrive_time']}时刻的任务 边缘 {edge_index} 没有等待执行 超时 下一步，冷热启动",j + 1 - slot_time_remain) 
                            task_on_process_edge[iot_index][edge_index]['function_id'] = get_task['function_id']
                            task_on_process_edge[iot_index][edge_index]['data_size'] = get_task['function_id']
                            task_on_process_edge[iot_index][edge_index]['cpu_cycle'] = get_task['cpu_cycle']
                            task_on_process_edge[iot_index][edge_index]['max_delay'] = get_task['max_delay']
                            task_on_process_edge[iot_index][edge_index]['task_arrive_time'] = get_task['task_arrive_time']
                            task_on_process_edge[iot_index][edge_index]['tran_finish_time'] = get_task['tran_finish_time']
                            #task_on_process_edge[iot_index][edge_index]['flag'] = get_task['function_id']
                            task_on_process_edge[iot_index][edge_index]['remain'] = get_task['cpu_cycle']
                            if j + 1 - slot_time_remain - edge_pool[edge_index][iot_index][id_index] < keep_alive[id_index] and edge_pool[edge_index][iot_index][id_index] != 0:
                                cold_count_list[iot_index][time_index][0] = 0
                                cold_start_delay[iot_index][time_index][0] = 0
                                task_on_process_edge[iot_index][edge_index]['flag'] = 0
                                edge_pool[edge_index][iot_index][id_index] = np.max([j + 1 - slot_time_remain,edge_pool[edge_index][iot_index][id_index]])
                                #print(f"{get_task['task_arrive_time']}时刻的任务 边缘 {edge_index} 热启动  ",j + 1 - slot_time_remain)
                            if j + 1 - slot_time_remain - edge_pool[edge_index][iot_index][id_index] >= keep_alive[id_index] or edge_pool[edge_index][iot_index][id_index] == 0:
                                cold_count_list[iot_index][time_index][0] = 1
                                cold_start_delay[iot_index][time_index][0] = task_on_process_edge[iot_index][edge_index]['data_size'] / pull_uplink_rate_edge
                                task_on_process_edge[iot_index][edge_index]['flag'] = cold_start_delay[iot_index][time_index][0]
                                #print(f"{get_task['task_arrive_time']}时刻的任务 边缘 {edge_index} 冷启动启动  ",j + 1 - slot_time_remain)
                            break
                if slot_time_remain > 0 and task_on_process_edge[iot_index][edge_index]['remain'] > 0 and task_on_process_edge[iot_index][edge_index]['flag'] >0:
                    #print(f"{task_on_process_edge[iot_index][edge_index]['task_arrive_time']}时刻的任务 边缘 {edge_index} 冷启动启动中，，，，  ",j + 1 - slot_time_remain)
                    task_on_process_edge[iot_index][edge_index]['flag'] -= slot_time_remain
                    id_index = task_on_process_edge[iot_index][edge_index]['function_id']
                    time_index = task_on_process_edge[iot_index][edge_index]['task_arrive_time']
                    if time_index == 0:
                            print("边缘取冷启动",slot_time_remain)
                    if task_on_process_edge[iot_index][edge_index]['flag'] > 0:
                        slot_time_remain = 0
                    if task_on_process_edge[iot_index][edge_index]['flag'] <= 0:
                        slot_time_remain = -task_on_process_edge[iot_index][edge_index]['flag']
                        if j + 1 - slot_time_remain - task_on_process_edge[iot_index][edge_index]['task_arrive_time'] >= task_on_process_edge[iot_index][edge_index]['max_delay']:
                            #print(f"{task_on_process_edge[iot_index][edge_index]['task_arrive_time']}时刻的任务 边缘 {edge_index} 冷启动 失败  ",j + 1 - slot_time_remain)
                            unfinish_indi[iot_index][time_index][0] = 4
                            computing_process_delay[iot_index][time_index][0] = 0
                            delay_list[iot_index][time_index][0] = j + 1 - slot_time_remain - task_on_process_edge[iot_index][edge_index]['task_arrive_time']
                            energy_list[iot_index][time_index][0] = (tr_power * transing_process_delay[iot_index][time_index][0] 
                                                    + esc * ((comp_cap_edge[edge_index] / edge_count[0][edge_index]) ** 2) * ((computing_process_delay[iot_index][time_index][0]+cold_start_delay[iot_index][time_index][0])))
                            if edge_count[0][edge_index] == 0:
                                print("有任务在边缘执行，任务在当前的边缘统计的数据为0；是错误的，2")
                            expense_list[iot_index][time_index][0] = 0.01 * 2 * computing_process_delay[iot_index][time_index][0] + 6e-5
                            task_on_process_edge[iot_index][edge_index]['function_id'] = -1
                            task_on_process_edge[iot_index][edge_index]['data_size'] = 0
                            task_on_process_edge[iot_index][edge_index]['cpu_cycle'] = 0
                            task_on_process_edge[iot_index][edge_index]['task_arrive_time'] = 0
                            task_on_process_edge[iot_index][edge_index]['tran_finish_time'] = 0
                            task_on_process_edge[iot_index][edge_index]['flag'] = 0
                            task_on_process_edge[iot_index][edge_index]['remain'] = 0
                            task_on_process_edge[iot_index][edge_index]['max_delay'] = 0
                            edge_pool[edge_index][iot_index][id_index] = np.max([j + 1 - slot_time_remain,edge_pool[edge_index][iot_index][id_index]])
                        else:
                            #print(f"{task_on_process_edge[iot_index][edge_index]['task_arrive_time']}时刻的任务 边缘 {edge_index} 冷启动结束  ",j + 1 - slot_time_remain)
                            task_on_process_edge[iot_index][edge_index]['flag'] = 0
                            edge_pool[edge_index][iot_index][id_index] = np.max([j + 1 - slot_time_remain,edge_pool[edge_index][iot_index][id_index]])
                if slot_time_remain > 0 and task_on_process_edge[iot_index][edge_index]['remain'] > 0 and task_on_process_edge[iot_index][edge_index]['flag'] ==0:    
                    #print(f"{task_on_process_edge[iot_index][edge_index]['task_arrive_time']}时刻的任务 边缘 {edge_index} 执行中，，  ",j + 1 - slot_time_remain)  
                    id_index = task_on_process_edge[iot_index][edge_index]['function_id']
                    time_index = task_on_process_edge[iot_index][edge_index]['task_arrive_time'] 
                    if time_index == 0:
                            print("边缘执行",slot_time_remain)
                    task_remain_time =  task_on_process_edge[iot_index][edge_index]['max_delay'] -(j + 1 - slot_time_remain - task_on_process_edge[iot_index][edge_index]['task_arrive_time'])
                    #print(f"{task_on_process_edge[iot_index][edge_index]['task_arrive_time']}时刻的任务 边缘 {edge_index} 执行中，，  ",task_remain_time , slot_time_remain)  
                    if edge_count[0][edge_index] == 0:
                                print("有任务在边缘执行，任务在当前的边缘统计的数据为0；是错误的，3",slot_time_remain,task_on_process_edge[iot_index][edge_index]['remain'] ,(not Queue_edge_comp[iot_index][edge_index].empty()))
                    if task_remain_time >= slot_time_remain:
                        task_on_process_edge[iot_index][edge_index]['remain'] = task_on_process_edge[iot_index][edge_index]['remain'] - (comp_cap_edge[edge_index] / edge_count[0][edge_index]) * slot_time_remain
                        if task_on_process_edge[iot_index][edge_index]['remain'] > 0:
                            slot_time_remain = 0
                            edge_pool[edge_index][iot_index][id_index] = np.max([j + 1 - slot_time_remain,edge_pool[edge_index][iot_index][id_index]])
                        if task_on_process_edge[iot_index][edge_index]['remain'] <= 0:
                            task_on_process_edge[iot_index][edge_index]['remain'] = task_on_process_edge[iot_index][edge_index]['remain'] + (comp_cap_edge[edge_index] / edge_count[0][edge_index]) * slot_time_remain
                            task_remain_need_time = task_on_process_edge[iot_index][edge_index]['remain'] / (comp_cap_edge[edge_index] / edge_count[0][edge_index])
                            task_on_process_edge[iot_index][edge_index]['remain'] = 0
                            slot_time_remain = slot_time_remain - task_remain_need_time 
                            unfinish_indi[iot_index][time_index][0] = 0
                            #print(f"{task_on_process_edge[iot_index][edge_index]['task_arrive_time']}时刻的任务边缘{edge_index}执行完成",j + 1 - slot_time_remain) 
                            computing_process_delay[iot_index][time_index][0] = task_on_process_edge[iot_index][edge_index]['cpu_cycle'] / (comp_cap_edge[edge_index] / edge_count[0][edge_index])
                            delay_list[iot_index][time_index][0] = j + 1 - slot_time_remain - task_on_process_edge[iot_index][edge_index]['task_arrive_time']
                            energy_list[iot_index][time_index][0] = (tr_power * transing_process_delay[iot_index][time_index][0] 
                                                    + esc * ((comp_cap_edge[edge_index] / edge_count[0][edge_index]) ** 2) * ((computing_process_delay[iot_index][time_index][0]+cold_start_delay[iot_index][time_index][0])))
                            expense_list[iot_index][time_index][0] = 0.01 * 2 * computing_process_delay[iot_index][time_index][0] + 6e-5
                            task_on_process_edge[iot_index][edge_index]['function_id'] = -1
                            task_on_process_edge[iot_index][edge_index]['data_size'] = 0
                            task_on_process_edge[iot_index][edge_index]['cpu_cycle'] = 0
                            task_on_process_edge[iot_index][edge_index]['task_arrive_time'] = 0
                            task_on_process_edge[iot_index][edge_index]['tran_finish_time'] = 0
                            task_on_process_edge[iot_index][edge_index]['flag'] = 0
                            task_on_process_edge[iot_index][edge_index]['remain'] = 0
                            task_on_process_edge[iot_index][edge_index]['max_delay'] = 0
                            edge_pool[edge_index][iot_index][id_index] = np.max([j + 1 - slot_time_remain,edge_pool[edge_index][iot_index][id_index]])
                    if task_remain_time < slot_time_remain: 
                        task_on_process_edge[iot_index][edge_index]['remain'] = task_on_process_edge[iot_index][edge_index]['remain'] - (comp_cap_edge[edge_index] / edge_count[0][edge_index]) * task_remain_time
                          
                        if task_on_process_edge[iot_index][edge_index]['remain'] <= 0:
                            if task_on_process_edge[iot_index][edge_index]['remain'] == 0:
                                
                                slot_time_remain = slot_time_remain - task_remain_time 
                                ##print(f"{task_on_process_edge[iot_index][edge_index]['task_arrive_time']}时刻的任务边缘{edge_index}执行完成",j + 1 - slot_time_remain)
                            if task_on_process_edge[iot_index][edge_index]['remain'] < 0:
                                task_on_process_edge[iot_index][edge_index]['remain'] = task_on_process_edge[iot_index][edge_index]['remain'] + (comp_cap_edge[edge_index] / edge_count[0][edge_index]) * task_remain_time
                                task_remain_need_time = task_on_process_edge[iot_index][edge_index]['remain'] / (comp_cap_edge[edge_index] / edge_count[0][edge_index])
                                if edge_count[0][edge_index] == 0:
                                    print("有任务在边缘执行，任务在当前的边缘统计的数据为0；是错误的，5")
                                task_on_process_edge[iot_index][edge_index]['remain'] = 0
                                slot_time_remain = slot_time_remain - task_remain_need_time
                            unfinish_indi[iot_index][time_index][0] = 0
                            #print(f"{task_on_process_edge[iot_index][edge_index]['task_arrive_time']}时刻的任务边缘{edge_index}执行完2",j + 1 - slot_time_remain)
                            computing_process_delay[iot_index][time_index][0] = task_on_process_edge[iot_index][edge_index]['cpu_cycle'] / (comp_cap_edge[edge_index] / edge_count[0][edge_index])
                            delay_list[iot_index][time_index][0] = j + 1 - slot_time_remain - task_on_process_edge[iot_index][edge_index]['task_arrive_time']
                            energy_list[iot_index][time_index][0] = (tr_power * transing_process_delay[iot_index][time_index][0] 
                                                    + esc * ((comp_cap_edge[edge_index] / edge_count[0][edge_index]) ** 2) * ((computing_process_delay[iot_index][time_index][0]+cold_start_delay[iot_index][time_index][0])))
                            if edge_count[0][edge_index] == 0:
                                print("有任务在边缘执行，任务在当前的边缘统计的数据为0；是错误的，6")
                            expense_list[iot_index][time_index][0] = 0.01 * 2 * computing_process_delay[iot_index][time_index][0] + 6e-5
                            task_on_process_edge[iot_index][edge_index]['function_id'] = -1
                            task_on_process_edge[iot_index][edge_index]['data_size'] = 0
                            task_on_process_edge[iot_index][edge_index]['cpu_cycle'] = 0
                            task_on_process_edge[iot_index][edge_index]['task_arrive_time'] = 0
                            task_on_process_edge[iot_index][edge_index]['tran_finish_time'] = 0
                            task_on_process_edge[iot_index][edge_index]['flag'] = 0
                            task_on_process_edge[iot_index][edge_index]['remain'] = 0
                            task_on_process_edge[iot_index][edge_index]['max_delay'] = 0
                            edge_pool[edge_index][iot_index][id_index] = np.max([j + 1 - slot_time_remain,edge_pool[edge_index][iot_index][id_index]])
                        if task_on_process_edge[iot_index][edge_index]['remain'] > 0:
                            
                            slot_time_remain = slot_time_remain - task_remain_time
                            #print(f"{task_on_process_edge[iot_index][edge_index]['task_arrive_time']}时刻的任务边缘{edge_index}执行失败1",j + 1 - slot_time_remain)
                            unfinish_indi[iot_index][time_index][0] = 5
                            computing_process_delay[iot_index][time_index][0] = (task_on_process_edge[iot_index][edge_index]['cpu_cycle'] - task_on_process_edge[iot_index][edge_index]['remain']) / (comp_cap_edge[edge_index] / edge_count[0][edge_index])
                            delay_list[iot_index][time_index][0] = j + 1 - slot_time_remain - task_on_process_edge[iot_index][edge_index]['task_arrive_time']
                            energy_list[iot_index][time_index][0] = (tr_power * transing_process_delay[iot_index][time_index][0] 
                                                    + esc * ((comp_cap_edge[edge_index] / edge_count[0][edge_index]) ** 2) * ((computing_process_delay[iot_index][time_index][0]+cold_start_delay[iot_index][time_index][0])))
                            if edge_count[0][edge_index] == 0:
                                print("有任务在边缘执行，任务在当前的边缘统计的数据为0；是错误的，7")
                            expense_list[iot_index][time_index][0] = 0.01 * 2 * computing_process_delay[iot_index][time_index][0] + 6e-5
                            task_on_process_edge[iot_index][edge_index]['function_id'] = -1
                            task_on_process_edge[iot_index][edge_index]['data_size'] = 0
                            task_on_process_edge[iot_index][edge_index]['cpu_cycle'] = 0
                            task_on_process_edge[iot_index][edge_index]['task_arrive_time'] = 0
                            task_on_process_edge[iot_index][edge_index]['tran_finish_time'] = 0
                            task_on_process_edge[iot_index][edge_index]['flag'] = 0
                            task_on_process_edge[iot_index][edge_index]['remain'] = 0
                            task_on_process_edge[iot_index][edge_index]['max_delay'] = 0
                            edge_pool[edge_index][iot_index][id_index] = np.max([j + 1 - slot_time_remain,edge_pool[edge_index][iot_index][id_index]]) 
    
    #云执行器
    for iot_index in range(n_iot):
        for cloud_index in range(n_cloud):
            slot_time_remain = 1 
            while slot_time_remain >0:
                if task_on_process_cloud[iot_index][cloud_index]['remain'] == 0 and Queue_cloud_comp[iot_index][cloud_index].empty():
                    slot_time_remain = 0
                if task_on_process_cloud[iot_index][cloud_index]['remain'] == 0 and (not Queue_cloud_comp[iot_index][cloud_index].empty()):  
                    while not Queue_cloud_comp[iot_index][cloud_index].empty():  
                        get_task =   Queue_cloud_comp[iot_index][cloud_index].get()   
                        id_index = int(get_task['function_id'])
                        time_index = int(get_task['task_arrive_time'])
                        if time_index == 0:
                            print("云取任务",slot_time_remain)
                        if  j + 1 - slot_time_remain <= get_task['tran_finish_time']:
                            slot_time_remain = j + 1 - get_task['tran_finish_time']
                        else:
                            slot_time_remain = slot_time_remain
                        #print(f"{get_task['task_arrive_time']}时刻的任务,从云{cloud_index}待执行队列中取出",j + 1 - slot_time_remain,"任务进入云{cloud_index}待执行队列的时间",get_task['tran_finish_time'])
                        if j + 1 - slot_time_remain < get_task['tran_finish_time']:
                            #print("边缘取任务的时间比任务还早!!!!!!")
                            #slot_time_remain = j + 1 - get_task['tran_finish_time']
                            return 
                        all_task_wait_cloud_comp_count[iot_index][cloud_index][id_index] -= 1
                        per_task_wait_cloud_comp_count_cpu_cycle[iot_index][cloud_index][id_index] -= get_task['cpu_cycle']
                        all_task_wait_cloud_comp_size_cpu_cycle[iot_index][cloud_index] -= get_task['cpu_cycle']
                        wait_comp_process_delay[iot_index][time_index][0] = j + 1 - slot_time_remain - get_task['tran_finish_time']
                        if j + 1 - slot_time_remain - get_task['task_arrive_time'] >= get_task['max_delay']:
                            #print(f"{get_task['task_arrive_time']}时刻的任务,云{cloud_index} 等待执行超时 而不会执行",j + 1 - slot_time_remain) 
                            cold_count_list[iot_index][time_index][0] = 2
                            cold_start_delay[iot_index][time_index][0] = 0
                            computing_process_delay[iot_index][time_index][0] = 0
                            unfinish_indi[iot_index][time_index][0] = 3
                            delay_list[iot_index][time_index][0] = j + 1 - slot_time_remain - get_task['task_arrive_time']
                            energy_list[iot_index][time_index][0] = (tr_power * transing_process_delay[iot_index][time_index][0] 
                                                    + esc * (comp_cap_cloud[cloud_index] ** 2) * ((computing_process_delay[iot_index][time_index][0]+cold_start_delay[iot_index][time_index][0])))
                            expense_list[iot_index][time_index][0] = 0.01 * 2 * computing_process_delay[iot_index][time_index][0] + 6e-5  
                        else:
                            #print(f"{get_task['task_arrive_time']}时刻的任务,云{cloud_index} 没有等待执行 超时 下一步，冷热启动",j + 1 - slot_time_remain)  
                            task_on_process_cloud[iot_index][cloud_index]['function_id'] = get_task['function_id']
                            task_on_process_cloud[iot_index][cloud_index]['data_size'] = get_task['function_id']
                            task_on_process_cloud[iot_index][cloud_index]['cpu_cycle'] = get_task['cpu_cycle']
                            task_on_process_cloud[iot_index][cloud_index]['max_delay'] = get_task['max_delay']
                            task_on_process_cloud[iot_index][cloud_index]['task_arrive_time'] = get_task['task_arrive_time']
                            task_on_process_cloud[iot_index][cloud_index]['tran_finish_time'] = get_task['tran_finish_time']
                            #task_on_process_cloud[iot_index][cloud_index]['flag'] = get_task['function_id']
                            task_on_process_cloud[iot_index][cloud_index]['remain'] = get_task['cpu_cycle']
                            if j + 1 - slot_time_remain - cloud_pool[cloud_index][iot_index][id_index] < keep_alive[id_index] and cloud_pool[cloud_index][iot_index][id_index] != 0:
                                cold_count_list[iot_index][time_index][0] = 0
                                cold_start_delay[iot_index][time_index][0] = 0
                                task_on_process_cloud[iot_index][cloud_index]['flag'] = 0
                                cloud_pool[cloud_index][iot_index][id_index] = np.max([j + 1 - slot_time_remain,cloud_pool[cloud_index][iot_index][id_index]])
                                
                                #print(f"{get_task['task_arrive_time']}时刻的任务,云{cloud_index} 热启动",j + 1 - slot_time_remain) 
                            if j + 1 - slot_time_remain - cloud_pool[cloud_index][iot_index][id_index] >= keep_alive[id_index] or cloud_pool[cloud_index][iot_index][id_index] == 0:
                                cold_count_list[iot_index][time_index][0] = 1
                                cold_start_delay[iot_index][time_index][0] = task_on_process_cloud[iot_index][cloud_index]['data_size'] / pull_uplink_rate_cloud
                                task_on_process_cloud[iot_index][cloud_index]['flag'] = cold_start_delay[iot_index][time_index][0]
                                #print(f"{get_task['task_arrive_time']}时刻的任务,云{cloud_index} 冷启动启动",j + 1 - slot_time_remain) 
                            break
                if slot_time_remain > 0 and task_on_process_cloud[iot_index][cloud_index]['remain'] > 0 and task_on_process_cloud[iot_index][cloud_index]['flag'] >0:
                    #print(f"{task_on_process_cloud[iot_index][cloud_index]['task_arrive_time']}时刻的任务,云{cloud_index} 冷启动启动,,,,",j + 1 - slot_time_remain) 
                    task_on_process_cloud[iot_index][cloud_index]['flag'] -= slot_time_remain
                    id_index = task_on_process_cloud[iot_index][cloud_index]['function_id']
                    time_index = task_on_process_cloud[iot_index][cloud_index]['task_arrive_time']
                    if time_index == 0:
                            print("云取冷启动",slot_time_remain)
                    if task_on_process_cloud[iot_index][cloud_index]['flag'] > 0:
                        slot_time_remain = 0
                    if task_on_process_cloud[iot_index][cloud_index]['flag'] <= 0:
                        slot_time_remain = -task_on_process_cloud[iot_index][cloud_index]['flag']
                        if j + 1 - slot_time_remain - task_on_process_cloud[iot_index][cloud_index]['task_arrive_time'] >= task_on_process_cloud[iot_index][cloud_index]['max_delay']:
                            #print(f"{task_on_process_cloud[iot_index][cloud_index]['task_arrive_time']}时刻的任务,云{cloud_index} 冷启动 失败 ",j + 1 - slot_time_remain)
                            unfinish_indi[iot_index][time_index][0] = 4
                            computing_process_delay[iot_index][time_index][0] = 0
                            delay_list[iot_index][time_index][0] = j + 1 - slot_time_remain - task_on_process_cloud[iot_index][cloud_index]['task_arrive_time']
                            energy_list[iot_index][time_index][0] = (tr_power * transing_process_delay[iot_index][time_index][0] 
                                                    + esc * (comp_cap_cloud[cloud_index] ** 2) * ((computing_process_delay[iot_index][time_index][0]+cold_start_delay[iot_index][time_index][0])))
                            expense_list[iot_index][time_index][0] = 0.01 * 2 * computing_process_delay[iot_index][time_index][0] + 6e-5
                            task_on_process_cloud[iot_index][cloud_index]['function_id'] = -1
                            task_on_process_cloud[iot_index][cloud_index]['data_size'] = 0
                            task_on_process_cloud[iot_index][cloud_index]['cpu_cycle'] = 0
                            task_on_process_cloud[iot_index][cloud_index]['task_arrive_time'] = 0
                            task_on_process_cloud[iot_index][cloud_index]['tran_finish_time'] = 0
                            task_on_process_cloud[iot_index][cloud_index]['flag'] = 0
                            task_on_process_cloud[iot_index][cloud_index]['remain'] = 0
                            task_on_process_cloud[iot_index][cloud_index]['max_delay'] = 0
                            cloud_pool[cloud_index][iot_index][id_index] = np.max([j + 1 - slot_time_remain,cloud_pool[cloud_index][iot_index][id_index]])
                        else:
                            #print(f"{task_on_process_cloud[iot_index][cloud_index]['task_arrive_time']}时刻的任务,云{cloud_index} 冷启动 结束 ",j + 1 - slot_time_remain)
                            task_on_process_cloud[iot_index][cloud_index]['flag'] = 0
                            cloud_pool[cloud_index][iot_index][id_index] = np.max([j + 1 - slot_time_remain,cloud_pool[cloud_index][iot_index][id_index]])
                if slot_time_remain > 0 and task_on_process_cloud[iot_index][cloud_index]['remain'] > 0 and task_on_process_cloud[iot_index][cloud_index]['flag'] ==0:    
                    #print(f"{task_on_process_cloud[iot_index][cloud_index]['task_arrive_time']}时刻的任务,云{cloud_index} 开始执行中，， ",j + 1 - slot_time_remain)  
                    id_index = task_on_process_cloud[iot_index][cloud_index]['function_id']
                    time_index = task_on_process_cloud[iot_index][cloud_index]['task_arrive_time'] 
                    if time_index == 0:
                            print("云取任务执行",slot_time_remain)
                    task_remain_time =  task_on_process_cloud[iot_index][cloud_index]['max_delay'] -(j + 1 - slot_time_remain - task_on_process_cloud[iot_index][cloud_index]['task_arrive_time'])
                    if task_remain_time >= slot_time_remain:
                        task_on_process_cloud[iot_index][cloud_index]['remain'] = task_on_process_cloud[iot_index][cloud_index]['remain'] - comp_cap_cloud[cloud_index] * slot_time_remain
                        if task_on_process_cloud[iot_index][cloud_index]['remain'] > 0:
                            slot_time_remain = 0
                            cloud_pool[cloud_index][iot_index][id_index] = np.max([j + 1 - slot_time_remain,cloud_pool[cloud_index][iot_index][id_index]])
                        if task_on_process_cloud[iot_index][cloud_index]['remain'] <= 0:
                            task_on_process_cloud[iot_index][cloud_index]['remain'] = task_on_process_cloud[iot_index][cloud_index]['remain'] + comp_cap_cloud[cloud_index] * slot_time_remain
                            task_remain_need_time = task_on_process_cloud[iot_index][cloud_index]['remain'] / comp_cap_cloud[cloud_index]
                            task_on_process_cloud[iot_index][cloud_index]['remain'] = 0
                            slot_time_remain = slot_time_remain - task_remain_need_time 
                            unfinish_indi[iot_index][time_index][0] = 0
                            #print(f"{task_on_process_cloud[iot_index][cloud_index]['task_arrive_time']}时刻的任务云{cloud_index}执行完1",j + 1 - slot_time_remain)
                            computing_process_delay[iot_index][time_index][0] = task_on_process_cloud[iot_index][cloud_index]['cpu_cycle'] / comp_cap_cloud[cloud_index]
                            delay_list[iot_index][time_index][0] = j + 1 - slot_time_remain - task_on_process_cloud[iot_index][cloud_index]['task_arrive_time']
                            energy_list[iot_index][time_index][0] = (tr_power * transing_process_delay[iot_index][time_index][0] 
                                                    + esc * (comp_cap_cloud[cloud_index] ** 2) * ((computing_process_delay[iot_index][time_index][0]+cold_start_delay[iot_index][time_index][0])))
                            expense_list[iot_index][time_index][0] = 0.01 * 2 * computing_process_delay[iot_index][time_index][0] + 6e-5
                            task_on_process_cloud[iot_index][cloud_index]['function_id'] = -1
                            task_on_process_cloud[iot_index][cloud_index]['data_size'] = 0
                            task_on_process_cloud[iot_index][cloud_index]['cpu_cycle'] = 0
                            task_on_process_cloud[iot_index][cloud_index]['task_arrive_time'] = 0
                            task_on_process_cloud[iot_index][cloud_index]['tran_finish_time'] = 0
                            task_on_process_cloud[iot_index][cloud_index]['flag'] = 0
                            task_on_process_cloud[iot_index][cloud_index]['remain'] = 0
                            task_on_process_cloud[iot_index][cloud_index]['max_delay'] = 0
                            cloud_pool[cloud_index][iot_index][id_index] = np.max([j + 1 - slot_time_remain,cloud_pool[cloud_index][iot_index][id_index]])
                    if task_remain_time < slot_time_remain: 
                        task_on_process_cloud[iot_index][cloud_index]['remain'] = task_on_process_cloud[iot_index][cloud_index]['remain'] - comp_cap_cloud[cloud_index] * task_remain_time
                          
                        if task_on_process_cloud[iot_index][cloud_index]['remain'] <= 0:
                            if task_on_process_cloud[iot_index][cloud_index]['remain'] == 0:
                                ##print("任务在最大时延内，刚好完成，任务是执行成功")
                                slot_time_remain = slot_time_remain - task_remain_time 
                            if task_on_process_cloud[iot_index][cloud_index]['remain'] < 0:
                                task_on_process_cloud[iot_index][cloud_index]['remain'] = task_on_process_cloud[iot_index][cloud_index]['remain'] + comp_cap_cloud[cloud_index] * task_remain_time
                                task_remain_need_time = task_on_process_cloud[iot_index][cloud_index]['remain'] / comp_cap_cloud[cloud_index]
                                task_on_process_cloud[iot_index][cloud_index]['remain'] = 0
                                slot_time_remain = slot_time_remain - task_remain_need_time
                            unfinish_indi[iot_index][time_index][0] = 0
                            #print(f"{task_on_process_cloud[iot_index][cloud_index]['task_arrive_time']}时刻的任务云{cloud_index}执行完1",j + 1 - slot_time_remain)
                            computing_process_delay[iot_index][time_index][0] = task_on_process_cloud[iot_index][cloud_index]['cpu_cycle'] / comp_cap_cloud[cloud_index]
                            delay_list[iot_index][time_index][0] = j + 1 - slot_time_remain - task_on_process_cloud[iot_index][cloud_index]['task_arrive_time']
                            energy_list[iot_index][time_index][0] = (tr_power * transing_process_delay[iot_index][time_index][0] 
                                                    + esc * (comp_cap_cloud[cloud_index] ** 2) * ((computing_process_delay[iot_index][time_index][0]+cold_start_delay[iot_index][time_index][0])))
                            expense_list[iot_index][time_index][0] = 0.01 * 2 * computing_process_delay[iot_index][time_index][0] + 6e-5
                            task_on_process_cloud[iot_index][cloud_index]['function_id'] = -1
                            task_on_process_cloud[iot_index][cloud_index]['data_size'] = 0
                            task_on_process_cloud[iot_index][cloud_index]['cpu_cycle'] = 0
                            task_on_process_cloud[iot_index][cloud_index]['task_arrive_time'] = 0
                            task_on_process_cloud[iot_index][cloud_index]['tran_finish_time'] = 0
                            task_on_process_cloud[iot_index][cloud_index]['flag'] = 0
                            task_on_process_cloud[iot_index][cloud_index]['remain'] = 0
                            task_on_process_cloud[iot_index][cloud_index]['max_delay'] = 0
                            cloud_pool[cloud_index][iot_index][id_index] = np.max([j + 1 - slot_time_remain,cloud_pool[cloud_index][iot_index][id_index]])
                        if task_on_process_cloud[iot_index][cloud_index]['remain'] > 0:
                            slot_time_remain = slot_time_remain - task_remain_time
                            #print(f"{task_on_process_cloud[iot_index][cloud_index]['task_arrive_time']}时刻的任务云{cloud_index}执行失败",j + 1 - slot_time_remain)
                            unfinish_indi[iot_index][time_index][0] = 5
                            computing_process_delay[iot_index][time_index][0] = (task_on_process_cloud[iot_index][cloud_index]['cpu_cycle'] - task_on_process_cloud[iot_index][cloud_index]['remain']) / comp_cap_cloud[cloud_index]
                            delay_list[iot_index][time_index][0] = j + 1 - slot_time_remain - task_on_process_cloud[iot_index][cloud_index]['task_arrive_time']
                            energy_list[iot_index][time_index][0] = (tr_power * transing_process_delay[iot_index][time_index][0] 
                                                    + esc * (comp_cap_cloud[cloud_index] ** 2) * ((computing_process_delay[iot_index][time_index][0]+cold_start_delay[iot_index][time_index][0])))
                            expense_list[iot_index][time_index][0] = 0.01 * 2 * computing_process_delay[iot_index][time_index][0] + 6e-5
                            task_on_process_cloud[iot_index][cloud_index]['function_id'] = -1
                            task_on_process_cloud[iot_index][cloud_index]['data_size'] = 0
                            task_on_process_cloud[iot_index][cloud_index]['cpu_cycle'] = 0
                            task_on_process_cloud[iot_index][cloud_index]['task_arrive_time'] = 0
                            task_on_process_cloud[iot_index][cloud_index]['tran_finish_time'] = 0
                            task_on_process_cloud[iot_index][cloud_index]['flag'] = 0
                            task_on_process_cloud[iot_index][cloud_index]['remain'] = 0
                            task_on_process_cloud[iot_index][cloud_index]['max_delay'] = 0
                            cloud_pool[cloud_index][iot_index][id_index] = np.max([j + 1 - slot_time_remain,cloud_pool[cloud_index][iot_index][id_index]])
                             
    #当前时隙结束：
    edge_count = np.zeros([1,n_edge])
    for edge_index in range(n_edge):
        #print("统计每个边缘通信的iot设备的数量")
        for iot_index in range(n_iot):
            if (task_on_transmit_local[iot_index]['remain'] > 0  and task_on_transmit_local[iot_index]['iot_action'] - 1 == edge_index) or (all_task_wait_iot_tran_edge_count[iot_index][edge_index] !=0 and  (not Queue_iot_tran[iot_index].empty())) or task_on_process_edge[iot_index][edge_index]['remain'] > 0 or (not Queue_edge_comp[iot_index][edge_index].empty()):
                edge_count[0][edge_index] += 1
                
    observation_all = np.zeros([n_iot, n_features-5])
    ##print(np.shape(observation_all),n_features_task,n_features_system_iot,n_features_system_edge,n_features_system_cloud,n_features)
    for iot_index in range(n_iot):
        #n_features_system_iot
        for n_task_type_index in range(n_task_type):
            #还有多少个未执行   0,0,0,...,0
            observation_all[iot_index, n_task_type_index] = all_task_wait_iot_comp_count[iot_index][n_task_type_index]
            #0*'cpu_cycle',0*'cpu_cycle',0*'cpu_cycle',...,0*'cpu_cycle'
            observation_all[iot_index, n_task_type * 1 + n_task_type_index] = per_task_wait_iot_comp_count_cpu_cycle[iot_index][n_task_type_index] 
            #还有多少个未传输  0,0,0,...,0
            observation_all[iot_index, n_task_type * 2 + n_task_type_index] = all_task_wait_iot_tran_count[iot_index][n_task_type_index]
            #0*'data_size',0*'data_size',0*'data_size',...,0*'data_size'
            observation_all[iot_index, n_task_type * 3 + n_task_type_index] = per_task_wait_iot_tran_count_size[iot_index][n_task_type_index]      
            observation_all[iot_index, n_task_type * 4 + n_task_type_index] = np.min([j+ 1 - iot_pool[iot_index][n_task_type_index] , keep_alive[n_task_type_index]])                
        observation_all[iot_index, n_task_type * 5] = all_task_wait_iot_comp_cpu_cycle[iot_index]
        observation_all[iot_index, n_task_type * 5 + 1] = task_on_process_local[iot_index]['remain']
        observation_all[iot_index, n_task_type * 5 + 2] = all_task_wait_iot_tran_size[iot_index]
        observation_all[iot_index, n_task_type * 5 + 3] = task_on_transmit_local[iot_index]['remain']
        observation_all[iot_index, n_task_type * 5 + 4] = pull_uplink_rate_iot
        observation_all[iot_index, n_task_type * 5 + 5] = comp_cap_iot[iot_index]
        for i in range(n_edge):
            observation_all[iot_index, n_task_type * 5 + 6 + i] = tran_edge_cap_iot[iot_index][i]
        for i in range(n_cloud):
            observation_all[iot_index, n_task_type * 5 + 6 + n_edge + i] = tran_cloud_cap_iot[iot_index][i]
        
        #n_features_system_edge_0
        observation_all[iot_index,n_task_type * 5 + 6 + n_edge + n_cloud] = pull_uplink_rate_edge
        observation_all[iot_index, n_task_type * 5 + 6 + n_edge + n_cloud + 1] =  edge_count[0][0]
        observation_all[iot_index, n_task_type * 5 + 6 + n_edge + n_cloud + 2] = all_task_wait_edge_comp_size_cpu_cycle[iot_index][0]
        observation_all[iot_index, n_task_type * 5 + 6 + n_edge + n_cloud + 3] = task_on_process_edge[iot_index][0]['remain']
        
        for n_task_type_index in range(n_task_type):
            observation_all[iot_index, n_task_type * 5 + 6 + n_edge + n_cloud + 4 + n_task_type_index] = all_task_wait_edge_comp_count[iot_index][0][n_task_type_index]
            observation_all[iot_index, n_task_type * 6 + 6 + n_edge + n_cloud + 4 + n_task_type_index] = per_task_wait_edge_comp_count_cpu_cycle[iot_index][0][n_task_type_index]
            temp_edge_pool = np.max(edge_pool[0][:,n_task_type_index])
            for iot_index in range(n_iot):
                edge_pool[0][iot_index][n_task_type_index] = temp_edge_pool
            observation_all[iot_index, n_task_type * 7 + 6 + n_edge + n_cloud + 4 + n_task_type_index] = np.min([j+ 1 - temp_edge_pool , keep_alive[n_task_type_index]])
    
        #n_features_system_edge_1                                                                        np.min([j+ 1 - edge_pool[0][n_task_type_index] , keep_alive[n_task_type_index]]) 
        observation_all[iot_index, n_task_type * 8 + 6 + n_edge + n_cloud + 4] = pull_uplink_rate_edge
        observation_all[iot_index, n_task_type * 8 + 6 + n_edge + n_cloud + 5] =  edge_count[0][1]
        observation_all[iot_index, n_task_type * 8 + 6 + n_edge + n_cloud + 6] = all_task_wait_edge_comp_size_cpu_cycle[iot_index][1]
        observation_all[iot_index, n_task_type * 8 + 6 + n_edge + n_cloud + 7] = task_on_process_edge[iot_index][1]['remain']
        for n_task_type_index in range(n_task_type):
            observation_all[iot_index, n_task_type * 8 + 6 + n_edge + n_cloud + 8 + n_task_type_index] = all_task_wait_edge_comp_count[iot_index][1][n_task_type_index]
            observation_all[iot_index, n_task_type * 9 + 6 + n_edge + n_cloud + 8 + n_task_type_index] = per_task_wait_edge_comp_count_cpu_cycle[iot_index][1][n_task_type_index]
            temp_edge_pool = np.max(edge_pool[1][:,n_task_type_index])
            for iot_index in range(n_iot):
                edge_pool[1][iot_index][n_task_type_index] = temp_edge_pool
            observation_all[iot_index, n_task_type * 10 + 6 + n_edge + n_cloud + 8 + n_task_type_index] = np.min([j+ 1 - temp_edge_pool , keep_alive[n_task_type_index]])
    
        #n_features_system_cloud
        observation_all[iot_index, n_task_type * 11 + 6 + n_edge + n_cloud + 8] = pull_uplink_rate_cloud
        observation_all[iot_index, n_task_type * 11 + 6 + n_edge + n_cloud + 9] = comp_cap_cloud[0]
        observation_all[iot_index, n_task_type * 11 + 6 + n_edge + n_cloud + 10] = all_task_wait_cloud_comp_size_cpu_cycle[iot_index][0]
        observation_all[iot_index, n_task_type * 11 + 6 + n_edge + n_cloud + 11] = task_on_process_cloud[iot_index][0]['remain']
        for n_task_type_index in range(n_task_type):
            observation_all[iot_index, n_task_type * 11 + 6 + n_edge + n_cloud + 12 + n_task_type_index] = all_task_wait_cloud_comp_count[iot_index][0][n_task_type_index] 
            observation_all[iot_index, n_task_type * 12 + 6 + n_edge + n_cloud + 12 + n_task_type_index] = per_task_wait_cloud_comp_count_cpu_cycle[iot_index][0][n_task_type_index]
            temp_cloud_pool = np.max(cloud_pool[0][:,n_task_type_index])
            for iot_index in range(n_iot):
                cloud_pool[0][iot_index][n_task_type_index] = temp_cloud_pool
            
            observation_all[iot_index, n_task_type * 13 + 6 + n_edge + n_cloud + 12 + n_task_type_index] = np.min([j+ 1 - cloud_pool[0][iot_index][n_task_type_index] , keep_alive[n_task_type_index]])    
    return observation_all
                   

class DeepQNetwork:
    def __init__(self,
                 n_actions,
                 n_features,
                 n_time,
                 learning_rate=0.001,
                 batch_size=64,
                 reward_decay=0.99,
                 alpha = 0.1,
                 beta_increment = 0.001, 
                 e_greedy=0.99,
                 replace_target_iter=150,#400-->200-->100
                 memory_size=3500,
                 e_greedy_increment=0.0005,
                 N_L1 = 64):
        self.n_actions = n_actions
        self.n_features = n_features
        self.n_time = n_time
        self.lr = learning_rate
        self.gamma = reward_decay
        self.epsilon_max = e_greedy
        self.replace_target_iter = replace_target_iter
        self.memory_size = memory_size
        self.batch_size = batch_size
        self.epsilon_increment = e_greedy_increment
        self.alpha = alpha
        self.beta_increment = beta_increment
        self.beta = 0.004  # initial value of beta
        self.epsilon = 0
        self.N_L1 = N_L1
        
        
        tf.reset_default_graph()

        self.learn_step_counter = 0
        self.memory = np.zeros((self.memory_size, n_features * 2 + 2))
        self.priority = np.zeros(self.memory_size)  # Initialize priorities
        
        
        self.memory_counter = 0
        self.target_params_replaced_counter = 0

        self._build_net()
        t_params = tf.get_collection('target_net_params')
        e_params = tf.get_collection('eval_net_params')
        self.replace_target_op = [tf.assign(t, e) for t, e in zip(t_params, e_params)]

        self.sess = tf.Session()
        self.sess.run(tf.global_variables_initializer())
        self.cost_his = []
        
        self.reward_store = list()
        self.action_store = list()
        self.delay_store = list()
        self.energy_store = list()
        self.store_q_value = list()
        self.loss_store = list()

    def store_transition(self, s, a, r, s_):
        ##print(np.shape(s),np.shape(s_))
        #print(np.shape(s),np.shape(s_))
        #print(s)
        #print(a)
        #print(r)
        #print(s_)
        #print()
        transition = np.hstack((s, [a, r], s_))
        index = self.memory_counter % self.memory_size
        self.memory[index, :] = transition
        
        # Calculate TD error
        td_q_eval = self.sess.run(self.q_eval, feed_dict={self.s: s[np.newaxis, :]})   #评估网络
        td_q_next = self.sess.run(self.q_next, feed_dict={self.s_: s_[np.newaxis, :]})  #目标网络
        q_eval_next = self.sess.run(self.q_eval, feed_dict={self.s: s_[np.newaxis, :]})
        max_act_next = np.argmax(q_eval_next, axis=1)
        selected_q_next = td_q_next[0, max_act_next[0]]
        td_q_target = td_q_eval.copy()
        td_q_target[0, int(a)] = r + self.gamma * selected_q_next
        td_error = abs(td_q_target[0, int(a)] - td_q_eval[0, int(a)]) + 0.0000000000001
        if np.isnan(td_error) or np.isinf(td_error):
            #print(f"Invalid TD error: {td_error}. Setting to 0.")
            td_error =  0.0000000000001
        self.priority[index] = td_error
        
        self.memory_counter += 1
        #print("向回放区存入经验的次数：self.memory_counter：",self.memory_counter)
        if (self.memory_counter > 200) and (self.memory_counter % 10 == 0):
            self.learn()
            #print("self.learn_step_counter",self.learn_step_counter)
        #print(transition[:self.n_features])
        #print(transition[self.n_features],transition[self.n_features+1])
        #print(transition[-self.n_features:])

     
    def _build_net(self):
        # ------------------ build evaluate_net ------------------
        self.s = tf.placeholder(tf.float32, [None, self.n_features], name='s')  # input
        self.q_target = tf.placeholder(tf.float32, [None, self.n_actions], name='Q_target')  # for calculating loss
        self.is_weights = tf.placeholder(tf.float32, [None], name='is_weights')  # importance sampling weights

        with tf.variable_scope('eval_net'):
            # c_names(collections_names) are the collections to store variables
            c_names, n_l1, w_initializer, b_initializer = \
                ['eval_net_params', tf.GraphKeys.GLOBAL_VARIABLES], self.N_L1,  \
                tf.random_normal_initializer(0., 0.3), tf.constant_initializer(0.1)  # config of layers

            # first layer. collections is used later when assign to target net
            with tf.variable_scope('l1'):
                w1 = tf.get_variable('w1', [self.n_features, n_l1], initializer=w_initializer, collections=c_names)
                b1 = tf.get_variable('b1', [1, n_l1], initializer=b_initializer, collections=c_names)
                l1 = tf.nn.relu(tf.matmul(self.s, w1) + b1)

            # hidden layer. collections is used later when assign to target net
            with tf.variable_scope('lm1'):
                wm1 = tf.get_variable('wm1', [n_l1, n_l1], initializer=w_initializer, collections=c_names)
                bm1 = tf.get_variable('bm1', [1, n_l1], initializer=b_initializer, collections=c_names)
                lm1 = tf.nn.relu(tf.matmul(l1, wm1) + bm1)

            # Value stream
            with tf.variable_scope('Value'):
                w2_V  = tf.get_variable('w2_V', [n_l1, 1], initializer=w_initializer, collections=c_names)
                b2_V  = tf.get_variable('b2_V', [1, 1], initializer=b_initializer, collections=c_names)
                self.V = tf.matmul(lm1, w2_V ) + b2_V

            # Advantage stream
            with tf.variable_scope('Advantage'):
                w2_A  = tf.get_variable('w2_A', [n_l1, self.n_actions], initializer=w_initializer, collections=c_names)
                b2_A  = tf.get_variable('b2_A', [1, self.n_actions], initializer=b_initializer, collections=c_names)
                self.A = tf.matmul(lm1, w2_A ) + b2_A 

            with tf.variable_scope('Q'):
                self.q_eval = self.V + (self.A - tf.reduce_mean(self.A, axis=1, keepdims=True))

        # ------------------ build target_net ------------------
        self.s_ = tf.placeholder(tf.float32, [None, self.n_features], name='s_')  # input
        with tf.variable_scope('target_net'):
            # c_names(collections_names) are the collections to store variables
            c_names = ['target_net_params', tf.GraphKeys.GLOBAL_VARIABLES]

            # first layer. collections is used later when assign to target net
            with tf.variable_scope('l1'):
                w1 = tf.get_variable('w1', [self.n_features, n_l1], initializer=w_initializer, collections=c_names)
                b1 = tf.get_variable('b1', [1, n_l1], initializer=b_initializer, collections=c_names)
                l1 = tf.nn.relu(tf.matmul(self.s_, w1) + b1)

            # hidden layer. collections is used later when assign to target net
            with tf.variable_scope('lm1'):
                wm1 = tf.get_variable('wm1', [n_l1, n_l1], initializer=w_initializer, collections=c_names)
                bm1 = tf.get_variable('bm1', [1, n_l1], initializer=b_initializer, collections=c_names)
                lm1 = tf.nn.relu(tf.matmul(l1, wm1) + bm1)

            # Value stream
            with tf.variable_scope('Value'):
                w2_V  = tf.get_variable('w2_V', [n_l1, 1], initializer=w_initializer, collections=c_names)
                b2_V  = tf.get_variable('b2_V', [1, 1], initializer=b_initializer, collections=c_names)
                self.V_ = tf.matmul(lm1, w2_V ) + b2_V 

            # Advantage stream
            with tf.variable_scope('Advantage'):
                w2_A = tf.get_variable('w2_A', [n_l1, self.n_actions], initializer=w_initializer, collections=c_names)
                b2_A = tf.get_variable('b2_A', [1, self.n_actions], initializer=b_initializer, collections=c_names)
                self.A_ = tf.matmul(lm1, w2_A) + b2_A 

            with tf.variable_scope('Q'):
                self.q_next = self.V_ + (self.A_ - tf.reduce_mean(self.A_, axis=1, keepdims=True))
    

        with tf.variable_scope('loss'):
            # Compute the weighted loss
            squared_diff = tf.squared_difference(self.q_target, self.q_eval)
            is_weights_expanded = tf.expand_dims(self.is_weights, axis=1)
            weighted_squared_diff = is_weights_expanded * squared_diff
            self.loss = tf.reduce_mean(weighted_squared_diff)
            #self.loss = tf.reduce_mean(self.is_weights * tf.squared_difference(self.q_target, self.q_eval))

        with tf.variable_scope('train'):
            self._train_op = tf.train.RMSPropOptimizer(self.lr).minimize(self.loss)

    
    def learn(self):
        # check to replace target parameters超过100步，每十步学一次，每200步更新目标网络参数，更新的步长得是学习步长得整数倍，不然就错过网络更新环节
        if self.learn_step_counter % self.replace_target_iter == 0:
            self.sess.run(self.replace_target_op)
            self.target_params_replaced_counter = self.target_params_replaced_counter + 1
            #print('\ntarget_params_replaced','学习总步长', self.learn_step_counter,'\n')
            # print('\ntarget_params_replaced\n')

        # sample batch memory from all memory
        if self.memory_counter > self.memory_size:
            #sample_index = np.random.choice(self.memory_size, size=self.batch_size)
            sample_size = self.memory_size
        else:
            sample_size = self.memory_counter
            #sample_index = np.random.choice(self.memory_counter, size=self.batch_size)
        
        # Normalize priorities to create sampling probabilities
        priority_sum = np.sum((self.priority[:sample_size])** self.alpha)
        sampling_probabilities = ((self.priority[:sample_size])** self.alpha) / priority_sum
        # Sample indices based on probabilities
        sample_indices = np.random.choice(sample_size, self.batch_size, p=sampling_probabilities)
        batch_memory = self.memory[sample_indices, :]
        # Compute importance sampling weights
        is_weights = ((1 / sample_size) * (1 / sampling_probabilities[sample_indices])) ** self.beta
        #is_weights /= is_weights.max()  # Normalize weights
        # Evaluate q_next and q_eval using target_net and eval_net
        
        #batch_memory = self.memory[sample_index, :]

        # Evaluate q_next and q_eval using target_net and eval_net
        q_next, q_eval4next = self.sess.run(
            [self.q_next, self.q_eval],
            feed_dict={
                self.s_: batch_memory[:, -self.n_features:],  # next state
                self.s: batch_memory[:, -self.n_features:],  # current state
            })

        q_eval = self.sess.run(self.q_eval, {self.s: batch_memory[:, :self.n_features]})

        # Change q_target w.r.t q_eval's action
        q_target = q_eval.copy()

        batch_index = np.arange(self.batch_size, dtype=np.int32)
        eval_act_index = batch_memory[:, self.n_features].astype(int)
        reward = batch_memory[:, self.n_features + 1]
        #DDQN算法在估计回报时只需要用 评估网络确定动作，用 目标网络确定动作价值 即可
        max_act4next = np.argmax(q_eval4next, axis=1)  # the action that maximizes the next Q value
        #selected_q_next = q_eval4next[batch_index, max_act4next]    #DQN
        selected_q_next = q_next[batch_index, max_act4next]        # Double DQN
        

        q_target[batch_index, eval_act_index] = reward + self.gamma * selected_q_next

        # Train eval network
        _, self.cost = self.sess.run([self._train_op, self.loss],
                                    feed_dict={self.s: batch_memory[:, :self.n_features],
                                                self.q_target: q_target,
                                                self.is_weights: is_weights})
        self.cost_his.append(self.cost)

        # Increasing epsilon
        self.epsilon = self.epsilon + self.epsilon_increment if self.epsilon < self.epsilon_max else self.epsilon_max
        if self.beta < 1:
            self.beta = self.beta + self.beta_increment
        else:
            self.beta = 1
        self.learn_step_counter += 1 



    def choose_action(self, observation):
        observation = observation[np.newaxis, :]
        #action_choose = np.random.randint(0, self.n_actions)
        #print()
        choose_action_way_temp = -1
        if np.random.uniform() < self.epsilon:
            actions_value = self.sess.run(self.q_eval, feed_dict={self.s: observation})
            
            action_choose = np.argmax(actions_value, axis=1)
            #print("",action_choose)
            #print("网络选择动作,actions_value",actions_value,action_choose)
            choose_action_way_temp = 0
        else:
            #print("随机选择动作")
            action_choose = np.random.randint(0, self.n_actions)
            choose_action_way_temp = 1
        #action_choose = np.random.randint(0, 4)
        #action_choose = 3
        #print("        选择动作",action_choose)
        return action_choose, choose_action_way_temp

if __name__ == "__main__":
    task = []
    for i in range(n_iot):
        with open(f'任务列表/iot_{i}_trace_4_new.json', 'r') as f:
            task.append(json.load(f))
            #print(task[i][999][6]['function_id'])

    total_task = 0  
    total_task_non = 0   
    before_max_delay = 0
    after_max_delay = 0                                           

    for i in range(n_iot):
        for j in range(n_time):
            if j <= (n_time - n_no_task) :
                
                if task[i][j][0]['function_id'] != -1:
                        #task[i][j][t]['data_size'] = task_size[t]
                        #task[i][j][t]['cpu_cycle'] = task_cpu_cycle_count[t]
                        before_max_delay += task[i][j][0]['max_delay']
                        task[i][j][0]['max_delay'] = task[i][j][0]['max_delay']
                        after_max_delay += task[i][j][0]['max_delay']
                        total_task = total_task +1
                else:
                        #task[i][j][t]['function_id'] = t
                        #task[i][j][t]['data_size'] = task_size[t]
                        #task[i][j][t]['cpu_cycle'] = task_cpu_cycle_count[t]
                        #total_task = total_task +1
                        total_task_non = total_task_non + 1
            else:
                #for t in range(n_task_type):
                    task[i][j][0]['function_id'] = -1
                    task[i][j][0]['data_size'] = 0
                    task[i][j][0]['cpu_cycle'] = 0
                    total_task_non = total_task_non + 1

    print("任务请求总数量、non：7002 2998",total_task,total_task_non)
    with open('任务数txt/record-Dou_Due_priority_4_arrive_001_learning_99_discount_64_batchsize_x1_8_cold_delay_4_iot_10X_timeslot.txt', 'w') as f:
        f.write(f"[{total_task}, {total_task_non},{before_max_delay},{after_max_delay}]\n")
    '''with open('iot_1_trace_0.4.json', 'w') as f:
        json.dump(task[0], f, ensure_ascii=False, indent=4)
    cloud_agent = DeepQNetwork(n_actions, n_features, n_time)
    train(cloud_agent, NUM_EPISODE)'''
    
    
    iot_RL_list = list()             # 创建了一个包含多个强化学习智能体（IoT设备）的列表 iot_RL_list，每个设备都使用 DeepQNetwork 类来建模。
    for iot in range(n_iot):
        iot_RL_list.append(DeepQNetwork(n_actions, n_features, n_time))
        
    train(iot_RL_list, NUM_EPISODE)
    print('Training Finished')
    
     
    
