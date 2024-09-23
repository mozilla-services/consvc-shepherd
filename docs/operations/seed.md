# Seed Shepherd DB with Random Data

The [seed script](../../consvc_shepherd/management/commands/seed.py) generates mock data to test various [models we have](../../consvc_shepherd/models.py) and their functionality. It uses the [Faker library](https://faker.readthedocs.io/en/master/) to generate realistic random data such as names, countries to populate our local dev database with randomized entries for models such as
BoostrDeal, Campaign, and others, which can then be viewed and
managed through the admin interface.

As new models are added in the future, we should consider including them in the seed script to make it easier to see how all the models interact.

## How to Run

1. Run Shepherd locally and exec into the Shepherd container to run the script:
    ```shell
    docker exec -it consvc-shepherd-app-1 bash # can also run with `make debug`

    python manage.py seed
    ```

1. The script will output a success message once the database has been seeded:
    ```shell
    Successfully seeded the database with random data
    ```
1. Next, access the admin panel on [http://0.0.0.0:7001/admin](http://0.0.0.0:7001/admin) or exec into the local database to visualize the models. For example, this is how the BoostrDeal table looks when seeded with random data:
    ```shell
    id | boostr_id |                  name                  |         advertiser         | currency | amount | sales_representatives | start_date |  end_date  |          created_on           |          updated_on           
    ----+-----------+----------------------------------------+----------------------------+----------+--------+-----------------------+------------+------------+-------------------------------+-------------------------------
    1  |         1 | Deal 1 - Austin Inc                    | Jones-Walsh                | €        | 196990 | Debbie Brown          | 2024-04-18 | 2024-10-18 | 2024-09-23 18:40:55.196291+00 | 2024-09-23 18:40:55.196293+00
    2  |         2 | Deal 2 - Caldwell Group                | Williams, Pugh and English | €        | 183838 | Paul Mcguire          | 2024-03-04 | 2024-11-24 | 2024-09-23 18:40:55.197087+00 | 2024-09-23 18:40:55.197089+00
    3  |         3 | Deal 3 - Landry-Mitchell               | Baker Group                | £        | 173672 | Lauren Hill           | 2024-01-31 | 2024-11-13 | 2024-09-23 18:40:55.1978+00   | 2024-09-23 18:40:55.197803+00
    4  |         4 | Deal 4 - Swanson-Martin                | Pace, Johnson and Robbins  | €        | 144987 | John Fisher           | 2024-08-05 | 2024-10-26 | 2024-09-23 18:40:55.19852+00  | 2024-09-23 18:40:55.198522+00
    5  |         5 | Deal 5 - Jackson, Leonard and Flores   | Parker-Scott               | €        |  79479 | Gina Garcia           | 2024-06-28 | 2024-09-29 | 2024-09-23 18:40:55.199237+00 | 2024-09-23 18:40:55.199239+00
    6  |         6 | Deal 6 - Conner PLC                    | Davis-Taylor               | $        | 160330 | Joseph Mcgrath        | 2024-09-22 | 2024-10-20 | 2024-09-23 18:40:55.19989+00  | 2024-09-23 18:40:55.199893+00
    7  |         7 | Deal 7 - Hopkins, Estes and Richardson | Griffith Group             | £        | 103188 | Donna Singleton MD    | 2024-04-09 | 2024-10-02 | 2024-09-23 18:40:55.20058+00  | 2024-09-23 18:40:55.200582+00
    8  |         8 | Deal 8 - Nguyen-Johnson                | Hanna PLC                  | €        | 197414 | Nicholas Clark        | 2024-06-29 | 2024-10-10 | 2024-09-23 18:40:55.201329+00 | 2024-09-23 18:40:55.201331+00
    9  |         9 | Deal 9 - Patton, Graham and Mendoza    | Scott-Hogan                | £        | 147552 | Theresa Morris        | 2024-09-01 | 2024-11-13 | 2024-09-23 18:40:55.202145+00 | 2024-09-23 18:40:55.202147+00
    10 |        10 | Deal 10 - Jackson, Campos and Webb     | Martinez Inc               | €        |  52764 | Darren Martin         | 2024-02-01 | 2024-11-27 | 2024-09-23 18:40:55.202924+00 | 2024-09-23 18:40:55.202926+00
    (10 rows)
    ```

## Notes

1. Use this script when developing or testing the consvc_shepherd models, verifying that the admin interface displays data correctly, or when you need a fully populated database for testing purposes.
1. This script is intended to be run manually during development and should not be executed by our unit tests.