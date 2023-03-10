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
        return self.circuit(self.data)

# defining player wallet
class Wallet:
    def __init__(self, name, init_funds = 0):
        self.name =  name
        self.funds = init_funds

    def __str__(self):
        return f"{self.name}({self.funds})"

    def deposit(self, delta):
        self.funds += delta

    def burn(self, delta):
        if delta > self.funds:
            print("Insufficient funds")
        else:
            self.funds = self.funds - delta

class Verifier:
    def __init__(self, wallet, circuit_info):
        self.wallet = wallet
        self.circuit_info = circuit_info
        self.proof_info = 0
        self.r = random.randint(10000, 100000)
        # self.hash = hash(self.r)

    def player_commit_hash(self, contract):
        my_hash = hash(self.r)
        contract.commit_hash(id = "Vivian", hash = my_hash)

class Prover:
    def __init__(self, wallet, proof):
        self.wallet = wallet
        self.circuit_info = InfoPacket()
        self.proof_info = InfoPacket(0, proof)
        self.r = random.randint(10000, 100000)
        # self.hash = hash(self.r)

    def do_computation(self):
        # do the computation and save to proof info packet
        self.proof_info.data = self.circuit_info.evaluate()

    def player_commit_hash(self, contract):
        my_hash = hash(self.r)
        contract.commit_hash(id = "Petra", hash = my_hash)

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
        self.circuit_info = circuit_info
        self.proof_info = proof_info  # circuit verifier wants solved
        self.state = 1 # start
        self.v_hash = 0
        self.p_hash = 0

    def __str__(self):
        return( f"Staked funds: {self.funds}" + " Contract State: "+ str(contract_states(self.state).name))

    # burns funds in contract. burns all funds by default
    def burn(self, delta = 0):
        if delta == 0:
            self.funds = 0
        else:
            self.funds = self.funds - delta

    def deposit(self, delta):
        self.funds += delta

    def z(self,p):
        return coin_flip(p)

    def verify(self):
        my_input = self.circuit_info.data
        proof_output = self.proof_info.evaluate()
        # print("my input " + str(my_input)+"\nproof output " + str(proof_output))
        if my_input == proof_output:
            return True
        else:
            return False

    def commit_hash(self, id, hash):
        if id == "Vivian" and self.v_hash == 0:
            self.v_hash = hash
        elif id == "Petra" and self.p_hash == 0:
            self.p_hash = hash
        else:
            print("commit failed")

    def check_hash(self, r, old_hash):
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

    def exicute_0(self):
        # check correct funds, return
        if self.funds != self.stake_p + self.stake_v:  # this is a tautology, should change
            transfer(self, verifier, stake_v)
            transfer(self, prover, stake_p)
            self.state = 5 # badness
        else:
            self.state = 2 # committed

    def exicute_1(self, p, r_v, r_p):
        check_1 = self.check_hash(r_v, self.v_hash)
        check_2 = self.check_hash(r_p, self.p_hash)

        if check_1 and check_2 == True:
            self.state = 2
        else:
            self.state = 5

        seed = r_v ^ r_p

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

    def exicute_2(self):
        if self.state == 4: # good
            transfer(self, self.verifier.wallet, self.funds) # pay verifier
        elif self.state == 5: # badness
            transfer(self, self.prover.wallet, self.funds)
            self.burn()
            print("burnt")
        else:
            print("panic")


def main():
    p = 0.9
    # initialize everyone with funds
    wallet_v = Wallet("Vivian", 100)
    wallet_p = Wallet("Petra", 100)

    # verifier's info
    circuit = lambda x:x*x
    x = 5
    info_v = InfoPacket(x, circuit)
    player_v = Verifier(wallet_v, info_v)

    # prover's info
    proof = lambda y:int(math.sqrt(y))
    player_p = Prover(wallet_p, proof)

    # print(player_p.r)
    # print(player_p.hash)


    # contract info
    stake_v = 40 # staking value alpha from notes
    stake_p = 50 # staking value lambda from notes

    contract = SmartContract(player_p, player_v, stake_p, stake_v)

    # verifier stakes funds and sends info
    transfer(player_v.wallet, contract, contract.stake_v) # stake

    player_p.circuit_info = player_v.circuit_info # send info packet to prover
    contract.circuit_info = player_v.circuit_info # send info packet to contract
    print("V: I want my input, " + str(player_v.circuit_info.data) + ", squared.")

    # prover stakes funds, evaluates and 'creates proof'
    transfer(player_p.wallet, contract, stake_p) # stake funds

    contract.exicute_0() # check correct staking

    # contract.v_hash = player_v.hash
    # contract.p_hash = player_p.hash
    player_v.player_commit_hash(contract)
    player_p.player_commit_hash(contract)

    player_p.proof_info.data = player_p.circuit_info.evaluate() # do computation
    print("P: Result of computation: "+ str(player_p.proof_info.data))

    player_v.proof_info = player_p.proof_info.data # result to verifier

    contract.exicute_1(p, r_v = player_v.r, r_p = player_p.r)

    if contract.state == 3: # 3 means verify
        contract.proof_info = player_p.proof_info # prover sends proof to contract
        contract.exicute_verify()

    contract.exicute_2()

    print(player_v.wallet)
    print(player_p.wallet)
    print(contract)

if __name__ == "__main__":
    main()
