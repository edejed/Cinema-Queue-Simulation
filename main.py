import collections
import random

import simpy


seed = 42
tickets = 50  # Tickets available per show
sim_time = 120  # The simulation will run until


def customer(env, movie, num_tickets, theater):

    with theater.counter.request() as my_turn:
        result = yield my_turn | theater.sold_out[movie]

        if my_turn not in result:
            theater.num_renegers[movie] += 1
            return

        # Check if there is still available tickets
        if theater.available[movie] < num_tickets:
            # The customer will leave if there's no available ticket
            yield env.timeout(0.5)
            return

        # The customer who's in queue will buy a ticket
        theater.available[movie] -= num_tickets
        if theater.available[movie] < 2:
            theater.sold_out[movie].succeed()
            theater.when_sold_out[movie] = env.now
            theater.available[movie] = 0
        yield env.timeout(1)


def customer_arrivals(env, theater):
    while True:
        yield env.timeout(random.expovariate(1 / 0.5))

        movie = random.choice(theater.movies)
        num_tickets = random.randint(1, 6)
        if theater.available[movie]:
            env.process(customer(env, movie, num_tickets, theater))


Theater = collections.namedtuple('Theater', 'counter, movies, available, '
                                            'sold_out, when_sold_out, '
                                            'num_renegers')


# Setup and start the simulation
print('Cinema Queue Simulation')
random.seed(seed)
env = simpy.Environment()

# Create Environment
counter = simpy.Resource(env, capacity=1)
movies = ['Avengers: Endgame', 'Inception', 'Grave Of The Fireflies']
available = {movie: tickets for movie in movies}
sold_out = {movie: env.event() for movie in movies}
when_sold_out = {movie: None for movie in movies}
num_renegers = {movie: 0 for movie in movies}
theater = Theater(counter, movies, available, sold_out, when_sold_out,
                  num_renegers)

# build and run
env.process(customer_arrivals(env, theater))
env.run(until=sim_time)

# Results of data
for movie in movies:
    if theater.sold_out[movie]:
        print('Show "%s" sold out %.1f minutes after ticket counter '
              'opening.' % (movie, theater.when_sold_out[movie]))
        print(' %s People leaves the queue after the ticket got sold out' %
              theater.num_renegers[movie])
