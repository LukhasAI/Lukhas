// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

/**
 * @title DreamContentNFT
 * @dev NFT contract for tokenizing dream experiences from LUKHAS platform
 *
 * This contract implements ERC-721 with royalty support for dream content.
 * Dream content is stored on IPFS, with metadata following OpenSea standards.
 *
 * Features:
 * - Mint dream NFTs with IPFS content hash
 * - Configurable creator royalties (0-100%)
 * - Immutable dream seed association
 * - On-chain royalty tracking for secondary sales
 * - ERC-721 compliant with URI storage
 *
 * LUKHAS: Λ Consciousness Infrastructure
 */
contract DreamContentNFT is ERC721, ERC721URIStorage, Ownable {
    using Counters for Counters.Counter;

    // Token ID counter
    Counters.Counter private _tokenIdCounter;

    /**
     * @dev Struct representing a minted dream NFT
     */
    struct DreamNFT {
        string contentHash;          // IPFS hash of dream content
        uint256 royaltyPercentage;   // Royalty % (0-100) for secondary sales
        address creator;             // Original creator address
        string dreamSeedId;          // Associated dream seed identifier
        uint256 mintedAt;            // Timestamp of minting
    }

    // Token ID => Dream NFT data
    mapping(uint256 => DreamNFT) public dreamNFTs;

    // Events
    event DreamMinted(
        uint256 indexed tokenId,
        string contentHash,
        address indexed creator,
        uint256 royaltyPercentage,
        string dreamSeedId
    );

    event RoyaltyPaid(
        uint256 indexed tokenId,
        address indexed creator,
        address indexed buyer,
        uint256 amount
    );

    /**
     * @dev Constructor initializes the NFT collection
     */
    constructor() ERC721("DreamContent", "DREAM") Ownable(msg.sender) {
        // Token counter starts at 0
    }

    /**
     * @dev Mint a new dream NFT with content and royalty information
     * @param contentHash IPFS hash of the dream content
     * @param royaltyPercentage Royalty percentage for creator (0-100)
     * @return tokenId The newly minted token ID
     */
    function mintDreamNFT(
        string memory contentHash,
        uint256 royaltyPercentage
    ) public returns (uint256) {
        return mintDreamNFTWithSeedId(contentHash, royaltyPercentage, "");
    }

    /**
     * @dev Mint a new dream NFT with full metadata
     * @param contentHash IPFS hash of the dream content
     * @param royaltyPercentage Royalty percentage for creator (0-100)
     * @param dreamSeedId Associated dream seed identifier
     * @return tokenId The newly minted token ID
     */
    function mintDreamNFTWithSeedId(
        string memory contentHash,
        uint256 royaltyPercentage,
        string memory dreamSeedId
    ) public returns (uint256) {
        require(royaltyPercentage <= 100, "Royalty cannot exceed 100%");
        require(bytes(contentHash).length > 0, "Content hash cannot be empty");

        uint256 tokenId = _tokenIdCounter.current();
        _tokenIdCounter.increment();

        // Mint to the caller (creator)
        _safeMint(msg.sender, tokenId);

        // Store dream NFT data
        dreamNFTs[tokenId] = DreamNFT({
            contentHash: contentHash,
            royaltyPercentage: royaltyPercentage,
            creator: msg.sender,
            dreamSeedId: dreamSeedId,
            mintedAt: block.timestamp
        });

        // Set token URI to IPFS content hash
        string memory uri = string(abi.encodePacked("ipfs://", contentHash));
        _setTokenURI(tokenId, uri);

        emit DreamMinted(
            tokenId,
            contentHash,
            msg.sender,
            royaltyPercentage,
            dreamSeedId
        );

        return tokenId;
    }

    /**
     * @dev Get dream NFT data for a token
     * @param tokenId The token ID to query
     * @return DreamNFT struct with full metadata
     */
    function getDreamNFT(uint256 tokenId) public view returns (DreamNFT memory) {
        require(_ownerOf(tokenId) != address(0), "Token does not exist");
        return dreamNFTs[tokenId];
    }

    /**
     * @dev Calculate royalty amount for a sale
     * @param tokenId The token ID
     * @param salePrice The sale price in wei
     * @return creator The creator address
     * @return royaltyAmount The royalty amount in wei
     */
    function calculateRoyalty(uint256 tokenId, uint256 salePrice)
        public
        view
        returns (address creator, uint256 royaltyAmount)
    {
        require(_ownerOf(tokenId) != address(0), "Token does not exist");

        DreamNFT memory nft = dreamNFTs[tokenId];
        creator = nft.creator;
        royaltyAmount = (salePrice * nft.royaltyPercentage) / 100;
    }

    /**
     * @dev Get total number of minted tokens
     * @return count Total token count
     */
    function totalSupply() public view returns (uint256) {
        return _tokenIdCounter.current();
    }

    /**
     * @dev Get all token IDs owned by an address
     * @param owner The address to query
     * @return tokenIds Array of token IDs
     */
    function tokensOfOwner(address owner) public view returns (uint256[] memory) {
        uint256 tokenCount = balanceOf(owner);
        uint256[] memory tokenIds = new uint256[](tokenCount);
        uint256 index = 0;

        // Iterate through all tokens to find owned ones
        for (uint256 tokenId = 0; tokenId < _tokenIdCounter.current(); tokenId++) {
            if (_ownerOf(tokenId) == owner) {
                tokenIds[index] = tokenId;
                index++;
                if (index >= tokenCount) break;
            }
        }

        return tokenIds;
    }

    /**
     * @dev Override to resolve conflicting inheritance
     */
    function tokenURI(uint256 tokenId)
        public
        view
        override(ERC721, ERC721URIStorage)
        returns (string memory)
    {
        return super.tokenURI(tokenId);
    }

    /**
     * @dev Override to resolve conflicting inheritance
     */
    function supportsInterface(bytes4 interfaceId)
        public
        view
        override(ERC721, ERC721URIStorage)
        returns (bool)
    {
        return super.supportsInterface(interfaceId);
    }
}
