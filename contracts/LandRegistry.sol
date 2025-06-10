// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract PDFStorage {
    struct Document {
        string name;
        string fileHash; // e.g., SHA256 or IPFS hash
    }

    mapping(uint => Document) public documents;
    uint public docCount;

    function addDocument(string memory name, string memory fileHash) public {
        documents[docCount] = Document(name, fileHash);
        docCount++;
    }

    function getDocument(uint index) public view returns (string memory, string memory) {
        Document memory doc = documents[index];
        return (doc.name, doc.fileHash);
    }
}
