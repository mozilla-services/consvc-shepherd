# Sync BigQuery Data Cron Job

The Sync BigQuery data script documented in [SyncBigQueryData.md](./syncBigQueryData.md.md) is orchestrated by a [Kubernetetes Cronjob](https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/) that lives in the [webservices-infra](https://github.com/mozilla-it/webservices-infra) repository.

### How it runs

The CronJob spins up a new pod on a configurable schedule using the latest container image of the Shepherd application. It then triggers the 
[sync_bq_data.py](../../consvc_shepherd/management/commands/sync_bq_data.py) script within the pod. Refer to [SyncBoostrData.md](syncBoostrDataCron.md) to understand more about the inner workings of the script.

### Debugging, troubleshooting and viewing logs

Debugging involves accessing the `shepherd-bq-sync` pods that are created by the cronjob resource and inspecting the logs. 

There are many approaches but, with tools like [Gcloud CLI](https://cloud.google.com/sdk/docs/install), [kubectl](https://kubernetes.io/docs/reference/kubectl/), and [k9s](https://k9scli.io/) one can do the following:

1. Authenticate to Gcloud
```
gcloud auth login
```
2. Connect to the bastion for accessing the topsites project in Gcloud
```
gcloud compute ssh --zone "us-central1-a" "bastion-us-central1" --project "moz-fx-bastion-nonprod-global" --ssh-flag="-D" --ssh-flag="5001" --ssh-flag="-N" --tunnel-through-iap
``` 
3. Get credentials for topsites. Use  topsites-prod-v1 for produuction
```
gcloud container clusters get-credentials topsites-nonprod-v1 --region us-west1 --project moz-fx-topsites-nonprod-619d
```
4. Set the local proxy
```
export HTTPS_PROXY=socks5://127.0.0.1:5001
```
5. Switch to the topsites-dev namespace
```
kubectl config set-context --current --namespace=dev-topsites
```
6. Login to k9s
```
k9s
```
7. Access all pods
```
type :pods, then press enter on the keyboard
```
8. Select the latest runnning cronjob `shepherd-bq-sync` pod. Note that the cronjob spins up a new pod each time it runs but does not destroy older pods once the process has completed.

9. Access the logs for the pod
```
press l on the keyboard
```

Below are steps for viewing logs through the GCP console

1. Access the topsites project
```
https://console.cloud.google.com/logs/query;project=moz-fx-topsites-prod-6d32
```

2. Use the query input field to search for logs for the shepherd-bq-sync pods
```
resource.labels.namespace_name="dev-topsites"
resource.labels.container_name="shepherd"
resource.labels.pod_name:"shepherd-bq-sync"
```
