import random
from datetime import datetime
import math

def coin_flip(p = 0.5):
    random.seed(datetime.now().timestamp())
    result = random.random()
    # print(str(result))
    if result <= p:
        return 1
    else:
        return 0

# defining transfer function between players/player and contract
def transfer(sender, receiver, amount):
    if sender.funds < amount:
        print("Insufficient funds, transaction failed")
    else:
        sender.burn(amount)
        receiver.deposit(amount)

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


# defining contract
class SmartContract:
    def __init__(self, prover, verifier, funds = 0, circuit = "none"):
        self.prover = prover
        self.verifier = verifier
        self.funds = funds
        self.circuit = circuit

    def __str__(self):
        return f"P: {self.prover} V: {self.verifier} staked funds: {self.funds}"

    def burn(self, delta = 0):
        if delta == 0:
            self.funds = 0
        else:
            self.funds = self.funds - delta

    def deposit(self, delta):
        self.funds += delta

def main():
    p = 0.9
    # initialize everyone with funds
    player_v = Wallet("Vivian", 100)
    player_p = Wallet("Petra", 100)
    contract = SmartContract(player_p, player_v)

    # verifier fundss funds and sends info
    funds_amount_v = 40
    transfer(player_v, contract, funds_amount_v)

    x = 5
    print("I want my input, " + str(x) + ", squared.")

    circuit = lambda x:x*x

    # prover stakes funds
    funds_amount_p = 50
    transfer(player_p, contract, funds_amount_p)
    y = circuit(x) # + 100
    proof = lambda y:int(math.sqrt(y))

    # exicute contract
    z = coin_flip(p)

    if z == 0:
        transfer(contract, player_v, contract.funds)
    else:
        print("check")
        # print(str(x) + str(y) + str(proof(y)))
        if proof(y) == x:
            transfer(contract, player_v, contract.funds)
        else:
            transfer(contract, player_p, funds_amount_p)
            print("boooo you lied")
            contract.burn()

    print(contract)

if __name__ == "__main__":
    main()
