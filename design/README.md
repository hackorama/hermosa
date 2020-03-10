# Backend Design Notes

## Requirements

Fault tolerant low latency back end system that would be the backend system for both mobile and web frontends.

- Technology stack
- No downtime
- PII data handling
- Deployment Strategy
- Zero downtime patching

## High level design

TODO

### Technology stack

- Deployment
  - K8s
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
  - Envoy with Consul Connect and Ambassador because of better integration with K8s
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
- Observability, logging and metrics
  - ELK and Prometheus because of integration with K8s

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
Instead targeting a deployment platform like K8s allow us to deploy on premise and to any cloud vendor
since all top vendors provide k8s support.

Source repository(git), binary repository(nexus, artifactory) and CI/CD pipline(jenkins) integration to deploy and test (unit) dev builds (on demand by developer) and integration builds (nightly, full end to end integration).

### Zero downtime patching

For apps with k8s replicas, we can leverage k8s provided rolling upgrade and rollback to
roll out upgrades without application downtime.

The patch and the rolling upgrade is qualified on an internal staging server before rolling out.

Or if the app is an API server can leverage API gateway to do canary deployment of the patch to be production tested before promoting the canary to production.

Automation/integration between CI/CD pipeline and k8s management tools to automate canary deployments and/or rolling upgrades.
