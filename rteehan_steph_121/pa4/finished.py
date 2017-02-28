# CS121: Polling places
#
# Ryan Teehan + Stephanie Williams 
#
# Main file for polling place simulation

import sys
import util
import random 

from queue import PriorityQueue

class Voter(object):
    ID = 0
    def __init__(self, arrival_time, voting_duration):
        Voter.ID += 1
        self.voter_id = Voter.ID
        self._arrival_time = arrival_time
        self._voting_duration = voting_duration
        self._start_time = None
        self._departure_time = None

    def get_arrival_time(self):
        return self._arrival_time

    def set_arrival_time(self, arrival_time):
        self._arrival_time = arrival_time

    def get_voting_duration(self):
        return self._voting_duration

    def set_voting_duration(self, voting_duration):
        self._voting_duration = voting_duration

    def get_start_time(self):
        return self._start_time

    def set_start_time(self, start_time):
        self._start_time = start_time
    
    def get_departure_time(self):
        return self._departure_time

    def set_departure_time(self, departure_time):
        self._departure_time = departure_time
    
    '''
    def update_departure_time(self):
        if self.start_time == None:
            dept_time = None
        elif start_time == int(start_time):
            dept_time = self.start_time + self.voting_duration
        return dept_time
    '''

   
    arrival_time = property(get_arrival_time, set_arrival_time)
    voting_duration = property(get_voting_duration, set_voting_duration)
    start_time = property(get_start_time, set_start_time)
    departure_time = property(get_departure_time, set_departure_time)
  

class Sample(object):
    def __init__(self, hours_open, arrival_rate, 
        num_voters,voting_duration_rate):

        self.mins_open = hours_open * 60
        self.arrival_rate = arrival_rate
        self.num_voters = num_voters
        self.voting_duration_rate = voting_duration_rate
        self.last_arrival = 0
        self.last_duration = None
        self.gen_voters = 0

    def has_next(self):
        gap, voter_duration = util.gen_voter_parameters(self.arrival_rate, 
            self.voting_duration_rate)
        self.last_duration = voter_duration
        self.last_arrival = self.last_arrival + gap
        self.gen_voters += 1 
        if self.gen_voters > self.num_voters: 
            return False
        if self.last_arrival > self.mins_open:
            return False  
        return True

    def next(self):
        return Voter(self.last_arrival, self.last_duration)
        #assert later

class Precinct(object):
    def __init__(self, number_of_booths):
        self.sorted_v_booths = PriorityQueue(number_of_booths)
        self.prev_depart = 0
    
    def exit(self):
        (a, b) = self.sorted_v_booths.get()
        self.prev_depart = a 
        return b

    def enter(self, voter):
        print(voter.departure_time)
        self.sorted_v_booths.put((voter.departure_time, voter))
        

    def is_full(self):
        return self.sorted_v_booths.full()

def simulate_election_day(config):
    voters = []  
    random.seed(config['seed']) 
    sample = Sample(config['hours_open'], config['arrival_rate'], config['num_voters'], config['voting_duration_rate'])
    p = Precinct(config['number_of_booths'])
    while sample.has_next():
        voter = sample.next()
        if p.is_full():
            p.exit() 
        if voter.arrival_time > p.prev_depart:
            voter.start_time = voter.arrival_time
            voter.departure_time = voter.start_time + voter.voting_duration
        else:
            voter.start_time = p.prev_depart
            voter.departure_time = voter.start_time + voter.voting_duration 
        p.enter(voter) 
        voters.append(voter)
    return voters

if __name__ == "__main__":
    # process arguments
    num_booths = 1

    if len(sys.argv) == 2:
        config_filename = sys.argv[1]
    elif len(sys.argv) == 3:
        config_filename = sys.argv[1]
        num_booths = int(sys.argv[2])
    else:
        s = "usage: python3 {0} <configuration filename>"
        s = s + " [number of voting booths]"
        s = s.format(sys.argv[0])
        print(s)
        sys.exit(0)
    config = util.setup_config(config_filename, num_booths)
    voters = simulate_election_day(config)
    util.print_voters(voters)

