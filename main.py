import collections
import random

import simpy


seed = 42
tickets = 100  # Tickets available per show
sim_time = 120  # The simulation will run until


def customer(env, movie, num_tickets, cinema):

    with cinema.counter.request() as my_turn:
        result = yield my_turn | cinema.sold_out[movie]

        if my_turn not in result:
            cinema.num_renegers[movie] += 1
            return

        # Check if there is still available tickets
        if cinema.available[movie] < num_tickets:
            # The customer will leave if there's no available ticket
            yield env.timeout(0.5)
            return

        # The customer who's in queue will buy a ticket
        cinema.available[movie] -= num_tickets
        if  cinema.available[movie] < 2:
             cinema.sold_out[movie].succeed()
             cinema.when_sold_out[movie] = env.now
             cinema.available[movie] = 0
        yield env.timeout(1)


def customer_arrivals(env, cinema):
    while True:
        yield env.timeout(random.expovariate(1 / 0.5))

        movie = random.choice( cinema.movies)
        num_tickets = random.randint(1, 6)
        if  cinema.available[movie]:
            env.process(customer(env, movie, num_tickets,  cinema))


 cinema = collections.namedtuple('cinema', 'counter, movies, available, '
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
 cinema =  cinema(counter, movies, available, sold_out, when_sold_out,
                  num_renegers)

# build and run
env.process(customer_arrivals(env,  cinema))
env.run(until=sim_time)

# Results of data
for movie in movies:
    if  cinema.sold_out[movie]:
        print('Show "%s" sold out %.1f minutes after ticket counter '
              'opening.' % (movie,  cinema.when_sold_out[movie]))
        print(' %s People leaves the queue after the ticket got sold out' %
               cinema.num_renegers[movie])
