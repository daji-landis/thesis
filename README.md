# A Trade-Off Between Prover Overhead and Stake in Interactive Proofs

This code is part of my thesis which will likely be online soon.  It is a proof of
concept for the proposed protocol in my work.  It relies heavily on ZoKrates, the
documentation for which can be found [here](https://zokrates.github.io/).

The main idea is to hold a stake in order to incentivize the prover to behave honestly.
Thus this contract holds that stake as well as the deposit of the customer.  It then
rolls some randomness, which is submitted by the users, and based on that requires
the proof of the underlying work.  Here that work is a hash function.  That proof
is checked by the verification contract and if the result is found to be correct,
the stake and the payment can be withdrawn.

## The `main_contract.sol` contract
This is the framework of the protocol.  This includes checking the status of the
contract, which is likely not granular enough for proper security. The should also
be a timeout functionality for security. The contract checks
that the correct addresses are behind the methods being called. It also interfaces
with the `verification_contract.sol` and checks the hashes of the submitted randomness.

## The `verification_contract.sol` contract
This contract checks the proof.  It is `hash.zok` script compiled into Solidity with
only minor adjustments.  it is a ZK-SNARK proof and thus requires a trusted set up.
It follows the functionality from this [article](https://medium.com/asecuritysite-when-bob-met-alice/proof-that-i-know-something-proving-i-know-x-for-hash-x-8509e21cfb54).

## Other files
There are other auxiliary and testing files in this repository.  
- I used `toy_example.py` to model the functionality I needed in Solidity
- The script `make_hash.py` makes the hashes for the random
