import subprocess
# Keep track of the running subprocesses
processes = []

while True:
    # Start a new subprocess
    proc1 = subprocess.Popen(["python", "test_off_state_config.py"])
    processes.append(proc1)

    # Wait for the first subprocess to finish
    proc1.wait()

    # Terminate all other processes
    for proc in processes:
        proc.terminate()

    # Start the next subprocess
    proc2 = subprocess.Popen(["python", "state_machine.py"])
    processes = [proc2]  # Keep only the current subprocess

    # Wait for the second subprocess to finish
    proc2.wait()