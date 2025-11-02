class ContractNetInitiator:
    def __init__(self, task, timeout=5):
        self.task = task
        self.timeout = timeout
        self.proposals = []

    def call_for_proposals(self):
        print(f"Initiator: Calling for proposals for task: {self.task}")
        # In a real system, this would broadcast a message to the network

    def receive_proposal(self, proposal):
        print(f"Initiator: Received proposal: {proposal}")
        self.proposals.append(proposal)

    def award_contract(self):
        if not self.proposals:
            print("Initiator: No proposals received.")
            return None

        # Simple selection criteria: choose the best proposal (e.g., lowest bid)
        best_proposal = min(self.proposals, key=lambda p: p.get("bid", float("inf")))
        print(f"Initiator: Awarding contract to: {best_proposal['participant_id']}")
        # In a real system, this would send a message to the winning participant
        return best_proposal


class ContractNetParticipant:
    def __init__(self, participant_id, capabilities):
        self.participant_id = participant_id
        self.capabilities = capabilities

    def handle_call_for_proposals(self, task):
        print(f"Participant {self.participant_id}: Received call for proposals for task: {task}")
        if self.can_perform_task(task):
            bid = self.calculate_bid(task)
            return {"participant_id": self.participant_id, "bid": bid}
        return None

    def can_perform_task(self, task):
        # Simple capability check
        return task["type"] in self.capabilities

    def calculate_bid(self, task):
        # Simple bid calculation
        return len(task.get("data", "")) * 0.1  # Example: 10 cents per character
