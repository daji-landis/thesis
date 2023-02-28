import random
from datetime import datetime

def coin_flip(p = 0.5):
    random.seed(datetime.now().timestamp())
    result = random.random()
    print(str(result))
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
    def __init__(self, prover, verifier, stake = 0, circut = "none"):
        self.prover = prover
        self.verifier = verifier
        self.stake = stake
        self.circut = circut

    def __str__(self):
        return f"P: {self.prover} V: {self.verifier} staked funds: {self.stake}"

    def burn(self, delta = 0):
        if delta == 0:
            self.stake = 0
        else:
            self.stake = self.stake - delta

    def deposit(self, delta):
        self.stake += delta

def main():
    p=0.1
    # initialize everyone with funds
    player_v = Wallet("Vivian", 100)
    player_p = Wallet("Petra", 100)
    contract = SmartContract(player_p, player_v)

    # verifier stakes funds and sends info
    stake_amount_v = 40
    transfer(player_v, contract, stake_amount_v)

    x = 5
    print("I want my input, " + str(x) + ",squared.")

    # prover stakes funds
    stake_amount_p = 50
    transfer(player_p, contract, stake_amount_p)
    y = x^2

    coin_flip(p)

    print(contract)

if __name__ == "__main__":
    main()
