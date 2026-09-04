# DATA PROVENANCE SCHEMA

Every dataset introduced into the `data/` directory must be accompanied by a `metadata.json` file conforming to this provenance schema to ensure strict scientific reproducibility.

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Sangam Vidyut Dataset Provenance",
  "type": "object",
  "properties": {
    "dataset_id": {
      "type": "string",
      "description": "Unique identifier (e.g., NSSO_CES_2022)"
    },
    "source_name": {
      "type": "string",
      "description": "Official name of the dataset"
    },
    "publisher": {
      "type": "string",
      "description": "Agency/Ministry (e.g., MoSPI, MNRE)"
    },
    "source_url": {
      "type": "string",
      "description": "URL where the data was acquired"
    },
    "access_date": {
      "type": "string",
      "format": "date",
      "description": "Date the file was downloaded"
    },
    "release_date": {
      "type": "string",
      "format": "date",
      "description": "Official publication date of the dataset"
    },
    "coverage_start": {
      "type": "string",
      "description": "Start of temporal coverage"
    },
    "coverage_end": {
      "type": "string",
      "description": "End of temporal coverage"
    },
    "geography": {
      "type": "string",
      "description": "Spatial extent (e.g., All India, State-level)"
    },
    "license": {
      "type": "string",
      "description": "Data license or access constraint (e.g., Open Data, Regulated)"
    },
    "version": {
      "type": "string",
      "description": "Publisher's version if applicable"
    },
    "checksum": {
      "type": "string",
      "description": "SHA-256 hash of the raw downloaded file"
    },
    "raw_filename": {
      "type": "string",
      "description": "Name of the file in data/raw/"
    },
    "processing_version": {
      "type": "string",
      "description": "Version of the ETL script used to clean it"
    },
    "notes": {
      "type": "string",
      "description": "Any manual assumptions or anomalies noted during acquisition"
    }
  },
  "required": ["dataset_id", "source_name", "publisher", "access_date", "checksum"]
}
```

## Lineage Rules
- A `data/processed/` file must document its parent `dataset_id`.
- The ABM configuration must document which processed files were used to sample agents.
