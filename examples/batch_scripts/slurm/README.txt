slurm_mult.sh:
This script has been used on NASA's Discover cluster. 
It uses srun to launch mutliple parallel jobs. 
This only counts as a single job, so in principle this script can 
be used to run as many parallel jobs as the limit on the number of CPUs allows (~6000).
Note that the job will not be launched until slurm
allocates all of the needed resources to run everything together.

slurm_single.sh:
This script has been used on NASA's Discover cluster.
It is for submitting a single job.  

slurm_packable.sh:
This script has been used on NASA's Discover cluster.
It is for submitting an array job on the 'packable' partition. 
The packable partition is a special partition that sends each job
in the array to its own CPU by default. 

In normal partitions, each job in an array takes up an entire node, 
and you are limited by the total number of allowed jobs, which for Discover 
is only ~25. Thus, to fully utilize all the CPUs in a normal partition requires
something like srun, as employed in slurm_mult.sh decribed above.  

A Discover user can gain access to the packable partition by making a request
to the system admins (as described in the cluster documentation). 
In contrast to slurm_mult.sh decribed above, in this case slurm does not
wait for all needed resources to become available before launching the job; 
instead, it will launch jobs in the array as CPUs become open. 

slurm_run_script.sh:
This script has been used on MOGON (JGU Mainz).
It uses the 'smp' partition, which is similar 
to the packable partition described above. 
Instead of using the batch script to call another script,
the entire job is executed in the batch script itself. 
