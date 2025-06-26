# Cache Database Schema

**Generated:** 2025-06-26 16:24:51  
**Database Type:** SQLite  
**Version:** File not found  
**Connection:** `sqlite:///cache_dev.db`

## Overview

This database contains schema for SONiC (Software for Open Networking in the Cloud) feature and test management system. The schema supports tracking of both community SONiC features and Edgecore proprietary implementations across different branches and fabric configurations.

### Key Concepts

- **EC**: Edgecore Networks - hardware vendor
- **Feature Key**: Unique identifier for SONiC features (community and proprietary)
- **Community Branches**: 2111, 2211, 2311 refer to SONiC community release branches
- **Component**: JIRA Cloud component for issue tracking
- **VS**: Virtual Switch implementation
- **Fabric**: Network fabric implementation support

## Error

❌ **Database file cache_dev.db does not exist**

