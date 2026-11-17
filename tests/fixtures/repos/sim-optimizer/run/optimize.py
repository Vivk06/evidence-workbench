import subprocess
subprocess.run(["mpirun", "-np", "4", "solver", "run.cfg"])
