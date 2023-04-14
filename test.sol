// SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.8;

contract test {
    enum ContractState { Start, Committed, Verify, Good, Bad }
    ContractState state;
    ContractState constant defaultState = ContractState.Start;

    function getState() public view returns (ContractState) {
        return state;
    }

    function getBalance() public view returns(uint256) {
      return address(this).balance;
    }
    struct Agreement {
        address verifierAddress;
        address proverAddress;
        uint verifierStake;
        uint proverStake;
        uint verifierInput;
        uint verifierCircuit;
    }

    struct Randomness{
        bool proverBit;
        bool verifierBit;
    }

    Agreement public agreement;
    Randomness public randomness;

    function verifierCommit(uint _verifierStake, uint _proverStake, uint _verifierInput, uint _verifierCircuit) public payable {
        require(_verifierStake > 0);
        require(_proverStake > 0);
        require(msg.value == _verifierStake);
        agreement = Agreement(msg.sender,address(0),_verifierStake, _proverStake, _verifierInput, _verifierCircuit);
    }


    function proverCommit() public payable {
        require(msg.value == agreement.proverStake);
        agreement.proverAddress = msg.sender;
    }

    function checkCommit() public {
        require(msg.sender == agreement.verifierAddress);
        require(agreement.proverAddress != agreement.verifierAddress);
        require(agreement.proverStake > 0);
        require(agreement.verifierStake > 0);
        state = ContractState.Committed;
    }

    function verifierRandomness(bool _verifierBit) public {
        require(msg.sender == agreement.verifierAddress);
        randomness.verifierBit = _verifierBit;
    }

    function proverRandomness(bool _proverBit) public {
        require(msg.sender == agreement.proverAddress);
        randomness.verifierBit = _proverBit;
    }

    uint result;
    function submitResult(uint _result) public{
        require(msg.sender == agreement.proverAddress);
        result = _result;
    }

    function resolveState() public {
        require(msg.sender == agreement.verifierAddress);
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
        // withdraw
    }

    function verifierWithdraw() public payable {
        require(msg.sender == agreement.verifierAddress);
        require(state == ContractState.Bad);
        // withdraw
    }

}
