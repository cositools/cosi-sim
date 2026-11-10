# Imports:
from cosi_sim.pipeline.calc_aeff import CalcAeff

# Define instance with input parameter card:
instance = CalcAeff("inputs.yaml")

# Generate tra file for simulation challenge:
instance.define_sim()
instance.run_cosima()
instance.run_nuclearizer()
instance.run_revan()
instance.run_mimrec(extract_root=True)

# Now calculate Aeff:
data_file = "Output/extracted_spectrum.dat"
model_file = "cosi-data-challenges/Source_Library/your_source/your_source_spec.dat"
pandas_kwargs = {"sep":r"\s+","skiprows":4}
instance.aeff_from_continuum_sims(data_file,model_file,check_mdl_cnts=True,pandas_kwargs=pandas_kwargs)
