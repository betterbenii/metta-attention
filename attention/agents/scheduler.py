import concurrent.futures
import time
import sys
import os
import threading
from queue import Queue
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.agent_base import AgentObject

class ParallelScheduler:
    def __init__(self, metta):
        self.metta = metta
        self.agent_creators = {}
        self.agent_instances = {}
        self.lock = threading.Lock()  # Add a lock for synchronization
        
    def register_agent(self, agent_id, agent_creator):
        """ Register an agent factory function (not instance) """
        self.agent_creators[agent_id] = agent_creator
        print(f"Registered agent: {agent_id}")

    def get_or_create_agent(self, agent_id: str) -> AgentObject:
        """ Get existing agent or create a new one if not exists """
        if agent_id not in self.agent_instances:
            if agent_id in self.agent_creators:
                self.agent_instances[agent_id] = self.agent_creators[agent_id]()
                print(f"Created new agent: {agent_id}")
            else:
                print(f"Agent {agent_id} not found.")
                return None
        
        return self.agent_instances[agent_id]

    def run_continuously(self):
        """ Run all agents continuously in parallel without stopping """
        if not self.agent_creators:
            print("No agents registered!")
            return

        print("\nStarting continuous agent execution... (Press Ctrl+C to stop)")

        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:  # Limit to 1 worker
                while True:
                    futures = []
                    for agent_id in self.agent_creators:
                        with self.lock:  # Acquire lock before agent execution
                            agent = self.get_or_create_agent(agent_id)
                            if agent:
                                futures.append(executor.submit(agent.run))

                        # Small delay between agent executions
                        time.sleep(0.1)

                    # Wait for all agents to complete before starting next iteration
                    concurrent.futures.wait(futures)
                    time.sleep(0.5)  # Add delay between iterations

        except KeyboardInterrupt:
            print("\nStopping continuous execution...")
