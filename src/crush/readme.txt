*****************************************************************
* Manual of the CRUSH simulator
* Author: Lipeng Wan
* Email: lwan1@utk.edu
*****************************************************************
"layers.txt" -- This file contains the the storage hierarchy 
information. For example, we can put the following info into
the "layers.txt":
cab uniform 24
row tree 4
pool list 2
...
Each line of this file represents a layer of the storage hierarchy.
The first attribute of each line is the type of the layer, which 
might be cabinet, row, pool, etc. The second attribute is the type 
of the bucket, which can be “uniform”, “list”, “tree”, or “straw”,
as mentioned in CRUSH paper. The third attribute is the number of 
items each bucket contains.
******************************************************************
"dev_weight.txt" -- This file contains the id and normalized weight
of the devices whose weight is between 0 and the maximum weight a 
device could have. The content of this file might be like the follows:
75	0.35166
25	0.83083
49	0.58526
67	0.54972
85	0.91719
91	0.28584
51	0.7572
...
******************************************************************
"args.txt" -- This file contains the arguments that are needed by
the simulator. The content of this file might be like the follows:
num_osds 100              # The number of osds
min_x 0                   # The minimum value of the input 
max_x 1023                # The maximum value of the input
			  # The input data are all integers 
			  # from min_x to max_x which represent
		          # the identifiers of the data objects
num_replicas 3            # The number of replicas
bucket_down_ratio 0.5     # The ratio of buckets that are down        
dev_down_ratio 0.1        # The ratio of devices that are down 
num_batches 10		  # The number of batches used for testing
