// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract CompliancePassport {
    struct Passport {
        string passportId;
        string msmeId;
        string dpiitNo;
        string productCode;
        uint256 lcvScore;
        string docHash;
        string ipfsHash;
        uint256 issuedAt;
        uint256 validUntil;
        string status;
    }

    mapping(string => Passport) private _passports;
    mapping(string => string[]) private _msmePassportIds;
    mapping(string => bool) private _passportExists;

    address public owner;
    uint256 public totalPassports;

    event PassportIssued(string passportId, string msmeId, uint256 lcvScore, uint256 issuedAt);
    event PassportRevoked(string passportId, string reason, uint256 revokedAt);

    constructor() {
        owner = msg.sender;
    }

    function issuePassport(string calldata _passportId, string calldata _msmeId, string calldata _dpiitNo, string calldata _productCode, uint256 _lcvScore, string calldata _docHash, string calldata _ipfsHash) external returns (bool) {
        require(!_passportExists[_passportId], "Passport already exists");
        
        uint256 issuedAt = block.timestamp;
        uint256 validUntil = issuedAt + 365 days;
        
        _passports[_passportId] = Passport({
            passportId: _passportId,
            msmeId: _msmeId,
            dpiitNo: _dpiitNo,
            productCode: _productCode,
            lcvScore: _lcvScore,
            docHash: _docHash,
            ipfsHash: _ipfsHash,
            issuedAt: issuedAt,
            validUntil: validUntil,
            status: "ACTIVE"
        });
        
        _passportExists[_passportId] = true;
        _msmePassportIds[_msmeId].push(_passportId);
        totalPassports += 1;
        
        emit PassportIssued(_passportId, _msmeId, _lcvScore, issuedAt);
        return true;
    }

    function verifyPassport(string calldata _passportId) external view returns (string memory, string memory, string memory, uint256, string memory, uint256, string memory) {
        require(_passportExists[_passportId], "Passport does not exist");
        Passport storage p = _passports[_passportId];
        return (p.msmeId, p.productCode, p.status, p.lcvScore, p.docHash, p.validUntil, p.ipfsHash);
    }

    function isPassportValid(string calldata _passportId) external view returns (bool) {
        if (!_passportExists[_passportId]) return false;
        Passport storage p = _passports[_passportId];
        bool isActive = keccak256(abi.encodePacked(p.status)) == keccak256(abi.encodePacked("ACTIVE"));
        return isActive && block.timestamp <= p.validUntil;
    }

    function getPassportsByMSME(string calldata _msmeId) external view returns (string[] memory) {
        return _msmePassportIds[_msmeId];
    }

    function revokePassport(string calldata _passportId, string calldata _reason) external returns (bool) {
        require(msg.sender == owner, "Only owner can revoke");
        require(_passportExists[_passportId], "Passport does not exist");
        _passports[_passportId].status = "REVOKED";
        emit PassportRevoked(_passportId, _reason, block.timestamp);
        return true;
    }
}
