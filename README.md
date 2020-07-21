# Usage:
(pip install -r requirements.txt)
python annealing.py [-h -p -f]

-h, --help  show help message and exit
-p          choose from Taillard's instances
-f          choose file to load problem from


# Parameters:  
initial_temperature - Initial temperature for simulated annealing  
frozen_temperature - Abort temperature for simulated annaeling  
cooling_ratio - Rate of temperature decrease  
iterations - Number of iterations per cooling step  
initial_method - How to generate initial solution. Either "random" or "trivial"  
neighbor_method - How to generate neighborhood. "far" swaps any two operations on a machine,  
		"near" only swaps adjacent operations
