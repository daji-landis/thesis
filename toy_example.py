import random
from datetime import datetime
import math
from enum import Enum
import hashlib


# defining transfer function between players/player and contract
def transfer(sender, receiver, amount):
    if sender.funds < amount:
        print("Insufficient funds, transaction failed")
    else:
        sender.burn(amount)
        receiver.deposit(amount)

# coin flip function
def coin_flip(p = 0.5, seed = 0):
    if seed == 0:
        seed = datetime.now().timestamp()
    random.seed(seed)
    result = random.random()
    if result <= p:
        return 1
    else:
        return 0

def hash(r):
    if type(r) is not bin:
        r = bin(r).encode('utf-8')
    m = hashlib.sha256()
    m.update(r)
    m.hexdigest()
    return m


# defining player's information for computation
class InfoPacket:
    def __init__(self, data = 0, circuit = lambda x:x):
        self.data = data
        self.circuit = circuit

    def evaluate(self):
        # plug the data into the lambda
        return self.circuit(self.data)

class Player:
    def __init__(self, name, proof = lambda x:x, circuit_info = InfoPacket(), funds = 0):
        self.name =  name
        self.funds = funds
        self.circuit_info = circuit_info
        self.proof_info = InfoPacket(0, proof)
        self.r = random.randint(10000, 100000)

    def __str__(self):
        # print name and fund info
        return f"{self.name}({self.funds})"

    def do_computation(self):
        # do the computation and save to proof info packet, just for prover
        self.proof_info.data = self.circuit_info.evaluate()

    def player_commit_hash(self, contract):
        # does hash and publishes the result to the contract
        my_hash = hash(self.r)
        contract.commit_hash(id = self.name , hash = my_hash)

    def deposit(self, delta):
        # deposit function for the players, called by the transaction function
        self.funds += delta

    def burn(self, delta):
        # burn function for the players, called by the transaction function
        if delta > self.funds:
            print("Insufficient funds")
        else:
            self.funds = self.funds - delta

class contract_states(Enum):
    start = 1
    committed = 2
    verify = 3
    good = 4
    badness = 5

# defining contract
class SmartContract:
    def __init__(self, prover, verifier, stake_p, stake_v,
                funds = 0, circuit_info=InfoPacket(), proof_info = InfoPacket()):
        self.prover = prover    # object of the prover
        self.verifier = verifier # " verifier
        self.stake_p = stake_p  # lambda
        self.stake_v = stake_v  # alpha
        self.funds = funds      # total funds in the contract
        self.circuit_info = circuit_info # info packet of the circuit to be solved
        self.proof_info = proof_info  # circuit verifier wants solved
        self.state = 1 # starting state
        self.v_hash = 0 # for the verifier to submit the hash of their randomness
        self.p_hash = 0 # for the prover to submit the same

    def __str__(self):
        # returns funds and staked money left in the contract at the end, which should be 0
        return( f"Staked funds: {self.funds}" + " Contract State: "+ str(contract_states(self.state).name))

    def burn(self, delta = 0):
    # burns funds in contract. burns all funds by default
        if delta == 0:
            self.funds = 0
        else:
            self.funds = self.funds - delta

    def deposit(self, delta):
        # add money to the contract. called by transfer function
        self.funds += delta

    def z(self,p):
        # rolls coin_flip with probability p
        return coin_flip(p)

    def verify(self):
        my_input = self.circuit_info.data
        proof_output = self.proof_info.evaluate()
        if my_input == proof_output:
            return True
        else:
            return False

    def commit_hash(self, id, hash):
        # the players call this function to commit the hash of their randomness
        if id == "Vivian" and self.v_hash == 0:
            self.v_hash = hash
        elif id == "Petra" and self.p_hash == 0:
            self.p_hash = hash
        else:
            print("Commit Failed")

    def check_hash(self, r, old_hash): # old_hash is the player's commited hash
        # hashes randomness to check the hash of the player
        old_hash = old_hash.hexdigest()
        new_hash = hash(r).hexdigest()
        if new_hash == old_hash:
            return True
        else:
            print("old ")
            print(old_hash.hexdigest())
            print("new ")
            print(new_hash.hexdigest())
            return False

    def exicute_check_stake(self):
        # check correct funds, return
        if self.funds != self.stake_p + self.stake_v:  # this is a tautology, should change
            transfer(self, verifier, stake_v)
            transfer(self, prover, stake_p)
            self.state = 5 # badness
        else:
            self.state = 2 # committed

    def exicute_randomness(self, p, r_v, r_p):
        check_1 = self.check_hash(r_v, self.v_hash)
        check_2 = self.check_hash(r_p, self.p_hash)

        if check_1 and check_2 == True:
            self.state = 2 # 2 is commited
        else:
            self.state = 5 # 5 is badness

        seed = r_v ^ r_p # combine the hashed randomness of the players

        if self.state == 2:
            z = coin_flip(p, seed)

            if z == 0:
                self.state = 4  # good
            else:
                print("check")
                self.state = 3 # verify

    def exicute_verify(self):
        check = self.verify() # contract verifies proof
        if check == True:
            self.state = 4 # good
        else:
            self.state = 5 # badness

    def exicute_assess_state(self):
        if self.state == 4: # good
            transfer(self, self.verifier, self.funds) # pay verifier
        elif self.state == 5: # badness
            transfer(self, self.prover, self.funds) # prover gets her money back
            self.burn() # burn everything else
            print("burnt")
        else:
            print("panic")


def main():
    p = 0.9 #prob of rolling to require verification by the contract

    # verifier's info
    circuit = lambda x:x*x # circuit is squaring the input
    x = 5 # and here is the input
    info_v = InfoPacket(x, circuit) # the verifier's information, data and circuit
    player_v = Player("Vivian", circuit_info = info_v, funds = 100)

    # prover's info
    proof = lambda y:int(math.sqrt(y)) # hardcode the proof of the computation
    player_p = Player("Petra", proof = proof, funds = 100)

    # contract info
    stake_v = 40 # staking value alpha from notes
    stake_p = 50 # staking value lambda from notes

    contract = SmartContract(player_p, player_v, stake_p, stake_v)

    # verifier stakes funds and sends info
    transfer(player_v, contract, contract.stake_v) # stake

    player_p.circuit_info = player_v.circuit_info # send info packet to prover
    contract.circuit_info = player_v.circuit_info # send info packet to contract
    print("V: I want my input, " + str(player_v.circuit_info.data) + ", squared.")

    # prover stakes funds, evaluates and 'creates proof'
    transfer(player_p, contract, stake_p) # stake funds

    contract.exicute_check_stake() # check correct staking

    player_v.player_commit_hash(contract)
    player_p.player_commit_hash(contract)

    player_p.proof_info.data = player_p.circuit_info.evaluate() # do computation
    print("P: Result of computation: "+ str(player_p.proof_info.data))

    player_v.proof_info = player_p.proof_info.data # result to verifier

    contract.exicute_randomness(p, r_v = player_v.r, r_p = player_p.r)

    if contract.state == 3: # 3 means verify
        contract.proof_info = player_p.proof_info # prover sends proof to contract
        contract.exicute_verify()

    contract.exicute_assess_state()

    print(player_v)
    print(player_p)
    print(contract)

if __name__ == "__main__":
    main()
