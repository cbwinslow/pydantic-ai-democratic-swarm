# Pydantic AI Swarm Efficiency Rules & Guardrails

This document outlines the rules and guardrails that govern the Pydantic AI Democratic Swarm to ensure efficiency, code reusability, and quality in all operations.

## 🎯 Core Efficiency Principles

### 1. **Code Reusability First**
- **NEVER create duplicate files or functions**
- **ALWAYS search for and reuse existing code**
- **MODIFY existing files instead of creating new ones**
- **EXTEND existing agents rather than creating redundant ones**
- **Check agent capability registry before creating new agents**
- **Use existing tool integrations instead of rebuilding**

### 2. **Single Responsibility**
- **Each file/component has one clear purpose**
- **Functions do one thing well**
- **Agents specialize in specific domains**
- **Tools solve specific problems**
- **Documentation stays with its component**
- **Tests mirror the structure they validate**

### 3. **DRY (Don't Repeat Yourself)**
- **Extract common functionality into shared utilities**
- **Use inheritance and composition over duplication**
- **Create reusable base classes and mixins**
- **Implement shared configuration patterns**
- **Standardize error handling and logging patterns**
- **Use common data structures and protocols**

### 4. **Domain Separation**
- **Keep domain logic separate from infrastructure**
- **Isolate business rules from technical implementation**
- **Maintain clear boundaries between agent responsibilities**
- **Use domain-specific knowledge bases**
- **Separate configuration from code**

### 5. **Progressive Enhancement**
- **Start with minimal viable functionality**
- **Add features through extension, not replacement**
- **Maintain backward compatibility**
- **Version API changes appropriately**
- **Support feature flags for gradual rollout**

## 🚫 Prohibited Actions

### File Creation Rules
- **❌ NEVER create a new file if existing functionality exists**
- **❌ NEVER duplicate existing agent classes or tools**
- **❌ NEVER create redundant documentation files**
- **❌ NEVER create new test files for existing functionality**
- **❌ NEVER create duplicate configuration files**

### Code Modification Rules
- **❌ NEVER modify core functionality without consensus**
- **❌ NEVER break existing APIs without migration plans**
- **❌ NEVER remove functionality without replacement**
- **❌ NEVER introduce breaking changes without deprecation**

### Agent Behavior Rules
- **❌ Agents MUST NOT create new files without approval**
- **❌ Agents MUST NOT duplicate existing agent capabilities**
- **❌ Agents MUST NOT create redundant tools or utilities**
- **❌ Agents MUST NOT modify core system files**

## ✅ Required Actions

### Before Creating New Code
1. **SEARCH existing codebase thoroughly**
2. **ANALYZE existing agents, tools, and utilities**
3. **IDENTIFY opportunities for extension/modification**
4. **GET consensus from swarm before proceeding**
5. **DOCUMENT rationale for new code**

### Code Reuse Checklist
- [ ] **Searched for existing similar functionality**
- [ ] **Reviewed existing agent capabilities**
- [ ] **Checked existing tool registry**
- [ ] **Analyzed existing utility functions**
- [ ] **Confirmed no duplication exists**

### Quality Gates
- [ ] **Code passes linting and type checking**
- [ ] **Tests exist and pass**
- [ ] **Documentation is updated**
- [ ] **No breaking changes introduced**
- [ ] **Performance impact assessed**

## 🏗️ Architecture Guidelines

### Agent Design
```python
# ✅ GOOD: Extend existing agents
class VideoAnalysisAgent(PydanticVideoEditorAgent):
    """Extends existing video agent with analysis capabilities."""

# ❌ BAD: Create duplicate agent
class NewVideoAgent(PydanticAIAgent):  # Redundant
    """Duplicate video functionality."""
```

### Tool Design
```python
# ✅ GOOD: Register new tools with existing registry
await tool_factory.register_tool_with_registry(new_tool, "existing_namespace")

# ❌ BAD: Create new tool files
# new_tool_file.py  # Creates fragmentation
```

### File Organization
```
# ✅ GOOD: Logical file structure
agents/
├── base_agent.py          # Single base agent
├── video_editing_agent.py # Specialized extension
└── tools/
    └── video_tools.py     # Related tools together

# ❌ BAD: Fragmented structure
agents/
├── base_agent.py
├── video_agent.py
├── video_agent_v2.py      # Duplicate
├── video_tools.py
└── video_utilities.py     # Fragmented
```

## 🔍 Code Analysis & Prevention

### Duplicate Detection
The swarm automatically analyzes code for duplicates before allowing new file creation:

```python
async def analyze_code_duplication(self, new_code: str) -> Dict[str, Any]:
    """Analyze new code for potential duplications."""
    analysis = {
        "existing_similar_files": await self.find_similar_files(new_code),
        "duplicate_functions": await self.find_duplicate_functions(new_code),
        "redundant_capabilities": await self.find_redundant_capabilities(new_code),
        "reuse_opportunities": await self.find_reuse_opportunities(new_code)
    }

    if analysis["existing_similar_files"]:
        return {"action": "REJECT", "reason": "Use existing files", "alternatives": alternatives}

    return {"action": "APPROVE", "confidence": confidence_score}
```

### Agent Capability Mapping
```python
AGENT_CAPABILITY_MAP = {
    "video_editing": ["PydanticVideoEditorAgent"],
    "content_analysis": ["ContentAnalysisAgent"],
    "github_management": ["GitHubAgent"],
    "social_media": ["SocialMediaAgent"],
    # Prevents duplicate agent creation
}
```

## 🛡️ Guardrail Implementation

### Pre-Action Validation
```python
async def validate_swarm_action(self, action: SwarmAction) -> ValidationResult:
    """Validate any swarm action against efficiency rules."""

    if action.type == "create_file":
        # Check for duplicates
        duplicates = await self.check_file_duplicates(action.file_path, action.content)
        if duplicates:
            return ValidationResult(
                approved=False,
                reason="Duplicate file detected",
                alternatives=duplicates
            )

    elif action.type == "create_agent":
        # Check for redundant agents
        existing = await self.find_similar_agents(action.agent_config)
        if existing:
            return ValidationResult(
                approved=False,
                reason="Similar agent already exists",
                alternatives=existing
            )

    return ValidationResult(approved=True)
```

### Consensus Requirements
- **File Creation**: Requires 80%+ consensus from all agents
- **Agent Creation**: Requires 90%+ consensus (higher bar)
- **Core Modifications**: Requires 95%+ consensus (highest bar)
- **Simple Extensions**: Requires 60%+ consensus (lower bar)
- **Documentation Updates**: Requires 70%+ consensus
- **Configuration Changes**: Requires 75%+ consensus

### Documentation Requirements
- **All agents MUST have documentation in their folder**
- **README.md required for each major component**
- **API documentation for public interfaces**
- **Usage examples for tools and agents**
- **Cross-references to related components**

### Automatic Enforcement
```python
class EfficiencyEnforcer:
    """Automatically enforces efficiency rules."""

    async def enforce_rules(self, proposed_action: SwarmAction) -> EnforcementResult:
        """Enforce efficiency rules on proposed actions."""

        # Rule 1: Check for existing functionality
        existing = await self.find_existing_functionality(proposed_action)
        if existing:
            return self.reject_with_alternatives("Use existing code", existing)

        # Rule 2: Validate necessity
        necessity = await self.assess_necessity(proposed_action)
        if necessity < 0.7:
            return self.reject_with_alternatives("Not sufficiently necessary", [])

        # Rule 3: Check code quality
        quality = await self.assess_code_quality(proposed_action)
        if quality < 0.8:
            return self.reject_with_alternatives("Code quality too low", [])

        return EnforcementResult(approved=True)
```

## 📊 Efficiency Metrics

### Swarm Performance Tracking
```python
class EfficiencyMetrics:
    """Track swarm efficiency metrics."""

    def __init__(self):
        self.metrics = {
            "duplicate_prevention_rate": 0.0,  # % of duplicates prevented
            "code_reuse_rate": 0.0,            # % of code that reuses existing
            "file_creation_efficiency": 0.0,   # Files created vs modified
            "agent_specialization_index": 0.0, # How specialized agents are
        }

    async def update_metrics(self):
        """Update efficiency metrics."""
        # Calculate duplicate prevention
        prevented_duplicates = len(self.prevented_duplicate_actions)
        total_actions = len(self.all_actions)
        self.metrics["duplicate_prevention_rate"] = prevented_duplicates / total_actions

        # Calculate reuse rate
        reuse_actions = len([a for a in self.all_actions if a.reused_existing])
        self.metrics["code_reuse_rate"] = reuse_actions / total_actions
```

### Quality Assurance
- **Duplicate Detection**: Automatic scanning for code duplication
- **Dependency Analysis**: Track and prevent circular dependencies
- **Test Coverage**: Ensure all new code has adequate tests
- **Documentation**: Require docs for all new functionality

## 🎯 Agent Guidelines

### When to Create New Files
- **Only when NO existing functionality exists**
- **Only when extending core capabilities**
- **Only with swarm consensus**
- **Only when benefits outweigh maintenance costs**

### When to Modify Existing Files
- **When adding features to existing agents**
- **When fixing bugs in existing code**
- **When optimizing existing functionality**
- **When refactoring for better structure**

### Agent Communication Rules
- **Share findings before creating new solutions**
- **Ask swarm for existing solutions first**
- **Document reuse decisions**
- **Report efficiency improvements**

## 🔧 Implementation Tools

### Code Analysis Tools
```python
class CodeAnalyzer:
    """Analyze code for efficiency and reusability."""

    async def analyze_codebase(self) -> CodebaseAnalysis:
        """Comprehensive codebase analysis."""
        return {
            "duplicate_functions": await self.find_duplicate_functions(),
            "unused_code": await self.find_unused_code(),
            "reuse_opportunities": await self.find_reuse_opportunities(),
            "complexity_metrics": await self.calculate_complexity(),
            "maintainability_score": await self.assess_maintainability()
        }
```

### Agent Capability Registry
```python
class CapabilityRegistry:
    """Registry of all agent capabilities to prevent duplication."""

    def __init__(self):
        self.capabilities = {}

    async def register_capability(self, agent_name: str, capability: str):
        """Register an agent capability."""
        if capability in self.capabilities:
            existing_agent = self.capabilities[capability]
            logger.warning(f"Capability '{capability}' already exists in {existing_agent}")
        else:
            self.capabilities[capability] = agent_name

    async def find_capability(self, capability: str) -> Optional[str]:
        """Find which agent has a capability."""
        return self.capabilities.get(capability)
```

## 📈 Continuous Improvement

### Efficiency Reviews
- **Weekly swarm efficiency assessments**
- **Monthly codebase complexity reviews**
- **Quarterly architecture optimization**
- **Annual technology stack evaluation**

### Learning from Experience
- **Track successful reuse cases**
- **Document lessons from duplication prevention**
- **Update rules based on swarm performance**
- **Share best practices across agents**

## 🚨 Enforcement & Monitoring

### Automatic Monitoring
- **Real-time duplicate detection**
- **Continuous code quality monitoring**
- **Performance impact assessment**
- **Dependency cycle detection**

### Agent Accountability
- **Efficiency score for each agent**
- **Reuse contribution tracking**
- **Code quality metrics**
- **Peer review requirements**

---

## 📋 Checklist for Swarm Actions

**Before any action, agents must complete:**

- [ ] **Searched existing codebase**
- [ ] **Found no duplicates**
- [ ] **Got swarm consensus**
- [ ] **Assessed code quality**
- [ ] **Planned for testing**
- [ ] **Updated documentation**
- [ ] **Considered maintenance impact**

**This ensures the swarm remains efficient, maintainable, and valuable over time.**

---

**Remember: Efficiency is not just about less code - it's about better code, smarter reuse, and sustainable growth.**
