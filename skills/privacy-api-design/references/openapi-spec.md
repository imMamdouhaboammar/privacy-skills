# DSAR OpenAPI Specification

```yaml
openapi: 3.1.0
info:
  title: Cipher Engineering Labs - Data Subject Rights API
  version: 1.0.0
  description: >
    API for data subjects to exercise their privacy rights under GDPR,
    CCPA/CPRA, and other applicable privacy regulations.
  contact:
    name: Privacy Engineering Team
    email: privacy-engineering@cipherengineeringlabs.com

servers:
  - url: https://api.cipherengineeringlabs.com/privacy/v1
    description: Production

security:
  - BearerAuth: []
  - OAuth2: [dsar:read, dsar:write]

paths:
  /dsar/requests:
    post:
      operationId: createDSARRequest
      summary: Submit a new data subject access request
      tags: [DSAR]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/DSARCreateRequest'
      responses:
        '202':
          description: Request accepted for processing
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/DSARResponse'
          headers:
            X-Request-ID:
              schema:
                type: string
                format: uuid
            Location:
              schema:
                type: string
                format: uri
        '400':
          $ref: '#/components/responses/BadRequest'
        '401':
          $ref: '#/components/responses/Unauthorized'
        '429':
          $ref: '#/components/responses/RateLimited'

    get:
      operationId: listDSARRequests
      summary: List data subject's own requests
      tags: [DSAR]
      parameters:
        - name: status
          in: query
          schema:
            type: string
            enum: [pending, in_progress, completed, rejected]
        - name: type
          in: query
          schema:
            type: string
            enum: [access, deletion, portability, rectification, restriction, objection]
        - name: page
          in: query
          schema:
            type: integer
            minimum: 1
            default: 1
        - name: per_page
          in: query
          schema:
            type: integer
            minimum: 1
            maximum: 100
            default: 20
      responses:
        '200':
          description: List of DSAR requests
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/DSARListResponse'

  /dsar/requests/{requestId}:
    get:
      operationId: getDSARRequest
      summary: Get status and details of a specific DSAR
      tags: [DSAR]
      parameters:
        - name: requestId
          in: path
          required: true
          schema:
            type: string
            format: uuid
      responses:
        '200':
          description: DSAR details
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/DSARDetailResponse'
        '404':
          $ref: '#/components/responses/NotFound'

  /dsar/requests/{requestId}/download:
    get:
      operationId: downloadDSARData
      summary: Download the data package for a completed access request
      tags: [DSAR]
      parameters:
        - name: requestId
          in: path
          required: true
          schema:
            type: string
            format: uuid
      responses:
        '200':
          description: Data package download
          content:
            application/zip:
              schema:
                type: string
                format: binary
          headers:
            Content-Disposition:
              schema:
                type: string
        '404':
          $ref: '#/components/responses/NotFound'
        '410':
          description: Download link has expired

components:
  schemas:
    DSARCreateRequest:
      type: object
      required:
        - requestType
        - email
        - identityVerification
      properties:
        requestType:
          type: string
          enum: [access, deletion, portability, rectification, restriction, objection]
          description: Type of data subject right being exercised
        email:
          type: string
          format: email
          description: Email address associated with the account
        identityVerification:
          type: object
          properties:
            method:
              type: string
              enum: [account_login, email_verification, document_upload]
            verificationToken:
              type: string
          required: [method]
        details:
          type: string
          maxLength: 2000
          description: Additional details about the request
        dataCategories:
          type: array
          items:
            type: string
            enum: [profile, transactions, communications, analytics, marketing, all]
          description: Specific data categories (for access/portability)
        rectificationData:
          type: object
          additionalProperties: true
          description: Corrected data values (for rectification requests)
        preferredFormat:
          type: string
          enum: [json, csv, pdf]
          default: json
          description: Preferred data export format (for access/portability)

    DSARResponse:
      type: object
      properties:
        requestId:
          type: string
          format: uuid
        status:
          type: string
          enum: [pending, identity_verification, in_progress, completed, rejected]
        requestType:
          type: string
        submittedAt:
          type: string
          format: date-time
        estimatedCompletionDate:
          type: string
          format: date-time
        regulatoryDeadline:
          type: string
          format: date-time
          description: Maximum date by which response must be provided

    DSARDetailResponse:
      allOf:
        - $ref: '#/components/schemas/DSARResponse'
        - type: object
          properties:
            statusHistory:
              type: array
              items:
                type: object
                properties:
                  status:
                    type: string
                  timestamp:
                    type: string
                    format: date-time
                  note:
                    type: string
            downloadAvailable:
              type: boolean
            downloadExpiresAt:
              type: string
              format: date-time

    DSARListResponse:
      type: object
      properties:
        data:
          type: array
          items:
            $ref: '#/components/schemas/DSARResponse'
        pagination:
          $ref: '#/components/schemas/Pagination'

    Pagination:
      type: object
      properties:
        page:
          type: integer
        perPage:
          type: integer
        totalPages:
          type: integer
        totalItems:
          type: integer

  responses:
    BadRequest:
      description: Invalid request parameters
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ErrorResponse'
    Unauthorized:
      description: Authentication required
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ErrorResponse'
    NotFound:
      description: Resource not found
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ErrorResponse'
    RateLimited:
      description: Rate limit exceeded
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ErrorResponse'
      headers:
        Retry-After:
          schema:
            type: integer
        X-RateLimit-Limit:
          schema:
            type: integer
        X-RateLimit-Remaining:
          schema:
            type: integer

  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
    OAuth2:
      type: oauth2
      flows:
        authorizationCode:
          authorizationUrl: https://auth.cipherengineeringlabs.com/oauth2/authorize
          tokenUrl: https://auth.cipherengineeringlabs.com/oauth2/token
          scopes:
            dsar:read: Read DSAR request status
            dsar:write: Submit DSAR requests
            consent:read: Read consent preferences
            consent:write: Update consent preferences
            audit:read: Read audit logs
```
