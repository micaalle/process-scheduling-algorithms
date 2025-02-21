import sys

class Process:
    def __init__(self, name, arrival, burst):
        self.name = name
        self.arrival = int(arrival)
        self.burst = int(burst)
        self.remaining_burst = int(burst)
        self.start_time = None
        self.finish_time = None
        self.wait_time = None
        self.turnaround_time = None
        self.response_time = None

def read_input_file(input_filename):
    try:
        with open(input_filename, 'r') as file:
            lines = file.readlines()
    except FileNotFoundError:
        print(f"Error: The file {input_filename} was not found.")
        sys.exit(1)

    processes = []
    runfor = None
    algorithm = None
    quantum = None
    process_count = None

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if line.startswith("processcount"):
            process_count = int(line.split()[1])

        elif line.startswith("runfor"):
            runfor = int(line.split()[1])

        elif line.startswith("use"):
            algorithm = line.split()[1]

        elif line.startswith("quantum"):
            quantum = int(line.split()[1])

        elif line.startswith("process"):
            parts = line.split()
            # Correct input names 
            if len(parts) == 7 and parts[0] == "process" and parts[1] == "name" and parts[3] == "arrival" and parts[5] == "burst":
                name = parts[2]
                arrival = parts[4]
                burst = parts[6]
                processes.append(Process(name, arrival, burst))
            else:
                print(f"Error: Invalid process line format: {line}")
                sys.exit(1)

        elif line == "end":
            if algorithm == "rr" and quantum is None:
                print("Error: Missing quantum parameter when use is 'rr'")
                sys.exit(1)

            if algorithm is None:
                print("Error: Missing parameter 'use'")
                sys.exit(1)

            if runfor is None:
                print("Error: Missing parameter 'runfor'")
                sys.exit(1)

            if process_count is None or len(processes) != process_count:
                print(f"Error: Missing or invalid processcount")
                sys.exit(1)

    return processes, runfor, algorithm, quantum

def print_summary(processes, runfor, algorithm, quantum):
    print(f"{len(processes)} processes")
    if algorithm == 'rr':
        print(f"Using Round Robin with quantum {quantum}")
    else:
        print(f"Using {algorithm.capitalize()}")
    
    for process in processes:
        if process.finish_time is not None:
            process.wait_time = process.finish_time - process.arrival - process.burst
            process.turnaround_time = process.finish_time - process.arrival
            process.response_time = process.start_time - process.arrival

    print(f"Finished at time {runfor}")

    for process in processes:
        if process.finish_time is None:
            print(f"{process.name} did not finish")
        else:
            print(f"{process.name} wait {process.wait_time} turnaround {process.turnaround_time} response {process.response_time}")

def preemptive_sjf(processes, runfor):
    time = 0
    queue = []
    finished_processes = []
    current_process = None  
    print(f"Time {time:3} : Idle")  

    while time < runfor:
        # add processes to the queue when their timer check comes 
        for process in processes:
            if process.arrival <= time and process not in queue and process not in finished_processes:
                print(f"Time {time:3} : {process.name} arrived") 
                queue.append(process)

        if queue:
            # sort the queue via the remaining burst time 
            queue.sort(key=lambda x: x.remaining_burst)

            next_process = queue[0]

  
            if next_process != current_process:
                if current_process:  
                    print(f"Time {time:3} : {current_process.name} preempted")

                current_process = next_process

                if current_process.start_time is None:
                    current_process.start_time = time

                print(f"Time {time:3} : {current_process.name} selected (burst {current_process.remaining_burst})")

            current_process.remaining_burst -= 1
            time += 1  

            # if the process has finished, mark its finish time and remove it from the queue
            if current_process.remaining_burst == 0:
                current_process.finish_time = time
                print(f"Time {time:3} : {current_process.name} finished")
                finished_processes.append(current_process)
                queue.pop(0)  
                current_process = None 
        else:
            print(f"Time {time:3} : Idle")
            time += 1 

    print_summary(processes, runfor, 'sjf', None)

def fcfs(processes, runfor):
    time = 0
    queue = []
    finished_processes = []
    current_process = None 
    print(f"Time {time:3} : Idle") 

    while time < runfor:
        for process in processes:
            if process.arrival <= time and process not in queue and process not in finished_processes:
                print(f"Time {time:3} : {process.name} arrived")  
                queue.append(process)

        if queue:
            next_process = queue[0]

            # if there's a different process from the current one, handle selection
            if next_process != current_process:
                if current_process:  
                    print(f"Time {time:3} : {current_process.name} preempted")

                current_process = next_process

                
                if current_process.start_time is None:
                    current_process.start_time = time

                print(f"Time {time:3} : {current_process.name} selected (burst {current_process.remaining_burst})")

          
            current_process.remaining_burst -= 1
            time += 1 

            # mark the current finish time if compeletion 
            if current_process.remaining_burst == 0:
                current_process.finish_time = time
                print(f"Time {time:3} : {current_process.name} finished")
                finished_processes.append(current_process)
                queue.pop(0)  #
                current_process = None 
        else:
            print(f"Time {time:3} : Idle")
            time += 1  

    print_summary(processes, runfor, 'fcfs', None)

def round_robin(processes, runfor, quantum):
    time = 0
    queue = []
    finished_processes = []
    print(f"Time {time:3} : Idle")  # Initially idle

    while time < runfor:
     
        for process in processes:
            if process.arrival <= time and process not in queue and process not in finished_processes:
                print(f"Time {time:3} : {process.name} arrived") 
                queue.append(process)

        if queue:
  
            next_process = queue.pop(0)

          
            if next_process.start_time is None:
                next_process.start_time = time

           
            print(f"Time {time:3} : {next_process.name} selected (burst {next_process.remaining_burst})")

 
            time_slice = min(quantum, next_process.remaining_burst)

            next_process.remaining_burst -= time_slice

            # for loop because I couldn't figure out how to add the time_slice straight into time without messing up the arrival order in the queue 
            for _ in range(time_slice):
                time += 1 

                # arrival check
                for process in processes:
                    if process.arrival == time and process not in queue and process not in finished_processes:
                        print(f"Time {time:3} : {process.name} arrived") 
                        queue.append(process)

            if next_process.remaining_burst == 0:
                next_process.finish_time = time
                print(f"Time {time:3} : {next_process.name} finished")
                finished_processes.append(next_process)
            else:
               
                queue.append(next_process)
        else:
            print(f"Time {time:3} : Idle")
            time += 1  

    print_summary(processes, runfor, 'rr', quantum)

def main():
    if len(sys.argv) != 2:
        print("Usage: scheduler-gpt.py <input file>")
        sys.exit(1)

    input_filename = sys.argv[1]
    processes, runfor, algorithm, quantum = read_input_file(input_filename)

    if algorithm == "fcfs":
        fcfs(processes, runfor)
    elif algorithm == "sjf":
        preemptive_sjf(processes, runfor)
    elif algorithm == "rr":
        if quantum is None:
            print("Error: Missing quantum parameter when use is 'rr'")
            sys.exit(1)
        round_robin(processes, runfor, quantum)
    else:
        print(f"Error: Invalid scheduling algorithm: {algorithm}")
        sys.exit(1)

if __name__ == "__main__":
    main()