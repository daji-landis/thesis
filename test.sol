// SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.8;

contract test {  // enum for contract states.  I don't understand all the syntax here
    enum ContractState { Start, Committed, Verify, Good, Bad }
    ContractState state;
    ContractState constant defaultState = ContractState.Start;

    function getState() public view returns (ContractState) {
        return state; //TODO: make this return the actual name of the state
    }

    function getBalance() public view returns(uint256) {
      return address(this).balance;
    }

    // basic info for players.  This could be naked but this is fine
    struct Agreement {
        address verifierAddress;
        address proverAddress;
        uint verifierStake;
        uint proverStake;
        uint verifierInput;
        uint verifierCircuit;
    }

    // randomness structure that is also unnecessary
    struct Randomness{
        bool proverBit;
        bool verifierBit;
    }

    Agreement public agreement;  // initialize agreement structure
    Randomness public randomness; // initialize randomness

    function verifierCommit(uint _verifierStake, uint _proverStake, uint _verifierInput, uint _verifierCircuit) public payable {
        // verifier sets stakes and sumbits its address and input info
        require(_verifierStake > 0); // require non-zero stakes
        require(_proverStake > 0);
        require(msg.value == _verifierStake); // require that the verifier deposits the amount they say the do
        agreement = Agreement(msg.sender,address(0),_verifierStake, _proverStake, _verifierInput, _verifierCircuit);
        // above puts all the values into the agreement structure
    }


    function proverCommit() public payable {
        // prover commits to the agreement as stipulated by verifier
        require(msg.value == agreement.proverStake); // deposited funds much match
        agreement.proverAddress = msg.sender; // record prover address
    }

    function checkCommit() public { // checks proper committment.  Must be called to advance
        require(msg.sender == agreement.verifierAddress); // can only be called by verifier (maybe not necessary)
        require(agreement.proverAddress != agreement.verifierAddress); // check that the addresses are not the same
        require(agreement.proverStake > 0);  // check that nonzero commitment means there must be proper commitment
        require(agreement.verifierStake > 0);
        state = ContractState.Committed; // update state to Committed
    }

    function verifierRandomness(bool _verifierBit) public {
        // verifer commits randomness
        require(msg.sender == agreement.verifierAddress);
        randomness.verifierBit = _verifierBit;
    }

    function proverRandomness(bool _proverBit) public {
        // prover commits to randomness
        require(msg.sender == agreement.proverAddress);
        randomness.verifierBit = _proverBit;
    }

    uint result; // result of computation
    function submitResult(uint _result) public{
        require(msg.sender == agreement.proverAddress);  // must be
        result = _result;
    }

    function resolveState() public {
        require(msg.sender == agreement.proverAddress); // maybe both
        bool coinflip = randomness.proverBit != randomness.verifierBit;
        if (coinflip == true){
            state = ContractState.Good;
        }
        else{
            state = ContractState.Verify;
        }
    }

    uint proof;
    function resolveVerify(uint _proof) public {
        require(msg.sender == agreement.proverAddress);
        proof = _proof;
        // check validity of proof somehow
        bool correctProof = true;

        if (correctProof == true){
            state = ContractState.Good;
        }
        else{
            state = ContractState.Bad;
        }
    }

    function proverWithdraw() public payable {
        require(msg.sender == agreement.proverAddress);
        require(state == ContractState.Good);
        payable(msg.sender).transfer(address(this).balance); // empty into prover wallet
    }

    function verifierWithdraw() public payable {
        require(msg.sender == agreement.verifierAddress);
        require(state == ContractState.Bad);
        payable(msg.sender).transfer(agreement.verifierStake); // withdraw stake
    }

}
