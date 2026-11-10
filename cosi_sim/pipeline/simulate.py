############################################################
# 
# Written by Chris karwin; November 2021; Clemson University.
#
# Purpose: Main script for generating simulation challenge.
# 
###########################################################

# Imports:
import os,sys,shutil 
import yaml
import pandas as pd
import numpy as np
import scipy.integrate as integrate
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
import math
import gzip
import cosi_sim
import gc

# Superclass:
class Simulate:
    
    
    """Main inputs are specified in inputs.yaml file"""
    
    def __init__(self,input_yaml):

        # Get home directory:
        self.home = os.getcwd()
        
        # Get install directory:
        self.sim_dir = os.path.split(cosi_sim.__file__)[0]

        # Load main inputs from yaml file:
        with open(input_yaml,"r") as file:
            inputs = yaml.load(file,Loader=yaml.FullLoader)

        self.run_dir = inputs["run_dir"]
        self.geo_file = inputs["geometry_file"]
        self.name = inputs["name"]
        self.source_file = self.name + ".source"
        self.time = inputs["time"]
        self.src_list = inputs["src_list"]
        self.orientation_file = inputs["orientation_file"]
        self.lightcurve_file = inputs["lightcurve_file"]
        self.lightcurve = inputs["lightcurve"]
        self.parallel_time_sims = inputs["parallel_time_sims"]
        self.num_sims = inputs["num_sims"]
        self.run_type = inputs["run_type"]
        self.clear_sims = inputs["clear_sims"]
        self.src_lib = os.path.join(self.sim_dir,"Source_Library")
        self.run_nuc = inputs["run_nuc"]
        self.nuc_config = inputs["nuc_config"]
        self.revan_config = inputs["revan_config"]
        self.mimrec_config = inputs["mimrec_config"]
        self.mcosima = inputs["mcosima"]
        self.num_cores = inputs["num_cores"]
        self.ntriggers = inputs["ntriggers"]
        self.ASphere = inputs["ASphere"]
        self.include_transmission_prob = inputs["include_transmission_prob"]
        self.transmission_prob_file = inputs["transmission_prob_file"]

    def define_sim(self, external_src=False):

        """
        This function makes the main source file for the simulation. 

        The input source list is passed from inputs.yaml,
        and it must be a list of strings, where each string is from 
        the available options.
        
        Optional input: 
        external_src: Option to use source outside of source library. 
            - True or False; default is False.
        """

        # Make print statement:
        print()
        print("********** Run_Data_Challenge_Module ************")
        print("Running define_sim...")
        print()

        # Print source list:      
        print()
        print("Simulation will include the following sources:")
        print(self.src_list)
        print()

        # Make output data directory:
        if os.path.isdir("Output") == True:
            shutil.rmtree("Output")
        os.system("mkdir Output")

        # Copy orientation file if running parallel jobs:
        if os.path.exists("GalacticScan.ori"):
            os.system("scp GalacticScan.ori Output")
        
        # Also need to copy LC file for parallel jobs:
        if self.lightcurve == True:
            os.system("scp lightcurve.dat Output")

        # Need to update name of orientation file if running parallel time sims:
        if self.parallel_time_sims == True:
            orientation_file = "GalacticScan.ori"
        else: orientation_file = self.orientation_file

        # Option to use source outside of library:
        if external_src == True:
            src_files = os.path.join(self.run_dir,"Sources","*.source")
            os.system("scp %s %s" %(src_files,"./Output"))

        if external_src == False:
           
            # Write source file:
            f = open(os.path.join("Output",self.source_file),"w")
            f.write("#Source file for data challenge\n")
            f.write("#The detector rotates in the Galactic coordiante system as given in the ori file.\n")
            f.write("#The point sources are fixed in Galactic coordinates.\n\n")
            f.write("#geometry file\n")
            f.write("Version         1\n")
            f.write("Geometry %s\n\n" %self.geo_file)
            f.write("#Physics list\n")
            f.write("PhysicsListEM                        LivermorePol\n\n")
            f.write("#Output formats\n")
            f.write("StoreSimulationInfo                  init-only\n\n")
            f.write("#Define run:\n")
            f.write("Run DataChallenge\n")
            f.write("DataChallenge.FileName               %s\n" %self.name)
            f.write("DataChallenge.Time                   %s\n" %self.time)
            f.write("DataChallenge.OrientationSky         Galactic File NoLoop %s\n\n" %orientation_file)
        
            # Add sources:
            for each in self.src_list:

                this_name = os.path.basename(each)
                this_src = os.path.join(self.run_dir, "Sources" ,this_name + ".source")
                f.write("#include %s\n" %each)
                f.write("Include %s\n\n" %this_src)
            
            f.close()
    
        return
    
    def run_cosima(self, seed="none", verbosity=0, output_name="cosima"):
        
        """
        input definitions:
        
        seed: Specify seed to be used in simulations for reproducing results.
            - Default is no seed. 
        verbosity: Verbosity level of cosima output. 
            - Default is same as cosima default (0). 
        output_name: Name of cosima output file.
            - Set to 'none' for no output file. 
        """

        # Make print statement:
        print()
        print("Running run_cosima...")
        print()
 
        # Change to output directory:
        os.chdir("Output")
   
        # Construct executable:
        # Option to run cosima or mcosima with numerous cores.
        if self.mcosima == False:
            executable = "cosima -v %s" %str(verbosity)
        if self.mcosima == True:
            executable = "mcosima -t %s -w -a" %self.num_cores
            # Check that no seed has been passed:
            if seed != "none":
                print("ERROR: mcosima needs to be ran without a seed.")
                print("Exiting code.")
                sys.exit()

        # Option to write terminal output to file:
        if output_name != "none":
            output = "| tee %s_terminal_output.txt" %output_name
        if output_name == "none":
            output = ""

        # Run executable:
        if seed != "none":
            print("running with a seed...")
            os.system("%s -s %s -z %s %s" %(executable,seed,self.source_file,output))
        if seed == "none":
            print("running with no seed...")
            os.system("%s -z %s %s" %(executable,self.source_file,output))

        # Concatenate sim files:
        if self.mcosima == True:
            self.msimconcatter()
        
        # Return home:
        os.chdir(self.home)

        return

    def get_time_constant(self, ori_file):

        """
        Returns first time in ori file. 
        """
        
        this_file = "Output/" + ori_file
        f = open(this_file,"r")
        lines = f.readlines()
        split = lines[1].split()
        constant = float(split[1])

        return constant 

    def modify_sim_times(self, filename, time_constant):

        """
        Modify time stamps in sim file by time constant. 
        
        Inputs:
        filename: Name of cosima sim file to modify.

        time_constant: Time in seconds used to modify time stamps. 
        """

        # Inputs:
        this_file = "Output/" + filename
        new_file = "Output/fixed_times.inc1.id1.sim"

        # Open new file for writing:
        g = open(new_file,"w")

        # Read through sim file and fix times:
        if this_file.endswith(".gz"):
            f = gzip.open(this_file,"rt")

        if this_file.endswith(".sim"):
            f = open(this_file,"r")

        i = 0
        j = 0
        while True:

            this_line = f.readline().strip()

            i += 1

            if len(this_line) == 0:
                g.write(this_line+"\n")

            if this_line:

                if this_line.split()[0] != "TI":
                    g.write(this_line+"\n")

                if this_line.split()[0] == "TI":
                    new_time = str(float(this_line.split()[1]) + time_constant)
                    g.write("TI %s\n" %new_time)
            
                if this_line.split()[0] == "TS":
                    break

            if not this_line:
                if i > 100:
                    j += 1
                    if j > 1:
                        break

        g.close()
        f.close()
        os.system("gzip %s -f" %new_file)

        return

    def msimconcatter(self):
        
        """Concatenate output sim files from mcosima."""

        # Construct string of files to concatenate:
        cat_string = ""
        for i in range(0,self.num_cores):
            cat_string += " %s.p1.inc%s.id1.sim.gz" %(self.name,str(i+1))
        
        # Concatenate files:
        os.system("msimconcatter %s" %cat_string)
        
        return

    def check_cosima_parallel(self, show_plot=True, 
            input_file="cosima_terminal_output.txt", get_cpu=True, start=0, stop=None):

        """
        Check that all cosima jobs converged, and get mean cpu time.
        
        Optional input:
        show_plot: whether or not to display the plot. Default is True.  
        input_file: terminal output file to check
        get_cpu: Whether or not to get cpu time. 
            - default is True.
        start: staring integer for iterating through sim files. 
            - default is 0.
        stop: ending integer for iterating through sim files.
            - default is total number of sim files.
        """

        print()
        print("checking output fils...")
        print()

        cpu_list = []
        problem_list = []
        if stop == None:
            stop = self.num_sims+1
        for i in range(start,stop):
            print("checking sim " + str(i))

            this_file = "Simulations/sim_%s/Output/%s" %(str(i),input_file)
            
            # Make sure the file exists:
            check = os.path.isfile(this_file)
            if check == False:
                print("WARNING: cosima output does not exists: " + str(i))
                problem_list.append(i)
                continue
            
            # The output files are large, but we really only need the end, 
            # so to save time let's just use the last 100 lines:
            os.system("tail -n 100 %s > temp.txt" %this_file)

            # Read file:
            f = open("temp.txt","r")
            lines = f.readlines()
            
            # Make sure the job has finished properly:
            try: 
                if "deleting..." not in lines[len(lines)-1]:
                    print("WARNING: something wrong with job: " + str(i))
                    problem_list.append(i)
                    continue
            except: 
                print("WARNING: no lines in file: " + str(i))
                problem_list.append(i)
                continue

            # Get cpu time:
            if get_cpu == True:
            
                for k in range(1,10):
                    try:
                        this_line = lines[len(lines)-k]
                        if "CPU" in this_line:
                            split = this_line.split()
                    except: 
                        print("WARNING: something wrong with file: " + str(i))
                        continue

                cpu_list.append(float(split[6])/60.0)
            gc.collect()
        
        f.close()
        os.system("rm temp.txt")

        print("problem sims:")
        print(problem_list)

        if get_cpu == True:
            cpu_list = np.array(cpu_list)
            mean = np.mean(cpu_list)
            print("mean cpu time [min]: " + str(mean))
    
            # Save numpy array:
            np.save("cpu_time",cpu_list)

            # Plot:
            plt.plot(cpu_list,ls="-",marker="",color="black",label="run")
            plt.axhline(y=mean, color="cornflowerblue", ls="--",label="mean")
            plt.xlabel("Time Bin", fontsize=14)
            plt.ylabel("CPU Time [min]", fontsize=14)
            plt.savefig("cpu_time.pdf")
            if show_plot == True:
                plt.show() 

        return

    def modify_isotope_sim_time(self, isotope_file, new_time):

        """
        Modifies the simulation time in the output isotope file from 
        step 1 of the activation simulations. This is neccessary when 
        using an orientation file, becuase the time does not start at zero.

        Inputs:
        isotope_file: name of isotope file from step 1. 
      
        new_time: exposure time in seconds used for the simulation, 
        for the given time bin.
        """
        
        # Update time for each time bin:
        for i in range(0,self.num_sims): 
            print("changing sim %s" %str(i))
            temp_file = "Simulations/sim_%s/Output/temp.dat" %str(i)
            this_file = "Simulations/sim_%s/Output/%s" %(str(i),isotope_file)

            # Read file line by line and update TT:
            g = open(temp_file,"w")
            f = open(this_file,"r")
            
            lines = f.readlines()
            for each in lines:
                
                split = each.split()
                
                if len(split) == 0:
                    g.write(each)
                
                if len(split) > 0:
                    
                    if split[0] == "TT":
                        new_line = split[0] + " " + str(new_time) + "\n"
                        g.write(new_line)
                    
                    if split[0] != "TT":
                        g.write(each)
            g.close()
            f.close()
        
            # Replace original file with updated one:
            os.system("mv %s %s" %(temp_file,this_file))

        return

    def run_nuclearizer(self, geo_file="default"):
        
        """
        input definitions:
            
         geo_file: Optional input.
            - Option to use a different geometry file. Must specify full path.  
            - This option is for cosima runs only.

        Note: If running mcosima, then the nuclearizer configuration file 
              must point to the correct geometry file. 
        """

        # Make print statement:
        print()
        print("Running run_nuclearizer...")
        print()

        # Option to use a different geo file:
        if geo_file != "default":
            self.geo_file = geo_file

        # Change to output directory:
        os.chdir("Output")
   
        # Default mode:
        if self.mcosima == False:

            # Remove output file if it already exists (for rerunning option):
            if os.path.exists("output.evta.gz"):
                os.system("rm output.evta.gz nuclearizer_terminal_output.txt")
        
            # Define input sim file:
            sim_file = self.name + ".inc1.id1.sim.gz"

            # Make sure input sim file exists:
            if os.path.exists(sim_file) == False:
                print("ERROR: The input file needed for nuclearizer does not exist.") 
                print("Exiting Code!")
                sys.exit()
                  
            if self.nuc_config != "none":
                os.system("nuclearizer -a -g %s -c %s \
                    -C ModuleOptions.XmlTagSimulationLoader.SimulationFileName=%s \
                    | tee nuclearizer_terminal_output.txt" %(self.geo_file, self.nuc_config, sim_file))
        
            if self.nuc_config == "none":
                print("running without a configuration file...")
                os.system("nuclearizer -a -g %s \
                    -C ModuleOptions.XmlTagSimulationLoader.SimulationFileName=%s \
                    | tee nuclearizer_terminal_output.txt" %(self.geo_file, sim_file))

        # mcosima mode:
        if self.mcosima == True:
            sim_files = "%s.p1.inc{1..%s}.id1.sim.gz"  %(self.name, str(self.num_cores))
            os.system("mnuclearizer -c %s -f %s\
                    | tee nuclearizer_terminal_output.txt" %(self.nuc_config, sim_files))

        # Go home:
        os.chdir(self.home)

        return

    def run_revan(self, geo_file="default", output_name="revan_terminal_output"):
        
        """
        optional inputs:
        
        geo_file: Option to use a different geometry file. Must specify full path. 
        
        output_name: Name of terminal output file. 
        """

        # Make print statement:
        print()
        print("Running run_revan...")
        print()

        # Option to use a different geo file:
        if geo_file != "default":
            self.geo_file = geo_file
        
        # Change to output directory:
        os.chdir("Output")
 
        # Default mode:
        if self.mcosima == False:
       
            # Remove output file if it already exists (option for rerunning):
            tra_file_name = self.name + ".inc1.id1.tra.gz"
            if os.path.exists(tra_file_name):
                os.system("rm %s revan_terminal_output.txt" %tra_file_name)

            # Define input sim file:
            if self.run_nuc == False:
                sim_file = self.name + ".inc1.id1.sim.gz"
            if self.run_nuc == True:
                sim_file = "output.evta.gz" # depends on name in nuclearizer configuration file!
            
            # Make sure input sim file exists:
            if os.path.exists(sim_file) == False:
                print("ERROR: The input file needed for revan does not exist.")
                print("Exiting code!")
                sys.exit()
        
            # Run revan:
            if self.revan_config != "none":

                print("running with a configuration file...")
                os.system("revan -g %s -c %s -f %s -n -a | tee %s.txt" %(self.geo_file, self.revan_config, sim_file, output_name))

            if self.revan_config == "none":
                print("running without a configuration file...")
                os.system("revan -g %s -f %s -n -a | tee %s.txt" %(self.geo_file, sim_file, output_name))
    
            # Change name of output if running nuclearizer:
            if self.run_nuc == True:
                os.system("mv output.tra.gz %s" %tra_file_name)
        
        # mcosima mode:
        if self.mcosima == True:
            if self.run_nuc == True:
                sim_files = "%s.p1.inc{1..%s}.id1.evta.gz"  %(self.name, str(self.num_cores))
            if self.run_nuc == False:
                sim_files = "%s.p1.inc{1..%s}.id1.sim.gz"  %(self.name, str(self.num_cores))
            os.system("mrevan -g %s -c %s -f %s\
                    | tee %s.txt" %(self.geo_file, self.revan_config, sim_files, output_name))
            
        # Go home:
        os.chdir(self.home)

        return

    def check_revan_parallel(self, show_plot=True, input_file="revan_terminal_output.txt", 
            savefile="revan_events", start=0, stop=None):

        """
        Check that all revan jobs converged, and get number of events.
        
        Optional input: 
        show_plot: whether or not to display the plot. Default is True. 
        input_file: input file to parse.
        savefile: name of output array file and plot pdf. 
        start: staring integer for iterating through sim files. 
            - default is 0. 
        stop: ending integer for iterating through files.
            - default is total number of sims.
        """

        print()
        print("Checking revan output files...")
        print()
    
        event_list = []
        problem_list = []
        
        if stop == None:
            stop = self.num_sims+1
        
        for i in range(start,stop):
            print()
            print("checking sim " + str(i))
            print()
            
            main_file = "Simulations/sim_%s/Output/%s.inc1.id1.tra.gz" %(str(i),self.name)
            # Make sure the file exists:
            check = os.path.isfile(main_file)
            if check == False:
                print("WARNING: revan main output does not exists: " + str(i))
                problem_list.append(i)
                continue

            this_file = "Simulations/sim_%s/Output/%s" %(str(i),input_file)
            
            # Make sure the file exists:
            check = os.path.isfile(this_file)
            if check == False:
                print("WARNING: revan terminal output does not exists: " + str(i))
                if i not in problem_list:
                    problem_list.append(i)
                continue
           
            # The output files are large, but we really only need the end, 
            # so to save time let's just use the last 100 lines:
            os.system("tail -n 100 %s > temp.txt" %this_file)
            
            # Read file:
            f = open("temp.txt","r")
            lines = f.readlines()
        
            # Make sure the job has finished:
            try:
                if "Event reconstruction finished" not in lines[len(lines)-1]:
                    if "Event reconstruction finished" not in lines[len(lines)-2]:
                        problem_list.append(i)
                        print("WARNING: something wrong with run: " + str(i))
                        continue
            except: 
                print("WARNING: no lines in file: " + str(i))
                problem_list.append(i)
                continue 

            # Get number of events:
            check = 0
            for k in range(1,25):
                this_line = lines[len(lines)-k]
                if "Compton" in this_line:
                    split = this_line.split()
                    event_list.append(float(split[2]))
                    check += 1
                    break
            if check == 0:
                print("WARNING: No Compton events recorded: " + str(i))

            f.close()
            gc.collect()
            os.system("rm temp.txt")
            
        event_list = np.array(event_list)
        mean = np.mean(event_list)
        print("mean events [counts]: " + str(mean))
        print("problem sims:")
        print(problem_list)

        # Save numpy array:
        np.save(savefile,event_list)

        # Plot:
        plt.plot(event_list,ls="-",marker="",color="black",label="run")
        plt.axhline(y=mean, color="cornflowerblue", ls="--",label="mean")
        plt.xlabel("Time Bin", fontsize=14)
        plt.ylabel("Compton Events [counts]", fontsize=14)
        plt.savefig("%s.pdf" %savefile)
        if show_plot == True:
            plt.show() 

        return

    def run_mimrec(self, extract_root=False, geo_file="default", tra_input="default", energy=None,
            extract_events=True, make_spectrum=True, make_image=True, make_LC=True):
        
        """
        input definitions:
         
         extract_root: if true will extract data for LC and spectrum. 
            - Default is False.

         geo_file: Option to use a different geometry file. Must specify full path. 
        
         tra_input: Option to use a different input tra file. 
         File name must end with '.tra.gz'. This option is particulary 
         useful for processing outputs from mcosima. 

         energy: Energy in keV. For calculating Aeff from monoenergetic sims. 
        
         extract_events: Option to extract events. True or False. 

         make_spectrum: Option to extract spectrum. True or False.

         make_image: Option to extract image. True or False.

         make_LC: Option to exctract LC. True or False. 
        """

        # Make print statement:
        print()
        print("Running run_mimrec...")
        print()

        # Option to use a different geo file:
        if geo_file != "default":
            self.geo_file = geo_file

        # Change to output directory:
        os.chdir("Output")
   
        if tra_input == "default":
        
            # Define tra file:
            tra_file =  self.name + ".inc1.id1.tra.gz"

            # Define outputs:
            output_events =  "%s.inc1.id1.extracted.tra.gz" %self.name

        if tra_input != "default":
            tra_file = tra_input
            
            # Get output file:
            split = tra_input.split(".")
            
            # Check that proper name format is used:
            if (split[-1] != "gz") | (split[-2] != "tra"):
                print("tra input file must end with '.tra.gz'")
                sys.exit()
            
            # Construct output file name:
            split.insert(-2,"extracted")
            output_events = '.'.join(split)

        # Set pdf or root output:
        file_type = ".pdf"
        if extract_root == True:
            file_type = ".root"
        
        # Specify output files:
        output_spec = "sim_counts_spectrum" + file_type
        output_image = "sim_image" + file_type
        output_LC = "sim_LC" + file_type

        # Run mimrec:
        if self.mimrec_config != "none":
            
            print("running with a configuration file...")
           
            # Extract events:
            if extract_events == True:
                os.system("mimrec -g %s -c %s -f %s -x -o %s -n \
                    | tee mimrec_events_terminal_output.txt" \
                    %(self.geo_file, self.mimrec_config, tra_file, output_events))
            
            # Note: the output file from the extracted events is now used as inputs below:

            # Make spectrum:
            if make_spectrum == True:
                os.system("mimrec -g %s -c %s -f %s -s -o %s -n \
                    | tee mimrec_spectrum_terminal_output.txt" \
                    %(self.geo_file, self.mimrec_config, output_events, output_spec))
           
            # Make image:
            if make_image == True:
                os.system("mimrec -g %s -c %s -f %s -i -o %s -n \
                    | tee mimrec_image_terminal_output.txt" \
                    %(self.geo_file, self.mimrec_config, output_events, output_image))

            # Make LC:
            if make_LC == True:
                os.system("mimrec -g %s -c %s -f %s -l -o %s -n \
                    | tee mimrec_LC_terminal_output.txt" \
                    %(self.geo_file, self.mimrec_config, output_events, output_LC))

            # Extract arm:
            if energy is not None:
                elow = energy - 11
                ehigh = energy + 11
                os.system("mimrec -g %s -c %s -f %s -a -n \
                    -C EventSelections.FirstEnergyWindow.Min=%s \
                    -C EventSelections.FirstEnergyWindow.Max=%s \
                    | tee mimrec_arm_output.txt" \
                    %(self.geo_file, self.mimrec_config, tra_file, str(elow), str(ehigh)))
            
        if self.mimrec_config == "none":
            
            print("running without a configuration file...")
            
            # Extract events:
            if extract_events == True:
                os.system("mimrec -g %s -f %s -x -o %s -n \
                    | tee mimrec_events_terminal_output.txt" \
                    %(self.geo_file, tra_file, output_events))

            # Make spectrum:
            if make_spectrum == True:
                os.system("mimrec -g %s -f %s -s -o %s -n \
                    | tee mimrec_spectrum_terminal_output.txt" \
                    %(self.geo_file, output_events, output_spec))
      
            # Make image:
            if make_image == True:
                os.system("mimrec -g %s -f %s -i -o %s -n \
                    | tee mimrec_image_terminal_output.txt" \
                    %(self.geo_file, output_events, output_image))
            
            # Make LC:
            if make_LC == True:
                os.system("mimrec -g %s -f %s -l -o %s -n \
                    | tee mimrec_LC_terminal_output.txt" \
                    %(self.geo_file, output_events, output_LC))
        
        if extract_root == True:
            
            # Extract spectrum histogram:
            if make_spectrum == True:
                extract_spectrum_file = os.path.join(self.sim_dir,"pipeline/ExtractSpectrum.cxx")
                os.system("root -q -b %s" %extract_spectrum_file)

            # Extract light curve histogram:
            if make_LC == True:
                extract_lc_file = os.path.join(self.sim_dir,"pipeline/ExtractLightCurve.cxx")
                os.system("root -q -b %s" %extract_lc_file)
        
            # Extract image histogram:
            if make_image == True:
                extract_image_file = os.path.join(self.sim_dir,"pipeline/ExtractImage.cxx")
                os.system("root -q -b %s" %extract_image_file)

        # Go home:
        os.chdir(self.home)

        return

    def plot_spectrum(self, show_plots=True, exp_time=None, plot_kwargs={}, fig_kwargs={}):

        """
        Plots extracted mimrec spectrum.

        show_plots: Option to not show plot (True or False). 

        exp_time: exposure time in seconds. 

        plot_kwargs: Pass any kwargs to plt.plot().

        fig_kwargs: Pass any kwargs to plt.gca().set().
        """

        # Setup figure:
        fig = plt.figure(figsize=(9,6))
        ax = plt.gca()

        # Plot prompt:
        spec = "Output/extracted_spectrum.dat"
        df = pd.read_csv(spec,sep=r"\s+")
        e = df["EC[keV]"]
        e_width = df["BW[keV]"]
        r = df["src_ct/keV"]
        r_err = np.sqrt(r*e_width)/e_width
        xerr = e_width/2.0

        # Option to divide by exposure time:
        if exp_time != None:
            r = r/exp_time
            r_err = r_err/exp_time

        plt.loglog(e,r,color="black",marker="o",ms=8,ls="",label="crab", **plot_kwargs)
        plt.errorbar(e,r,yerr=r_err,xerr=xerr,color="black",marker="o",ms=8,ls="",label="_nolabel_", **plot_kwargs)

        plt.xticks(fontsize=12)
        plt.yticks(fontsize=12)
        plt.xlabel("Energy [keV]", fontsize=14)
        plt.ylabel("counts/keV", fontsize=14)
        if exp_time != None:
            plt.ylabel("counts/keV/s", fontsize=14)
        plt.grid(color="grey",alpha=0.3,ls="--")
        ax.set(**fig_kwargs)
        plt.savefig("Output/spectra.pdf")
        if show_plots == True:
            plt.show()
        plt.close()

        return

    def plot_lc(self, normed_time=True, show_plots=True, plot_kwargs={}, fig_kwargs={}):

        """
        Plots extracted mimrec light curve.

        normed_time: normalize the time to the initial time. 
            - Default is True.
            - If False, true time will be shown.
        
        show_plots: Option to not show plot (True or False).
        """
        
        # Setup figure:
        fig = plt.figure(figsize=(9,6))
        ax = plt.gca()

        # Plot prompt diffuse:
        lc = "Output/extracted_lc.dat"
        df = pd.read_csv(lc,sep=r"\s+")
        t = df["t_center[s]"]
        if normed_time == True:
            t = (t - t[0])
        r = df["ct/s"]
        t_width = df["t_width[s]"]
        yerr = np.sqrt(r*t_width)/t_width

        plt.semilogy(t,r,color="black",alpha=1,zorder=0,ls="-",marker="",label="cosmic photons", **plot_kwargs)
        plt.errorbar(t,r,color="black",yerr=yerr,alpha=1,zorder=0,ls="-",marker="",label="_nolabel_", **plot_kwargs)

        plt.xticks(fontsize=12)
        plt.yticks(fontsize=12)
        plt.xlabel("Time  [s]", fontsize=14)
        plt.ylabel("Rate [Hz]", fontsize=14)
        plt.grid(color="grey",alpha=0.3,ls="--")
        ax.set(**fig_kwargs)
        plt.savefig("Output/LCs.pdf")
        if show_plots == True:
            plt.show()
        plt.close()

    def plot_image(self, show_plots=True):

        """
        Plots mimrec image.

        show_plots: Option to not show plot (True or False).
        """

        # Upload data:
        df = pd.read_csv("Output/extracted_image.dat",sep=r"\s+")

        x = df["Phi_center[deg]"]
        y = df["Theta_center[deg]"]
        z = df["Intensity[a.u.]"]

        # Binning for all-sky map, in Galactic coordinates.
        # This needs to match the mimrec output.
        # Note: I need to update this to get the correct binning automatically. 
        x_range = np.arange(-177,183,6)
        y_range = np.arange(-88.5,91.5,3)

        # Convert z data into array:
        array_list = []
        for each in x_range:
            this_column_index = x == each
            this_column = z[this_column_index]
            array_list.append(this_column)
        array_list = np.array(array_list)

        # Setup figure:
        fig = plt.figure(figsize=(12,6))
        ax = plt.gca()

        # Plot:
        img = ax.pcolormesh(np.flip(x_range),y_range,array_list.T,cmap="cubehelix",vmin=0,vmax=1,shading=None)
        plt.xticks(fontsize=16)
        plt.yticks(fontsize=16)

        cbar = plt.colorbar(img,fraction=0.045)
        cbar.set_label("Intensity [a.u.]",size=16,labelpad=12)
        cbar.ax.tick_params(labelsize=12)

        plt.ylabel('Galactic Latitude [$\circ$]',fontsize=18)
        plt.xlabel('Galactic Longitude [$\circ$]',fontsize=18)
        plt.xticks(fontsize=16)
        plt.yticks(fontsize=16)

        ax.tick_params(axis='both',which='major',length=9)
        ax.tick_params(axis='both',which='minor',length=5)

        plt.grid(lw=1,ls="--",color="grey",alpha=0.3)
        plt.xlim(179.5,-179.5)

        plt.savefig("Output/sim_image.png",bbox_inches='tight')
        if show_plots == True:
            plt.show()

        return

    def clear_unessential_data(self):

        """By default the main simulation pipeline saves all of the output,
        for diagnostic purposes. This method removes un-needed output 
        files in order to reduce disk space."""

        # Get initial disk usage:
        print()
        print("Checking initial directory size...")
        os.system("du -h -d0 Simulations/")
        
        # Change to Simulations directory:
        os.chdir("Simulations")
        
        # Write directories to temporary file and read:
        os.system("ls -d */ > dirs.dat")
        df = pd.read_csv("dirs.dat", names=["dirs"], header=None)
        dirs_list = df["dirs"].tolist()
        
        # Remove un-needed files:
        print("Removing un-needed files...")
        for each in dirs_list:
            os.chdir(os.path.join(each,"Output"))
            os.system("rm -rf crossections cosima_terminal_output.txt \
                    revan_terminal_output.txt nuclearizer_terminal_output.txt")
            os.chdir("../..")
        os.system("rm dirs.dat")
        
        # Go home:
        os.chdir(self.home)

        # Get final disk usage:
        print("Checking final directory size...")
        os.system("du -h -d0 Simulations/")
        print()

        return

