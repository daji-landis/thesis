import random
from datetime import datetime
import math

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
        self.proof_info = InfoPacket()

    # def verify(self):
    #     my_input = self.circuit_info.data
    #     proof_output = self.proof_info.evaluate()
    #     print("my input " + str(my_input)+"\nproof output " + str(proof_output))
    #     if my_input == proof_output:
    #         return True
    #     else:
    #         print("boooo you lied")
    #         return False

class Prover:
    def __init__(self, wallet, proof):
        self.wallet = wallet
        self.circuit_info = InfoPacket()
        self.proof_info = InfoPacket(0, proof)

    def do_computation(self):
        # do the computation and save to proof info packet
        self.proof_info.data = self.circuit_info.evaluate()


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

    def __str__(self):
        return f"Staked funds: {self.funds}"

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

    def exicute(self, we_good, player_v, player_p):
        if we_good == 0:
            print("we good? " + str(we_good))
            transfer(self, player_v.wallet, self.funds)
        else:
            transfer(contract, player_p.wallet, stake_p)
            contract.burn()
            print("burnt")

    def verify(self):
        my_input = self.circuit_info.data
        proof_output = self.proof_info.evaluate()
        print("my input " + str(my_input)+"\nproof output " + str(proof_output))
        if my_input == proof_output:
            return True
        else:
            print("boooo you lied")
            return False


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

    # contract info
    stake_v = 40 # staking value alpha from notes
    stake_p = 50 # staking value lambda from notes

    contract = SmartContract(player_p, player_v, stake_p, stake_v)

    # verifier stakes funds and sends info
    transfer(player_v.wallet, contract, contract.stake_v) # stake

    player_p.circuit_info = player_v.circuit_info # send info packet
    contract.circuit_info = player_v.circuit_info
    print("I want my input, " + str(player_p.circuit_info.data) + ", squared.")

    # prover stakes funds, evaluates and 'creates proof'
    transfer(player_p.wallet, contract, stake_p) # stake funds
    player_p.proof_info.data = player_p.circuit_info.evaluate() # do computation
    print("result of computation: "+ str(player_p.proof_info.data))

    player_v.proof_info = player_p.proof_info # transfer proof and result to verifier

    z = contract.z(p) # contract creates randomness

    we_good = 1 # initialize contract status

    if z == 0:
        we_good = 0
    else:
        print("check")
        contract.proof_info = player_v.proof_info # does v send this or does p?
        check = contract.verify() # contract verifies proof
        if check == True:
            we_good = 0
        else:
            we_good = 1

    contract.exicute(we_good, player_v, player_p)
    print(player_v.wallet)
    print(player_p.wallet)
    print(contract)

if __name__ == "__main__":
    main()
