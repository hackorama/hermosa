# Backend Design Notes

## Requirements

Fault tolerant low latency back end system that would be the backend system for both mobile and web frontends.

- [System Design](#system-design)
- [Technology stack](#technology-stack)
- [High level design principles](#high-level-design-principles)
- [No downtime](#no-downtime)
- [PII data handling](#pii-data-handling)
- [Deployment Strategy](#deployment-strategy)
- [Zero downtime patching](#zero-downtime-patching)

> For full size version of the inline design diagrams used, please download [design-diagrams.pdf](design-diagrams.pdf)

## System design

| High level system design diagram |
| :---: |
| ![High Level System Design](system-design.png) |
| High level system design that can be adapated to on premise or cloud hosted Kubernetes or cloud native deployments. Design details with design choice explained in the sections below. |

> Additional optional data processing integrations (A stream processing cluster like Spark, a data warehouse/lake etc.) are not shown but can be integrated if the system requires it. Auth services can be internal or external and will be centrally integrated with the API Gateway.

### Technology stack

| Example deployment stack on Kubernetes which can be on premise or on cloud |
| :---: |
| ![Example System Stack](example-system-stack.png) |
| This shows an example Kubernetes specific deployment of the system design. Kubernetes can be on premise or cloud hosted.|


| Example cloud native deployment stack specific to a cloud vendor like AWS |
| :---: |
| ![Cloud Native Stack](example-cloud-native-system-stack.png) |
| This shows how the system design can be easily adapted for a cloud native stack and deployment. |


| Deployment example using cloud hosted Kubernetes and cloud native services. |
| :---: |
| ![Cloud hosted Kubernetes](example-cloud-hosted-kubernetes-stack.png) |
| This shows the system design adapted for a hybrid approach, using some of the cloud native stack while the main application services are deployed on the cloud hosted Kuberenetes. |


| Kubernetes deployment of services with namespace separation |
| :---: |
| ![Kubernetes deployment](kubernetes-deployment.png) |
| Shows the details of a Kubernetes deployment of the application services. |


| Service technology stack examples at the Docker container and Kubernetes pod level |
| :---: |
| ![Service stack](example-service-stack.png) |
| Provides the application service level view of the technology stack. |


Above we have few example deployment topologies and technology stack options. There are many options for technology stack that will fit with the system design which are discussed below.

- Deployment
  - Kubernetes
  - Helm charts
- Workload Containers
  - Docker
- Languages
  - Java on server side apps as primary because most widely supported integrations and libraries so
we can integrate with other systems and frameworks easily.
  - Because of micro service architecture other languages can also be used for specific scenarios (Python for Machine learnig).
  - Front end for web apps will be JavasCript based.
- Application Containers
  - Selected on reliability and maturity
  - Netty if leveraging async event loops for responsiveness
  - Tomcat if using Spring boot since its embedded
- Data stores
  - Will depend on the type of application and CAP requirements and schema flexibility
  - Postgres/MySQL for RDBMS
  - Cassandra for  scalable distributed stores
  - MongoDB for  scalable document stores
  - Redis for scalable distributed key/value stores
  - Elastic for search
- Queus/Caches
  - Selected based on most widely used and feature rich and mature
  - Redis for shared cache/queue
  - Kafka for message queue
- Proxy
  - NGINX or HAProxy
- Service Mesh and API gateway
  - Envoy with Consul Connect and Ambassador because of better integration with Kubernetes
  - TODO: Must evaluate ishtio, kong etc.
- API model
  - REST based because of wide adoption and helps in integration with other systems
  - GraphQl and gRPC are only good for specific scenarios and is still behind REST in terms of adoption
  - REST is better for supporting mobile and web frontends together(instead of only web frontend using GraphQL)
  - Webhooks could be used for specific scenarios as needed
- Stream processing
  - Spark if we can afford a seprate cluster and the workload demands it
  - KafkaStreams - for light weight stream processing if we already have Kafka~
Frontend
  - Vue/React and not Angular for new projects
  - Async HTTP client like axios for making REST API calls from frontend
- Observability, logging and metrics
  - ELK and Prometheus because of integration with Kubernetes

## High level design principles

- Stateless shared-nothing horizontal scaling app servers
- Break services based on single responsibility and using the appropriate data system
  - Cart/Session using Redis, Order processing with PostgreSQL, Comments/Review using MongoDB etc.
- Load balanced ingress to REST API services used by mobile app and nodejs servers
- Web frontend will also be served by horizontally scaled nodjs servers through load balancer
- Distributed datastores should be selected and configured for easy cluster extension and node failure toleration
- Service mesh and api gateway for service discoverability and centralized API entrypoint and management
- Performance (latency, concurrency) consideration when designing apps and systems architecture
  - Reactive event driven design where applicable for concurrency
  - Queuing, caching, batching for distributed processing
  - Rate limit, Circuit breaker retries, queueing to avoid cascading failures
  - Regular Load, scalability tests to track performance regressions
  - Compression, batching for networking optimizations
  - CDN edge caches to offload static assets and caching policies
- Prefer mature and active technology over very new technology stack that may not get adoption
  - If trying out new technology make it easily swappable using an adapter/plugin layer
  - Try to leverage newer infra tooling outside the application code, especially on evolving ecosystem like Kubernetes
- Deployment strategies for HA, Failover, Disaster Recovery using geo separated multi-region DC's
- Strong CI/CD deployment quick code change to fully tested deployed cluster
- Along with features, keep focus on non-functional logging, observability, scaling etc.
- Deployment separation of platform infrastructure that could be shared by multiple application
- Application deployment isolation using namespaces and grouping using pods
- Security must be baked in from design, development to deployment
  - Leverage automated security scanning tools as part of CI/CD

### No downtime

Multiple replicas for HA, geo separated multi region instances for redundancy and disaster recovery.
For databases and data queues configure enough replicas for the expected failure toleration and
cross geo backups for database recovery in case of failures.

Network (DNS/proxy/gateway) strategies (ddos prevention, rate limiting) for auto failover
based on load/failure to other regions to minimise degraded performance.

### PII data handling

Track all PII data and minimize where they are stored and other systems they are shared with.
PII data in transit and in rest must be protected using minimising access to essential users/entities.
Leverage available format-preseving encryption, anonymization/masking solutions at the data store level.
Leverage PII data compliance/discovery/scanning tools for all existing legacy apps and data store.

### Deployment Strategy

If we want to target multiple clouds going cloud native will either tie us
into a specific cloud vendor or we have to do native deployment for each specific cloud vendor.
Instead targeting a deployment platform like Kubernetes allow us to deploy on premise and to any cloud vendor
since all top vendors provide Kubernetes support.

Source repository(git), binary repository(nexus, artifactory) and CI/CD pipline(jenkins) integration to deploy and test (unit) dev builds (on demand by developer) and integration builds (nightly, full end to end integration).

### Zero downtime patching

For apps with Kubernetes replicas, we can leverage Kubernetes provided rolling upgrade and rollback to
roll out upgrades without application downtime.

The patch and the rolling upgrade is qualified on an internal staging server before rolling out.

Or if the app is an API server can leverage API gateway to do canary deployment of the patch to be production tested before promoting the canary to production.

Automation/integration between CI/CD pipeline and Kubernetes management tools to automate canary deployments and/or rolling upgrades.
