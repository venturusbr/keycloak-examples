# Python Simple Access Token with Roles Example

This is the first and simplest example.
In this example we will just configure some users, a client and some roles in Keycloak.
After, the resource server will use the access tokens to do authorization in its endpoints.

If this is your first time running the environment, so the first thing to be done is to run the following
*'docker-compose'* script from the root dir of the example(**/keycloak-examples/python-ex1*):

```sh
docker-compose -f docker-compose-import-realm.yml up --build --remove-orphans
```
This command will build all the containers and install the configurations on Keycloak.
**(Important): This command will not finish by itself, so we must press CTRL+C when the message of
Keycloak have stopped appears in console like the following:

```sh
auth_server_1   | 2022-11-10 12:27:26,424 INFO  [io.quarkus] (main) Keycloak stopped in 0.095s
```

Please note the existence of a test environment where many scenarios are covered to show
the authorization roles working and there is a user environment where someone can interact with the
resource server through OpenAPI and visual login. 

To run the tests environment we just need to execute the following command:
```sh
docker-compose -f docker-compose-test.yml up --build --remove-orphans
```

To run the interactive OpenAPI interface we need to execute the following command:
```sh
docker-compose -f docker-compose.yml up --build --remove-orphans
```
And then access the address http://127.0.0.1:8000/docs on your prefered browser! 

On both environments it is possible to just regenerate the resource server container without
having to wait for the database container and authserver to restart. If you have changed the
resource server code and want to update the only th running container you must execute the following
command(Note that it will rebuild and restart the container):

- For re-execute the resource server tests:
```sh
docker-compose -f docker-compose-test.yml up --detach --build resource_server
```

- For re-execute the resource server in interactive mode:
```sh
docker-compose up --detach --build resource_server
```

Following we have the auth pseudo schema, this can help on manual tests and to understand how
functions are working.

```yaml
Realm:
    python-ex1
Clients:
    - python-ex1
        Secret: 3RLY6WCCO4NWi54J7lFaQRjgBzfZlZ75
Users:
    - user1
        Password: test1
        Roles:
          - common_user
          - read_data
    - user2
        Password: test2
        Roles:
          - common_user
          - read_data
          - write_data
    - admin1
        Password: testa
        Roles:
          - admin_user
          - read_data
```