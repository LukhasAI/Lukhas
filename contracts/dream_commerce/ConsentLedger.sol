// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title ConsentLedger
 * @dev Immutable consent tracking for LUKHAS dream commerce
 *
 * This contract maintains an auditable, permanent record of user consent
 * for dream content experiences and commercial activities. Consent records
 * are stored on-chain for transparency and regulatory compliance.
 *
 * Features:
 * - Record user consent for specific dream seeds
 * - Immutable audit trail of all consent decisions
 * - Query consent status by user and dream seed
 * - Support for consent revocation tracking
 * - Event emission for off-chain indexing
 *
 * Privacy Note: Only consent decisions are stored on-chain, not personal data.
 * Users are identified by blockchain addresses (pseudonymous).
 *
 * LUKHAS: Λ Consciousness Infrastructure
 */
contract ConsentLedger is Ownable {
    /**
     * @dev Struct representing a consent record
     */
    struct ConsentData {
        bool consentGiven;     // Whether consent was given
        uint256 timestamp;     // When consent was recorded
        bool revoked;          // Whether consent was later revoked
        uint256 revokedAt;     // When consent was revoked (0 if not revoked)
    }

    // User address => Dream seed ID => Consent data
    mapping(address => mapping(string => ConsentData)) private consents;

    // User address => Dream seed ID => Consent history (for audit trail)
    mapping(address => mapping(string => ConsentData[])) private consentHistory;

    // Events
    event ConsentRecorded(
        address indexed user,
        string indexed dreamSeedId,
        bool consent,
        uint256 timestamp
    );

    event ConsentRevoked(
        address indexed user,
        string indexed dreamSeedId,
        uint256 timestamp
    );

    event ConsentUpdated(
        address indexed user,
        string indexed dreamSeedId,
        bool previousConsent,
        bool newConsent,
        uint256 timestamp
    );

    /**
     * @dev Constructor initializes the consent ledger
     */
    constructor() Ownable(msg.sender) {}

    /**
     * @dev Record consent for a dream seed
     * @param dreamSeedId The dream seed identifier
     * @param consent Whether consent is given (true) or denied (false)
     */
    function recordConsent(string memory dreamSeedId, bool consent) public {
        require(bytes(dreamSeedId).length > 0, "Dream seed ID cannot be empty");

        address user = msg.sender;
        ConsentData storage existingConsent = consents[user][dreamSeedId];

        // Check if this is an update
        bool isUpdate = existingConsent.timestamp != 0;
        bool previousConsent = existingConsent.consentGiven;

        // Create new consent record
        ConsentData memory newConsent = ConsentData({
            consentGiven: consent,
            timestamp: block.timestamp,
            revoked: false,
            revokedAt: 0
        });

        // Update current consent
        consents[user][dreamSeedId] = newConsent;

        // Add to history
        consentHistory[user][dreamSeedId].push(newConsent);

        // Emit appropriate event
        if (isUpdate) {
            emit ConsentUpdated(
                user,
                dreamSeedId,
                previousConsent,
                consent,
                block.timestamp
            );
        } else {
            emit ConsentRecorded(user, dreamSeedId, consent, block.timestamp);
        }
    }

    /**
     * @dev Revoke previously given consent
     * @param dreamSeedId The dream seed identifier
     */
    function revokeConsent(string memory dreamSeedId) public {
        require(bytes(dreamSeedId).length > 0, "Dream seed ID cannot be empty");

        address user = msg.sender;
        ConsentData storage consent = consents[user][dreamSeedId];

        require(consent.timestamp != 0, "No consent record exists");
        require(consent.consentGiven, "Cannot revoke denied consent");
        require(!consent.revoked, "Consent already revoked");

        // Mark as revoked
        consent.revoked = true;
        consent.revokedAt = block.timestamp;

        emit ConsentRevoked(user, dreamSeedId, block.timestamp);
    }

    /**
     * @dev Get current consent status for a user and dream seed
     * @param user The user address
     * @param dreamSeedId The dream seed identifier
     * @return consent Whether consent is currently given
     */
    function getConsent(address user, string memory dreamSeedId)
        public
        view
        returns (bool)
    {
        ConsentData memory consentData = consents[user][dreamSeedId];

        // Return false if no consent recorded, revoked, or explicitly denied
        if (consentData.timestamp == 0 || consentData.revoked || !consentData.consentGiven) {
            return false;
        }

        return true;
    }

    /**
     * @dev Get detailed consent data
     * @param user The user address
     * @param dreamSeedId The dream seed identifier
     * @return consentData Full consent record
     */
    function getConsentData(address user, string memory dreamSeedId)
        public
        view
        returns (ConsentData memory)
    {
        return consents[user][dreamSeedId];
    }

    /**
     * @dev Get full consent history for a user and dream seed
     * @param user The user address
     * @param dreamSeedId The dream seed identifier
     * @return history Array of all consent records
     */
    function getConsentHistory(address user, string memory dreamSeedId)
        public
        view
        returns (ConsentData[] memory)
    {
        return consentHistory[user][dreamSeedId];
    }

    /**
     * @dev Check if user has ever given consent (even if later revoked)
     * @param user The user address
     * @param dreamSeedId The dream seed identifier
     * @return hasConsented Whether user has ever consented
     */
    function hasEverConsented(address user, string memory dreamSeedId)
        public
        view
        returns (bool)
    {
        ConsentData[] memory history = consentHistory[user][dreamSeedId];

        for (uint256 i = 0; i < history.length; i++) {
            if (history[i].consentGiven) {
                return true;
            }
        }

        return false;
    }

    /**
     * @dev Get consent history count for a user and dream seed
     * @param user The user address
     * @param dreamSeedId The dream seed identifier
     * @return count Number of consent records
     */
    function getConsentHistoryCount(address user, string memory dreamSeedId)
        public
        view
        returns (uint256)
    {
        return consentHistory[user][dreamSeedId].length;
    }

    /**
     * @dev Batch check consent for multiple dream seeds
     * @param user The user address
     * @param dreamSeedIds Array of dream seed identifiers
     * @return consents Array of consent statuses
     */
    function batchGetConsent(address user, string[] memory dreamSeedIds)
        public
        view
        returns (bool[] memory)
    {
        bool[] memory consentStatuses = new bool[](dreamSeedIds.length);

        for (uint256 i = 0; i < dreamSeedIds.length; i++) {
            consentStatuses[i] = getConsent(user, dreamSeedIds[i]);
        }

        return consentStatuses;
    }
}
