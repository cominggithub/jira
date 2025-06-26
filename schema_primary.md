# Primary Database Schema

**Generated:** 2025-06-26 16:24:51  
**Database Type:** PostgreSQL  
**Version:** PostgreSQL 17.4 on x86_64-pc-linux-gnu, compiled by gcc (Debian 12.2.0-14) 12.2.0, 64-bit  
**Connection:** `postgresql://postgres:k8sadmin@10.102.6.16:15432/ESTS_Dev`

## Overview

This database contains schema for SONiC (Software for Open Networking in the Cloud) feature and test management system. The schema supports tracking of both community SONiC features and Edgecore proprietary implementations across different branches and fabric configurations.

### Key Concepts

- **EC**: Edgecore Networks - hardware vendor
- **Feature Key**: Unique identifier for SONiC features (community and proprietary)
- **Community Branches**: 2111, 2211, 2311 refer to SONiC community release branches
- **Component**: JIRA Cloud component for issue tracking
- **VS**: Virtual Switch implementation
- **Fabric**: Network fabric implementation support

## Table of Contents

- [s_feature_label](#s-feature-label)
- [s_feature_map](#s-feature-map)
- [s_test_case](#s-test-case)
- [s_test_case_label](#s-test-case-label)

## Database Statistics

- **Total Tables:** 4
- **Total Columns:** 32

## Tables

### s_feature_label

**Type:** BASE TABLE

#### Columns

| Column | Type | Nullable | Default | Primary Key | Description |
|--------|------|----------|-------------|-------------|-------------|
| feature_key | character varying(255) | ❌ |  | 🔑 | Unique identifier for SONiC features (community and Edgecore proprietary) |
| label | character varying(255) | ❌ |  | 🔑 | Classification label or tag for the feature |
| created_at | timestamp without time zone | ✅ | CURRENT_TIMESTAMP |  | Timestamp when the record was created |

**Primary Keys:** feature_key, label

#### Foreign Keys

| Column | References Table | References Column |
|--------|------------------|-------------------|
| feature_key | s_feature_map | feature_key |

#### Indexes

- **s_feature_label_pkey** (UNIQUE) on feature_key
- **s_feature_label_pkey** (UNIQUE) on label

---

### s_feature_map

**Type:** BASE TABLE

#### Columns

| Column | Type | Nullable | Default | Primary Key | Description |
|--------|------|----------|-------------|-------------|-------------|
| feature_key | character varying(255) | ❌ |  | 🔑 | Unique identifier for SONiC features (community and Edgecore proprietary) |
| created_at | timestamp without time zone | ✅ | CURRENT_TIMESTAMP |  | Timestamp when the record was created |
| category | text | ✅ |  |  | Feature category classification |
| feature_n1 | text | ✅ |  |  | Feature name or title |
| ec_sonic_2111 | text | ✅ |  |  | Edgecore SONiC 2111 branch support status (community branch) |
| ec_sonic_2211 | text | ✅ |  |  | Edgecore SONiC 2211 branch support status (community branch) |
| ec_202211_fabric | text | ✅ |  |  | Edgecore 202211 fabric implementation support |
| ec_sonic_2311_x | text | ✅ |  |  | Edgecore SONiC 2311-x branch support status (community branch) |
| ec_sonic_2311_n | text | ✅ |  |  | Edgecore SONiC 2311-n branch support status (community branch) |
| vs_202311 | text | ✅ |  |  | Virtual Switch 202311 implementation support |
| vs_202311_fabric | text | ✅ |  |  | Virtual Switch 202311 fabric implementation support |
| ec_proprietary | text | ✅ |  |  | Edgecore proprietary feature implementation |
| component | text | ✅ |  |  | JIRA Cloud component associated with this feature |

**Primary Keys:** feature_key

#### Indexes

- **s_feature_map_pkey** (UNIQUE) on feature_key

---

### s_test_case

**Type:** BASE TABLE

#### Columns

| Column | Type | Nullable | Default | Primary Key | Description |
|--------|------|----------|-------------|-------------|-------------|
| test_case_id | character varying(255) | ❌ |  | 🔑 | Unique identifier for the test case |
| test_case_name | text | ✅ |  |  | Human-readable name of the test case |
| description | text | ✅ |  |  | Detailed description of what the test case covers |
| step | text | ✅ |  |  | Test execution steps and procedures |
| topology | text | ✅ |  |  | Network topology or test environment configuration |
| pytest_mark | text | ✅ |  |  | Pytest markers for test categorization and execution |
| validation | text | ✅ |  |  | Validation criteria and expected results |
| traffic_pattern | text | ✅ |  |  | Network traffic patterns used in testing |
| project_customer | text | ✅ |  |  | Associated project or customer information |
| time | text | ✅ |  |  | Estimated execution time or duration |
| note | text | ✅ |  |  | Additional notes and comments |
| created_at | timestamp without time zone | ✅ | CURRENT_TIMESTAMP |  | Timestamp when the record was created |

**Primary Keys:** test_case_id

#### Indexes

- **s_test_case_pkey** (UNIQUE) on test_case_id

---

### s_test_case_label

**Type:** BASE TABLE

#### Columns

| Column | Type | Nullable | Default | Primary Key | Description |
|--------|------|----------|-------------|-------------|-------------|
| test_case_id | character varying(255) | ❌ |  | 🔑 | Unique identifier for the test case |
| test_case_name | text | ✅ |  |  | Human-readable name of the test case |
| label | character varying(255) | ❌ |  | 🔑 | Classification label or tag for the feature |
| created_at | timestamp without time zone | ✅ | CURRENT_TIMESTAMP |  | Timestamp when the record was created |

**Primary Keys:** test_case_id, label

#### Foreign Keys

| Column | References Table | References Column |
|--------|------------------|-------------------|
| test_case_id | s_test_case | test_case_id |

#### Indexes

- **s_test_case_label_pkey** (UNIQUE) on label
- **s_test_case_label_pkey** (UNIQUE) on test_case_id

---

