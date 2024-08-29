# Boostr Data Sync Cron

The Boostr data sync process documented in the [SyncBoostrData.md](syncBoostrDataCron.md) document is orchestrated by a [Kubernetetes Cronjob](https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/) that is maintained in the [topsites](https://github.com/mozilla-services/cloudops-infra/tree/master/projects/topsites) project of the 
[Cloud Ops Infra](https://github.com/mozilla-services/cloudops-infra/tree/master) repository. 

### How it runs

The CronJob spins up a new pod on a configurable schedule using the latest container image of the Shepherd application. It then triggers the 
[sync_boostr_data.py](consvc_shepherd/management/commands/sync_boostr_data.py) script within the pod. Refer to [SyncBoostrData.md](syncBoostrDataCron.md) to understand more about the inner workings of the script.



### A Note on Secrets

Secrets such as the email and password used to access the Boostr API are stored in 1Pass, BUT the CronJob resource does not retrieve the secrets from 1Pass. Instead, they are stored somewhere by SRE and pulled dynamically by the deployment processes established by SRE. Please contact the [SRE](https://mozilla.enterprise.slack.com/archives/C019WG3TTM2) team for more info on this process.


### Debugging and troubleshooting

Debugging involves accessing the `shepherd-boostr-sync` pods that are created by the cronjob resource and inspecting the logs. 

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
8. Select the latest runnning cronjob `shepherd-boostr-sync` pod. Note that the cronjob spins up a new pod each time it runs but does not destroy older pods was the process has completed.

9. Access the logs for the pod
```
pres l on the keyboard
```
