#422510839
#s22010004
#L.A.M.C.H.Karunasena

import simpy
import random
import statistics
import csv
import os
import matplotlib.pyplot as plt



# Simulation Parameters
RANDOM_SEED = 42
ARRIVAL_RATE = 2
MEAN_SERVICE = 4
SIM_TIME = 8 * 60

CUSTOMER_COUNTS = [10, 18, 27, 35, 48, 56, 66]

OUTPUT_FILE = "supermarket_results.csv"



# Customer Process

def customer(env, cashiers, waits, services, queues):

    # Record customer arrival time
    arrival = env.now

    # Record queue length at arrival
    queues.append(len(cashiers.queue))

    # Request a cashier
    with cashiers.request() as request:

        # Wait until a cashier becomes available
        yield request

        # Calculate waiting time
        wait_time = env.now - arrival
        waits.append(wait_time)

        # Generate service time using exponential distribution
        service = random.expovariate(1 / MEAN_SERVICE)
        services.append(service)

        # Customer receives checkout service
        yield env.timeout(service)


# Customer Generator

def generate_customers(
    env,
    cashiers,
    waits,
    services,
    queues,
    total
):

    for i in range(total):

        # Generate random time between customer arrivals
        arrival = random.expovariate(ARRIVAL_RATE)

        yield env.timeout(arrival)

        # Create customer process
        env.process(
            customer(
                env,
                cashiers,
                waits,
                services,
                queues
            )
        )


# Run One Simulation
def simulate(customers, cashier_count):

    # Reset random generator using fixed seed
    random.seed(RANDOM_SEED)

    # Create SimPy environment
    env = simpy.Environment()

    # Create cashier resource
    cashiers = simpy.Resource(
        env,
        capacity=cashier_count
    )

    # Lists for performance measurements
    waits = []
    services = []
    queues = []

    # Start customer generator
    env.process(
        generate_customers(
            env,
            cashiers,
            waits,
            services,
            queues,
            customers
        )
    )

    # Run simulation for 480 minutes
    env.run(until=SIM_TIME)

    # Calculate average waiting time
    avg_wait = (
        statistics.mean(waits)
        if waits else 0
    )

    # Calculate average queue length
    avg_queue = (
        statistics.mean(queues)
        if queues else 0
    )

    # Calculate throughput
    throughput = len(services) / SIM_TIME

    # Calculate cashier utilization
    utilization = (
        sum(services) /
        (cashier_count * SIM_TIME)
    )

    return [
        len(services),
        avg_wait,
        throughput,
        avg_queue,
        utilization
    ]


# Run All Simulations
def run_simulations(cashier_count):

    results = []

    print("\n" + "=" * 75)
    print(f"Results for {cashier_count} Cashiers")
    print("=" * 75)

    print(
        f"{'Customers':<12}"
        f"{'Wait':<12}"
        f"{'Throughput':<15}"
        f"{'Queue':<12}"
        f"{'Utilization':<12}"
    )

    print("-" * 75)

    # Run simulation for each customer load
    for customers in CUSTOMER_COUNTS:

        result = simulate(
            customers,
            cashier_count
        )

        results.append(result)

        print(
            f"{result[0]:<12}"
            f"{result[1]:<12.2f}"
            f"{result[2]:<15.4f}"
            f"{result[3]:<12.2f}"
            f"{result[4]:<12.3f}"
        )

    # Save results to CSV
    save_csv(
        results,
        cashier_count
    )

    # Create graphs
    create_graphs(
        results,
        cashier_count
    )


# Save Results to CSV
def save_csv(results, cashier_count):

    exists = os.path.exists(OUTPUT_FILE)

    with open(
        OUTPUT_FILE,
        "a",
        newline=""
    ) as file:

        writer = csv.writer(file)

        
        if not exists:

            writer.writerow([
                "Customers",
                "Cashiers",
                "Average Wait",
                "Throughput",
                "Average Queue",
                "Utilization"
            ])

        # simulation results
        for r in results:

            writer.writerow([
                r[0],
                cashier_count,
                round(r[1], 2),
                round(r[2], 4),
                round(r[3], 2),
                round(r[4], 3)
            ])

    print(
        f"\nResults saved to {OUTPUT_FILE}"
    )


# Create Graphs
def create_graphs(
    results,
    cashier_count
):

    customers = [
        r[0] for r in results
    ]

    wait = [
        r[1] for r in results
    ]

    queue = [
        r[3] for r in results
    ]

    utilization = [
        r[4] for r in results
    ]

    throughput = [
        r[2] for r in results
    ]

    # Graph information
    graphs = [

        (
            wait,
            "Average Waiting Time",
            "Waiting Time (minutes)",
            "average_waiting_time.png"
        ),

        (
            queue,
            "Average Queue Length",
            "Queue Length",
            "average_queue_length.png"
        ),

        (
            utilization,
            "Cashier Utilization",
            "Utilization",
            "cashier_utilization.png"
        ),

        (
            throughput,
            "Customer Throughput",
            "Customers per Minute",
            "throughput.png"
        )
    ]

    # Create each graph
    for values, title, ylabel, filename in graphs:

        plt.figure(figsize=(8, 5))

        plt.plot(
            customers,
            values,
            marker="o"
        )

        plt.title(
            f"{title} - {cashier_count} Cashiers"
        )

        plt.xlabel(
            "Number of Customers"
        )

        plt.ylabel(ylabel)

        plt.grid(True)

        plt.tight_layout()

        plt.savefig(filename)

        plt.show()

    print(
        "\n4 diagrams created successfully!"
    )


#Main Program
if __name__ == "__main__":

    try:

        cashier_count = int(
            input(
                "Enter number of cashiers: "
            )
        )

        # Check cashier count
        if cashier_count <= 0:

            raise ValueError

        # Run simulations
        run_simulations(
            cashier_count
        )

    except ValueError:

        print(
            "Invalid input. "
            "Please enter a positive number."
        )