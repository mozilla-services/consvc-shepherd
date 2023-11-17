## Adding Advertiser Paths

This is restricted to the Content Discovery Engineering team or AdOps.

1. From the main admin page, under the Contile subsection, click the Advertisers link to see the list of existing advertisers.
2. Find the advertiser in the list and click on that row.
3. Add new Urls associated with this advertiser. Each Url will have a country, domain, and path. Urls can be from different countries and domains (e.g. Amazon could have amazon.de in Germany and amazon.ca in Canada). Be careful not to add duplicate paths, as this will cause the snapshot publish step will fail.
    1. Select the Geolocation from the dropdown to select the country for the advertiser.
    2. Enter the advertising root domain, like www.mozilla.com, with no trailing forward slash.
    3. Enter the path, which at a minimum must be a /.
    4. Select the radio button for exact or prefix matching.
4. Click Save to persist the advertiser settings. Repeat 1-4 for each new advertiser.
5. Proceed to [Creating and Publishing a Snapshot](./createPublishSnapshots.md) to publish the updates to make them live in production.
6. Apply the same changes in staging