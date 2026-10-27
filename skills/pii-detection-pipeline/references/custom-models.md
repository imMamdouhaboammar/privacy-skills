# Custom PII Detection Models (spaCy NER & AWS Macie)

## spaCy NER Custom Training

### Training Custom Entity Types

```python
"""
Train custom spaCy NER model for domain-specific PII entities.
"""

import spacy
from spacy.training import Example
import random


def create_training_data() -> list[tuple[str, dict]]:
    """
    Create training examples for custom PII entity types.

    Returns list of (text, annotations) tuples.
    """
    training_data = [
        (
            "Patient MRN 12345678 was admitted on 2024-01-15",
            {"entities": [(12, 20, "MEDICAL_RECORD_NUMBER")]}
        ),
        (
            "Employee CEL-00142 reported the incident",
            {"entities": [(9, 18, "EMPLOYEE_ID")]}
        ),
        (
            "Policy holder number PLH-2024-99887 filed a claim",
            {"entities": [(22, 35, "POLICY_NUMBER")]}
        ),
        (
            "The customer with loyalty ID LYL-A1B2C3 requested data export",
            {"entities": [(29, 39, "LOYALTY_ID")]}
        ),
    ]
    return training_data


def train_custom_ner(
    base_model: str = "en_core_web_lg",
    training_data: list = None,
    n_iter: int = 30,
    output_dir: str = "./custom_ner_model"
):
    """
    Fine-tune spaCy NER model with custom PII entity types.

    Args:
        base_model: Base spaCy model to fine-tune
        training_data: List of (text, annotations) tuples
        n_iter: Number of training iterations
        output_dir: Directory to save trained model
    """
    if training_data is None:
        training_data = create_training_data()

    nlp = spacy.load(base_model)

    # Get or create NER pipe
    if "ner" not in nlp.pipe_names:
        ner = nlp.add_pipe("ner", last=True)
    else:
        ner = nlp.get_pipe("ner")

    # Add custom entity labels
    custom_labels = set()
    for _, annotations in training_data:
        for ent in annotations.get("entities", []):
            custom_labels.add(ent[2])

    for label in custom_labels:
        ner.add_label(label)

    # Train
    optimizer = nlp.resume_training()
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != "ner"]

    with nlp.disable_pipes(*other_pipes):
        for iteration in range(n_iter):
            random.shuffle(training_data)
            losses = {}

            for text, annotations in training_data:
                doc = nlp.make_doc(text)
                example = Example.from_dict(doc, annotations)
                nlp.update([example], drop=0.35, sgd=optimizer, losses=losses)

            if iteration % 10 == 0:
                print(f"Iteration {iteration}, Losses: {losses}")

    nlp.to_disk(output_dir)
    return nlp
```

## AWS Macie Integration

### Architecture

```
S3 Buckets --> Macie Classification Jobs --> Findings --> EventBridge --> Lambda
                                                |                          |
                                                v                          v
                                        Security Hub              Remediation
                                        (centralized)             - Tag sensitive
                                                                  - Encrypt
                                                                  - Notify owner
                                                                  - Quarantine
```

### Macie Job Configuration

```python
"""
AWS Macie integration for cloud-native PII detection in S3 buckets.
"""

import boto3
from datetime import datetime


class MacieIntegration:
    """
    Configure and manage AWS Macie classification jobs for
    automated PII detection across S3 data stores.
    """

    def __init__(self, region: str = "us-east-1"):
        self.macie_client = boto3.client("macie2", region_name=region)

    def create_classification_job(
        self,
        bucket_name: str,
        job_name: str,
        custom_data_identifiers: list[str] = None,
        schedule: str = "ONE_TIME"
    ) -> str:
        """
        Create a Macie classification job for an S3 bucket.

        Args:
            bucket_name: Target S3 bucket
            job_name: Descriptive job name
            custom_data_identifiers: IDs of custom data identifier resources
            schedule: ONE_TIME or SCHEDULED

        Returns:
            Job ID
        """
        job_config = {
            "name": job_name,
            "description": f"PII detection scan for {bucket_name}",
            "jobType": schedule,
            "s3JobDefinition": {
                "bucketDefinitions": [
                    {
                        "accountId": self._get_account_id(),
                        "buckets": [bucket_name]
                    }
                ],
                "scoping": {
                    "includes": {
                        "and": [
                            {
                                "simpleScopeTerm": {
                                    "comparator": "STARTS_WITH",
                                    "key": "OBJECT_EXTENSION",
                                    "values": ["csv", "json", "txt", "pdf", "docx", "xlsx", "parquet"]
                                }
                            }
                        ]
                    }
                }
            },
            "managedDataIdentifierSelector": "ALL",
            "tags": {
                "Team": "Privacy Engineering",
                "Purpose": "PII Detection"
            }
        }

        if custom_data_identifiers:
            job_config["customDataIdentifierIds"] = custom_data_identifiers

        response = self.macie_client.create_classification_job(**job_config)
        return response["jobId"]

    def create_custom_data_identifier(
        self,
        name: str,
        description: str,
        regex: str,
        keywords: list[str] = None,
        maximum_match_distance: int = 50
    ) -> str:
        """
        Create a custom data identifier for organization-specific PII patterns.

        Returns:
            Custom data identifier ID
        """
        params = {
            "name": name,
            "description": description,
            "regex": regex,
            "maximumMatchDistance": maximum_match_distance
        }

        if keywords:
            params["keywords"] = keywords

        response = self.macie_client.create_custom_data_identifier(**params)
        return response["customDataIdentifierId"]

    def _get_account_id(self) -> str:
        """Get the current AWS account ID."""
        sts = boto3.client("sts")
        return sts.get_caller_identity()["Account"]

    def get_findings_summary(self, job_id: str) -> dict:
        """Get summary of findings from a classification job."""
        response = self.macie_client.list_findings(
            findingCriteria={
                "criterion": {
                    "classificationDetails.jobId": {
                        "eq": [job_id]
                    }
                }
            }
        )

        findings = []
        if response["findingIds"]:
            details = self.macie_client.get_findings(findingIds=response["findingIds"])
            findings = details["findings"]

        summary = {
            "total_findings": len(findings),
            "severity_counts": {},
            "entity_type_counts": {},
            "affected_objects": []
        }

        for finding in findings:
            severity = finding.get("severity", {}).get("description", "unknown")
            summary["severity_counts"][severity] = (
                summary["severity_counts"].get(severity, 0) + 1
            )

            sensitive_data = finding.get("classificationDetails", {}).get(
                "result", {}
            ).get("sensitiveData", [])

            for sd in sensitive_data:
                category = sd.get("category", "unknown")
                summary["entity_type_counts"][category] = (
                    summary["entity_type_counts"].get(category, 0)
                    + sd.get("totalCount", 0)
                )

            resource = finding.get("resourcesAffected", {}).get("s3Object", {})
            if resource:
                summary["affected_objects"].append(resource.get("key", "unknown"))

        return summary
```

## Confidence Scoring Framework

| Score Range | Confidence Level | Recommended Action |
|-------------|-----------------|-------------------|
| 0.95 - 1.00 | Very High | Auto-redact |
| 0.80 - 0.94 | High | Auto-redact with logging |
| 0.60 - 0.79 | Medium | Flag for human review |
| 0.40 - 0.59 | Low | Log only, no action |
| 0.00 - 0.39 | Very Low | Ignore |

## References

- Microsoft Presidio Documentation: microsoft.github.io/presidio
- spaCy NER Documentation: spacy.io/usage/linguistic-features#named-entities
- AWS Macie Documentation: docs.aws.amazon.com/macie
- Google Cloud DLP API Documentation
- NIST SP 800-188 — De-Identifying Government Datasets
- Article 29 WP Opinion 05/2014 on Anonymisation Techniques