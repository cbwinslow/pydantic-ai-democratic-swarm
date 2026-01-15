# Governance System Documentation

## Overview

The Pydantic AI Democratic Swarm implements a comprehensive democratic governance system that enables agents to make collective decisions through various voting mechanisms and consensus-building algorithms.

## Core Components

### 1. Voting System (`voting.py`)

The voting system supports multiple voting methods to accommodate different decision-making scenarios.

#### Voting Methods

##### Plurality Voting
Simple majority voting where each agent gets one vote, and the option with the most votes wins.

```python
from pydantic_ai_swarm.governance.voting import VotingSystem, VotingMethod, Vote

system = VotingSystem(voting_method=VotingMethod.PLURALITY)

votes = [
    Vote(agent_name="agent1", option="option_a", confidence=0.8),
    Vote(agent_name="agent2", option="option_a", confidence=0.7),
    Vote(agent_name="agent3", option="option_b", confidence=0.6),
]

result = system.conduct_vote(votes, eligible_voters=3)
print(f"Winner: {result.winner}")  # option_a
print(f"Consensus: {result.consensus_level:.2%}")
```

##### Weighted Voting
Votes are weighted by agent confidence, giving more influence to agents with higher confidence in their decision.

```python
system = VotingSystem(voting_method=VotingMethod.WEIGHTED)

votes = [
    Vote(agent_name="expert", option="option_a", weight=2.0, confidence=0.9),
    Vote(agent_name="novice", option="option_b", weight=0.5, confidence=0.4),
]

result = system.conduct_vote(votes, eligible_voters=2)
# Expert's vote carries more weight
```

##### Ranked-Choice Voting
Agents rank their preferences, and instant runoff voting is used to determine the winner.

```python
from pydantic_ai_swarm.governance.voting import RankedVote

votes = [
    RankedVote(
        agent_name="agent1",
        option="option_a",
        rankings=["option_a", "option_b", "option_c"]
    ),
    RankedVote(
        agent_name="agent2",
        option="option_b",
        rankings=["option_b", "option_c", "option_a"]
    ),
]

system = VotingSystem(voting_method=VotingMethod.RANKED_CHOICE)
result = system.conduct_vote(votes, eligible_voters=2)
```

##### Approval Voting
Agents can approve multiple options, and the option with the most approvals wins.

```python
from pydantic_ai_swarm.governance.voting import ApprovalVote

votes = [
    ApprovalVote(
        agent_name="agent1",
        option="option_a",
        approved_options={"option_a", "option_b"}
    ),
    ApprovalVote(
        agent_name="agent2",
        option="option_b",
        approved_options={"option_b", "option_c"}
    ),
]

system = VotingSystem(voting_method=VotingMethod.APPROVAL)
result = system.conduct_vote(votes, eligible_voters=2)
```

##### Consensus Voting
Requires a high agreement threshold (e.g., 66%) for a decision to pass.

```python
system = VotingSystem(
    voting_method=VotingMethod.CONSENSUS,
    consensus_threshold=0.66
)

votes = [
    Vote(agent_name="agent1", option="option_a", weight=1.0, confidence=0.9),
    Vote(agent_name="agent2", option="option_a", weight=1.0, confidence=0.8),
    Vote(agent_name="agent3", option="option_b", weight=1.0, confidence=0.7),
]

result = system.conduct_vote(votes, eligible_voters=3)
# Returns winner only if consensus threshold is met
```

#### Vote Abstention

Agents can abstain from voting when they lack confidence or expertise:

```python
vote = Vote(
    agent_name="uncertain_agent",
    option="",
    abstain=True,
    reasoning="Insufficient expertise in this domain"
)
```

### 2. Consensus Building (`consensus.py`)

The consensus system helps agents reach agreement through deliberative processes.

#### Consensus Algorithms

##### Simple Majority
Requires more than 50% agreement.

```python
from pydantic_ai_swarm.governance.consensus import (
    ConsensusBuilder,
    ConsensusAlgorithm,
    ConsensusProposal
)

builder = ConsensusBuilder(algorithm=ConsensusAlgorithm.SIMPLE_MAJORITY)

proposal = ConsensusProposal(
    proposal_id="decision_001",
    title="Choose deployment strategy",
    description="Select the best deployment approach",
    options=["blue_green", "canary", "rolling"],
    proposer="orchestrator"
)

result = await builder.build_consensus(proposal, agents)
```

##### Supermajority
Requires a higher threshold (default 66%) for important decisions.

```python
builder = ConsensusBuilder(
    algorithm=ConsensusAlgorithm.SUPERMAJORITY,
    agreement_threshold=0.75  # 75% agreement required
)

result = await builder.build_consensus(proposal, agents)
```

##### Unanimous
Requires 100% agreement from all participating agents.

```python
builder = ConsensusBuilder(algorithm=ConsensusAlgorithm.UNANIMOUS)

result = await builder.build_consensus(proposal, agents)
if result.consensus_reached:
    print("All agents agree!")
```

##### Quorum-Based
Requires minimum participation plus majority agreement.

```python
builder = ConsensusBuilder(
    algorithm=ConsensusAlgorithm.QUORUM_BASED,
    quorum=0.7  # 70% must participate
)

result = await builder.build_consensus(proposal, agents)
```

##### Iterative Refinement
Multiple rounds of voting to build consensus over time.

```python
builder = ConsensusBuilder(
    algorithm=ConsensusAlgorithm.ITERATIVE_REFINEMENT,
    max_rounds=3,
    round_timeout_seconds=60.0
)

result = await builder.build_consensus(proposal, agents)
print(f"Consensus reached after {len(result.rounds)} rounds")
```

##### Delegated Consensus
High-confidence agents make the decision.

```python
builder = ConsensusBuilder(algorithm=ConsensusAlgorithm.DELEGATED)

result = await builder.build_consensus(proposal, agents)
# Only agents with confidence >= 0.7 influence the decision
```

### 3. Confidence Metrics (`confidence.py`)

The confidence system tracks and calculates agent confidence for informed decision-making.

#### Confidence Calculation

```python
from pydantic_ai_swarm.governance.confidence import (
    calculate_task_confidence,
    calculate_voting_weight,
    create_confidence_report
)

# Calculate confidence for a specific task
confidence = calculate_task_confidence(
    agent_domains={"coding": 0.9, "testing": 0.7},
    agent_tools={"python": 0.8, "pytest": 0.7},
    task_domain="coding",
    required_tools=["python"],
    recent_performance=[True, True, False, True],  # Recent success history
    base_confidence=0.5
)

# Calculate voting weight based on expertise
weight = calculate_voting_weight(
    confidence=0.8,
    domain_expertise=0.9,
    participation_history=50,
    voting_accuracy=0.85
)
```

#### Confidence Reports

```python
# Generate comprehensive confidence report
report = create_confidence_report(
    agent_name="expert_agent",
    confidence_metrics=agent.confidence,
    window_days=30
)

print(f"Overall confidence: {report.overall_confidence:.2%}")
print(f"Trend: {report.trend}")
print("Recommendations:")
for rec in report.recommendations:
    print(f"  - {rec}")
```

## Integration with Orchestrator

### Basic Usage

```python
from pydantic_ai_swarm import PydanticAISwarmOrchestrator
from pydantic_ai_swarm.governance.voting import VotingMethod
from pydantic_ai_swarm.governance.consensus import ConsensusAlgorithm

# Create orchestrator with voting configuration
orchestrator = PydanticAISwarmOrchestrator(
    swarm_name="MySwarm",
    voting_method=VotingMethod.WEIGHTED,
    consensus_algorithm=ConsensusAlgorithm.SUPERMAJORITY,
    consensus_threshold=0.66,
    voting_timeout_seconds=300
)

# Register agents
await orchestrator.register_agent(agent1)
await orchestrator.register_agent(agent2)
await orchestrator.start_swarm()

# Tasks are automatically assigned through democratic voting
result = await orchestrator.execute_task(
    "Analyze this dataset",
    context={"domain": "data_analysis"}
)

print(f"Task assigned to: {result.agent_name}")
print(f"Confidence: {result.confidence_score:.2%}")
print(f"Consensus level: {result.consensus_level:.2%}")
```

### Building Consensus

```python
# Make important decisions through consensus
result = await orchestrator.build_consensus(
    proposal_title="Select database technology",
    proposal_description="Choose the best database for our use case",
    options=["PostgreSQL", "MongoDB", "Redis"],
    context={"domain": "architecture", "priority": "high"}
)

if result.consensus_reached:
    print(f"Consensus reached: {result.chosen_option}")
    print(f"Agreement level: {result.agreement_level:.2%}")
else:
    print("No consensus reached")
    print(f"Best option so far: {result.chosen_option}")
```

### Voting Statistics

```python
# Get voting and consensus statistics
stats = orchestrator.get_voting_statistics()

print(f"Total votes: {stats['voting']['total_votes']}")
print(f"Average consensus: {stats['voting']['average_consensus']:.2%}")
print(f"Average participation: {stats['voting']['average_participation']:.2%}")
print(f"Consensus rate: {stats['consensus']['consensus_rate']:.2%}")
```

## Agent Implementation

### Confidence-Based Voting

Agents automatically calculate their confidence for tasks:

```python
class MyAgent(BaseAgent):
    async def calculate_task_confidence(
        self,
        task_description: str,
        context: Dict[str, Any]
    ) -> float:
        """Calculate confidence for this specific task."""
        # Custom confidence calculation based on:
        # - Domain expertise
        # - Required tools
        # - Recent performance
        # - Task complexity
        
        domain = context.get("domain", "")
        confidence = self.confidence.get_domain_confidence(domain)
        
        # Adjust based on task-specific factors
        if "complex" in task_description.lower():
            confidence *= 0.8
        
        return confidence
```

### Abstention Logic

```python
async def should_abstain_from_vote_async(
    self,
    task_description: str,
    context: Optional[Dict[str, Any]] = None
) -> bool:
    """Decide whether to abstain from voting."""
    confidence = await self.calculate_task_confidence(task_description, context or {})
    
    # Abstain if confidence is too low
    if confidence < 0.3:
        return True
    
    # Abstain if outside area of expertise
    domain = context.get("domain", "") if context else ""
    if domain and self.confidence.get_domain_confidence(domain) < 0.4:
        return True
    
    return False
```

## Best Practices

### 1. Choose Appropriate Voting Methods

- **Plurality**: Quick decisions, non-critical tasks
- **Weighted**: Leverage expertise, quality over quantity
- **Ranked-Choice**: Multiple good options, avoid vote splitting
- **Approval**: Broad acceptance needed
- **Consensus**: Critical decisions requiring high agreement

### 2. Set Appropriate Thresholds

```python
# For routine decisions
orchestrator = PydanticAISwarmOrchestrator(
    voting_method=VotingMethod.PLURALITY,
    consensus_threshold=0.51  # Simple majority
)

# For important decisions
orchestrator = PydanticAISwarmOrchestrator(
    voting_method=VotingMethod.CONSENSUS,
    consensus_threshold=0.75  # Strong agreement
)

# For critical decisions
orchestrator = PydanticAISwarmOrchestrator(
    consensus_algorithm=ConsensusAlgorithm.UNANIMOUS  # Everyone must agree
)
```

### 3. Monitor Voting Patterns

```python
# Regular monitoring
stats = orchestrator.get_voting_statistics()

if stats['voting']['average_participation'] < 0.6:
    print("Warning: Low agent participation in voting")

if stats['consensus']['consensus_rate'] < 0.5:
    print("Warning: Difficulty reaching consensus")
```

### 4. Handle Failed Consensus

```python
result = await orchestrator.build_consensus(proposal, agents)

if not result.consensus_reached:
    # Fallback strategies:
    # 1. Use the best option available
    best_option = result.chosen_option
    
    # 2. Request human intervention
    human_decision = await request_human_input(proposal)
    
    # 3. Try again with lower threshold
    builder.agreement_threshold = 0.5
    result = await builder.build_consensus(proposal, agents)
```

### 5. Track Confidence Over Time

```python
# Update confidence after task completion
agent.update_confidence_after_execution(tool_name, success=True)

# Generate periodic reports
report = create_confidence_report(
    agent_name=agent.agent_name,
    confidence_metrics=agent.confidence
)

# Act on recommendations
if report.trend == "declining":
    # Reduce agent workload or provide training
    agent.confidence.domains["weak_area"] = 0.6
```

## Advanced Features

### Custom Vote Weighting

```python
class CustomVotingSystem(VotingSystem):
    def _weighted_vote(self, votes):
        """Custom weighting logic."""
        vote_counts = {}
        
        for vote in votes:
            # Custom weight calculation
            experience_factor = vote.metadata.get("years_experience", 1)
            recent_accuracy = vote.metadata.get("recent_accuracy", 0.5)
            
            effective_weight = (
                vote.weight * 
                vote.confidence * 
                (1 + experience_factor * 0.1) *
                recent_accuracy
            )
            
            vote_counts[vote.option] = vote_counts.get(vote.option, 0) + effective_weight
        
        winner = max(vote_counts.items(), key=lambda x: x[1])[0]
        return vote_counts, winner
```

### Async Consensus Building

```python
# Run multiple consensus processes in parallel
proposals = [proposal1, proposal2, proposal3]

results = await asyncio.gather(*[
    orchestrator.build_consensus(
        proposal_title=p.title,
        proposal_description=p.description,
        options=p.options
    )
    for p in proposals
])

for result in results:
    print(f"Proposal: {result.proposal_id}")
    print(f"Reached: {result.consensus_reached}")
    print(f"Choice: {result.chosen_option}")
```

## Troubleshooting

### Low Participation Rates

```python
# Check agent confidence levels
for agent in orchestrator.agents.values():
    report = agent.get_confidence_report()
    if report['overall_confidence'] < 0.4:
        print(f"{agent.agent_name} has low confidence")
        # Provide training or adjust domain expertise
```

### Voting Deadlocks

```python
# Use iterative refinement to resolve
builder = ConsensusBuilder(
    algorithm=ConsensusAlgorithm.ITERATIVE_REFINEMENT,
    max_rounds=5
)

result = await builder.build_consensus(proposal, agents)

if not result.consensus_reached:
    # Escalate or use delegated consensus
    builder.algorithm = ConsensusAlgorithm.DELEGATED
    result = await builder.build_consensus(proposal, agents)
```

### Confidence Calibration

```python
from pydantic_ai_swarm.governance.confidence import assess_confidence_calibration

# Check if confidence predictions match outcomes
calibration = assess_confidence_calibration(
    predicted_confidences=[0.8, 0.6, 0.9, 0.5],
    actual_outcomes=[True, False, True, False]
)

print(f"Calibration error: {calibration['calibration_error']:.3f}")
print(f"Brier score: {calibration['brier_score']:.3f}")
print(f"Accuracy: {calibration['accuracy']:.2%}")
```

## Summary

The governance system provides:

1. **Multiple voting methods** for different scenarios
2. **Consensus algorithms** for collective decision-making
3. **Confidence tracking** for informed voting
4. **Abstention handling** for uncertain agents
5. **Statistics and monitoring** for system health
6. **Integration with orchestrator** for seamless operation

This democratic approach ensures that decisions are made collectively, with appropriate weight given to expertise and confidence, while maintaining transparency and accountability.
