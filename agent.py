import os
from cradle import Cradle

class ResearcherAgent(Cradle):
    def __init__(self):
        super().__init__()
        self.role = "Researcher"

    def perform_research(self, query):
        """
        Performs research on a given query.
        """
        print(f"[{self.role}] Performing research on: {query}")
        results = self.search_web(query)
        print(f"[{self.role}] Found results: {results}")
        return results

if __name__ == "__main__":
    agent = ResearcherAgent()
    agent.perform_research("new large language models")
