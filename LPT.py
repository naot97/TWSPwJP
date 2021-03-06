# -*- coding: utf-8 -*-
"""TWSPwJP.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1fBJvZvCaQWloMcdcDWQgm77_BHTKnnCk
"""

import cvxpy as cp
import numpy as np
import json
import time
import os
import pandas as pd
import math

main_datasets = './dataset'
datasets = os.listdir(main_datasets)
print(datasets)
result_list = []
for dataset in datasets:
  dataset_path = os.path.join(main_datasets, dataset)
  list_json = [fil for fil in os.listdir(dataset_path) if fil[-4:] == 'json']
  for json_name in list_json:
    json_path = os.path.join(dataset_path, json_name)
    f = open(json_path)
    input = json.load(f)
    f.close()

    Jobs = input['Jobs']
    n = len(Jobs)
    p = np.zeros(n)
    for i, J in enumerate(Jobs):
      p[i] = J['Processing']


    Machines = input['Machines']
    k = len(Machines)
    b = [[] for i in range(k)]
    w = [[] for i in range(k)]
    W = [[] for i in range(k)]
    m = np.zeros(k, dtype=np.int8)
    for i, M in enumerate(Machines):
      sum = 0
      m[i] = len(M['Windows'])
      for t, Windown in enumerate(M['Windows']):
        b[i].append(Windown['StartTime'])
        w[i].append(Windown['Capacity'])
        W[i].append([sum, sum + w[i][t]])
        sum += w[i][t]
      b[i].append(99999)

    split_min = input['Splitmin']
    LB = math.ceil(np.sum(p) / k)
    UB = LB + math.ceil( np.sum(m - 1) / k) * 2 * split_min

    # sort array of processing time
    sorted_p = np.sort(p)[::-1]
    c = np.zeros(k)

    for p_i in sorted_p:

      # Find the machine has minimum work in the current
      min_c = 99999
      current_machine = -1
      for j in range(k):
        if c[j] < min_c:
          min_c = c[j]
          current_machine = j

      # check split_min condition and calculate idle time
      for W_i in W[current_machine]:
        if W_i[0] <= c[current_machine] + p_i <= W_i[1]:
          break

      if c[current_machine] + p_i - W_i[0] < split_min:
        idle_time = split_min - (c[current_machine] + p_i - W_i[0])
        c[current_machine] = c[current_machine] + p_i + idle_time
      else :
        c[current_machine] = c[current_machine] + p_i

      if W_i[1] - c[current_machine] < split_min:
        c[current_machine] = W_i[1]
    # Find C_max
    c_max = 0
    for j in range(k):
      if c[j] > c_max:
        c_max = c[j]

    data = {}
    data['name'] = json_name
    data['n'] = n
    data['k'] = k
    data['LB'] = LB
    data['C_max'] = c_max
    data['t'] = 0
    result_list.append(data)



    df = pd.DataFrame(result_list)
    df.to_excel('LPT.xlsx')
