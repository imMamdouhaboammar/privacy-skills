---
name: privacy-api-design
description: Use when design privacy API patterns including data subject API for DSAR
  endpoints, consent API for preference management, deletion API with cascading delete
  orchestration, and audit API for compliance reporting. Provides OpenAPI specifications,
  error handling, rate limiting, and authentication patterns. Do NOT use for generic
  mathematical computing or non-privacy algorithm benchmarking.
license: Apache-2.0
metadata:
  author: mukul975
  version: '1.0'
  domain: privacy
  subdomain: privacy-engineering
  tags: privacy-api, dsar-api, consent-api, deletion-api, openapi-specification
---

# Privacy API Design Patterns

## Overview

Privacy APIs provide programmatic interfaces for data subject rights exercise, consent management, data deletion, and audit logging. Well-designed privacy APIs enable organizations to automate compliance workflows, integrate with consent management platforms, and provide data subjects with self-service privacy controls. This skill covers API design patterns, OpenAPI specifications, authentication, and error handling for privacy-critical endpoints.

## API Architecture Overview

```
External Consumers                    Privacy API Gateway                    Backend Services
+------------------+                 +--------------------+                 +------------------+
| Data Subject App |----HTTPS/TLS--->| Authentication     |                 | DSAR Service     |
+------------------+                 | Rate Limiting      |----internal---->| Consent Service  |
                                     | Request Validation |                 | Deletion Service |
+------------------+                 | Audit Logging      |                 | Audit Service    |
| Partner Portal   |----HTTPS/TLS--->| Versioning         |                 | Identity Service |
+------------------+                 +--------------------+                 +------------------+
                                            |
+------------------+                        v
| Internal Systems |----mTLS-------->+--------------------+
+------------------+                 | Privacy Event Bus  |
                                     | (async processing) |
                                     +--------------------+
```

## 1. Data Subject API (DSAR Endpoints)

### OpenAPI Specification

The full OpenAPI 3.0 specification for data subject requests, identity verification, status polling, and data export endpoints is available in [DSAR OpenAPI Specification](references/openapi-spec.md).

## 2. Consent API

### Consent Preference Management

```yaml
paths:
  /consent/preferences:
    get:
      operationId: getConsentPreferences
      summary: Get current consent preferences for the authenticated user
      tags: [Consent]
      responses:
        '200':
          description: Current consent preferences
          content:
            application/json:
              schema:
                type: object
                properties:
                  subjectId:
                    type: string
                  preferences:
                    type: array
                    items:
                      $ref: '#/components/schemas/ConsentPreference'
                  lastUpdated:
                    type: string
                    format: date-time

    put:
      operationId: updateConsentPreferences
      summary: Update consent preferences (bulk update)
      tags: [Consent]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [preferences]
              properties:
                preferences:
                  type: array
                  items:
                    type: object
                    required: [purposeId, granted]
                    properties:
                      purposeId:
                        type: string
                      granted:
                        type: boolean
                      channels:
                        type: array
                        items:
                          type: string
                          enum: [email, sms, push, phone, postal]
      responses:
        '200':
          description: Preferences updated
          content:
            application/json:
              schema:
                type: object
                properties:
                  updated:
                    type: array
                    items:
                      $ref: '#/components/schemas/ConsentPreference'
                  consentReceiptId:
                    type: string
                    format: uuid
                    description: ID of the issued consent receipt

  /consent/purposes:
    get:
      operationId: listConsentPurposes
      summary: List all available consent purposes
      tags: [Consent]
      responses:
        '200':
          description: List of consent purposes
          content:
            application/json:
              schema:
                type: object
                properties:
                  purposes:
                    type: array
                    items:
                      type: object
                      properties:
                        purposeId:
                          type: string
                        name:
                          type: string
                        description:
                          type: string
                        category:
                          type: string
                          enum: [essential, functional, analytics, marketing]
                        mandatory:
                          type: boolean
                        defaultState:
                          type: boolean
                        dataCategories:
                          type: array
                          items:
                            type: string

  /consent/receipts/{receiptId}:
    get:
      operationId: getConsentReceipt
      summary: Retrieve a specific consent receipt
      tags: [Consent]
      parameters:
        - name: receiptId
          in: path
          required: true
          schema:
            type: string
            format: uuid
      responses:
        '200':
          description: Consent receipt
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ConsentReceipt'
```

## 3. Deletion API

### Cascading Delete Orchestration

The complete distributed cascading deletion orchestrator implementation (supporting parallel worker pools, dependency graphs, and compensating transactions) is documented in [Cascading Deletion Orchestration](references/deletion-orchestration.md).

## 4. Audit API

### Audit Log Query Endpoints

```yaml
paths:
  /audit/events:
    get:
      operationId: queryAuditEvents
      summary: Query privacy audit events
      tags: [Audit]
      security:
        - OAuth2: [audit:read]
      parameters:
        - name: subjectId
          in: query
          schema:
            type: string
        - name: eventType
          in: query
          schema:
            type: string
            enum: [data_access, consent_change, deletion, dsar_submitted, dsar_completed, breach_detected]
        - name: startDate
          in: query
          required: true
          schema:
            type: string
            format: date-time
        - name: endDate
          in: query
          required: true
          schema:
            type: string
            format: date-time
        - name: actorId
          in: query
          schema:
            type: string
        - name: page
          in: query
          schema:
            type: integer
            default: 1
        - name: perPage
          in: query
          schema:
            type: integer
            default: 50
            maximum: 200
      responses:
        '200':
          description: Audit events
          content:
            application/json:
              schema:
                type: object
                properties:
                  events:
                    type: array
                    items:
                      type: object
                      properties:
                        eventId:
                          type: string
                          format: uuid
                        eventType:
                          type: string
                        timestamp:
                          type: string
                          format: date-time
                        actorId:
                          type: string
                        actorType:
                          type: string
                          enum: [user, system, admin, api_client]
                        subjectId:
                          type: string
                        resource:
                          type: string
                        action:
                          type: string
                        purpose:
                          type: string
                        outcome:
                          type: string
                          enum: [success, failure, denied]
                        details:
                          type: object
                  pagination:
                    $ref: '#/components/schemas/Pagination'

  /audit/reports/compliance:
    get:
      operationId: getComplianceReport
      summary: Generate compliance audit report for a date range
      tags: [Audit]
      parameters:
        - name: startDate
          in: query
          required: true
          schema:
            type: string
            format: date
        - name: endDate
          in: query
          required: true
          schema:
            type: string
            format: date
        - name: format
          in: query
          schema:
            type: string
            enum: [json, pdf, csv]
            default: json
      responses:
        '200':
          description: Compliance report
          content:
            application/json:
              schema:
                type: object
                properties:
                  reportId:
                    type: string
                  generatedAt:
                    type: string
                    format: date-time
                  period:
                    type: object
                    properties:
                      start:
                        type: string
                      end:
                        type: string
                  summary:
                    type: object
                    properties:
                      totalDataAccesses:
                        type: integer
                      totalConsentChanges:
                        type: integer
                      totalDeletions:
                        type: integer
                      totalDSARs:
                        type: integer
                      accessDenials:
                        type: integer
                      policyViolations:
                        type: integer
```

## API Security Patterns

### Authentication and Authorization

| Endpoint Category | Auth Method | Scopes Required | Rate Limit |
|-------------------|-------------|-----------------|------------|
| DSAR (data subject) | OAuth2 PKCE / JWT | dsar:read, dsar:write | 10 req/min |
| DSAR (admin) | OAuth2 Client Credentials | dsar:admin | 100 req/min |
| Consent (data subject) | OAuth2 PKCE / JWT | consent:read, consent:write | 30 req/min |
| Deletion (internal) | mTLS + API key | deletion:execute | 5 req/min |
| Audit (compliance) | OAuth2 Client Credentials | audit:read | 50 req/min |

### Error Response Format

```json
{
  "error": {
    "code": "PRIVACY_001",
    "type": "identity_verification_required",
    "message": "Identity verification is required before processing this request",
    "details": {
      "verificationMethods": ["email_verification", "document_upload"],
      "supportUrl": "https://support.cipherengineeringlabs.com/privacy"
    },
    "requestId": "req_a1b2c3d4",
    "timestamp": "2026-03-14T10:30:00.000Z"
  }
}
```

## References

- OpenAPI Specification 3.1.0
- GDPR Articles 12-22 (Data Subject Rights)
- CCPA/CPRA Sections 1798.100-1798.135
- RFC 6749 — OAuth 2.0 Authorization Framework
- RFC 7519 — JSON Web Token (JWT)
- OWASP API Security Top 10 (2023)
- Google Privacy Sandbox API Design Guidelines
- Apple App Tracking Transparency API Design Patterns