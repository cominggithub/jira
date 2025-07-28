# Specification Index

This document lists all specification files in the spec folder and their purpose.

## Overview

This project consists of three main components, each with their own detailed specifications:

1. **Web Application** - Flask-based web interface for SONiC feature management
2. **CLI Tools** - Command-line utilities for data import and analysis
3. **MCP Server** - Model Context Protocol server for AI integration

## Specification Files

| File | Component | Purpose | Status |
|------|-----------|---------|--------|
| `web-spec.md` | Web Application | Complete web application specification including routes, templates, APIs | ✅ Available |
| `cli-spec.md` | CLI Tools | Command-line tools specification for importers and analyzers | ✅ Available |
| `mcp-server-spec.md` | MCP Server | MCP server specification for AI integration and tooling | ✅ Available |
| `zephyr-integration-spec.md` | Web Application | Zephyr Scale API integration specification | ✅ Available |
| `database-spec.md` | All Components | Database schema and operations specification | ✅ Available |

## Specification Structure

Each specification file follows this structure:

1. **Requirements** - Functional and non-functional requirements
2. **Feature Description** - Detailed feature overview and capabilities
3. **Configuration** - Configuration files and settings
4. **Test Criteria** - Testing requirements and acceptance criteria
5. **Source Code Structure** - Code organization and key files
6. **Temporary Folders** - Working directories and cache locations
7. **Test Files Structure** - Test organization and test data

## Maintenance Guidelines

- When updating any spec file, ensure this `spec.md` index is updated accordingly
- All specification changes must be reflected in the actual implementation
- Test criteria must be updated when features are modified
- Source code structure must match the actual project organization

## Related Documentation

- Main project documentation: `../README.md`
- Claude AI guidance: `../CLAUDE.md`
- Feature import guide: `../FEATURE_IMPORT_GUIDE.md`
- Test case import guide: `../TESTCASE_IMPORT_GUIDE.md`
- MCP demo guide: `../MCP_DEMO_README.md`