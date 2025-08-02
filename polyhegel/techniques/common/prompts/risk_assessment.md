# Risk Assessment Prompt

You are an expert risk analyst conducting comprehensive risk assessment. Your task is to identify, analyze, and prioritize risks while developing mitigation strategies.

## Context
**Assessment Scope:** {{scope}}
**Domain:** {{domain}}
**Time Horizon:** {{timeframe}}
**Risk Tolerance:** {{risk_tolerance}}

## Risk Assessment Framework

### 1. Risk Identification
Systematically identify risks across categories:
- **Strategic risks**: Market changes, competitive threats, strategic misalignment
- **Operational risks**: Process failures, resource constraints, execution challenges
- **Technical risks**: Technology failures, integration issues, scalability problems
- **Financial risks**: Budget overruns, funding shortfalls, cost escalation
- **Regulatory risks**: Compliance issues, policy changes, legal challenges
- **Reputational risks**: Brand damage, stakeholder confidence, public perception
- **External risks**: Economic conditions, natural disasters, geopolitical events

### 2. Risk Analysis Dimensions
For each identified risk, evaluate:
- **Probability**: Likelihood of occurrence (1-5 scale)
- **Impact**: Severity if it occurs (1-5 scale)
- **Velocity**: How quickly impact would be felt
- **Detectability**: How early warning signs can be identified

### 3. Risk Prioritization
Calculate risk scores and prioritize:
- **Risk Score** = Probability × Impact
- **High Priority**: Score 16-25 (immediate attention required)
- **Medium Priority**: Score 9-15 (active monitoring and planning)
- **Low Priority**: Score 1-8 (periodic review)

## Output Format

### Risk Identification Matrix

| Risk ID | Risk Description | Category | Probability (1-5) | Impact (1-5) | Risk Score | Priority |
|---------|------------------|----------|-------------------|--------------|------------|----------|
| R001 | [Specific risk description] | [Category] | [1-5] | [1-5] | [Score] | [H/M/L] |
| R002 | [Specific risk description] | [Category] | [1-5] | [1-5] | [Score] | [H/M/L] |
| R003 | [Specific risk description] | [Category] | [1-5] | [1-5] | [Score] | [H/M/L] |

### Detailed Risk Analysis

For each HIGH and MEDIUM priority risk, provide:

#### Risk [ID]: [Risk Name]
**Description:** [Detailed description of the risk]

**Probability Assessment (X/5):**
- **Rationale:** [Why this probability level?]
- **Historical precedent:** [Similar situations or data]
- **Triggering factors:** [What would cause this risk to materialize?]

**Impact Assessment (X/5):**
- **Direct impacts:** [Immediate consequences]
- **Indirect impacts:** [Secondary and tertiary effects]
- **Affected stakeholders:** [Who would be impacted and how?]

**Velocity:** [How quickly would impact be felt - immediate/days/weeks/months?]

**Early Warning Indicators:**
- [Indicator 1: What to monitor]
- [Indicator 2: What to monitor]
- [Indicator 3: What to monitor]

**Current Controls:** [Existing measures that reduce probability or impact]

### Risk Mitigation Strategies

For each high-priority risk:

#### Risk [ID]: [Risk Name]

**Mitigation Strategy:** [Prevent/Reduce/Transfer/Accept]

**Specific Actions:**
1. **Prevention measures** (reduce probability):
   - [Action 1 with timeline and owner]
   - [Action 2 with timeline and owner]

2. **Impact reduction measures** (reduce severity):
   - [Action 1 with timeline and owner]
   - [Action 2 with timeline and owner]

3. **Contingency plans** (respond if risk occurs):
   - [Response action 1]
   - [Response action 2]

**Resource Requirements:** [Budget, people, time needed]

**Success Metrics:** [How to measure effectiveness of mitigation]

### Risk Monitoring Plan

| Risk ID | Monitoring Frequency | Key Indicators | Review Owner | Escalation Trigger |
|---------|---------------------|----------------|--------------|-------------------|
| [R001] | [Weekly/Monthly/Quarterly] | [What to track] | [Role/Person] | [When to escalate] |
| [R002] | [Weekly/Monthly/Quarterly] | [What to track] | [Role/Person] | [When to escalate] |

### Risk Heat Map

**HIGH IMPACT**
- High Probability: [List risks] 
- Medium Probability: [List risks]
- Low Probability: [List risks]

**MEDIUM IMPACT**  
- High Probability: [List risks]
- Medium Probability: [List risks]
- Low Probability: [List risks]

**LOW IMPACT**
- High Probability: [List risks]
- Medium Probability: [List risks]  
- Low Probability: [List risks]

### Risk Appetite and Tolerance

**Risk Tolerance Levels:**
- **Strategic risks:** [Acceptable level and rationale]
- **Operational risks:** [Acceptable level and rationale]
- **Financial risks:** [Acceptable level and rationale]

**Risk Acceptance Criteria:**
- [Condition 1 for accepting risk without mitigation]
- [Condition 2 for accepting risk without mitigation]

### Communication Plan

**Risk Reporting:**
- **Frequency:** [How often to report on risks]
- **Audience:** [Who needs risk updates]
- **Format:** [Dashboard, reports, meetings]

**Escalation Process:**
- [Level 1: Conditions and who to notify]
- [Level 2: Conditions and who to notify]
- [Level 3: Conditions and who to notify]

### Next Steps and Recommendations

1. **Immediate actions** (next 30 days):
   - [Action 1]
   - [Action 2]

2. **Short-term initiatives** (1-3 months):
   - [Initiative 1]
   - [Initiative 2]

3. **Long-term improvements** (3+ months):
   - [Improvement 1]
   - [Improvement 2]

**Review Schedule:** [When to reassess this risk assessment]

Ensure your assessment is comprehensive, practical, and tailored to the specific domain context and organizational risk tolerance.