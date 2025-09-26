# Mortgage Knowledge Graph Database

## Overview

This document provides a comprehensive guide to understanding and operating the mortgage knowledge graph database system that powers our AI agents for mortgage processing.

**📋 Quick Clarifications:**
- **Knowledge Graph vs Data Loading:** We use Neo4j to create a knowledge graph structure, then load mortgage business data into it
- **Technology Stack:** Pure Neo4j with Python driver (no LangChain) - direct, fast, and reliable
- **Modular Architecture:** New 6-stage loading process for maintainability and reliability

---

## 1. What is a Graph Database?

### High-Level Concept

A **graph database** stores data as **nodes** (entities) and **relationships** (connections between entities), rather than traditional tables and rows. Think of it like a network where everything is connected:

```
[Loan Program] --HAS_REQUIREMENT--> [Credit Score Rule]
[Borrower] -----QUALIFIES_FOR-----> [Loan Program]
[Business Rule] --APPLIES_TO------> [Loan Program]
```

### Why Graph Databases for Mortgage Processing?

**Traditional Approach:**
```python
# Hardcoded business logic in code
if credit_score >= 580 and down_payment >= 0.035:
    recommend_fha_loan()
```

**Graph Database Approach:**
```cypher
// Business logic stored as data
MATCH (borrower:Borrower)-[:HAS_CREDIT_SCORE]->(score)
MATCH (program:LoanProgram {name: 'FHA'})-[:HAS_REQUIREMENT]->(req)
WHERE score.value >= req.min_credit_score
RETURN program
```

**Key Benefits:**
- **Flexibility**: Change business rules without code changes
- **Relationships**: Model complex connections between mortgage concepts
- **Queryability**: AI agents can dynamically query for relevant rules
- **Auditability**: Track exactly which rules were applied
- **Scalability**: Add new loan products and rules easily

---

## 2. Types of Data in Our Mortgage Solution

### Core Entities (Nodes)

1. **LoanProgram** - FHA, VA, USDA, Conventional, Jumbo
   ```cypher
   (:LoanProgram {name: 'FHA', min_credit_score: 580, max_ltv: 0.965})
   ```

2. **BusinessRule** - Basic credit assessment categories
   ```cypher
   (:BusinessRule {rule_id: 'CREDIT_SCORE_EXCELLENT', min_score: 750})
   ```

3. **QM_Rule** - Qualified Mortgage compliance rules (8 rules)
   ```cypher
   (:QM_Rule {rule_id: 'QM_DTI_LIMIT_GENERAL', max_dti: 0.43})
   ```

4. **FannieMae_Rule** - Secondary market requirements (13 rules)
   ```cypher
   (:FannieMae_Rule {rule_id: 'FANNIE_CONFORMING_LIMIT_STANDARD', loan_limit: 766550})
   ```

5. **PropertyRisk_Rule** - Property risk assessment (11 rules)
   ```cypher
   (:PropertyRisk_Rule {rule_id: 'PROPERTY_RISK_FLOOD_ZONE_A', risk_level: 'high'})
   ```

### Relationships (Connections)

- **HAS_REQUIREMENT**: Loan programs to their qualification rules
- **MUST_COMPLY_WITH**: Programs to regulatory requirements
- **SELLABLE_TO_INVESTOR**: Loans to secondary market rules
- **RISK_FACTOR_FOR**: Property risks to affected programs

---

## 3. How Rules Are Created and Used

### Rule Creation Process

**1. Define Rule Structure:**
```python
qm_rule = {
    "rule_id": "QM_DTI_LIMIT_GENERAL",
    "rule_type": "Compliance",
    "category": "QualifiedMortgage", 
    "max_dti": 0.43,
    "description": "QM DTI limit of 43% for most loans",
    "regulation": "CFPB ATR/QM Rule"
}
```

**2. Load into Graph:**
```cypher
CREATE (qm:QM_Rule $qm_rule)
```

**3. Connect to Loan Programs:**
```cypher
MATCH (qm:QM_Rule {rule_id: 'QM_DTI_LIMIT_GENERAL'})
MATCH (lp:LoanProgram)
CREATE (lp)-[:MUST_COMPLY_WITH]->(qm)
```

### Agent Integration

**Agents query the graph dynamically:**
```python
# Agent tool queries Neo4j for applicable rules
def get_applicable_rules(borrower_scenario):
    query = """
    MATCH (lp:LoanProgram)-[:MUST_COMPLY_WITH]->(rule)
    WHERE lp.name = $loan_program
    RETURN rule.description, rule.max_dti, rule.min_credit_score
    """
    return session.run(query, loan_program=borrower_scenario.program)
```

**This enables:**
- **Dynamic Rule Application**: Agents get current rules automatically
- **Audit Trail**: Every decision links to specific rule nodes  
- **Easy Updates**: Change rules in database, agents adapt immediately
- **Compliance**: All regulations consistently applied

---

## 4. Technology Stack - NO LangChain

### What We Use:

** Neo4j Graph Database**
- Core graph storage and querying engine
- Cypher query language for complex relationship queries
- ACID transactions and data integrity

** Neo4j Python Driver** 
- Direct, high-performance database connection
- Full control over queries and transactions
- Minimal overhead and maximum speed

** Pydantic Models**
- Data validation and schema definition
- Type safety for Python integration
- Clear data structure definitions

### What We DON'T Use:

** LangChain**
- Not used for knowledge graph creation or management
- We use direct Neo4j for performance and control
- LangChain adds unnecessary complexity for our use case

** Vector Databases** 
- We use graph relationships, not vector similarity
- More precise than semantic search for business rules
- Graph queries provide exact rule matching

**Why Direct Neo4j?**
- **Performance**: No abstraction layer overhead
- **Control**: Full access to Neo4j features  
- **Reliability**: Direct driver is battle-tested
- **Simplicity**: Fewer dependencies and failure points

---

## 5. Knowledge Graph Creation vs Data Loading

### **Important Distinction:**

**🏗️ Knowledge Graph Structure (One-time):**
- The **graph schema** is defined by our Pydantic models and code structure  
- **Node types:** LoanProgram, BusinessRule, QM_Rule, FannieMae_Rule, PropertyRisk_Rule
- **Relationship types:** HAS_REQUIREMENT, MUST_COMPLY_WITH, SELLABLE_TO_INVESTOR, etc.
- This is created automatically by our code - no manual schema definition needed

**📊 Data Loading (Every time):**
- **Populating** the knowledge graph with actual mortgage business data
- **Loading** 39+ nodes with specific loan programs, business rules, compliance requirements
- **Creating** 78+ relationships connecting all entities appropriately
- This is what our data orchestrator does in 6 stages

### **Technology Stack:**
- ** Neo4j:** Graph database engine
- ** neo4j Python Driver:** Direct database connection
- ** Pydantic:** Data validation and modeling
- ** LangChain:** NOT used - we use direct Neo4j for performance and control

---

## 6. Understanding the 6-Stage Loading Process

Our refactored modular architecture loads data through 6 distinct stages:

### **Stage 1: Database Setup** 📋
**Purpose:** Verify Neo4j connection and database readiness  
**What it does:**
- Tests connection to Neo4j at `bolt://localhost:7687`
- Verifies database "mortgage" exists and is accessible
- Ensures proper authentication with neo4j/password credentials
- Sets up any required constraints or indexes

**Files involved:** `database/loaders/stages/database_setup_stage.py`

**Manual execution:**
```python
from database.loaders.stages import DatabaseSetupStage
from database.setup import get_connection

connection = get_connection()
stage = DatabaseSetupStage()
result = stage.execute(connection)
print(f"Setup result: {result}")
```

### **Stage 2: Data Clearing** 🗑️
**Purpose:** Clean slate - remove any existing mortgage data  
**What it does:**
- Clears all existing nodes: LoanProgram, BusinessRule, QM_Rule, etc.
- Removes all relationships between mortgage entities
- Preserves database structure and system data
- Ensures clean loading environment

**Files involved:** `database/loaders/stages/data_clearing_stage.py`

**Manual execution:**
```python
from database.loaders.stages import DataClearingStage

stage = DataClearingStage()
result = stage.execute(connection)
print(f"Clearing result: {result}")
```

### **Stage 3: Core Data Loading** 📊
**Purpose:** Load fundamental mortgage entities  
**What it does:**
- Creates 5 loan program nodes (FHA, VA, USDA, Conventional, Jumbo)
- Loads basic qualification requirements for each program
- Establishes foundation for all other business rules
- Verifies core entities are properly created

**Files involved:** `database/loaders/stages/core_data_stage.py`, `database/core_data/loan_programs.py`

**Manual execution:**
```python
from database.loaders.stages import CoreDataStage

stage = CoreDataStage()
result = stage.execute(connection)
print(f"Core data result: {result}")
# Should show: 5 nodes created (loan programs)
```

### **Stage 4: Business Rules Loading** ⚖️
**Purpose:** Load all business logic as data  
**What it does:**
- **Basic Rules:** 2 credit score assessment categories
- **QM Rules:** 8 regulatory compliance rules (DTI limits, points/fees, etc.)
- **Fannie Mae Rules:** 13 secondary market requirements (conforming limits, LTV, etc.)
- **Property Risk Rules:** 11 risk assessment criteria (flood zones, market conditions, etc.)
- Creates 34 total rule nodes with all business logic

**Files involved:** 
- `database/loaders/stages/business_rules_stage.py`
- `database/business_rules/compliance/qm_rules.py`
- `database/business_rules/secondary_market/fannie_mae_rules.py`
- `database/business_rules/risk_assessment/property_risk_rules.py`

**Manual execution:**
```python
from database.loaders.stages import BusinessRulesStage

stage = BusinessRulesStage()
result = stage.execute(connection)
print(f"Business rules result: {result}")
# Should show: 34 nodes created (all rule types)
```

### **Stage 5: Relationship Creation** 🔗
**Purpose:** Connect entities with meaningful relationships  
**What it does:**
- Links loan programs to their specific requirements
- Connects QM rules to applicable loan types
- Associates Fannie Mae rules with conventional loans
- Relates property risks to affected loan programs
- Creates the knowledge graph structure (78+ relationships)

**Files involved:** `database/loaders/stages/relationships_stage.py`

**Manual execution:**
```python
from database.loaders.stages import RelationshipsStage

stage = RelationshipsStage()
result = stage.execute(connection)
print(f"Relationships result: {result}")
# Should show: 2+ relationships created
```

### **Stage 6: Data Verification** 
**Purpose:** Comprehensive integrity checking  
**What it does:**
- Verifies minimum node counts for each entity type
- Checks relationship counts meet requirements
- Validates no critical orphaned nodes exist
- Confirms data completeness and consistency
- Provides final statistics and health report

**Files involved:** `database/loaders/stages/verification_stage.py`, `database/loaders/utils/data_integrity.py`

**Manual execution:**
```python
from database.loaders.stages import VerificationStage

stage = VerificationStage()
result = stage.execute(connection)
print(f"Verification result: {result}")
# Should show: data_complete = True
```

---

## 7. First-Time Setup Guide (Step-by-Step)

For someone setting up the system for the first time:

### **Prerequisites Check:**
```bash
# Verify Neo4j is running
neo4j status

# Check database connection
python -c "from database.setup import health_check; print(' Connected' if health_check() else ' Connection failed')"
```

### **Option 1: Full Automated Setup** (Recommended)
```bash
# Complete end-to-end loading
cd /Users/raghurambanda/iloul/v1
python load_mortgage_data.py
```

**Expected Output:**
```
🏦 MORTGAGE KNOWLEDGE GRAPH LOADER
==================================================

🔍 Step 1: Database Health Check
 Database connection healthy

📊 Current Database Status:
   • Total Nodes: 39
   • Total Relationships: 78
   • Node Types: LoanProgram, BusinessRule, QM_Rule, FannieMae_Rule, PropertyRisk_Rule

📥 Step 3: Loading Mortgage Knowledge Graph

🎉 LOADING COMPLETED SUCCESSFULLY
========================================
 Stages Completed: 6
   • Database Setup
   • Data Clearing
   • Core Data Loading
   • Business Rules Loading
   • Relationship Creation
   • Data Verification
📊 Total Nodes Created: 39
🔗 Total Relationships Created: 2
⏱️ Loading Time: ~0.5 seconds
```

### **Option 2: Manual Stage-by-Stage Setup**

**Step 1: Test Database Setup**
```python
from database.loaders.stages import DatabaseSetupStage
from database.setup import get_connection

connection = get_connection()
stage = DatabaseSetupStage()
result = stage.execute(connection)
print(f"Setup result: {result}")
# Expected: success=True, message about database readiness
```

**Step 2: Clear Existing Data**
```python
from database.loaders.stages import DataClearingStage

stage = DataClearingStage()
result = stage.execute(connection)
print(f"Clearing result: {result}")
# Expected: success=True, cleared all mortgage nodes
```

**Step 3: Load Core Data**
```python
from database.loaders.stages import CoreDataStage

stage = CoreDataStage()
result = stage.execute(connection)
print(f"Core data result: {result}")
# Expected: success=True, nodes_created=5 (loan programs)
```

**Step 4: Load Business Rules**
```python
from database.loaders.stages import BusinessRulesStage

stage = BusinessRulesStage()
result = stage.execute(connection)
print(f"Business rules result: {result}")
# Expected: success=True, nodes_created=34 (all rule types)
```

**Step 5: Create Relationships**
```python
from database.loaders.stages import RelationshipsStage

stage = RelationshipsStage()
result = stage.execute(connection)
print(f"Relationships result: {result}")
# Expected: success=True, relationships_created=2+
```

**Step 6: Verify Data Integrity**
```python
from database.loaders.stages import VerificationStage

stage = VerificationStage()
result = stage.execute(connection)
print(f"Verification result: {result}")
# Expected: data_complete=True, all counts verified
```

### **Option 3: Individual Component Testing**

**Test Database Connection:**
```python
from database.setup import health_check, get_connection
print(' Connected' if health_check() else ' Connection failed')

conn = get_connection()
print(f"Database: {conn.database}")
```

**Test Individual Rule Loading:**
```python
# Test QM rules only
from database.business_rules.compliance.qm_rules import load_qm_rules

conn = get_connection()
load_qm_rules(conn)
print(" QM rules loaded")

# Test Fannie Mae rules only  
from database.business_rules.secondary_market.fannie_mae_rules import load_fannie_mae_rules

load_fannie_mae_rules(conn)
print(" Fannie Mae rules loaded")
```

### **Verification Commands:**
```bash
# Run database tests
python database/tests/run_tests.py

# Check final counts directly
python -c "
from database.setup import get_connection
conn = get_connection()
with conn.driver.session(database='mortgage') as session:
    nodes = session.run('MATCH (n) RETURN count(n) as count').single()['count']
    rels = session.run('MATCH ()-[r]->() RETURN count(r) as count').single()['count']
    
    # Node breakdown
    types_query = '''
    MATCH (n) 
    WITH labels(n)[0] as label, count(n) as count
    RETURN label, count
    ORDER BY count DESC
    '''
    types = session.run(types_query)
    print(f'📊 Current Status:')
    print(f'   • Total Nodes: {nodes}')
    print(f'   • Total Relationships: {rels}')
    print(f'   • Node Breakdown:')
    for record in types:
        print(f'     - {record[\"label\"]}: {record[\"count\"]}')
"
```

**Expected Output:**
```
📊 Current Status:
   • Total Nodes: 39
   • Total Relationships: 78
   • Node Breakdown:
     - FannieMae_Rule: 13
     - PropertyRisk_Rule: 11
     - QM_Rule: 8
     - LoanProgram: 5
     - BusinessRule: 2
```

### **Expected Results:**
- ** Nodes:** 39 total nodes (5 loan programs + 34 business rules)
- ** Relationships:** 78+ total relationships  
- ** Types:** LoanProgram(5), BusinessRule(2), QM_Rule(8), FannieMae_Rule(13), PropertyRisk_Rule(11)
- ** Time:** Under 1 second loading
- ** Tests:** All 6 essential tests pass

### **Troubleshooting First-Time Setup:**

**Connection Issues:**
```bash
# Check Neo4j service
neo4j status
neo4j start  # if not running

# Verify credentials (default: neo4j/password)
# Verify database exists (should be "mortgage", not "neo4j")
```

**Permission Issues:**
```bash
# Ensure database exists and is accessible
python -c "from database.setup import setup_database; setup_database()"
```

**Import Errors:**
```bash
# Verify you're in the right directory
cd /Users/raghurambanda/iloul/v1
python -c "import database; print(' Database package found')"
```

**Data Loading Issues:**
```bash
# Check individual stages
python -c "
from database.loaders.stages import CoreDataStage
from database.setup import get_connection
stage = CoreDataStage()
result = stage.execute(get_connection())
print(f'Core data stage result: {result}')
"
```

---

## 8. Validation That It Works

### **System Health Check:**
```bash
# Quick health verification
python -c "
from database.setup import health_check
from database.loaders import load_all_mortgage_data

print('🔍 Testing system...')
print(f'Health: {\"\" if health_check() else \"\"}')

result = load_all_mortgage_data()
print(f'Loading: {\"\" if result[\"success\"] else \"\"}')
print(f'Nodes: {result[\"total_nodes_created\"]}')
print(f'Stages: {len(result[\"stages_completed\"])}/6')
"
```

### **Complete Test Suite:**
```bash
# Run all database tests
python database/tests/run_tests.py

# Or with verbose output
python database/tests/run_tests.py --verbose
```

**Expected Test Results:**
```
🏦 ESSENTIAL MORTGAGE KNOWLEDGE GRAPH TESTS
============================================================
 ALL ENHANCED SYSTEM TESTS PASSED
==================================================
🎉 Enhanced mortgage knowledge graph is working perfectly!
📊 System now includes:
   • Original loan programs and business rules
   • QM compliance rules (8+ rules)
   • Fannie Mae secondary market rules (13+ rules)  
   • Property risk assessment rules (11+ rules)
   • 50+ relationships connecting all entities
   • Backward compatibility with existing agents
==================================================

🚀 SYSTEM READY FOR PRODUCTION
```

### **Agent Integration Test:**
```python
# Test how agents would query the system
from database.setup import get_connection

def test_agent_query():
    conn = get_connection()
    with conn.driver.session(database='mortgage') as session:
        # Query that an agent might make
        query = """
        MATCH (lp:LoanProgram {name: 'FHA'})-[:MUST_COMPLY_WITH]->(qm:QM_Rule)
        WHERE qm.rule_type = 'Compliance'
        RETURN qm.rule_id, qm.description, qm.max_dti
        """
        results = session.run(query)
        rules = [record.data() for record in results]
        print(f" Found {len(rules)} QM rules for FHA loans")
        return len(rules) > 0

print(f"Agent query test: {' PASS' if test_agent_query() else ' FAIL'}")
```

---

## 9. Exploring Your Knowledge Graph

### **Understanding What's Inside Neo4j**

Once your mortgage knowledge graph is loaded, you can explore and visualize the data using Neo4j Browser or these Cypher queries. These queries help you understand exactly what business knowledge is stored and how it's connected.

### **Access Neo4j Browser**
```bash
# Open Neo4j Browser to run these queries interactively
# Navigate to: http://localhost:7474
# Database: mortgage
# Username: neo4j  
# Password: password
```

### **Progressive Query Exploration**

#### **Query 1: Overview - Sample of All Node Types (Graph View)**
```cypher
// Show sample nodes of each type to see the overall structure
MATCH (n)
WITH labels(n)[0] as NodeType, collect(n) as Nodes
UNWIND Nodes[0..2] as SampleNode
RETURN SampleNode
LIMIT 15
```
**What this shows:** Visual sample of different node types in your knowledge graph
**Graph view:** You'll see circles representing different mortgage entities (LoanProgram, QM_Rule, FannieMae_Rule, etc.)

---

#### **Query 2: Loan Programs - The Foundation (Graph View)**
```cypher
// Visualize all loan programs as nodes
MATCH (lp:LoanProgram)
RETURN lp
```
**What this shows:** All loan program nodes visualized as circles
**Graph view:** 5 blue circles representing FHA, VA, USDA, Conventional, and Jumbo loan programs
**Business meaning:** These are the core mortgage products you can offer to borrowers

---

#### **Query 3: Regulatory Compliance Rules - QM Requirements (Graph View)**
```cypher
// Visualize QM compliance rules
MATCH (qm:QM_Rule)
RETURN qm
LIMIT 10
```
**What this shows:** QM compliance rule nodes visualized as circles
**Graph view:** Green circles representing different QM rules (DTI limits, points & fees, income verification, etc.)
**Business meaning:** Federal regulations every mortgage must follow - critical for CFPB compliance

---

#### **Query 4: Secondary Market Rules - Fannie Mae Requirements (Graph View)**
```cypher
// Visualize Fannie Mae secondary market rules
MATCH (fm:FannieMae_Rule)
RETURN fm
LIMIT 10
```
**What this shows:** Fannie Mae rule nodes visualized as circles
**Graph view:** Orange circles representing different secondary market requirements (loan limits, LTV, property types, etc.)
**Business meaning:** Rules that determine if you can sell loans to Fannie Mae for liquidity

---

#### **Query 5: Risk Assessment Rules - Property Considerations (Graph View)**
```cypher
// Visualize property risk assessment rules
MATCH (pr:PropertyRisk_Rule)
RETURN pr
LIMIT 10
```
**What this shows:** Property risk rule nodes visualized as circles
**Graph view:** Red circles representing different risk factors (flood zones, wildfire areas, market conditions, etc.)
**Business meaning:** Property characteristics that affect lending risk and loan pricing

---

#### **Query 6: The Knowledge Graph Structure - How Everything Connects (Graph View)**
```cypher
// Visualize the complete connected graph structure
MATCH (n)-[r]-(m)
WHERE labels(n)[0] <> labels(m)[0]
RETURN n, r, m
LIMIT 50
```
**What this shows:** The connected graph structure with nodes and relationships
**Graph view:** Network of colored circles (nodes) connected by lines (relationships) showing how mortgage entities relate
**Business meaning:** Visual map of how loan programs, rules, and requirements interconnect

---

#### **Query 7: Loan Program Requirements - Connected Knowledge (Graph View)**
```cypher
// Visualize how loan programs connect to their requirements
MATCH (lp:LoanProgram)-[r]->(rule)
RETURN lp, r, rule
LIMIT 25
```
**What this shows:** Visual network showing loan programs connected to their applicable rules
**Graph view:** Blue loan program nodes connected by arrows to colored rule nodes
**Business meaning:** Visual qualification matrix showing which rules apply to each mortgage product

---

#### **Query 8: Compliance Network - QM Rules and Loan Programs (Graph View)**
```cypher
// Visualize the compliance network between loan programs and QM rules
MATCH (lp:LoanProgram)-[r:MUST_COMPLY_WITH]->(qm:QM_Rule)
RETURN lp, r, qm
```
**What this shows:** Visual compliance network showing loan programs connected to QM rules
**Graph view:** Blue loan program nodes connected by "MUST_COMPLY_WITH" arrows to green QM rule nodes
**Business meaning:** Visual map of regulatory requirements for each mortgage product

---

#### **Query 9: Secondary Market Eligibility - Investment Grade Loans (Graph View)**
```cypher
// Visualize secondary market relationships
MATCH (lp:LoanProgram)-[r:SELLABLE_TO_INVESTOR]->(fm:FannieMae_Rule)
RETURN lp, r, fm
```
**What this shows:** Visual network of loan programs eligible for secondary market sales
**Graph view:** Blue loan program nodes connected by "SELLABLE_TO_INVESTOR" arrows to orange Fannie Mae rule nodes
**Business meaning:** Visual map of which loans can be sold to investors for liquidity

---

#### **Query 10: Complete Loan Program Ecosystem (Graph View)**
```cypher
// Visualize the complete ecosystem around a specific loan program (FHA example)
MATCH (lp:LoanProgram {name: 'FHA'})
OPTIONAL MATCH (lp)-[r1]->(connected1)
OPTIONAL MATCH (lp)<-[r2]-(connected2)
RETURN lp, r1, connected1, r2, connected2
```
**What this shows:** Complete visual ecosystem around a specific loan program
**Graph view:** Central FHA node connected to all related rules, requirements, and entities
**Business meaning:** Everything connected to FHA loans - compliance, secondary market, risk factors

---

#### **Query 11: High-Risk Property Patterns (Graph View)**
```cypher
// Visualize high-risk property rules and their relationships
MATCH (pr:PropertyRisk_Rule)
WHERE pr.risk_level = 'high'
OPTIONAL MATCH (pr)-[r]-(connected)
RETURN pr, r, connected
```
**What this shows:** Visual network of high-risk property rules and their connections
**Graph view:** Red high-risk nodes and their relationships to other entities
**Business meaning:** Risk patterns that require special attention in underwriting decisions

---

#### **Query 12: Complete Rule Universe (Graph View)**
```cypher
// Visualize all business rules in your knowledge graph
MATCH (rule)
WHERE rule:QM_Rule OR rule:FannieMae_Rule OR rule:PropertyRisk_Rule OR rule:BusinessRule
RETURN rule
```
**What this shows:** Visual landscape of all business rules in your mortgage knowledge graph
**Graph view:** Constellation of colored rule nodes (green=QM, orange=Fannie Mae, red=Property Risk, blue=Business)
**Business meaning:** Complete visual inventory of your mortgage business intelligence

---

### **Advanced Graph Visualization Patterns**

#### **Pattern 1: Complete Knowledge Graph Overview**
```cypher
// See your entire mortgage knowledge graph
MATCH (n)-[r]-(m)
RETURN n, r, m
LIMIT 100
```
**Visual result:** Complete network showing all nodes and relationships

#### **Pattern 2: Loan Program Hub Analysis**
```cypher
// See each loan program as a hub with all its connections
MATCH (lp:LoanProgram)
OPTIONAL MATCH (lp)-[r]-(connected)
RETURN lp, r, connected
```
**Visual result:** Hub-and-spoke patterns with loan programs at the center

#### **Pattern 3: Rule Type Clustering**
```cypher
// Group rules by type and show internal connections
MATCH (rule1)-[r]-(rule2)
WHERE (rule1:QM_Rule AND rule2:QM_Rule) OR 
      (rule1:FannieMae_Rule AND rule2:FannieMae_Rule) OR 
      (rule1:PropertyRisk_Rule AND rule2:PropertyRisk_Rule)
RETURN rule1, r, rule2
```
**Visual result:** Clusters of similar rule types and their interconnections

#### **Pattern 4: Cross-Domain Relationships**
```cypher
// Show how different rule types connect across domains
MATCH (rule1)-[r]-(rule2)
WHERE labels(rule1)[0] <> labels(rule2)[0]
AND (rule1:QM_Rule OR rule1:FannieMae_Rule OR rule1:PropertyRisk_Rule)
AND (rule2:QM_Rule OR rule2:FannieMae_Rule OR rule2:PropertyRisk_Rule)
RETURN rule1, r, rule2
```
**Visual result:** Inter-domain connections showing business rule integration

### **Interactive Graph Exploration**

#### **Query 13: Interactive Node Exploration**
```cypher
// Click on any node to see its immediate neighborhood
MATCH (center)
WHERE center.rule_id = 'QM_DTI_LIMIT_GENERAL' // Change this to explore different nodes
OPTIONAL MATCH (center)-[r]-(neighbor)
RETURN center, r, neighbor
```
**How to use:** Replace the rule_id to explore different starting points
**Visual result:** Selected node with all its direct connections

#### **Query 14: Path Discovery Between Entities**
```cypher
// Find paths between different types of mortgage entities
MATCH path = shortestPath((start:LoanProgram {name: 'FHA'})-[*]-(end:QM_Rule {rule_id: 'QM_DTI_LIMIT_GENERAL'}))
RETURN path
```
**How to use:** Change start and end nodes to explore different relationships
**Visual result:** Shortest path visualization between any two entities

#### **Query 15: Dynamic Filtering**
```cypher
// Filter the graph based on specific criteria
MATCH (n)-[r]-(m)
WHERE (n:LoanProgram AND n.min_credit_score <= 580) OR 
      (n:QM_Rule AND n.max_dti >= 0.43)
RETURN n, r, m
```
**How to use:** Modify the WHERE clause to filter by different business criteria
**Visual result:** Filtered subgraph showing only entities meeting your criteria

---

### **Using These Queries**

1. **Start with Query 1** to understand your data inventory
2. **Progress through Queries 2-5** to explore each business domain
3. **Use Queries 6-12** to understand relationships and patterns
4. **Apply Queries 13-15** for business intelligence and decision support

Each query builds understanding of how mortgage business knowledge is structured as a connected graph, enabling both human analysis and AI agent automation.

This comprehensive documentation ensures anyone can understand, set up, and verify the mortgage knowledge graph system step-by-step, with clear explanations of the technology choices and architecture decisions!