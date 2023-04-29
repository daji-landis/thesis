// SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.8;


struct Proof {
    Pairing.G1Point a;
    Pairing.G2Point b;
    Pairing.G1Point c;
}


library Pairing {
    struct G1Point {
        uint X;
        uint Y;
    }
    // Encoding of field elements is: X[0] * z + X[1]
    struct G2Point {
        uint[2] X;
        uint[2] Y;
    }
    /// @return the generator of G1
    function P1() pure internal returns (G1Point memory) {
        return G1Point(1, 2);
    }
    /// @return the generator of G2
    function P2() pure internal returns (G2Point memory) {
        return G2Point(
            [10857046999023057135944570762232829481370756359578518086990519993285655852781,
             11559732032986387107991004021392285783925812861821192530917403151452391805634],
            [8495653923123431417604973247489272438418190587263600148770280649306958101930,
             4082367875863433681332203403145435568316851327593401208105741076214120093531]
        );
    }
    /// @return the negation of p, i.e. p.addition(p.negate()) should be zero.
    function negate(G1Point memory p) pure internal returns (G1Point memory) {
        // The prime q in the base field F_q for G1
        uint q = 21888242871839275222246405745257275088696311157297823662689037894645226208583;
        if (p.X == 0 && p.Y == 0)
            return G1Point(0, 0);
        return G1Point(p.X, q - (p.Y % q));
    }
    /// @return r the sum of two points of G1
    function addition(G1Point memory p1, G1Point memory p2) internal view returns (G1Point memory r) {
        uint[4] memory input;
        input[0] = p1.X;
        input[1] = p1.Y;
        input[2] = p2.X;
        input[3] = p2.Y;
        bool success;
        assembly {
            success := staticcall(sub(gas(), 2000), 6, input, 0xc0, r, 0x60)
            // Use "invalid" to make gas estimation work
            switch success case 0 { invalid() }
        }
        require(success);
    }


    /// @return r the product of a point on G1 and a scalar, i.e.
    /// p == p.scalar_mul(1) and p.addition(p) == p.scalar_mul(2) for all points p.
    function scalar_mul(G1Point memory p, uint s) internal view returns (G1Point memory r) {
        uint[3] memory input;
        input[0] = p.X;
        input[1] = p.Y;
        input[2] = s;
        bool success;
        assembly {
            success := staticcall(sub(gas(), 2000), 7, input, 0x80, r, 0x60)
            // Use "invalid" to make gas estimation work
            switch success case 0 { invalid() }
        }
        require (success);
    }
    /// @return the result of computing the pairing check
    /// e(p1[0], p2[0]) *  .... * e(p1[n], p2[n]) == 1
    /// For example pairing([P1(), P1().negate()], [P2(), P2()]) should
    /// return true.
    function pairing(G1Point[] memory p1, G2Point[] memory p2) internal view returns (bool) {
        require(p1.length == p2.length);
        uint elements = p1.length;
        uint inputSize = elements * 6;
        uint[] memory input = new uint[](inputSize);
        for (uint i = 0; i < elements; i++)
        {
            input[i * 6 + 0] = p1[i].X;
            input[i * 6 + 1] = p1[i].Y;
            input[i * 6 + 2] = p2[i].X[1];
            input[i * 6 + 3] = p2[i].X[0];
            input[i * 6 + 4] = p2[i].Y[1];
            input[i * 6 + 5] = p2[i].Y[0];
        }
        uint[1] memory out;
        bool success;
        assembly {
            success := staticcall(sub(gas(), 2000), 8, add(input, 0x20), mul(inputSize, 0x20), out, 0x20)
            // Use "invalid" to make gas estimation work
            switch success case 0 { invalid() }
        }
        require(success);
        return out[0] != 0;
    }
    /// Convenience method for a pairing check for two pairs.
    function pairingProd2(G1Point memory a1, G2Point memory a2, G1Point memory b1, G2Point memory b2) internal view returns (bool) {
        G1Point[] memory p1 = new G1Point[](2);
        G2Point[] memory p2 = new G2Point[](2);
        p1[0] = a1;
        p1[1] = b1;
        p2[0] = a2;
        p2[1] = b2;
        return pairing(p1, p2);
    }
    /// Convenience method for a pairing check for three pairs.
    function pairingProd3(
            G1Point memory a1, G2Point memory a2,
            G1Point memory b1, G2Point memory b2,
            G1Point memory c1, G2Point memory c2
    ) internal view returns (bool) {
        G1Point[] memory p1 = new G1Point[](3);
        G2Point[] memory p2 = new G2Point[](3);
        p1[0] = a1;
        p1[1] = b1;
        p1[2] = c1;
        p2[0] = a2;
        p2[1] = b2;
        p2[2] = c2;
        return pairing(p1, p2);
    }
    /// Convenience method for a pairing check for four pairs.
    function pairingProd4(
            G1Point memory a1, G2Point memory a2,
            G1Point memory b1, G2Point memory b2,
            G1Point memory c1, G2Point memory c2,
            G1Point memory d1, G2Point memory d2
    ) internal view returns (bool) {
        G1Point[] memory p1 = new G1Point[](4);
        G2Point[] memory p2 = new G2Point[](4);
        p1[0] = a1;
        p1[1] = b1;
        p1[2] = c1;
        p1[3] = d1;
        p2[0] = a2;
        p2[1] = b2;
        p2[2] = c2;
        p2[3] = d2;
        return pairing(p1, p2);
    }
}


interface VerifyInterface {
    // this is the weird set up that then checks the proof
    function verifyTx(Proof memory _proof, uint[2] memory input) external returns (bool);
}

contract test {  // enum for contract states.  I don't understand all the syntax here
    enum ContractState { Start, Committed, Verify, Good, Bad }
    ContractState state;
    ContractState constant defaultState = ContractState.Start;

    function getState() public view returns (string memory output) {
        if (state == ContractState.Start){
            output = "start";
        }
        else if (state == ContractState.Committed){
            output = "committed";
        }
        else if (state == ContractState.Verify){
            output = "verify";
        }
        else if (state == ContractState.Good){
            output = "good";
        }
        else if (state == ContractState.Bad){
            output = "bad";
        }
        return output;
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
        // verifier sets stakes and sumbits its address and input info //add check for empty
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

    //uint proof;
    address verifyAddr;

    function setVerifyAddr(address _verifyAddr) public payable {
        // set the address of the verify contract
       verifyAddr = _verifyAddr;
    }

    function resolveVerify(Proof memory _proof, uint[2] memory input) public payable{
        // require(msg.sender == agreement.proverAddress);
        // proof = _proof;
        bool correctProof;
        correctProof = VerifyInterface(verifyAddr).verifyTx(_proof, input);
        // // check validity of proof somehow

        // if (correctProof == true){
        //     state = ContractState.Good;
        // }
        // else{
        //     state = ContractState.Bad;
        // }
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
