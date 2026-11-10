# Imports:
import os,sys,shutil
import pandas as pd
import numpy as np
import scipy.integrate as integrate
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
import math
import gzip
from cosi_sim.pipeline.make_plots import MakePlots
from cosi_sim.pipeline.simulate import Simulate

class CalcAeff(Simulate):

    def define_aeff_sim(self,energy,theta=0):

        """
        This function makes the main source file for the Aeff 
        monoenergetic determination.

        Inputs:
        energy: monogenic energy to simulate.
        
        Optional:
        theta: off-axis angle. Default is zero.  
        """

        # Make output data directory:
        if os.path.isdir("Output") == True:
            shutil.rmtree("Output")
        os.system("mkdir Output")

        # Write source file:
        f = open(os.path.join("Output",self.source_file),"w")
        f.write("Version                1\n\n")
        f.write("#geometry file\n")
        f.write("Geometry %s\n\n" %self.geo_file)
        f.write("#Physics list\n")
        f.write("PhysicsListEM          LivermorePol\n\n")
        f.write("#Output formats\n")
        f.write("StoreSimulationInfo    all\n\n")
        f.write("#Define run:\n")
        f.write("Run Aeff\n")
        f.write("Aeff.FileName          %s\n" %self.name)
        f.write("Aeff.NTriggers         %s\n\n" %self.ntriggers)
        f.write("Aeff.Source            PS\n")
        f.write("PS.ParticleType        1\n")
        f.write("PS.Beam                FarFieldPointSource  %s 0\n" %str(theta))
        f.write("PS.Spectrum            Mono  %s\n" %str(energy))
        f.write("PS.Flux                1")
        
        # Option to include transmission probability:
        if self.include_transmission_prob == True:
            f.write("\nPS.FarFieldTransmissionProbability  %s" %self.transmission_prob_file)

        f.close()
    
        return

    def get_grid(self,elow,ehigh,num,remove=False):

        """
        Get log-spaced grid points for calculating Aeff.
        Returns list of grid points as strings.

        Inputs:
        elow: Lower energy bound in keV.
        ehigh: Upper energy bound in keV.
        num: number of grid points.

        Optional:
        remove: If true will remove all existing grid directories first. 
        """
        
        # Define grid:
        grid = np.logspace(np.log10(elow),np.log10(ehigh),num=num)

        grid_list = []
        for each in grid:

            this_dir = '{:.2f}'.format(each)
            grid_list.append(this_dir)

            # Remove directory if already exists:
            if (remove==True) & (os.path.isdir(this_dir) == True):
                shutil.rmtree(this_dir)

            # Make new directories:
            if os.path.isdir(this_dir) == False:
                os.system("mkdir %s" %str(this_dir))
                os.system("mkdir %s/Output" %str(this_dir))
            
            # Always copy files:
            os.system("scp inputs.yaml run_sims.py %s" %str(this_dir))
        
        print()
        print("Grid:")
        print(grid_list)
        print()

        return grid_list

    def get_sim_events(self):

        """Returns simulated events from cosima sim file."""
       
        # Get sim file:
        this_file = "Output/%s.inc1.id1.sim.gz" %(self.name)
        f = gzip.open(this_file,"rt")
        lines = f.readlines()
        
        for each in lines:
        
            # Get simulated counts:
            if "TS" in each:
                
                total_counts = float(each.split()[1])
        
        return total_counts
    
    def get_sim_events_parallel_time_bins(self):

        """
        Returns simulated events from cosima sim file
        for parallel time bins.
        """
       
        os.chdir("Simulations")

        total_counts = 0
        for i in range(0,self.num_sims+1):

            # Get sim file:
            this_file = "sim_%s/Output/%s.inc1.id1.sim.gz" %(str(i),self.name)
            f = gzip.open(this_file,"rt")
            lines = f.readlines()
        
            for each in lines:
        
                # Get simulated counts:
                if "TS" in each:
                
                    this_counts = float(each.split()[1])
                    total_counts += this_counts

        # Go home:
        os.chdir(self.home)
        
        return total_counts

    def get_sim_events_mcosima(self):


        """Returns the mean simulated events from all instances of mcosima."""

        os.chdir("Simulations")

        counts_list = []
        for j in range(1,self.num_cores+1):

            print()
            print("Working on core %s..." %str(j))

            total_counts = 0
            for i in range(0,self.num_sims+1):
    
                # Get sim file:
                this_file = "sim_%s/Output/%s.p1.inc%s.id1.sim.gz" %(str(i),self.name,str(j))
                f = gzip.open(this_file,"rt")
                lines = f.readlines()
        
                for each in lines:
        
                    # Get simulated counts:
                    if "TS" in each:
                
                        this_counts = float(each.split()[1])
                        total_counts += this_counts

            counts_list.append(total_counts)

        # Get means and std:
        counts_list = np.array(counts_list)
        mean_cts = np.mean(counts_list)
        cts_std = np.std(counts_list)
        total_cts = np.sum(counts_list)
        total_cts_err = np.sqrt(total_cts)

        print()
        print("counts list:")
        print(counts_list)
        print()
        print("mean counts: " + str(mean_cts) + " +/- " + str(cts_std))
        print("total counts: " + str(total_cts) + " +/- " + str(total_cts_err))
        print()

        # Go home:
        os.chdir(self.home)

        return total_cts

    def get_arm_counts(self):

        """
        Returns simulated events within FWHM of arm calculation.
            - Requires mimrec_arm_output.txt. 
        """
       
        # Get sim file:
        this_file = "Output/mimrec_arm_output.txt" 
        f = open(this_file,"r")
        lines = f.readlines()
        
        satisfied=False
        for each in lines:
        
            # Get simulated counts:
            if "Compton and pair events in histogram:" in each:
                
                self.arm_counts = float(each.split()[6])
                satisfied=True
                print()
                print("Counts within FWHM of ARM:")
                print(self.arm_counts)
        
        # If there are no ARM counts set to zero:
        if satisfied == False:
            print()
            print("WARNING: No counts in ARM!")
            print()
            self.arm_counts = 0.0

        return 
    
    def get_observed_counts(self,input_data):
 
        """
        Gets observed (simulated) counts for each energy bin and 
        corresponding energy bin info.
        
        Inputs:
        input_data: Input data file from run_mimrec output. 
        """

        # Observed events:
        df_data = pd.read_csv(input_data, sep=r"\s+")
        flux_data = df_data["src_ct/keV"] # ph/keV
        bin_width = df_data["BW[keV]"] # keV
        self.elow = df_data["EL[keV]"] 
        self.ehigh = df_data["EH[keV]"] 
        self.emean = np.sqrt(self.elow*self.ehigh) # geometric mean of energy bin 
        xerr_low = self.emean - self.elow
        xerr_high = self.ehigh - self.emean
        self.xerr = np.array([xerr_low.tolist(),xerr_high.tolist()])
        self.data_counts = flux_data*bin_width
        self.data_counts_err = np.sqrt(self.data_counts)
       
        return 

    def get_model_counts(self,input_model,sky_area=1.0,kwargs={}):

        """
        Gets predicted model counts per energy bin and corresponing 
        energy for a point source or an extended source.
        
        Inputs:
        input_model [str]: Data file giving spectrum of model.
            - col0: energy in keV.
            - col1: flux in ph/cm^2/s/keV for point source, 
                     or ph/cm^2/s/keV/sr for diffuse source.
        
        Optional:
        kwargs: pass any kwargs to pandas read_csv method. 
        sky_area [float]: Area of sky in steradians covered by input model.
            - Only needs to be specified for diffuse sources. 
        """

        # Input model:
        df_model = pd.read_csv(input_model,**kwargs)
        col0=df_model.columns[0]
        col1=df_model.columns[1]
        self.model_energy = df_model[col0] 
        model_flux = df_model[col1] 
        
        print()
        print("Model data frame:")
        print(df_model)
        print()

        # Convert to number of generated events:
        self.model_counts = model_flux * self.time * self.ASphere * sky_area #ph/keV

        return

    def aeff_from_mono_sims(self,input_data,energy):

        """
        Calculate the effective area from monoenergetic simulations.
        
        Inputs:
        input_data: Data file for observed counts.
            - Must be same format as from run_mimrec output. 
        energy: energy used for the simulations, in keV.
        """
        
        # Total observed events:
        self.get_observed_counts(input_data)
        
        # Observed events within FWHM of ARM:
        self.get_arm_counts()

        # Total simulated events:
        sim_events = self.get_sim_events()
        model_counts = np.array([sim_events])
                
        # Calculate effective area, for both total and ARM:
        self.A_eff_tot = ((np.sum(self.data_counts))/np.sum(model_counts)) * self.ASphere
        self.A_eff_arm = ((np.sum(self.arm_counts))/np.sum(model_counts)) * self.ASphere

        # Save effective_area:
        d = {"energy[keV]":[energy],"A_eff_tot[cm^2]":[self.A_eff_tot],"A_eff_arm[cm^2]":[self.A_eff_arm]}
        df = pd.DataFrame(data = d,columns=["energy[keV]","A_eff_tot[cm^2]","A_eff_arm[cm^2]"])
        df.to_csv("Output/Aeff.dat",sep="\t",index=False)

        return

    def aeff_from_continuum_sims(self,input_data,input_model,\
            sky_area=1.0,check_mdl_cnts=False,pandas_kwargs={}):
    
        """
        Calculates the effective area from the data challenge simulations
        for a continuum source.

        Inputs:
        input_data: Data file for observed count rate. 
            - Must be same format as from run_mimrec output. 

        input_model: Full path to model file.
            - Must be the same formate as from the source library. 

        Optional:
        sky_area [float]: Area of sky in steradians covered by input model.
            - Only needs to be specified for diffuse sources. 
         
        check_mdl_cts [float]: option to compare calculated model 
            counts to actual number of simulated events. 

        pandas_kwargs [dict]: pass any kwargs to pandas read_csv method
            - Used for reading input model.

        Important: When calculating Aeff for a diffuse source, ￼
        the input_model needs to be from the same sky region as 
        the input_data, which will correspond to the sky_area.
        """

        # Observed counts:
        self.get_observed_counts(input_data)

        # Model count rate:
        self.get_model_counts(input_model,sky_area=sky_area,kwargs=pandas_kwargs)

        # Interpolate model to match with the data energy binning:
        model_counts_interp = interp1d(self.model_energy, self.model_counts, kind='linear', bounds_error=True) 
 
        # Integrate model counts over energy bins:
        model_counts_list = []
        for k in range(0,len(self.elow)):
            intg = integrate.quad(lambda x:model_counts_interp(x),self.elow[k],self.ehigh[k])
            model_counts_list.append(intg[0])
        model_counts_list = np.array(model_counts_list)

        # Calculate effective area as a function of energy:
        self.A_eff = (self.data_counts/model_counts_list) * self.ASphere
        self.A_eff_err = (self.data_counts_err/model_counts_list) * self.ASphere

        # Calculate total effective area, integrated over all energies:
        self.A_eff_full = ((np.sum(self.data_counts))/np.sum(model_counts_list)) * self.ASphere
 
        # Save energy-dependent effective_area:
        d = {"energy[keV]":self.emean,"A_eff[cm^2]":self.A_eff}
        df = pd.DataFrame(data = d,columns=["energy[keV]","A_eff[cm^2]"])
        df.to_csv("Output/Aeff.dat",sep="\t",index=False)

        # Option to compare calculated total model counts to actual simulated events:
        if check_mdl_cnts == True:

            # Get bins from model file:
            # Note: Need to use exact match of first and last energy.
            energy_min = np.min(self.model_energy)
            energy_max = np.max(self.model_energy)
            bins = np.logspace(np.log10(energy_min),np.log10(energy_max),num=100)
        
            model_counts_true = []
            for k in range(0,len(bins)-1):
                intg = integrate.quad(lambda x:model_counts_interp(x),bins[k],bins[k+1])
                model_counts_true.append(intg[0])
            model_counts_true = np.array(model_counts_true)
       
            # Get simulated events from sim file:
            if (self.mcosima == True) & (self.parallel_time_sims == True):
                cosima_cts = self.get_sim_events_mcosima()
            elif  (self.mcosima == False) & (self.parallel_time_sims == True):
                cosima_cts = self.get_sim_events_parallel_time_bins()
            elif  (self.mcosima == False) & (self.parallel_time_sims == False):
                cosima_cts = self.get_sim_events()
            else:
                print()
                print("ERROR: Unable to get number of simulated events.")
                print("Check your input selections for mcosima and parallel_time_bins.")
                print()
                sys.exit()

            # Calculate difference:
            diff_err = (np.sum(model_counts_true) - cosima_cts) / math.sqrt(np.sum(model_counts_true))
            percent_diff = (np.sum(model_counts_true) - cosima_cts) / np.sum(model_counts_true)
            print()
            print("Total model counts calculated from flux input:")
            print(str(np.sum(model_counts_true)) + " +/- " + str(np.sqrt(np.sum(model_counts_true))))
            print("Simualted events from cosima:")
            print(cosima_cts)
            print()
            print("Percent diff wrt cosima: " + str(percent_diff))
            print("Number of sigma from cosima:" + str(diff_err))
            print()

        # Plot Aeff:
        plot_kwargs = {"ls":"", "marker":"s", "color":"black", "lw":2}
        
        fig_kwargs = {"xlabel":"Energy [keV]", \
                "ylabel":r"Effective Area [$\mathrm{cm^{2}}$]",\
                "yscale":"linear","ylim":(0,1.3*np.max(self.A_eff))}
    
        MakePlots().make_basic_plot(self.emean, self.A_eff, x_error=self.xerr,\
                plot_kwargs=plot_kwargs, fig_kwargs=fig_kwargs,\
                savefig="Output/Aeff.pdf")

        return
