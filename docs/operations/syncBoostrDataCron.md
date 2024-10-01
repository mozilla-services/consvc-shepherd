# Boostr Data Sync Cron

The Boostr data sync process documented in the [SyncBoostrData.md](syncBoostrData.md) document is orchestrated by a [Kubernetetes Cronjob](https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/) that is maintained in the [shepherd chart](https://github.com/mozilla-it/webservices-infra/tree/main/ads/k8s/shepherd) in the [webservices-infra](https://github.com/mozilla-it/webservices-infra/tree/main) repo. 

### How it runs

The CronJob spins up a new pod on a configurable schedule using the latest container image of the Shepherd application. It then triggers the 
[sync_boostr_data.py](consvc_shepherd/management/commands/sync_boostr_data.py) script within the pod. Refer to [SyncBoostrData.md](syncBoostrDataCron.md) to understand more about the inner workings of the script.


### A Note on Secrets

Secrets such as the email and password used to access the Boostr API are stored in 1Pass. However, since k8s cronjobs are ultimately k8s pods running a container image, we follow best practices and mount environment variables and secrets to the resulting pods via k8s configmaps & secrets. In this context, non-sensitive key-value pairs are deployed using a configmap (defined in the [shepherd chart]'s values files), sensitive values are deployed using a secret (secrets are defined in Google Secret Manager secrets in tenant projects and synced into tenant namespaces using the `external-secrets operator`, see [here](https://mozilla-hub.atlassian.net/wiki/x/cQaqAQ) for more details).

The process SRE has recommended for storing/using secrets is as follows:

1. Secrets should be stored in 1password for use by individuals (e.g. the dev team)
2. GCPv2 tenant projects make use of Google Secret Manager to distribute secrets to deployments. Helm charts that are deployed to tenant namespaces should define an external-secret that syncs secret data down to k8s secrets from Google Secret Manager Secrets. [see](https://mozilla-hub.atlassian.net/wiki/x/cQaqAQ)
3. Tenant developers & admins can update Google Secret Manager secrets as necessary. Please follow the process defined in the previous step to do so.
5. As a result of the above, the values for the secret variables in #2 are set and available in the resource (pod / container) as environment variables.

### Debugging, troubleshooting and viewing logs

To view logs, use Logs Explorer. All GKE pod logs are forwarded to tenant projects for tenant viewers, developers and admins to look at. To filter for boostr data sync's logs explicitly, set the following filter:

```
labels."k8s-pod/app_kubernetes_io/component" =~ "^shepherd-cron-boostr-sync"
```

The following links should lead to the right place:

* [prod/prod](https://cloudlogging.app.goo.gl/VPZZgGHdFPvzVBzB7)
* [nonprod/stage](https://cloudlogging.app.goo.gl/qT3JmY6bcLw54Cwi9)

As an alternative, `gcloud logging read` can be used to retrieve logs via the CLI (follow [this guide](https://cloud.google.com/sdk/gcloud/reference/logging/read), to get more details). It is possible to retrieve logs via `kubectl` as well, setup requires some additional steps, though, since we're running on private clusters that need to be accessed via jumphosts(more info can be found [here](https://mozilla-hub.atlassian.net/wiki/x/TAiqAQ)).
