from .schema import DreamTrace

class DreamsEngine:
    def __init__(self, flow_client): self.flow = flow_client
    async def run(self, seed, constraints) -> DreamTrace:
        # 1) bootstrap state  2) call flow.plan() 3) iterate actions 4) collect frames
        # 5) enforce guardian checks on each external action
        ...
