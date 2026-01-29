# TransUnion PDF to JSON - Documentation

## 📚 Documentation Index

Welcome to the project documentation. This directory contains all technical documentation for the TransUnion PDF to JSON API service.

---

## 📂 Structure

```
docs/
├── README.md                          # This file
├── planning/                          # Strategic & Requirements
│   └── architecture.md                # Technical architecture decisions
├── implementation/                    # Technical Documentation
│   └── fork-consolidation.md          # Fork consolidation implementation plan
└── deployment/                        # Deployment Guides
    └── vps_setup.md                   # VPS deployment guide
```

---

## 🗺️ Quick Navigation

### Planning Documents

| Document                                 | Description                              |
| ---------------------------------------- | ---------------------------------------- |
| [Architecture](planning/architecture.md) | System architecture and design decisions |

### Implementation Documents

| Document                                                   | Description                   | Status         |
| ---------------------------------------------------------- | ----------------------------- | -------------- |
| [Fork Consolidation](implementation/fork-consolidation.md) | Plan to merge fork components | 🟡 In Progress |

### Deployment Documents

| Document                                   | Description                          |
| ------------------------------------------ | ------------------------------------ |
| [VPS Setup Guide](deployment/vps_setup.md) | Complete VPS deployment instructions |

---

## 🔄 Documentation Workflow

Following the **ASD Framework** Single Source of Truth (SSOT) principle:

1. **Brain artifacts** are ephemeral (implementation plans, task checklists)
2. **Repository docs are canonical** (this directory)
3. After completing a feature, merge walkthrough content into appropriate docs

### Update Triggers

| Event                           | Required Updates                |
| ------------------------------- | ------------------------------- |
| Feature implementation complete | `docs/implementation/*.md`      |
| Architecture decision made      | `docs/planning/architecture.md` |
| Deployment changes              | `docs/deployment/*.md`          |

---

## 📖 See Also

- [README.md](../README.md) - Project overview and quick start
- [CONTRIBUTING.md](../CONTRIBUTING.md) - Contribution guidelines
- [LICENSE](../LICENSE) - Apache-2.0 license
