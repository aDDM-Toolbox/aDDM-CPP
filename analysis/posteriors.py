"""
@brief Create a posteriors pair plot from the generated marginal posteriors. 

This script can create a posteriors pair plot for an arbitrary number of 
parameters. For N parameters, the graph creates NxN subplots with 1-dimensional 
parameter probabilities along the diagonal and heatmaps of shared probabilities 
for pairs of parameters below. The CSV input format should have the first N
columns as parameters, with the final column 'p' representing the normalized 
probability of that combination. The necessary data can be generated by passing 
normalizedPosteriors=true as an argument to fitModelMLE. The expected input 
format is as follows: 

| para1 | para2 | ... | paraN |  p  | 
+-------+-------+ ... +-------+-----+
|   *   |   *   | ... |   *   |  *  |

The input file can be declared in the FILE_PATH variable. If the label for 
probabilities is something other than 'p', that can also be configured using
the PROB_LABEL variable. To save the resulting pair plot in the imgs directory, 
pass 'save' as a command line argument. Usage is as follows:

python3 analysis/posteriors.py [save]
"""
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict
from typing import Tuple, List
import queue
import sys
from datetime import datetime

PROB_LABEL = 'p'
FILE_PATH = 'results/addm_posteriors.csv'


# _MapData class is defined to store information for heatmaps
class _MapData:
    def __init__(self, par1_label: str, par2_label: str, 
                 par1_sums: defaultdict, par2_sums: defaultdict):
        self.par1_label = par1_label 
        self.par2_label = par2_label
        self.par1_sums = par1_sums
        self.par2_sums = par2_sums


df = pd.read_csv(FILE_PATH)

# num columns - 1 (exclude probability)
N = df.shape[1] - 1

# Calculate the sums of probabilities for each parameter
param_sums: List[Tuple[str, defaultdict]] = [] 
# Example entry: ('d', {0.005: 0.25, 0.006: 0.5, 0.007: 0.025})
for param in df:
    if param != PROB_LABEL:
        param_dict = defaultdict(int)
        for i, row in df.iterrows(): 
            param_row_val = row[param] # Current value of the parameter
            param_dict[param_row_val] += row[PROB_LABEL] # Probability determined given 
                # that parameter and some combination of the other parameters
        param_sums.append((param, param_dict))

# Create pairs of parameters for heatmaps
# Iterate down each column starting with the first parameter
heatmaps: List[_MapData] = list()
for i in range(N):
    for j in range(i + 1, N):
        heatmaps.append(_MapData(
            param_sums[i][0], param_sums[j][0], 
                param_sums[i][1], param_sums[j][1]))

# Queue to store data for heatmaps
heatmaps_queue: queue.Queue[Tuple[_MapData, np.ndarray]] = queue.Queue()

# Iterate over each _MapData object and calculate the sums for the 
# corresponding heatmap
for map_data in heatmaps: 
    # Create empty heatmap data based on number of possible values for 
    # each parameter
    arr_data = np.zeros((len(map_data.par1_sums), len(map_data.par2_sums))) 
    for i in range(len(map_data.par1_sums)):
        for j in range(len(map_data.par2_sums)):
            curr_par1 = list(map_data.par1_sums.keys())[i] # first parameter
            curr_par2 = list(map_data.par2_sums.keys())[j] # second parameter
            # Get the sum of all probabilities for the current pair of 
            # parameter values
            for k, row in df.iterrows():
                if row[map_data.par1_label] == curr_par1 and row[map_data.par2_label] == curr_par2:
                    arr_data[i][j] += row[PROB_LABEL]
    heatmaps_queue.put((map_data, arr_data))

# Create subplots grid for the bar plots and heatmaps
fig, axes = plt.subplots(figsize=(15, 10), ncols=N, nrows=N)

# Iterate over each subplot and plot either a bar plot or a heatmap
diag_idx = 0 
for j in range(N):
    for i in range(N):
        if i < j:
            # Turn off axes for subplots above the diagonal 
            axes[i, j].axis('off')  
        elif i == j:
            curr = param_sums[diag_idx]
            vals = curr[1]
            g = sns.barplot(
                x=list(vals.keys()), 
                y=list(vals.values()), 
                ax=axes[i, j], 
                color="grey", 
                )
            
            keys_labels = list(vals.keys())
            axes[i, j].set_xticks(np.arange(len(keys_labels)))
            axes[i, j].set_xticklabels(keys_labels)

            diag_idx += 1
        else:
            curr_heatmap = heatmaps_queue.get()
            data = curr_heatmap[0]
            arr = curr_heatmap[1]
            g = sns.heatmap(
                arr.T, 
                cbar=False, 
                cmap=sns.color_palette("blend:#510,#FFF", as_cmap=True), 
                ax=axes[i, j]
                )
            # Invert y-axis for heatmap to match the order of values
            g.invert_yaxis()  

            g.set_xticks(np.arange(len(data.par1_sums)) + 0.5, minor=False)  
            g.set_xticklabels(list(data.par1_sums.keys()), minor=False)  
            g.set_yticks(np.arange(len(data.par2_sums)) + 0.5, minor=False)  
            g.set_yticklabels(list(data.par2_sums.keys()), minor=False) 

# Set labels for x and y axes of plot
for i in range(N):
    axes[i, 0].set_ylabel(df.columns[i], size=24)
    axes[N - 1, i].set_xlabel(df.columns[i], size=24)

plt.tight_layout()

if (len(sys.argv) > 1 and "save" in sys.argv):
    currTime = datetime.now().strftime(u"%Y-%m-%d_%H:%M:%S")
    plt.savefig("imgs/posteriors_" + currTime + ".png")

plt.show()
