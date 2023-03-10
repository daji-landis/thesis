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
def coin_flip(p = 0.5):
    random.seed(datetime.now().timestamp())
    result = random.random()
    if result <= p:
        return 1
    else:
        return 0

def hash(bit):
    if type(bit) is not bin:
        bit = bin(bit)
    m = hashlib.sha256()
    m.update(b"Nobody inspects the spammish repetition")
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
        self.bit = coin_flip(p=0.5)
        self.hash = hash(self.bit)

class Prover:
    def __init__(self, wallet, proof):
        self.wallet = wallet
        self.circuit_info = InfoPacket()
        self.proof_info = InfoPacket(0, proof)
        self.bit = coin_flip(p=0.5)
        self.hash = hash(self.bit)

    def do_computation(self):
        # do the computation and save to proof info packet
        self.proof_info.data = self.circuit_info.evaluate()

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
        self.state = 1

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

    def exicute_0(self):
        # check correct funds, return
        if self.funds != self.stake_p + self.stake_v:  # this is a tautology, should change
            transfer(self, verifier, stake_v)
            transfer(self, prover, stake_p)
            self.state = 5
        else:
            self.state = 2

    def exicute_1(self, p):
        if self.state == 2:
            z = coin_flip(p)

            if z == 0:
                self.state = 4
            else:
                print("check")
                self.state = 3

    def exicute_verify(self):
        check = self.verify() # contract verifies proof
        if check == True:
            self.state = 4
        else:
            self.state = 5

    def exicute_2(self):
        if self.state == 4:
            transfer(self, self.verifier.wallet, self.funds) # pay verifier
        elif self.state == 5:
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

    print(player_p.bit)
    print(player_p.hash)


    # contract info
    stake_v = 40 # staking value alpha from notes
    stake_p = 50 # staking value lambda from notes

    contract = SmartContract(player_p, player_v, stake_p, stake_v)

    # verifier stakes funds and sends info
    transfer(player_v.wallet, contract, contract.stake_v) # stake

    player_p.circuit_info = player_v.circuit_info # send info packet to prover
    contract.circuit_info = player_v.circuit_info # send info packet to contract
    print("P: I want my input, " + str(player_p.circuit_info.data) + ", squared.")

    # prover stakes funds, evaluates and 'creates proof'
    transfer(player_p.wallet, contract, stake_p) # stake funds

    contract.exicute_0() # check correct staking

    player_p.proof_info.data = player_p.circuit_info.evaluate() # do computation
    print("V: Result of computation: "+ str(player_p.proof_info.data))

    player_v.proof_info = player_p.proof_info.data # result to verifier

    contract.exicute_1(p)

    if contract.state == 3: # 3 means verify
        contract.proof_info = player_p.proof_info # prover sends proof to contract
        contract.exicute_verify()

    contract.exicute_2()

    print(player_v.wallet)
    print(player_p.wallet)
    print(contract)

if __name__ == "__main__":
    main()
